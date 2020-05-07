from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from configparser import ConfigParser, ExtendedInterpolation
from os import getenv

app = Flask(__name__)
CORS(app, support_credentials=True)

if getenv("USE_ENV_VAR"):
    app.config['SECRET_KEY'] = getenv("SECRET")
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv("DATABASE_URL")
else:
    app_config = ConfigParser(interpolation=ExtendedInterpolation())
    app_config.read("app/config/config.ini")

    app.config['SECRET_KEY'] = app_config.get("SERVER", "SECRET")
    app.config['SQLALCHEMY_DATABASE_URI'] = app_config.get("DATABASE", "DB_URI")


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # added just to suppress a warning

socketio = SocketIO(app, cors_allowed_origins="*")

db = SQLAlchemy(app)

from app import main