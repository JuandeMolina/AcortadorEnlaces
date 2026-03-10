#!/usr/bin/env python3

"""
Module Name: Application Setup Script
Description:
    This module sets up the application, including
    database initialization and startup messages.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import sys
import socket
import subprocess
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core import create_app


def setup_app():
    """Setup the application: initialize database if needed and print startup info."""
    # Verificar y inicializar base de datos si no existe
    db_path = Path(__file__).parent.parent / "data" / "app.db"
    migrations_path = Path(__file__).parent.parent / "migrations"
    if not db_path.exists():
        print("Base de datos no encontrada. Inicializando...")
        # Crear directorio data si no existe
        db_path.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["FLASK_APP"] = "acortadorenlaces.py"
        cwd = Path(__file__).parent.parent
        flask_cmd = str(Path(__file__).parent.parent / "venv" / "bin" / "flask")
        if not migrations_path.exists():
            subprocess.run([flask_cmd, "db", "init"], env=env, cwd=cwd, check=True)
        subprocess.run(
            [flask_cmd, "db", "migrate", "-m", "Initial migration"],
            env=env,
            cwd=cwd,
            check=True,
        )
        subprocess.run([flask_cmd, "db", "upgrade"], env=env, cwd=cwd, check=True)
        print("Base de datos inicializada.")

    # Obtener la IP local
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Aplicación disponible en: http://{local_ip}:5003")


def init_db():
    """Legacy function for manual database initialization."""
    app = create_app()
    with app.app_context():
        from app.core import db

        db.create_all()
        print("Database initialized.")


if __name__ == "__main__":
    init_db()
