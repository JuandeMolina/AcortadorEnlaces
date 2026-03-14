"""
Module Name: Business Logic Services
Description:
    Service classes encapsulating business logic for the API server.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import random

from ..core import db
from ..models import URL


class URLService:
    """Service for URL shortening operations."""

    @staticmethod
    def generate_alias(length=6):
        """Generate a unique alias for the URL."""
        alphabet = "BCDEFGHJKLMNPQRSTUVWXYZ"
        while True:
            alias = "".join(random.choice(alphabet) for _ in range(length))
            if not URL.query.filter_by(alias=alias).first():
                return alias

    @staticmethod
    def create_short_url(original_url, user_id=None):
        """Create a new short URL."""
        alias = URLService.generate_alias()
        url = URL(alias=alias, original_url=original_url, user_id=user_id)  # type: ignore
        db.session.add(url)
        db.session.commit()
        return url

    @staticmethod
    def get_url_by_alias(alias):
        """Retrieve URL by alias."""
        return URL.query.filter_by(alias=alias).first()

    @staticmethod
    def delete_url(url_id, user_id=None):
        """
        Delete a URL.
        If user_id is provided, only deletes if the URL belongs to that user.
        If user_id is None (admin), deletes unconditionally.
        """
        url = URL.query.get(url_id)
        if not url:
            return False
        if user_id is not None and url.user_id != user_id:
            return False
        db.session.delete(url)
        db.session.commit()
        return True