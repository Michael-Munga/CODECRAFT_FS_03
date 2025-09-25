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

# Entry point
if __name__ == "__main__":
    app.run(port=5555, debug=True)