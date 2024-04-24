"""
This module initializes the Flask application and creates the application factory.

It imports necessary modules and sets up the Flask application with the required configurations.
The create_app function is the application factory that creates and configures the Flask application

Functions:
- create_app(test_config=None): Creates and configures the Flask application.

Variables:
- db: SQLAlchemy object for database operations.
"""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from .config import Config

db = SQLAlchemy()
cache = Cache()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

    with app.app_context():
        from .api import setup_routes
        setup_routes(app)

    return app

