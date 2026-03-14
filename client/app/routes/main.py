"""
Module Name: Main Blueprint
Description: Main routes for the application
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import requests

from flask import Blueprint, render_template, request, redirect, jsonify, abort, session
from flask_login import current_user, login_required

main = Blueprint("main", __name__)

API_BASE = "http://localhost:5001/api"


def _api_headers():
    """Devuelve las cabeceras con JWT si el usuario está autenticado."""
    token = session.get("jwt")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@main.route("/api/shorten", methods=["POST"])
def api_shorten():
    data = request.get_json(silent=True) or request.form or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "missing_url"}), 400

    try:
        r = requests.post(
            f"{API_BASE}/urls/shorten",
            json={"url": url},
            headers=_api_headers(),
            timeout=5,
        )
        if r.status_code == 201:
            return jsonify(r.json()), 201
        return jsonify(r.json()), r.status_code
    except requests.RequestException:
        return jsonify({"error": "api_unavailable"}), 503


@main.route("/<short_id>", methods=["GET"])
def redirect_short(short_id):
    if "." in short_id:
        abort(404)

    try:
        r = requests.get(
            f"{API_BASE}/urls/{short_id}", timeout=5, allow_redirects=False
        )
        if r.status_code == 200:
            return redirect(r.json().get("original_url"))
        abort(404)
    except requests.RequestException:
        abort(503)


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    try:
        r = requests.get(f"{API_BASE}/urls", headers=_api_headers(), timeout=5)
        urls = r.json() if r.status_code == 200 else []
    except requests.RequestException:
        urls = []
    return render_template("dashboard.html", urls=urls)


@main.route("/api/urls", methods=["GET"])
@login_required
def get_user_urls():
    try:
        r = requests.get(f"{API_BASE}/urls", headers=_api_headers(), timeout=5)
        return jsonify(r.json()), r.status_code
    except requests.RequestException:
        return jsonify({"error": "api_unavailable"}), 503


@main.route("/api/urls/<int:url_id>", methods=["DELETE"])
@login_required
def delete_user_url(url_id):
    try:
        r = requests.delete(
            f"{API_BASE}/urls/{url_id}", headers=_api_headers(), timeout=5
        )
        return jsonify(r.json()), r.status_code
    except requests.RequestException:
        return jsonify({"error": "api_unavailable"}), 503
