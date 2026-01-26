from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
import os
from datetime import timedelta
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
# Import extensions
from extensions import db, bcrypt, ma
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

# -----------------------------
# API
# -----------------------------
api = Api(app)

# Auth
api.add_resource(AuthResource, '/auth/<string:action>')

# Customer
api.add_resource(ProductListResource, "/products")
api.add_resource(CartResource, '/cart')               
api.add_resource(CartItemResource, '/cart/item/<int:item_id>') 

# Admin
api.add_resource(AdminProductsResource, '/admin/products', '/admin/products/<int:id>')
api.add_resource(CategoriesResource, '/admin/categories', '/admin/categories/<int:id>')
api.add_resource(AdminCustomersResource, "/admin/customers")

# Payment
api.add_resource(PaymentResource, '/payment/stk-push')
api.add_resource(PaymentCallbackResource, '/payment/callback')
api.add_resource(PaymentVerificationResource, '/payment/verify')

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return "Flask backend is running!"

@app.route("/healthz")
def health_check():
    return "OK", 200

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)
