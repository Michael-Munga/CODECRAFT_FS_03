from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from models import User, db
import re

EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

class AuthResorce(Resource):
    def post(self, action):
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        phone_number = data.get("phone_number", "").strip()

        if not email or not password:
            return {"error": "Email and Password are required"}, 400
        if not EMAIL_RE.match(email):
            return {"error": "Invalid Email Format"}, 400

        # Login
        if action == "login":
            user = User.query.filter_by(email=email).first()
            if not user or not user.verify_password(password):
                return {"error": "Invalid email or password"}, 401

            token = create_access_token(identity=user.id)

            if user.role == "admin":
                redirect_url = "/admin/dashboard"
            else:
                redirect_url = "/"

            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "name": user.full_name  
                },
                "access_token": token,
                "redirect_url": redirect_url
            }, 200

        # Register
        if action == "register":
            if not first_name or not last_name:
                return {"error": "First and Last name are required"}, 400
            if not phone_number:
                return {"error": "Phone number is required"}, 400
            if User.query.filter_by(email=email).first():
                return {"error": "Email already exists"}, 409
            if User.query.filter_by(phone_number=phone_number).first():
                return {"error": "Phone number already exists"}, 409

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                role="customer",
                phone_number=phone_number
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            token = create_access_token(identity=new_user.id)

            return {
                "message": "User registered successfully",
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "role": new_user.role,
                    "name": new_user.full_name,
                    "phone": new_user.phone_number
                },
                "access_token": token,
                "redirect_url": "/"
            }, 201

        else:
            return {"error": "Unsupported auth action"}, 400
