from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from models import User, db
from extensions import ma  # import the Marshmallow instance

from marshmallow import validate

# Import Layer 4 reliability components
from auth_context import authenticate_user_context, log_user_action
from logging_config import get_logger

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
                # Log failed login attempt
                auth_logger = get_logger('auth')
                auth_logger.warning(
                    f"Failed login attempt for email: {email}",
                    event='failed_login',
                    email=email,
                    remote_addr=request.environ.get('REMOTE_ADDR'),
                    user_agent=request.headers.get('User-Agent', 'Unknown')
                )
                return {"error": "Invalid email or password"}, 401

            # Successful login - set authentication context and log
            authenticate_user_context(user.id)
            log_user_action('login', user.id)
            
            token = create_access_token(identity=user.id)
            redirect_url = "/admin/dashboard" if user.role == "admin" else "/"
            user_data = UserResponseSchema().dump(user)

            # Log successful login
            auth_logger = get_logger('auth')
            auth_logger.info(
                f"User {user.id} logged in successfully",
                event='successful_login',
                user_id=user.id,
                email=user.email,
                role=user.role
            )

            return {"user": user_data, "access_token": token, "redirect_url": redirect_url}, 200

        # -------- REGISTER --------
        elif action == "register":
            print(f"Received data: {data}")  # Debug print
            errors = RegisterSchema().validate(data)
            if errors:
                print(f"Validation errors: {errors}")  # Debug print
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

            # Registration successful - set authentication context and log
            authenticate_user_context(new_user.id)
            log_user_action('registration', new_user.id)
            
            token = create_access_token(identity=new_user.id)
            user_data = UserResponseSchema().dump(new_user)

            # Log successful registration
            auth_logger = get_logger('auth')
            auth_logger.info(
                f"User {new_user.id} registered successfully",
                event='successful_registration',
                user_id=new_user.id,
                email=new_user.email,
                phone_number=new_user.phone_number
            )

            return {"message": "User registered successfully", "user": user_data, "access_token": token, "redirect_url": "/"}, 201

        # -------- UNSUPPORTED ACTION --------
        else:
            return {"error": "Unsupported auth action"}, 400
