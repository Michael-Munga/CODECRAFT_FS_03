from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from models import User, db
from extensions import ma  # import the Marshmallow instance

from marshmallow import validate

# -----------------------------
# Schemas: Request validation
# -----------------------------
class LoginSchema(ma.Schema):
    email = ma.Email(required=True)
    password = ma.Str(required=True, validate=validate.Length(min=1))

class RegisterSchema(ma.Schema):
    email = ma.Email(required=True)
    password = ma.Str(required=True, validate=validate.Length(min=8))
    first_name = ma.Str(required=True)
    last_name = ma.Str(required=True)
    phone_number = ma.Str(required=True, validate=validate.Length(min=10))

# -----------------------------
# Schemas: Response serialization
# -----------------------------
class UserResponseSchema(ma.Schema):
    id = ma.Int()
    email = ma.Email()
    role = ma.Str()
    name = ma.Method("full_name")
    phone = ma.Str(attribute="phone_number")

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

# -----------------------------
# Auth Resource
# -----------------------------
class AuthResource(Resource):

    def post(self, action):
        data = request.get_json() or {}

        # -------- LOGIN --------
        if action == "login":
            errors = LoginSchema().validate(data)
            if errors:
                return {"errors": errors}, 400

            email = data["email"].strip().lower()
            password = data["password"]

            user = User.query.filter_by(email=email).first()
            if not user or not user.verify_password(password):
                return {"error": "Invalid email or password"}, 401

            token = create_access_token(identity=user.id)
            redirect_url = "/admin/dashboard" if user.role == "admin" else "/"
            user_data = UserResponseSchema().dump(user)

            return {"user": user_data, "access_token": token, "redirect_url": redirect_url}, 200

        # -------- REGISTER --------
        elif action == "register":
            errors = RegisterSchema().validate(data)
            if errors:
                return {"errors": errors}, 400

            email = data["email"].strip().lower()
            password = data["password"]
            first_name = data["first_name"].strip()
            last_name = data["last_name"].strip()
            phone_number = data["phone_number"].strip()

            # Business rules: unique email & phone
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
            user_data = UserResponseSchema().dump(new_user)

            return {"message": "User registered successfully", "user": user_data, "access_token": token, "redirect_url": "/"}, 201

        # -------- UNSUPPORTED ACTION --------
        else:
            return {"error": "Unsupported auth action"}, 400
