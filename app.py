from flask import Flask, jsonify
import datetime

app = Flask(__name__)

word_list = [
    {"date": "2025-05-04", "word": "hello", "meaning": "A greeting"},
    {"date": "2025-05-05", "word": "world", "meaning": "The earth and all people"},
]

@app.route('/')
def index():
    return "Welcome to Daily English Word API!"

@app.route('/word')
def get_word():
    today = datetime.date.today().isoformat()
    for item in word_list:
        if item["date"] == today:
            return jsonify(item)
    return jsonify({"message": "No word for today yet!"})

if __name__ == '__main__':
    app.run(debug=True)
