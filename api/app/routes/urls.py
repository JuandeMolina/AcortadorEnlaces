"""
Module Name: URLs Namespace
Description: URL shortening endpoints
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from ..core import db
from ..services import URLService
from ..utils import validate_url, sanitize_url

ns = Namespace("urls", description="URL shortening operations", path="/api/urls")

# ── Models ────────────────────────────────────────────────────────────────────

shorten_input = ns.model(
    "ShortenInput", {"url": fields.String(required=True, description="URL to shorten")}
)

shorten_output = ns.model(
    "ShortenOutput", {"shortUrl": fields.String, "alias": fields.String}
)

url_item = ns.model(
    "URLItem",
    {
        "id": fields.Integer,
        "alias": fields.String,
        "original_url": fields.String,
        "created_at": fields.String,
    },
)


# ── Resources ─────────────────────────────────────────────────────────────────


@ns.route("/shorten")
class Shorten(Resource):

    @ns.doc(security="Bearer")
    @ns.expect(shorten_input)
    @ns.marshal_with(shorten_output)
    @jwt_required(optional=True)
    def post(self):
        """Shorten a URL. Authenticated users have the link saved to their account."""
        data = request.get_json(silent=True) or {}
        url = (data.get("url") or "").strip()

        if not url:
            ns.abort(400, "missing_url")

        url = sanitize_url(url)
        if not validate_url(url):
            ns.abort(400, "invalid_url")

        user_id = get_jwt_identity()  # None if not authenticated
        if user_id:
            user_id = int(user_id)

        try:
            new_url = URLService.create_short_url(url, user_id)
        except SQLAlchemyError:
            db.session.rollback()
            ns.abort(503, "storage_error")

        # Construir short URL usando el host de la petición
        base = request.host_url.rstrip("/")
        return {"shortUrl": f"{base}/{new_url.alias}", "alias": new_url.alias}, 201


@ns.route("")
class URLList(Resource):

    @ns.marshal_list_with(url_item)
    @ns.doc(security="Bearer")
    @jwt_required()
    def get(self):
        """Get all URLs belonging to the authenticated user."""
        user_id = int(get_jwt_identity())
        from ..models import URL

        urls = URL.query.filter_by(user_id=user_id).all()
        return [
            {
                "id": u.id,
                "alias": u.alias,
                "original_url": u.original_url,
                "created_at": u.created_at.isoformat(),
            }
            for u in urls
        ], 200


@ns.route("/<int:url_id>")
class URLDetail(Resource):

    @ns.doc(security="Bearer")
    @jwt_required()
    def delete(self, url_id):
        """Delete a URL owned by the authenticated user."""
        user_id = int(get_jwt_identity())
        try:
            success = URLService.delete_url(url_id, user_id)
        except SQLAlchemyError:
            db.session.rollback()
            ns.abort(500, "delete_failed")

        if not success:
            ns.abort(404, "not_found")

        return {"success": True}, 200


@ns.route("/<string:alias>")
class URLRedirect(Resource):

    def get(self, alias):
        """Get original URL by alias."""
        from ..models import URL

        url = URL.query.filter_by(alias=alias).first()
        if not url:
            ns.abort(404, "not_found")
        return {"original_url": url.original_url}, 200  # type: ignore
