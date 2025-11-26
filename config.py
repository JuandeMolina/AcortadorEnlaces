import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + str(BASE_DIR / "data" / "app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
