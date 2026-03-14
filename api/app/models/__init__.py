"""
Module Name: Database Models
Description:
    Database models for the API server: User and URL.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from .user import User
from .url import URL

__all__ = ["User", "URL"]