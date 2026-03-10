#!/usr/bin/env python3
"""
Application Entry Point
Description:
    This module serves as the entry point for the Flask application.
    It creates the app instance and runs the development server.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from app import create_app
from scripts.init_db import setup_app

app = create_app()

if __name__ == "__main__":
    setup_app()
    app.run(host="0.0.0.0", port=5003, debug=False, use_reloader=False)
