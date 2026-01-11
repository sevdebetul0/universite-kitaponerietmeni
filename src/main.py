from dotenv import load_dotenv
import json
import os

from flask import Flask, render_template, request, jsonify

from agents.profile_agent import build_user_profile
from agents.recommendation_agent import get_recommendations
from agents.explanation_agent import create_explanation

# .env yükle
load_dotenv()

# Flask app (templates klasörünü otomatik src/templates olarak görür
# yeter ki main.py src içinde olsun)
app = Flask(__name__)

# -----------------------------
# BOOKS API (book.json oku)
# -----------------------------
@app.route("/api/books", methods=["GET"])
def api_books():
    # main.py src içinde -> src/data/book.json
    data_path = os.path.join(app.root_path, "data", "book.json")

    # Dosya yoksa net hata döndür
    if not os.path.exists(data_path):
        return jsonify({
            "error": "book.json bulunamadı",
            "expected_path": data_path,
            "root_path": app.root_path
        }), 500

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            books = json.load(f)
        return jsonify(books)
    except Exception as e:
        return jsonify({
            "error": "book.json okunurken hata oluştu",
            "expected_path": data_path,
            "details": str(e)
        }), 500

# -----------------------------
# UI (index.html)
# -----------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# -----------------------------
# RECOMMEND API (Agents + Groq)
# -----------------------------
@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.get_json(force=True) or {}

    mood = (data.get("mood") or "").strip()
    genre = (data.get("genre") or "").strip()
    last_book = (data.get("last_book") or "").strip()

    if not mood or not genre or not last_book:
        return jsonify({"error": "mood, genre ve last_book zorunlu."}), 400

    user_input = {"mood": mood, "genre": genre, "last_book": last_book}

    try:
        profile = build_user_profile(user_input)
        recommendations = get_recommendations(profile)
        explanation = create_explanation(profile, recommendations)

        return jsonify({
            "profile": profile,
            "recommendations": recommendations,
            "explanation": explanation
        })
    except Exception as e:
        return jsonify({
            "error": "Öneri üretirken hata oluştu",
            "details": str(e)
        }), 500

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("Uyarı: GROQ_API_KEY bulunamadı. .env dosyanı kontrol et.")
    else:
        print("GROQ API anahtarı yüklendi:", key[:8] + "********")

    # debug=True -> otomatik reload
    app.run(host="127.0.0.1", port=5000, debug=True)
