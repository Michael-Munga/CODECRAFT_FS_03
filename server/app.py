from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
import os
from datetime import timedelta
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

from models import db,bcrypt
from resources.auth import AuthResorce
from resources.customer.products import ProductListResource
from resources.cart import CartItemResource,CartResource
from resources.admin.admin_products import AdminProductsResource
from resources.admin.categories import CategoriesResource
from resources.admin.customers import AdminCustomersResource


# load env variables 
load_dotenv()
app = Flask(__name__)


# config
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)


# EXTENSIONS
bcrypt.init_app(app)
jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

# API
api = Api(app)
# resources


api.add_resource(AuthResorce, '/auth/<string:action>')
api.add_resource(ProductListResource, "/products")
api.add_resource(CartResource, '/cart')               
api.add_resource(CartItemResource, '/cart/item/<int:item_id>') 
api.add_resource(AdminProductsResource, '/admin/products', '/admin/products/<int:id>')
api.add_resource(CategoriesResource, '/admin/categories', '/admin/categories/<int:id>')
api.add_resource(AdminCustomersResource, "/admin/customers")

# Root route
@app.route("/")
def home():
    return "Flask backend is running!"

# Health check route for Render
@app.route("/healthz")
def health_check():
    return "OK", 200


# Entry point
if __name__ == "__main__":
    app.run(port=5555, debug=True)