"""
Module Name: Auth Blueprint
Description: Register, login and logout routes
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT

Extra details:
    GET method: shows form (register or login)
    POST method: handles user input from the form
"""

from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required

from ..core import db
from ..models import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data
        username = (request.form.get("username") or "").strip()
        email    = (request.form.get("email")    or "").strip()
        password = request.form.get("password") or ""
        password_confirm = request.form.get("password_confirm") or ""

        # Validation errors: re-render the form with a message
        if not username or not email or not password:
            return render_template("register.html", error="Rellena todos los campos."), 400

        if password != password_confirm:
            return render_template("register.html", error="Las contraseñas no coinciden."), 400

        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Ese nombre de usuario ya está en uso."), 409

        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Ese correo ya tiene una cuenta asociada."), 409

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("main.index"))
        except Exception:
            db.session.rollback()
            abort(500)  # Triggers the 500 handler → renders error.html

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        # Validation error: re-render the form with a message
        if not username or not password:
            return render_template("login.html", error="Introduce tu usuario y contraseña."), 400

        user = User.query.filter_by(username=username).first()

        # Wrong credentials: re-render the form with a generic message
        # (deliberately vague: don't reveal whether the username exists)
        if not user or not user.check_password(password):
            return render_template("login.html", error="Usuario o contraseña incorrectos."), 401

        login_user(user, remember=True)
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))