from flask import Flask, jsonify, request
import sqlite3
from datetime import date
import random

app = Flask(__name__)
DB_NAME = "words.db"


# -------------------- 📦 数据库初始化 --------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            meaning TEXT NOT NULL,
            example TEXT
        );
    ''')
    conn.commit()
    conn.close()


# -------------------- 🔥 核心 API 功能 --------------------

@app.route("/")
def home():
    return jsonify({
        "message": "✅ Daily English Word API is running!",
        "endpoints": {
            "/api/today": "Get today's word",
            "/api/random": "Get random word",
            "/api/add": "Add new word (POST)",
            "/api/list": "Get all words"
        }
    })


@app.route("/api/today")
def get_today_word():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT word, meaning, example FROM words")
    words = cursor.fetchall()
    conn.close()

    if not words:
        return jsonify({"error": "No words in database. Please add words first!"}), 404

    index = date.today().toordinal() % len(words)
    word, meaning, example = words[index]

    return jsonify({
        "date": str(date.today()),
        "word": word,
        "meaning": meaning,
        "example": example
    })


@app.route("/api/random")
def get_random_word():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT word, meaning, example FROM words")
    words = cursor.fetchall()
    conn.close()

    if not words:
        return jsonify({"error": "Database is empty. Add some words first!"}), 404

    word, meaning, example = random.choice(words)
    return jsonify({
        "word": word,
        "meaning": meaning,
        "example": example
    })


@app.route("/api/add", methods=["POST"])
def add_word():
    data = request.json
    if not data or "word" not in data or "meaning" not in data:
        return jsonify({"error": "Missing 'word' or 'meaning' in request"}), 400

    word = data["word"]
    meaning = data["meaning"]
    example = data.get("example", "")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO words (word, meaning, example) VALUES (?, ?, ?)",
                   (word, meaning, example))
    conn.commit()
    conn.close()

    return jsonify({"message": "✅ Word added successfully!", "word": word})


@app.route("/api/list")
def list_words():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, word, meaning, example FROM words ORDER BY id DESC")
    words = cursor.fetchall()
    conn.close()

    return jsonify([
        {"id": w[0], "word": w[1], "meaning": w[2], "example": w[3]} for w in words
    ])


if __name__ == "__main__":
    init_db()
    print("🚀 Daily English Word API running at http://127.0.0.1:5000")
    app.run(debug=True)
