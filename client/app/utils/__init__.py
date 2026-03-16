"""
Module Name: Utility functions
Description:
    Utility functions for URL validation, sanitization and API communication.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import re
from functools import wraps

import requests
from flask import abort, session
from flask_login import current_user, logout_user


def validate_url(url):
    """Basic URL validation."""
    url_pattern = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return url_pattern.match(url) is not None


def sanitize_url(url):
    """Basic URL sanitization."""
    return url.strip()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


API_BASE = "http://localhost:5001/api"


def _api_headers():
    token = session.get("jwt")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _handle_401():
    session.pop("jwt", None)
    logout_user()


def api_get(url):
    try:
        r = requests.get(url, headers=_api_headers(), timeout=5)
        if r.status_code == 401:
            _handle_401()
            return None, 401
        if r.status_code == 429:
            return None, 429
        return r, r.status_code
    except requests.RequestException:
        return None, 503


def api_post(url, payload=None, handle_401=True):
    try:
        r = requests.post(url, json=payload, headers=_api_headers(), timeout=5)
        if r.status_code == 401:
            if handle_401:
                _handle_401()
            return None, 401
        if r.status_code == 429:
            return None, 429
        return r, r.status_code
    except requests.RequestException:
        return None, 503

def api_delete(url):
    try:
        r = requests.delete(url, headers=_api_headers(), timeout=5)
        if r.status_code == 401:
            _handle_401()
            return None, 401
        if r.status_code == 429:
            return None, 429
        return r, r.status_code
    except requests.RequestException:
        return None, 503
