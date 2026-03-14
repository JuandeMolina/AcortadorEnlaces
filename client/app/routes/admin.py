"""
Module Name: Admin Blueprint
Description: Routes for users with admin privileges
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import requests

from flask import Blueprint, render_template, jsonify, session
from flask_login import current_user

from ..utils import admin_required

admin = Blueprint("admin", __name__)

API_BASE = "http://localhost:5001/api"


def _api_headers():
    token = session.get("jwt")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@admin.route("/")
@admin_required
def index():
    try:
        r = requests.get(f"{API_BASE}/admin", headers=_api_headers(), timeout=5)
        data = r.json() if r.status_code == 200 else {}
    except requests.RequestException:
        data = {}

    return render_template(
        "admin.html",
        users=data.get("users", []),
        urls=data.get("urls", []),
        stats=data.get("stats", {})
    )


@admin.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@admin_required
def toggle_admin(user_id):
    if user_id == current_user.id:
        return jsonify({"error": "self_demotion"}), 400

    try:
        r = requests.post(
            f"{API_BASE}/admin/users/{user_id}/toggle-admin",
            headers=_api_headers(),
            timeout=5
        )
        return jsonify(r.json()), r.status_code
    except requests.RequestException:
        return jsonify({"error": "api_unavailable"}), 503


@admin.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({"error": "self_delete"}), 400

    try:
        r = requests.delete(
            f"{API_BASE}/admin/users/{user_id}",
            headers=_api_headers(),
            timeout=5
        )
        return jsonify(r.json()), r.status_code
    except requests.RequestException:
        return jsonify({"error": "api_unavailable"}), 503


@admin.route("/urls/<int:url_id>", methods=["DELETE"])
@admin_required
def delete_url(url_id):
    try:
        r = requests.delete(
            f"{API_BASE}/admin/urls/{url_id}",
            headers=_api_headers(),
            timeout=5
        )
        return jsonify(r.json()), r.status_code
    except requests.RequestException:
        return jsonify({"error": "api_unavailable"}), 503