"""
Order utilities for handling safe order creation with proper data integrity
"""

from models import db, Cart, CartItem, Order, OrderItem, Product
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

def create_order_with_stock_reservation(user_id, cart_id):
    """
    Create an order with proper stock reservation and transaction safety.
    This function handles all the complexity of creating an order while ensuring
    data integrity and preventing race conditions.
    """
    try:
        # Begin transaction
        db.session.begin_nested()
        
        # Get user's cart with all related data and lock it
        cart = db.session.query(Cart)\
            .options(joinedload(Cart.items).joinedload(CartItem.product))\
            .filter(Cart.id == cart_id, Cart.user_id == user_id)\
            .with_for_update()\
            .first()
        
        if not cart:
            raise ValueError("Cart not found or doesn't belong to user")
        
        if not cart.items:
            raise ValueError("Cart is empty")
        
        # Lock all products that are in the cart to prevent concurrent stock changes
        product_ids = [item.product_id for item in cart.items]
        locked_products = db.session.query(Product)\
            .filter(Product.id.in_(product_ids))\
            .with_for_update()\
            .all()
        
        # Create a product lookup dictionary for easy access
        product_lookup = {p.id: p for p in locked_products}
        
        # Validate stock availability for all items
        insufficient_stock = []
        for cart_item in cart.items:
            product = product_lookup.get(cart_item.product_id)
            if not product:
                raise ValueError(f"Product {cart_item.product_id} not found")
            
            if product.stock < cart_item.quantity:
                insufficient_stock.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'available': product.stock,
                    'requested': cart_item.quantity
                })
        
        # If any items have insufficient stock, raise an error
        if insufficient_stock:
            raise ValueError(f"Insufficient stock: {insufficient_stock}")
        
        # Calculate total amount
        total_amount = sum(
            cart_item.product.price * cart_item.quantity 
            for cart_item in cart.items
        )
        
        # Create the order
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status="pending"
        )
        db.session.add(order)
        db.session.flush()  # Get order ID without committing
        
        # Create order items and reserve stock
        order_items = []
        for cart_item in cart.items:
            product = product_lookup[cart_item.product_id]
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            order_items.append(order_item)
            
            # Deduct stock from product
            product.stock -= cart_item.quantity
            logger.info(f"Deducted {cart_item.quantity} from product {product.id} stock. New stock: {product.stock}")
        
        # Clear the cart items
        for cart_item in cart.items:
            db.session.delete(cart_item)
        
        # Commit all changes atomically
        db.session.commit()
        
        logger.info(f"Order {order.id} created successfully for user {user_id}")
        
        return {
            'order_id': order.id,
            'total_amount': total_amount,
            'status': 'success',
            'items_count': len(order_items)
        }
        
    except Exception as e:
        # Rollback all changes if anything fails
        db.session.rollback()
        logger.error(f"Order creation failed for user {user_id}: {str(e)}")
        raise e


def cancel_order_and_restore_stock(order_id):
    """
    Cancel an order and restore the stock for all items in the order.
    This is used when an order needs to be cancelled for any reason.
    """
    try:
        db.session.begin_nested()
        
        # Get order with items and lock it
        order = db.session.query(Order)\
            .options(joinedload(Order.items))\
            .filter(Order.id == order_id)\
            .with_for_update()\
            .first()
        
        if not order:
            raise ValueError("Order not found")
        
        if order.status in ["cancelled", "refunded"]:
            raise ValueError("Order already cancelled or refunded")
        
        # Get all products in the order and lock them
        product_ids = [item.product_id for item in order.items]
        locked_products = db.session.query(Product)\
            .filter(Product.id.in_(product_ids))\
            .with_for_update()\
            .all()
        
        product_lookup = {p.id: p for p in locked_products}
        
        # Restore stock for all order items
        restored_items = []
        for order_item in order.items:
            product = product_lookup.get(order_item.product_id)
            if product:
                product.stock += order_item.quantity
                restored_items.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'restored_quantity': order_item.quantity
                })
        
        # Update order status
        order.status = "cancelled"
        
        db.session.commit()
        
        logger.info(f"Order {order_id} cancelled and stock restored for {len(restored_items)} items")
        
        return {
            'order_id': order.id,
            'status': 'cancelled',
            'restored_items': restored_items
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Order cancellation failed for order {order_id}: {str(e)}")
        raise e


def validate_cart_for_checkout(cart_id, user_id):
    """
    Validate that a cart is ready for checkout.
    This function checks for stock availability and other business rules.
    """
    try:
        # Get cart with items and products (without locking since this is read-only)
        cart = db.session.query(Cart)\
            .options(joinedload(Cart.items).joinedload(CartItem.product))\
            .filter(Cart.id == cart_id, Cart.user_id == user_id)\
            .first()
        
        if not cart:
            raise ValueError("Cart not found or doesn't belong to user")
        
        if not cart.items:
            raise ValueError("Cart is empty")
        
        # Validate each item in the cart
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'total_amount': 0,
            'items_validated': 0
        }
        
        for cart_item in cart.items:
            product = cart_item.product
            
            # Check if product exists
            if not product:
                validation_results['errors'].append(f"Product {cart_item.product_id} no longer exists")
                validation_results['valid'] = False
                continue
            
            # Check if product is active (has positive price)
            if product.price <= 0:
                validation_results['errors'].append(f"Product {product.name} is not available for purchase")
                validation_results['valid'] = False
                continue
            
            # Check stock availability
            if product.stock < cart_item.quantity:
                validation_results['errors'].append(
                    f"Insufficient stock for {product.name}. Available: {product.stock}, Requested: {cart_item.quantity}"
                )
                validation_results['valid'] = False
                continue
            
            # Check quantity limits
            if cart_item.quantity <= 0:
                validation_results['errors'].append(f"Invalid quantity for {product.name}")
                validation_results['valid'] = False
                continue
            
            validation_results['items_validated'] += 1
            validation_results['total_amount'] += product.price * cart_item.quantity
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Cart validation failed for cart {cart_id}: {str(e)}")
        raise e


def get_optimized_cart_with_stock_info(cart_id, user_id):
    """
    Get cart with stock information optimized for display.
    This function uses eager loading to prevent N+1 queries.
    """
    cart = db.session.query(Cart)\
        .options(joinedload(Cart.items).joinedload(CartItem.product))\
        .filter(Cart.id == cart_id, Cart.user_id == user_id)\
        .first()
    
    if not cart:
        return None
    
    cart_data = {
        'id': cart.id,
        'user_id': cart.user_id,
        'created_at': cart.created_at,
        'items': [],
        'total_items': 0,
        'total_amount': 0,
        'items_with_stock_info': []
    }
    
    for item in cart.items:
        product = item.product
        cart_data['items'].append({
            'id': item.id,
            'product_id': product.id,
            'name': product.name,
            'price': float(product.price),
            'quantity': item.quantity,
            'subtotal': float(product.price * item.quantity),
            'stock_available': product.stock,
            'image_url': product.image_url,
            'in_stock': product.stock >= item.quantity
        })
        cart_data['items_with_stock_info'].append({
            'product_id': product.id,
            'requested': item.quantity,
            'available': product.stock,
            'sufficient': product.stock >= item.quantity
        })
        cart_data['total_items'] += item.quantity
        cart_data['total_amount'] += product.price * item.quantity
    
    return cart_data