"""
Module Name: Error Handlers
Description:
    This module registers HTTP error handlers for the Flask application.
    All errors render a single template (error.html) receiving the HTTP
    status code, a short title and a human-friendly description.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import json
import os

from flask import render_template


def register_error_handlers(app):
    # 1. Cargamos el JSON de forma segura
    # Buscamos la ruta absoluta del archivo errores.json en la misma carpeta
    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, "errors.json")

    with open(json_path, "r", encoding="utf-8") as f:
        error_data = json.load(f)

    # 2. La función única de manejo
    def handle_error(e):
        # Flask nos da el código como INT (ej: 403)
        # Pero el JSON tiene las llaves como STRING (ej: "403")
        code_str = str(getattr(e, "code", 500))

        # Buscamos en el dict usando el string. Fallback al string "500".
        info = error_data.get(code_str, error_data.get("500"))

        return render_template(
            "error.html",
            code=code_str,
            english_title=info["english_title"],
            spanish_title=info["spanish_title"],
            description=info["description"],
        ), int(code_str)

    # 3. Dynamic register
    for code_str in error_data.keys():
        app.register_error_handler(int(code_str), handle_error)
