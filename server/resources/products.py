from flask_restful import Resource
from models import Product

class ProductListResource(Resource):
    def get(self):
        products = Product.query.all()
        return [product.to_dict() for product in products], 200
