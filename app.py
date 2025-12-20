from flask import Flask, jsonify, request
import sqlite3
from datetime import date
import random

app = Flask(__name__)
DB_NAME = "words.db"


# -------------------- 📦 数据库初始化 --------------------
def init_db():
    try:
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
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
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
            "/api/list": "Get all words (with pagination)"
        }
    })


@app.route("/api/today")
def get_today_word():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT word, meaning, example FROM words")
        words = cursor.fetchall()
        
        if not words:
            # 如果没有词汇，则添加默认词汇
            default_word = ("serendipity", "the occurrence and development of events by chance in a happy or beneficial way", "The discovery was pure serendipity.")
            cursor.execute("INSERT INTO words (word, meaning, example) VALUES (?, ?, ?)", default_word)
            conn.commit()
            words.append(default_word)

        index = date.today().toordinal() % len(words)
        word, meaning, example = words[index]

        return jsonify({
            "date": str(date.today()),
            "word": word,
            "meaning": meaning,
            "example": example
        })
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        conn.close()


@app.route("/api/random")
def get_random_word():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT word, meaning, example FROM words")
        words = cursor.fetchall()

        if not words:
            return jsonify({"error": "No words in the database."}), 404

        word, meaning, example = random.choice(words)
        return jsonify({
            "word": word,
            "meaning": meaning,
            "example": example
        })
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        conn.close()


@app.route("/api/add", methods=["POST"])
def add_word():
    data = request.json
    if not data or "word" not in data or "meaning" not in data:
        return jsonify({"error": "Missing 'word' or 'meaning' in request"}), 400

    word = data["word"]
    meaning = data["meaning"]
    example = data.get("example", "")

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO words (word, meaning, example) VALUES (?, ?, ?)", (word, meaning, example))
        conn.commit()
        return jsonify({"message": "✅ Word added successfully!", "word": word})
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        conn.close()


@app.route("/api/list")
def list_words():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        offset = (page - 1) * per_page
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, word, meaning, example FROM words LIMIT ? OFFSET ?", (per_page, offset))
        words = cursor.fetchall()
        
        return jsonify([{
            "id": w[0], "word": w[1], "meaning": w[2], "example": w[3]
        } for w in words])
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("🚀 Daily English Word API running at http://127.0.0.1:5000")
    app.run(debug=True)
