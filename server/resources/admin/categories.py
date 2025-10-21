from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Category, User

class CategoriesResource(Resource):
    def get(self, id=None):
        """
        GET /admin/categories
        GET /admin/categories/<id>
        """
        if id:
            category = Category.query.get(id)
            if not category:
                return {"error": "Category not found"}, 404
            return category.to_dict(), 200

        categories = Category.query.all()
        return [cat.to_dict() for cat in categories], 200

    @jwt_required()
    def post(self):
        """
        POST /admin/categories
        Add a new category (admin only)
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != "admin":
            return {"error": "Admins only"}, 403

        data = request.get_json()
        name = data.get("name")
        description = data.get("description")

        if not name:
            return {"error": "'name' is required"}, 400

        # Prevent duplicates
        if Category.query.filter_by(name=name).first():
            return {"error": "Category already exists"}, 400

        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()

        return {"message": "Category added", "category": category.to_dict()}, 201

    @jwt_required()
    def put(self, id):
        """
        PUT /admin/categories/<id>
        Update a category (admin only)
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != "admin":
            return {"error": "Admins only"}, 403

        category = Category.query.get(id)
        if not category:
            return {"error": "Category not found"}, 404

        data = request.get_json()
        category.name = data.get("name", category.name)
        category.description = data.get("description", category.description)

        db.session.commit()
        return {"message": "Category updated", "category": category.to_dict()}, 200

    @jwt_required()
    def delete(self, id):
        """
        DELETE /admin/categories/<id>
        Delete a category (admin only)
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != "admin":
            return {"error": "Admins only"}, 403

        category = Category.query.get(id)
        if not category:
            return {"error": "Category not found"}, 404

        db.session.delete(category)
        db.session.commit()
        return {"message": f"Category '{category.name}' deleted"}, 200
