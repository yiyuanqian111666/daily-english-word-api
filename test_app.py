import json
import unittest
from app import app, init_db


class TestFlaskAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """所有测试运行前执行一次：初始化应用与数据库"""
        app.config["TESTING"] = True
        init_db()

    def setUp(self):
        """每个测试用例运行前执行：创建客户端和上下文"""
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()

    def tearDown(self):
        """每个测试用例运行后执行：清理上下文"""
        self.app_context.pop()

    # ==================== 🏠 首页 ====================
    def test_home(self):
        response = self.client.get("/")
        # 前端模板页面的状态码为 200
        self.assertEqual(response.status_code, 200)

    # ==================== 📘 学习接口（多难度、分类筛选与新字段适配） ====================
    def test_learn_by_difficulty(self):
        # 测试默认 easy 难度
        response = self.client.get("/api/learn")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["difficulty"], "easy")
        self.assertIn("word", data)
        self.assertIn("meaning", data)
        self.assertIn("example", data)
        self.assertIn("grammar_note", data)
        # 兼容 v7.0 新增的 user_status 字段（RPG 经验与称号）
        self.assertIn("user_status", data)
        self.assertIn("xp", data["user_status"])
        self.assertIn("title", data["user_status"])

    def test_learn_hard_difficulty(self):
        # 测试地道俚语与长句 Hard 难度
        response = self.client.get("/api/learn?difficulty=hard")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["difficulty"], "hard")
        self.assertIn("word", data)
        self.assertIn("meaning", data)
        self.assertIn("example", data)

    def test_learn_category_filter(self):
        # 测试分类筛选参数是否正常响应
        response = self.client.get("/api/learn?difficulty=easy&category=fruit")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["category"], "fruit")

    # ==================== 🛒 冒险商店与背包系统测试 ====================
    def test_shop_items(self):
        # 测试获取商店商品与用户 XP 余额
        response = self.client.get("/api/shop/items")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("items", data)
        self.assertIn("user_xp", data)
        self.assertIsInstance(data["items"], list)
        self.assertGreater(len(data["items"]), 0)

    def test_shop_buy_item(self):
        # 测试购买商品接口（购买 ID=1 的道具）
        payload = {"item_id": 1}
        response = self.client.post(
            "/api/shop/buy",
            data=json.dumps(payload),
            content_type="application/json",
        )
        # 若积分足够应返回 200 成功，若初始积分不足则返回 400（符合业务逻辑）
        self.assertIn(response.status_code, [200, 400])

    # ==================== 🧠 提交挑战与赌徒模式结算测试 ====================
    def test_submit_challenge(self):
        payload = {
            "used_time": 3.5,
            "success": True,
            "difficulty": "normal",
            "streak": 2,
            "bet_amount": 0,
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
        self.assertIn("interactive_comment", data)
        self.assertIn("earned_xp", data)
        self.assertIn("user_profile", data)
        self.assertIn("xp", data["user_profile"])
        self.assertIn("title", data["user_profile"])

    def test_submit_gambler_challenge(self):
        # 测试高风险赌徒模式挑战提交
        payload = {
            "used_time": 2.0,
            "success": True,
            "difficulty": "gambler",
            "streak": 0,
            "bet_amount": 10,
        }

        response = self.client.post(
            "/api/challenge/submit",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["earned_xp"], 10)

    def test_submit_challenge_bad_request(self):
        # 传递非法类型参数
        payload = {"used_time": "not-a-number"}
        response = self.client.post(
            "/api/challenge/submit",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()