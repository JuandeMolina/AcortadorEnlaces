from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Inicializar extensiones de base de datos
    db.init_app(app)
    migrate.init_app(app, db)

    # Inicializar gestor de autenticación
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # redirigir a login si no autenticado

    # Cargar usuario desde ID para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User

        return User.query.get(int(user_id))

    # Registrar blueprints
    from .routes.main import main
    from .routes.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")

    return app
