from flask import Blueprint, render_template, request, redirect, jsonify
from pathlib import Path
import json
import random

main = Blueprint("main", __name__)

# File-based storage (JSON) for demo/local usage
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "urls.json"


def load_urls():
    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_urls(urls):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(urls, f, ensure_ascii=False, indent=2)


def generate_alias(length=6):
    alphabet = "ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789"
    alias = ""
    for _ in range(length):
        alias += random.choice(alphabet)
    return alias


@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@main.route("/api/shorten", methods=["POST"])
def api_shorten():
    data = request.get_json(silent=True) or request.form or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "missing_url"}), 400

    # Basic validation: require http/https
    if not (url.startswith("http://") or url.startswith("https://")):
        return jsonify({"error": "invalid_url"}), 400

    urls = load_urls()

    # Generate a unique alias
    alias = generate_alias(6)
    attempt = 0
    while alias in urls and attempt < 5:
        alias = generate_alias(6)
        attempt += 1
    if alias in urls:
        return jsonify({"error": "could_not_generate_alias"}), 500

    # Save mapping
    urls[alias] = url
    try:
        save_urls(urls)
    except Exception:
        return jsonify({"error": "storage_error"}), 500

    short_url = request.host_url.rstrip("/") + "/" + alias
    return jsonify({"shortUrl": short_url, "alias": alias}), 201


@main.route("/<short_id>", methods=["GET"])
def redirect_short(short_id):
    urls = load_urls()
    target = urls.get(short_id)
    if not target:
        return "URL no encontrada", 404
    return redirect(target)
