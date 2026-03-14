"""
Module Name: Database URL Model
Description:
    Database URLs table model.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from datetime import datetime, timezone

from ..core import db


class URL(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    alias: str = db.Column(db.String(6), unique=True, nullable=False, index=True)
    original_url: str = db.Column(db.Text, nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<URL {self.alias} -> {self.original_url}>"
