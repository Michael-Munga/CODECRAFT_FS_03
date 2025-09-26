from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import db, Cart, CartItem, Product

# CART RESOURCE
class CartResource(Resource):
    @jwt_required()
    def get(self):
        """Get all items in the current user's cart"""
        user_id = get_jwt_identity()
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
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
        return {'items': items}, 200

    @jwt_required()
    def post(self):
        """Add a product to the cart"""
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'product_id' not in data:
            return {'message': 'Missing product_id'}, 400

        product_id = data['product_id']
        quantity = data.get('quantity', 1)

        if not isinstance(product_id, int) or not isinstance(quantity, int):
            return {'message': 'product_id and quantity must be integers'}, 400

        product = Product.query.get(product_id)
        if not product:
            return {'message': 'Product not found'}, 404

        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()

        existing_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
        if existing_item:
            existing_item.quantity += quantity
        else:
            existing_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
            db.session.add(existing_item)

        db.session.commit()

        return {
            'id': existing_item.id,
            'product_id': existing_item.product.id,
            'product_name': existing_item.product.name,
            'product_price': existing_item.product.price,
            'product_image': existing_item.product.image_url,
            'quantity': existing_item.quantity
        }, 201


# CART ITEM RESOURCE
class CartItemResource(Resource):
    @jwt_required()
    def patch(self, item_id):
        """Update quantity of a cart item"""
        user_id = get_jwt_identity()
        item = CartItem.query.get_or_404(item_id)

        if item.cart.user_id != user_id:
            return {'message': 'Unauthorized'}, 403

        data = request.get_json()
        if not data or 'quantity' not in data:
            return {'message': 'Missing quantity'}, 400

        quantity = data['quantity']
        if not isinstance(quantity, int):
            return {'message': 'Quantity must be an integer'}, 400

        item.quantity = quantity
        db.session.commit()

        return {
            'id': item.id,
            'product_id': item.product.id,
            'product_name': item.product.name,
            'product_price': item.product.price,
            'product_image': item.product.image_url,
            'quantity': item.quantity
        }, 200

    @jwt_required()
    def delete(self, item_id):
        """Remove an item from the cart"""
        user_id = get_jwt_identity()
        item = CartItem.query.get_or_404(item_id)

        if item.cart.user_id != user_id:
            return {'message': 'Unauthorized'}, 403

        db.session.delete(item)
        db.session.commit()

        return {'message': 'Deleted'}, 204
