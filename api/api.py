#!/usr/bin/env python3
"""
API Server Entry Point
Description:
    Entry point for the NanoLink API server.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
