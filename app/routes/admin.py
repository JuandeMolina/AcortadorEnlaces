"""
Module Name: Admin Blueprint
Description: Routes for users with admin privileges
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    abort,
    jsonify,
)
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from ..core import db
from ..models import User, URL
from ..utils import admin_required

admin = Blueprint("admin", __name__)


# ── Dashboard ──────────────────────────────────────────────────────────────


@admin.route("/")
@admin_required
def index():
    """Panel principal: stats globales + listado de usuarios y URLs."""
    users = User.query.order_by(User.id).all()  # type: ignore
    urls = URL.query.order_by(URL.created_at.desc()).all()

    stats = {
        "total_users": len(users),
        "total_admins": sum(1 for u in users if u.is_admin),
        "total_urls": len(urls),
        "anonymous_urls": sum(1 for u in urls if u.user_id is None),
    }

    return render_template("admin.html", users=users, urls=urls, stats=stats)


# ── User management ────────────────────────────────────────────────────────


@admin.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@admin_required
def toggle_admin(user_id):
    """Promover o degradar el rol admin de un usuario."""
    user = User.query.get_or_404(user_id)

    # Un admin no puede quitarse a sí mismo el rol
    if user.id == current_user.id:
        return jsonify({"error": "self_demotion"}), 400

    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        return jsonify({"success": True, "is_admin": user.is_admin}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "db_error"}), 500


@admin.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """Eliminar un usuario y todos sus enlaces."""
    user = User.query.get_or_404(user_id)

    # Un admin no puede eliminarse a sí mismo
    if user.id == current_user.id:
        return jsonify({"error": "self_delete"}), 400

    try:
        # Los URLs del usuario se eliminan en cascada gracias a la FK,
        # pero si no tienes ON DELETE CASCADE, los borramos explícitamente.
        URL.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "db_error"}), 500


# ── URL management ─────────────────────────────────────────────────────────


@admin.route("/urls/<int:url_id>", methods=["DELETE"])
@admin_required
def delete_url(url_id):
    """Eliminar cualquier URL del sistema."""
    url = URL.query.get_or_404(url_id)

    try:
        db.session.delete(url)
        db.session.commit()
        return jsonify({"success": True}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "db_error"}), 500
