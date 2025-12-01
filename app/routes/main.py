from flask import Blueprint, render_template, request, redirect, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import URL
import random
import sqlalchemy

main = Blueprint("main", __name__)


def generate_alias(length=6):
    alphabet = "ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789"
    alias = ""
    for _ in range(length):
        alias += random.choice(alphabet)
    return alias


@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@main.route("/api/shorten", methods=["POST"])
def api_shorten():
    """
    Endpoint para acortar URLs.
    Crea un alias único y lo guarda en la BD asociado al usuario (si está autenticado)
    """
    data = request.get_json(silent=True) or request.form or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "missing_url"}), 400

    # Validación básica: requiere http:// o https://
    if not (url.startswith("http://") or url.startswith("https://")):
        return jsonify({"error": "invalid_url"}), 400

    # Generar un alias único (comprobar colisiones en BD)
    alias = generate_alias(6)
    attempt = 0
    while URL.query.filter_by(alias=alias).first() is not None and attempt < 5:
        alias = generate_alias(6)
        attempt += 1
    if URL.query.filter_by(alias=alias).first() is not None:
        return jsonify({"error": "could_not_generate_alias"}), 500

    # Guardar en BD: si el usuario está autenticado, asociar la URL a su cuenta
    user_id = current_user.id if current_user.is_authenticated else None
    new_url = URL(alias=alias, original_url=url, user_id=user_id)
    try:
        db.session.add(new_url)
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "storage_error"}), 500

    short_url = request.host_url.rstrip("/") + "/" + alias
    return jsonify({"shortUrl": short_url, "alias": alias}), 201


@main.route("/<short_id>", methods=["GET"])
def redirect_short(short_id):
    target = URL.query.filter_by(alias=short_id).first()
    if not target:
        return "URL no encontrada", 404
    return redirect(target.original_url)


@main.route("/dashboard", methods=["GET"])
@login_required  # Solo accesible si el usuario está autenticado
def dashboard():
    """
    Panel de control del usuario: muestra sus URLs acortadas
    """
    # Obtener todas las URLs del usuario autenticado
    urls = URL.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", urls=urls)


@main.route("/api/urls", methods=["GET"])
@login_required  # Solo accesible si el usuario está autenticado
def get_user_urls():
    """
    API endpoint para obtener las URLs del usuario autenticado en JSON
    """
    urls = URL.query.filter_by(user_id=current_user.id).all()
    return (
        jsonify(
            [
                {
                    "alias": url.alias,
                    "original_url": url.original_url,
                    "created_at": url.created_at.isoformat(),
                }
                for url in urls
            ]
        ),
        200,
    )
