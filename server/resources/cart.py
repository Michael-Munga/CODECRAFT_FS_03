from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, Cart, CartItem, Product
from sqlalchemy import and_

from logging_config import get_logger, log_exception
from request_tracking import PerformanceTimer

logger = get_logger('cart')

# CART RESOURCE
class CartResource(Resource):
    @jwt_required()
    def get(self):
        """Get all items in the current user's cart"""
        user_id = get_jwt_identity()
        # Use joinedload to prevent N+1 queries
        from sqlalchemy.orm import joinedload
        
        with PerformanceTimer('db_query_cart'):
            cart = Cart.query.options(joinedload(Cart.items).joinedload(CartItem.product)).filter_by(user_id=user_id).first()
        
        if not cart:
            # Log cart viewed (empty)
            logger.info(
                "User viewed empty cart",
                event="cart_viewed",
                item_count=0
            )
            return {'items': []}, 200

        items = [
            {
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_price': item.product.price,
                'product_image': item.product.image_url,
                'quantity': item.quantity
            }
            for item in cart.items
        ]
        
        # Log cart viewed
        logger.info(
            f"User viewed cart with {len(items)} items",
            event="cart_viewed",
            item_count=len(items)
        )
        
        return {'items': items}, 200

    @jwt_required()
    def post(self):
        """Add a product to the cart with race condition protection"""
        try:
            db.session.begin_nested()  # Begin transaction
            
            user_id = get_jwt_identity()
            data = request.get_json()

            if not data or 'product_id' not in data:
                return {'message': 'Missing product_id'}, 400

            product_id = data['product_id']
            quantity = data.get('quantity', 1)

            if not isinstance(product_id, int) or not isinstance(quantity, int):
                return {'message': 'product_id and quantity must be integers'}, 400

            if quantity <= 0:
                return {'message': 'Quantity must be positive'}, 400

            # Get product with row-level locking to prevent race conditions
            product = db.session.query(Product).filter(Product.id == product_id).with_for_update().first()
            if not product:
                return {'message': 'Product not found'}, 404

            if product.stock < quantity:
                # Log insufficient stock
                logger.warning(
                    f"Insufficient stock for product {product_id}",
                    event="insufficient_stock",
                    product_id=product_id,
                    requested_quantity=quantity,
                    available_quantity=product.stock
                )
                return {'message': f'Insufficient stock. Available: {product.stock}, Requested: {quantity}'}, 400

            # Get or create cart with locking
            cart = db.session.query(Cart).filter_by(user_id=user_id).with_for_update().first()
            if not cart:
                cart = Cart(user_id=user_id)
                db.session.add(cart)
                db.session.flush()  # Get cart ID without committing

            # Check if item already exists in cart with locking
            existing_item = db.session.query(CartItem).filter(
                and_(CartItem.cart_id == cart.id, CartItem.product_id == product.id)
            ).with_for_update().first()
            
            new_quantity = quantity
            if existing_item:
                new_quantity = existing_item.quantity + quantity
                if product.stock < new_quantity:
                    # Log insufficient stock
                    logger.warning(
                        f"Insufficient stock for product {product_id} to add more",
                        event="insufficient_stock",
                        product_id=product_id,
                        requested_quantity=quantity,
                        available_quantity=product.stock
                    )
                    return {'message': f'Insufficient stock. Available: {product.stock}, Would have: {new_quantity}'}, 400
                existing_item.quantity = new_quantity
            else:
                if quantity > product.stock:
                    # Log insufficient stock
                    logger.warning(
                        f"Insufficient stock for product {product_id}",
                        event="insufficient_stock",
                        product_id=product_id,
                        requested_quantity=quantity,
                        available_quantity=product.stock
                    )
                    return {'message': f'Insufficient stock. Available: {product.stock}, Requested: {quantity}'}, 400
                new_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
                db.session.add(new_item)

            db.session.commit()
            
            # Return the item (need to query again since session was committed)
            if existing_item:
                final_item = CartItem.query.filter_by(id=existing_item.id).first()
            else:
                final_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()

            
            
            # Log successful item add
            logger.info(
                f"User added product {product_id} to cart",
                event="cart_item_added",
                product_id=product_id,
                product_name=final_item.product.name,
                quantity=quantity
            )

            return {
                'id': final_item.id,
                'product_id': final_item.product.id,
                'product_name': final_item.product.name,
                'product_price': final_item.product.price,
                'product_image': final_item.product.image_url,
                'quantity': final_item.quantity
            }, 201

        except Exception as e:
            db.session.rollback()
            # Log cart operation failure
            log_exception(
                "Failed to add item to cart",
                error=e,
                event="cart_operation_failure",
                operation="add_item"
            )
            return {'message': f'Error adding to cart: {str(e)}'}, 500


# CART ITEM RESOURCE
class CartItemResource(Resource):
    @jwt_required()
    def patch(self, item_id):
        """Update quantity of a cart item with race condition protection"""
        try:
            db.session.begin_nested()  # Begin transaction
            
            user_id = get_jwt_identity()
            # Get item with row-level locking
            item = db.session.query(CartItem).filter(CartItem.id == item_id).with_for_update().first()
            
            if not item:
                return {'message': 'Item not found'}, 404

            if item.cart.user_id != user_id:
                # Log unauthorized access
                logger.warning(
                    f"User attempted to update cart item not belonging to them",
                    event="unauthorized_cart_item_access",
                    actual_owner_id=item.cart.user_id,
                    item_id=item_id
                )
                return {'message': 'Unauthorized'}, 403

            data = request.get_json()
            if not data or 'quantity' not in data:
                return {'message': 'Missing quantity'}, 400

            quantity = data['quantity']
            if not isinstance(quantity, int):
                return {'message': 'Quantity must be an integer'}, 400

            if quantity <= 0:
                return {'message': 'Quantity must be positive'}, 400

            # Get product with locking to check stock
            product = db.session.query(Product).filter(Product.id == item.product_id).with_for_update().first()
            
            if quantity > product.stock:
                # Log insufficient stock
                logger.warning(
                    f"Insufficient stock for product {item.product_id} on update",
                    event="insufficient_stock",
                    product_id=item.product_id,
                    requested_quantity=quantity,
                    available_quantity=product.stock
                )
                return {'message': f'Insufficient stock. Available: {product.stock}, Requested: {quantity}'}, 400

            old_quantity = item.quantity
            item.quantity = quantity
            db.session.commit()

            # Refresh item after commit
            updated_item = CartItem.query.filter_by(id=item.id).first()

            # Log item update
            logger.info(
                f"User updated cart item {item.id}",
                event="cart_item_updated",
                item_id=item.id,
                old_quantity=old_quantity,
                new_quantity=quantity
            )

            return {
                'id': updated_item.id,
                'product_id': updated_item.product.id,
                'product_name': updated_item.product.name,
                'product_price': updated_item.product.price,
                'product_image': updated_item.product.image_url,
                'quantity': updated_item.quantity
            }, 200

        except Exception as e:
            db.session.rollback()
            # Log update failure
            log_exception(
                "Failed to update cart item",
                error=e,
                event="cart_operation_failure",
                operation="update_item",
                item_id=item_id
            )
            return {'message': f'Error updating cart item: {str(e)}'}, 500

    @jwt_required()
    def delete(self, item_id):
        """Remove an item from the cart"""
        try:
            user_id = get_jwt_identity()
            item = CartItem.query.filter_by(id=item_id).first()

            if not item:
                return {'message': 'Item not found'}, 404

            if item.cart.user_id != user_id:
                # Log unauthorized access
                logger.warning(
                    f"User attempted to delete cart item not belonging to them",
                    event="unauthorized_cart_item_access",
                    actual_owner_id=item.cart.user_id,
                    item_id=item_id
                )
                return {'message': 'Unauthorized'}, 403

            db.session.delete(item)
            db.session.commit()

            # Log item deletion
            logger.info(
                f"User deleted cart item {item_id}",
                event="cart_item_deleted",
                item_id=item_id
            )

            return {'message': 'Deleted'}, 204
        except Exception as e:
            db.session.rollback()
            # Log delete failure
            log_exception(
                "Failed to delete cart item",
                error=e,
                event="cart_operation_failure",
                operation="delete_item",
                item_id=item_id
            )
            return {'message': f'Error removing from cart: {str(e)}'}, 500