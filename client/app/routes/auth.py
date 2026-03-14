"""
Module Name: Auth Blueprint
Description: Register, login and logout routes
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import requests

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app,
)
from flask_login import login_user, logout_user, login_required

from ..models import User

auth = Blueprint("auth", __name__)

API_BASE = "http://localhost:5001/api"


def _api_post(endpoint, payload):
    """Helper para POST al api. Devuelve (data, status_code)."""
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=5)
        return r.json(), r.status_code
    except requests.RequestException:
        return {"message": "Error de conexión con el api"}, 503


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        password_confirm = request.form.get("password_confirm") or ""

        if not username or not email or not password:
            return (
                render_template("register.html", error="Rellena todos los campos."),
                400,
            )

        if password != password_confirm:
            return (
                render_template("register.html", error="Las contraseñas no coinciden."),
                400,
            )

        # Registrar en el api
        data, status = _api_post(
            "/users/register",
            {"username": username, "email": email, "password": password},
        )

        if status == 409:
            msg = (
                "Ese nombre de usuario ya está en uso."
                if "username" in data.get("message", "")
                else "Ese correo ya tiene una cuenta asociada."
            )
            return render_template("register.html", error=msg), 409
        if status != 201:
            return (
                render_template("register.html", error="Error al crear la cuenta."),
                status,
            )

        # Login automático tras registro
        login_data, login_status = _api_post(
            "/users/login", {"username": username, "password": password}
        )

        if login_status != 200:
            return redirect(url_for("auth.login"))

        session["jwt"] = login_data["access_token"]
        user = User.from_dict(data)
        login_user(user)
        return redirect(url_for("main.index"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            return (
                render_template(
                    "login.html", error="Introduce tu usuario y contraseña."
                ),
                400,
            )

        data, status = _api_post(
            "/users/login", {"username": username, "password": password}
        )

        if status != 200:
            return (
                render_template(
                    "login.html", error="Usuario o contraseña incorrectos."
                ),
                401,
            )

        session["jwt"] = data["access_token"]
        user = User.from_dict(data["user"])
        login_user(user, remember=True)
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.pop("jwt", None)
    logout_user()
    return redirect(url_for("main.index"))
