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

    # ==================== 📘 多邻国式三阶段学习接口测试 ====================
    def test_learn_stage_1(self):
        """测试阶段一：沉浸式认读接口"""
        response = self.client.get("/api/learn?difficulty=easy&stage=1")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["difficulty"], "easy")
        self.assertEqual(data["stage"], 1)
        self.assertIn("word", data)
        self.assertIn("meaning", data)
        self.assertIn("example", data)
        self.assertIn("challenge_config", data)
        self.assertIn("user_status", data)

    def test_learn_stage_2(self):
        """测试阶段二：互动拼写辅助接口（应包含乱序字母或提示）"""
        response = self.client.get("/api/learn?difficulty=normal&stage=2")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["stage"], 2)
        self.assertIn("scrambled_letters", data)
        self.assertIn("hint", data)

    def test_learn_hard_difficulty(self):
        """测试困难难度长句与学术词汇获取"""
        response = self.client.get("/api/learn?difficulty=hard&stage=3")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["difficulty"], "hard")
        self.assertIn("challenge_config", data)

    # ==================== 🛒 冒险商店与背包系统测试 ====================
    def test_shop_items(self):
        """测试获取商店商品与用户 XP 余额"""
        response = self.client.get("/api/shop/items")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("items", data)
        self.assertIn("user_xp", data)
        self.assertIsInstance(data["items"], list)
        self.assertGreater(len(data["items"]), 0)

    def test_shop_buy_item(self):
        """测试购买商品接口（购买 ID=1 的道具）"""
        payload = {"item_id": 1}
        response = self.client.post(
            "/api/shop/buy",
            data=json.dumps(payload),
            content_type="application/json",
        )
        # 若积分足够应返回 200 成功，若初始积分不足则返回 400（符合业务逻辑）
        self.assertIn(response.status_code, [200, 400])

    # ==================== 🧠 多阶段挑战与结算测试 ====================
    def test_submit_challenge_stage_3(self):
        """测试阶段三极限默写挑战提交与经验结算"""
        payload = {
            "word_id": 1,
            "stage": 3,
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
        self.assertEqual(data["stage"], 3)
        self.assertIn("grade", data)
        self.assertIn("streak", data)
        self.assertTrue(data["success"])
        self.assertIn("interactive_comment", data)
        self.assertIn("earned_xp", data)
        self.assertIn("user_profile", data)
        self.assertIn("xp", data["user_profile"])
        self.assertIn("title", data["user_profile"])


if __name__ == "__main__":
    unittest.main()