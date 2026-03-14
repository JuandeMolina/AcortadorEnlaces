"""
Module Name: Client User Model
Description:
    Lightweight User class for Flask-Login.
    No database — se construye con los datos que devuelve el api.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, username, email, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin

    @staticmethod
    def from_dict(data):
        """Construye un User a partir del dict que devuelve el api."""
        return User(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            is_admin=data.get("is_admin", False)
        )