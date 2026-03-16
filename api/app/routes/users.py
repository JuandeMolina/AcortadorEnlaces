"""
Module Name: Users Namespace
Description:
    Endpoints for user management.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from ..models import User
from ..core import db, limiter

ns = Namespace("users", description="Operaciones sobre usuarios", path="/api/users")

# Models (for swagger documentation)

login_model = ns.model(
    "Login",
    {
        "username": fields.String(required=True, description="Nombre de usuario"),
        "password": fields.String(required=True, description="Contraseña"),
    },
)

token_model = ns.model(
    "Token", {"access_token": fields.String(description="JWT access token")}
)

user_model = ns.model(
    "User",
    {
        "id": fields.Integer(description="ID del usuario"),
        "username": fields.String(description="Nombre de usuario"),
        "email": fields.String(description="Email"),
        "is_admin": fields.Boolean(description="Es administrador"),
    },
)

register_input = ns.model(
    "RegisterInput",
    {
        "username": fields.String(required=True),
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    },
)

user_output = ns.model(
    "UserOutput",
    {
        "id": fields.Integer,
        "username": fields.String,
        "email": fields.String,
        "is_admin": fields.Boolean,
    },
)

token_output = ns.model(
    "TokenOutput", {"access_token": fields.String, "user": fields.Nested(user_output)}
)

# Endpoints


@ns.route("/login")
class Login(Resource):

    @limiter.limit("10 per minute")
    @ns.expect(login_model)
    @ns.response(200, "Login correcto", token_model)
    @ns.response(400, "Faltan campos")
    @ns.response(401, "Credenciales incorrectas")
    def post(self):
        """Login and get a JWT"""
        data = request.get_json(silent=True) or {}

        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            ns.abort(400, "Introduce tu usuario y contraseña.")

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            ns.abort(401, "Usuario o contraseña incorrectos.")

        return {
            "access_token": create_access_token(identity=str(user.id)),  # type: ignore
            "user": {
                "id": user.id,  # type: ignore
                "username": user.username,  # type: ignore
                "email": user.email,  # type: ignore
                "is_admin": user.is_admin,  # type: ignore
            },
        }, 200


@ns.route("/register")
class Register(Resource):

    @limiter.limit("5 per minute")
    @ns.expect(register_input)
    @ns.marshal_with(user_output)
    def post(self):
        """Register a new user."""
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        if not username or not email or not password:
            ns.abort(400, "missing_fields")

        from ..models import User

        if User.query.filter_by(username=username).first():
            ns.abort(409, "username_taken")
        if User.query.filter_by(email=email).first():
            ns.abort(409, "email_taken")

        user = User(username=username, email=email, is_admin=False)  # type: ignore
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            ns.abort(500, "storage_error")

        return user, 201


@ns.route("/me")
class Me(Resource):

    @jwt_required()
    @ns.doc(security="Bearer")
    @ns.response(200, "OK", user_model)
    @ns.response(404, "Usuario no encontrado")
    def get(self):
        """Get authenticated user data"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            ns.abort(404, "Usuario no encontrado.")

        return {
            "id": user.id,  # type: ignore
            "username": user.username,  # type: ignore
            "email": user.email,  # type: ignore
            "is_admin": user.is_admin,  # type: ignore
        }, 200
