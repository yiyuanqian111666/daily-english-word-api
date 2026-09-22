import json
import unittest
from app import app, init_db


class TestFlaskAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 初始化数据库与应用上下文
        init_db()
        app.testing = True
        cls.client = app.test_client()

    # ==================== 🏠 首页 ====================
    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("version", data)
        self.assertIn("features", data)

    # ==================== 📘 学习接口 ====================
    def test_learn_word(self):
        response = self.client.get("/api/learn?mode=word")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["mode"], "word")
        self.assertIn("word", data)
        self.assertIn("meaning", data)
        self.assertIn("example", data)

    def test_learn_dialog(self):
        # 先添加一个测试对话，确保有数据可查
        self.client.post(
            "/api/add",
            data=json.dumps({"dialog": "Hello, how are you?", "scene": "daily"}),
            content_type="application/json",
        )

        response = self.client.get("/api/learn?mode=dialog&scene=daily")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["mode"], "dialog")
        self.assertIn("content", data)
        self.assertEqual(data["scene"], "daily")

    def test_learn_invalid_mode(self):
        response = self.client.get("/api/learn?mode=invalid")
        self.assertEqual(response.status_code, 400)

    # ==================== 🧠 提交挑战 ====================
    def test_submit_challenge(self):
        payload = {
            "used_time": 5,
            "success": True,
            "mode": "word",
            "content": "test",
            "streak": 1,
        }

        response = self.client.post(
            "/api/challenge/submit",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("grade", data)
        self.assertIn("streak", data)
        self.assertTrue(data["success"])

    def test_submit_challenge_bad_request(self):
        # 传递非法类型
        payload = {"used_time": "not-a-number"}
        response = self.client.post(
            "/api/challenge/submit",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    # ==================== 🏆 排行榜（含分页） ====================
    def test_leaderboard(self):
        response = self.client.get("/api/leaderboard?limit=5&offset=0")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 5)

    # ==================== 🔍 单词检索接口（新增） ====================
    def test_search_words(self):
        # 先添加一个特定单词
        self.client.post(
            "/api/add",
            data=json.dumps(
                {
                    "word": "telescope",
                    "meaning": "望远镜",
                    "example": "I look through the telescope.",
                }
            ),
            content_type="application/json",
        )

        response = self.client.get("/api/words/search?q=telescope")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(any(item["word"] == "telescope" for item in data))

    # ==================== ➕ 添加数据 ====================
    def test_add_word(self):
        payload = {
            "word": "testword",
            "meaning": "测试",
            "example": "This is a test.",
        }

        response = self.client.post(
            "/api/add",
            data=json.dumps(payload),
            content_type="application/json",
        )

        # 对应后端优化后的 201 Created 状态码
        self.assertEqual(response.status_code, 201)

        data = response.get_json()
        self.assertIn("message", data)

    def test_add_invalid_data(self):
        # 传入既没有 word 也没有 dialog 的空 payload
        payload = {"invalid_key": "value"}
        response = self.client.post(
            "/api/add",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()