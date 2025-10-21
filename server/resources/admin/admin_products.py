from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from models import db, Product, OrderItem, User


class AdminProductsResource(Resource):
    """
    Admin-only Product Management
    """

    # GET all products ( filter by low stock)
    @jwt_required()
    def get(self):
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != "admin":
            return {"error": "Admins only"}, 403

        low_stock = request.args.get("low_stock", type=int)
        query = Product.query
        if low_stock is not None:
            query = query.filter(Product.stock <= low_stock)

        products = query.all()

        data = []
        for product in products:
            total_sales = (
                db.session.query(func.sum(OrderItem.quantity))
                .filter(OrderItem.product_id == product.id)
                .scalar()
                or 0
            )

            total_revenue = (
                db.session.query(func.sum(OrderItem.price * OrderItem.quantity))
                .filter(OrderItem.product_id == product.id)
                .scalar()
                or 0
            )

            product_dict = product.to_dict()
            product_dict.update({
                "total_sales": total_sales,
                "total_revenue": total_revenue
            })

            data.append(product_dict)

        return data, 200

    
    # POST--> Add New Product
  
    @jwt_required()
    def post(self):
        """
        Add a new product (admin only)
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return {"error": "Admins only"}, 403

        data = request.get_json()

        required_fields = ["name", "price", "stock"]
        for field in required_fields:
            if field not in data:
                return {"error": f"'{field}' is required"}, 400

        new_product = Product(
            name=data["name"],
            description=data.get("description"),
            price=data["price"],
            stock=data["stock"],
            image_url=data.get("image_url"),
            category_id=data.get("category_id"),
        )

        db.session.add(new_product)
        db.session.commit()

        return {
            "message": "Product added successfully",
            "product": new_product.to_dict()
        }, 201

    # PUT ---> Edit Existing Product
    @jwt_required()
    def put(self, id):
        """
        Update product by id (admin only)
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return {"error": "Admins only"}, 403

        product = Product.query.get(id)
        if not product:
            return {"error": "Product not found"}, 404

        data = request.get_json() or {}

        # Update only fields that exist in Product model
        for key in ["name", "description", "price", "stock", "image_url", "category_id"]:
            if key in data and data[key] is not None:
                setattr(product, key, data[key])

        db.session.commit()

        return {
            "message": "Product updated successfully",
            "product": product.to_dict()
        }, 200


    # DELETE--> Remove Product
  
    @jwt_required()
    def delete(self, id):
        """
        Delete product by id (from URL)
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return {"error": "Admins only"}, 403

        product = Product.query.get(id)
        if not product:
            return {"error": "Product not found"}, 404

        db.session.delete(product)
        db.session.commit()

        return {"message": "Product deleted successfully"}, 200

