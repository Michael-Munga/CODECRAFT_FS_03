from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from utils.decorators import admin_required

class AdminCustomersResource(Resource):
    """
    Admin-only endpoint to view all customers.
    """

    @admin_required
    def get(self):

        customers = User.query.filter_by(role="customer").all()

        data = [
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "created_at": user.created_at,
            }
            for user in customers
        ]

        return {"customers": data}, 200
