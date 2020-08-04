from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from configparser import ConfigParser, ExtendedInterpolation
from os import getenv

from logging.config import dictConfig
from app.logging_helper.LogFilter import LogFilter

app = Flask(__name__)
CORS(app, support_credentials=True)

# Load Config
if getenv("USE_ENV_VAR"):
    app.config['SECRET_KEY'] = getenv("SECRET")
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv("DATABASE_URL")
    app.config['ROOM_BACK_OFF'] = getenv("ROOM_BACK_OFF")
    app.config['PLAYER_INACTIVITY'] = getenv("PLAYER_INACTIVITY")
    app.config['SCHEDULER_ROOM_DEACTIVATION'] = getenv("SCHEDULER_ROOM_DEACTIVATION")
    app.config['SCHEDULER_ROOM_DELETION'] = getenv("SCHEDULER_ROOM_DELETION")
    log_level = getenv("ROOT_LOG_LEVEL")
    default_format = getenv('DEFAULT_FORMAT')
else:
    app_config = ConfigParser(interpolation=ExtendedInterpolation())
    app_config.read("app/config/config.ini")

    app.config['SECRET_KEY'] = app_config.get("SERVER", "SECRET")
    app.config['SQLALCHEMY_DATABASE_URI'] = app_config.get("DATABASE", "DB_URI")
    app.config['ROOM_BACK_OFF'] = app_config.get("INTERVALS", "ROOM_BACK_OFF")
    app.config['PLAYER_INACTIVITY'] = app_config.get("INTERVALS", "PLAYER_INACTIVITY")
    app.config['SCHEDULER_ROOM_DEACTIVATION'] = app_config.get("INTERVALS", "SCHEDULER_ROOM_DEACTIVATION")
    app.config['SCHEDULER_ROOM_DELETION'] = app_config.get("INTERVALS", "SCHEDULER_ROOM_DELETION")
    log_level = app_config.get('LOGGER', 'ROOT_LOG_LEVEL')
    default_format = app_config.get('LOGGER', 'DEFAULT_FORMAT')

# Configure app logger
dictConfig({
    'version': 1,
    'filters': {
        'default_filter': {
            '()': LogFilter
        }
    },
    'formatters': {'default': {
        'format': default_format,
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default',
        'filters': ['default_filter']
    }},
    'root': {
        'level': log_level,
        'handlers': ['wsgi']
    }
})

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # added just to suppress a warning

socketio = SocketIO(app, cors_allowed_origins="*")

db = SQLAlchemy(app, metadata=metadata)

from app import main
