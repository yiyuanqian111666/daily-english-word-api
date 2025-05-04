from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 示例单词数据，可替换为从数据库或文件读取
word_data = {
    "2024-05-01": {"word": "hello", "definition": "a greeting"},
    "2024-05-02": {"word": "world", "definition": "the earth, or the universe"},
    "2024-05-03": {"word": "sun", "definition": "the star at the center of our solar system"}
}

@app.route('/word', methods=['GET'])
def get_word():
    date_str = request.args.get('date')
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')

    word_info = word_data.get(date_str)
    if word_info:
        return jsonify({"date": date_str, "word": word_info["word"], "definition": word_info["definition"]})
    else:
        return jsonify({"error": "No word found for this date"}), 404

if __name__ == '__main__':
    app.run(debug=True)
