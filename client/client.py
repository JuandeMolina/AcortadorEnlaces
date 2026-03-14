#!/usr/bin/env python3
"""
Application Entry Point
Description:
    This module serves as the entry point for the Flask client application.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
