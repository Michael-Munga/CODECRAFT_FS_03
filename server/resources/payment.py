from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, Cart, CartItem, Order, OrderItem, User, Product
from mpesa_utils import mpesa_service
import os
from sqlalchemy.orm import joinedload
from sqlalchemy import and_

from logging_config import get_logger, log_exception
from request_tracking import PerformanceTimer

logger = get_logger('payment')

def mask_phone(phone: str) -> str:
    if not phone or len(phone) < 4:
        return "****"
    return "*" * (len(phone) - 4) + phone[-4:]

class PaymentResource(Resource):
    @jwt_required()
    def post(self):
        """Initiate M-Pesa payment for cart items with proper transaction handling"""
        try:
            # Begin transaction
            db.session.begin_nested()
            
            user_id = get_jwt_identity()
            # Get user with locking
            user = db.session.query(User).filter(User.id == user_id).with_for_update().first()
            if not user:
                return {"error": "User not found"}, 404
            
            # Get cart with items and locking
            with PerformanceTimer('db_query_payment'):
                cart = db.session.query(Cart)\
                    .options(joinedload(Cart.items).joinedload(CartItem.product))\
                    .filter_by(user_id=user_id).with_for_update().first()
                
            if not cart or not cart.items:
                return {"error": "Cart is empty"}, 400
            
            # Lock all products in the cart to prevent concurrent updates
            cart_item_ids = [item.id for item in cart.items]
            cart_product_ids = [item.product_id for item in cart.items]
            
            # Get products with locking to check stock
            locked_products = db.session.query(Product)\
                .filter(Product.id.in_(cart_product_ids))\
                .with_for_update().all()
            
            # Validate stock availability
            insufficient_stock = []
            with PerformanceTimer('stock_validation'):
                for cart_item in cart.items:
                    if cart_item.product.stock < cart_item.quantity:
                        insufficient_stock.append({
                            'product_name': cart_item.product.name,
                            'available': cart_item.product.stock,
                            'requested': cart_item.quantity
                        })
            
            if insufficient_stock:
                return {
                    "error": "Insufficient stock for some items",
                    "details": insufficient_stock
                }, 400
            
            # Calculate total amount
            total_amount = sum(item.product.price * item.quantity for item in cart.items)
            
            # Get phone number from request or user profile
            data = request.get_json()
            phone_number = data.get("phone_number") or user.phone_number
            if not phone_number:
                return {"error": "Phone number is required"}, 400
            
            # Format phone number (ensure it starts with 254)
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            elif phone_number.startswith("+"):
                phone_number = phone_number[1:]
            
            # Initiate STK push
            account_ref = f"ORDER-{user_id}-{cart.id}"
            transaction_desc = f"Payment for order by {user.full_name}"
            
            with PerformanceTimer('mpesa_stk_push'):
                response = mpesa_service.initiate_stk_push(
                    phone_number=phone_number,
                    amount=int(total_amount),
                    account_reference=account_ref,
                    transaction_desc=transaction_desc
                )
            
            if "error" in response:
                return {"error": response["error"]}, 400
            
            # Create order
            order = Order(
                user_id=user_id,
                total_amount=total_amount,
                status="pending"
            )
            db.session.add(order)
            db.session.flush()  # Get order ID without committing
            
            # Create order items and reserve stock
            for cart_item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                db.session.add(order_item)
                
                # Deduct stock from product
                cart_item.product.stock -= cart_item.quantity
            
            # Save checkout request ID for later verification
            order.mesa_checkout_request_id = response.get("CheckoutRequestID")
            
            # Clear cart items
            for cart_item in cart.items:
                db.session.delete(cart_item)
            
            db.session.commit()
            
            # Log payment initiation
            logger.info(
                "Payment initiated",
                event="payment_initiated",
                order_id=order.id,
                amount=total_amount,
                phone_number=mask_phone(phone_number),
                checkout_request_id=response.get("CheckoutRequestID")
            )
            
            return {
                "message": "STK Push initiated successfully",
                "order_id": order.id,
                "checkout_request_id": response.get("CheckoutRequestID"),
                "merchant_request_id": response.get("MerchantRequestID")
            }, 200
            
        except Exception as e:
            db.session.rollback()
            # Log payment initiation failure
            log_exception(
                "Failed to initiate payment",
                error=e,
                event="payment_initiation_failure"
            )
            return {"error": "Failed to initiate payment"}, 500

class PaymentCallbackResource(Resource):
    def post(self):
        """Handle M-Pesa payment callback with proper transaction handling"""
        try:
            # Parse callback data
            data = request.get_json()
            logger.info("M-Pesa Callback Data received", event="payment_callback_raw_data")
            
            # Extract relevant information
            if "Body" in data and "stkCallback" in data["Body"]:
                callback_data = data["Body"]["stkCallback"]
                checkout_request_id = callback_data.get("CheckoutRequestID")
                result_code = callback_data.get("ResultCode")
                
                # Log callback received
                logger.info(
                    "Payment callback received",
                    event="payment_callback_received",
                    checkout_request_id=checkout_request_id,
                    result_code=result_code
                )
                
                # Begin transaction
                db.session.begin_nested()
                
                # Find order by checkout request ID with locking
                order = db.session.query(Order).filter_by(mpesa_checkout_request_id=checkout_request_id).with_for_update().first()
                if not order:
                    return {"error": "Order not found"}, 404
                
                if result_code == 0:  # Success
                    order.status = "paid"
                    order.paid_at = db.func.now()  # Record payment time
                    
                    # Clear cart items (if any remain)
                    cart = db.session.query(Cart).filter_by(user_id=order.user_id).first()
                    if cart:
                        # Delete all cart items for this cart
                        db.session.query(CartItem).filter_by(cart_id=cart.id).delete()
                    
                    db.session.commit()
                    
                    # Log payment successful
                    logger.info(
                        "Payment successful",
                        event="payment_successful",
                        order_id=order.id,
                        status="paid"
                    )
                    return {"message": "Payment successful"}, 200
                else:
                    # Payment failed - restore stock
                    order.status = "failed"
                    
                    # Log payment failed
                    logger.warning(
                        "Payment failed",
                        event="payment_failed",
                        order_id=order.id,
                        result_code=result_code
                    )
                    
                    # Restore stock for failed order
                    restored_count = 0
                    for order_item in order.items:
                        product = db.session.query(Product).filter(Product.id == order_item.product_id).with_for_update().first()
                        if product:
                            product.stock += order_item.quantity
                            restored_count += order_item.quantity
                    
                    db.session.commit()
                    
                    # Log stock restored
                    logger.info(
                        "Stock restored after failed payment",
                        event="stock_restored",
                        order_id=order.id,
                        restored_count=restored_count
                    )
                    return {"message": "Payment failed"}, 200
            
            return {"error": "Invalid callback data"}, 400
        except Exception as e:
            db.session.rollback()
            # Log callback handling failure
            log_exception(
                "Failed to handle payment callback",
                error=e,
                event="callback_handling_failure"
            )
            return {"error": "Failed to handle callback"}, 500

class PaymentVerificationResource(Resource):
    @jwt_required()
    def post(self):
        """Manually verify payment status with proper transaction handling"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            checkout_request_id = data.get("checkout_request_id")
            
            if not checkout_request_id:
                return {"error": "Checkout request ID is required"}, 400
            
            # Begin transaction
            db.session.begin_nested()
            
            # Verify transaction
            with PerformanceTimer('mpesa_verify'):
                response = mpesa_service.verify_transaction(checkout_request_id)
            
            if "error" in response:
                return {"error": response["error"]}, 400
            
            # Update order status based on verification
            result_code = response.get("ResultCode")
            order = db.session.query(Order).filter(
                and_(
                    Order.mesa_checkout_request_id == checkout_request_id,
                    Order.user_id == user_id
                )
            ).with_for_update().first()
            
            if not order:
                return {"error": "Order not found"}, 404
            
            if result_code == "0":  # Success
                order.status = "paid"
                order.paid_at = db.func.now()  # Record payment time
                
                # Clear cart items (if any remain)
                cart = db.session.query(Cart).filter_by(user_id=user_id).first()
                if cart:
                    db.session.query(CartItem).filter_by(cart_id=cart.id).delete()
                message = "Payment successful"
                
                # Log payment successful
                logger.info(
                    "Payment successful via verification",
                    event="payment_successful",
                    order_id=order.id,
                    status="paid"
                )
            else:
                # Payment failed - restore stock
                order.status = "failed"
                
                # Log payment failed
                logger.warning(
                    "Payment failed via verification",
                    event="payment_failed",
                    order_id=order.id,
                    result_code=result_code
                )
                
                # Restore stock for failed order
                restored_count = 0
                for order_item in order.items:
                    product = db.session.query(Product).filter(Product.id == order_item.product_id).with_for_update().first()
                    if product:
                        product.stock += order_item.quantity
                        restored_count += order_item.quantity
                        
                message = "Payment failed"
                
                # Log stock restored
                logger.info(
                    "Stock restored after failed payment verification",
                    event="stock_restored",
                    order_id=order.id,
                    restored_count=restored_count
                )
            
            db.session.commit()
            
            # Log verification
            logger.info(
                "Payment verified",
                event="payment_verified",
                order_id=order.id,
                status=order.status
            )
            
            return {
                "message": message,
                "order_status": order.status
            }, 200
            
        except Exception as e:
            db.session.rollback()
            # Log payment verification failure
            log_exception(
                "Failed to verify payment",
                error=e,
                event="payment_verification_failure"
            )
            return {"error": "Failed to verify payment"}, 500