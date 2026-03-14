"""
Module Name: Core Configuration
Description:
    Creates the Flask app and initializes extensios for the API server.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import os
import logging
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from flask_jwt_extended import JWTManager


# Extensions
db = SQLAlchemy()
migrate = Migrate()
api = Api(
    title="NanoLink API",
    version="1.0",
    description="API para acortamiento y gestión URLs.",
    doc="/docs",
    authorizations={
        "Bearer": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Escribe: Bearer <token> para autenticar",
        }
    },
)
jwt = JWTManager()


def create_app(config_class=None):
    """Aplication factory"""
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    app = Flask(__name__)

    # Load config
    if config_class:
        app.config.from_object(config_class)
    else:
        import config as cfg

        app.config.from_object(cfg.Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    setup_logging(app)
    jwt.init_app(app)

    # Register namespaces (equivalent to blueprints in Flask-RESTX)

    from ..routes.urls import ns as urls_ns
    from ..routes.users import ns as users_ns
    from ..routes.admin import ns as admin_ns

    api.add_namespace(urls_ns)
    api.add_namespace(users_ns)
    api.add_namespace(admin_ns)
    api.init_app(app)

    return app


def setup_logging(app):
    """Setup basic logging configuration"""
    if not app.debug:
        log_dir = "logs"
        log_file = os.path.join(log_dir, "api.log")

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)