from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
import os
from datetime import timedelta
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
# Import extensions
from extensions import db, bcrypt, ma, limiter
# Import resources
from resources.auth import AuthResource
from resources.customer.products import ProductListResource
from resources.cart import CartItemResource, CartResource
from resources.admin.admin_products import AdminProductsResource
from resources.admin.categories import CategoriesResource
from resources.admin.customers import AdminCustomersResource
from resources.payment import PaymentResource, PaymentCallbackResource, PaymentVerificationResource

# -----------------------------
# App setup
# -----------------------------
load_dotenv()
app = Flask(__name__)

# Config
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# -----------------------------
# Initialize extensions
# -----------------------------
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
CORS(app)
ma.init_app(app)
limiter.init_app(app)  # Initialize rate limiter

# -----------------------------
# Rate Limit Error Handler
# -----------------------------
@app.errorhandler(429)
def ratelimit_handler(e):
    return {
        "error": "Rate limit exceeded",
        "message": f"Too many requests. Please try again in {e.description}",
        "retry_after": e.retry_after
    }, 429

# -----------------------------
# API
# -----------------------------
api = Api(app)

# Auth - Stricter limits for login/signup to prevent brute force
api.add_resource(AuthResource, '/auth/<string:action>')
limiter.limit("10 per minute")(AuthResource)  # 10 requests per minute for auth

# Customer - Moderate limits
api.add_resource(ProductListResource, "/products")
limiter.limit("100 per hour")(ProductListResource)  # 100 requests per hour for products

api.add_resource(CartResource, '/cart')               
limiter.limit("50 per hour")(CartResource)  # 50 requests per hour for cart

api.add_resource(CartItemResource, '/cart/item/<int:item_id>') 
limiter.limit("50 per hour")(CartItemResource)  # 50 requests per hour for cart items

# Admin - Stricter limits for security
api.add_resource(AdminProductsResource, '/admin/products', '/admin/products/<int:id>')
limiter.limit("30 per hour")(AdminProductsResource)  # 30 requests per hour for admin products

api.add_resource(CategoriesResource, '/admin/categories', '/admin/categories/<int:id>')
limiter.limit("30 per hour")(CategoriesResource)  # 30 requests per hour for admin categories

api.add_resource(AdminCustomersResource, "/admin/customers")
limiter.limit("30 per hour")(AdminCustomersResource)  # 30 requests per hour for admin customers

# Payment - Very strict limits to prevent abuse
api.add_resource(PaymentResource, '/payment/stk-push')
limiter.limit("5 per minute")(PaymentResource)  # Only 5 payment requests per minute

api.add_resource(PaymentCallbackResource, '/payment/callback')
# Payment callbacks are exempt from rate limiting (they come from M-Pesa)

api.add_resource(PaymentVerificationResource, '/payment/verify')
limiter.limit("10 per minute")(PaymentVerificationResource)  # 10 verification requests per minute

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
@limiter.limit("10 per minute")  # 10 requests per minute for root
def home():
    return "Flask backend is running!"

@app.route("/healthz")
@limiter.exempt  # Health check is exempt from rate limiting
def health_check():
    return "OK", 200

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)