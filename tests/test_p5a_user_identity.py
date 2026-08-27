"""Phase 5-A: User Identity Layer 测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
from datetime import date, time

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import psycopg2


class TestUserIdentityLayer(unittest.TestCase):
    """测试 User Identity Layer。"""
    
    @classmethod
    def setUpClass(cls):
        """连接数据库。"""
        cls.conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            dbname="shuntian_kb",
            user="postgres",
            password="postgres"
        )
    
    @classmethod
    def tearDownClass(cls):
        """关闭连接。"""
        cls.conn.close()
    
    def test_user_profiles_table_exists(self):
        """user_profiles 表存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema='public' AND table_name='user_profiles'
        """)
        self.assertEqual(cur.fetchone()[0], 1)
        cur.close()
    
    def test_birth_profiles_table_exists(self):
        """birth_profiles 表存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema='public' AND table_name='birth_profiles'
        """)
        self.assertEqual(cur.fetchone()[0], 1)
        cur.close()
    
    def test_personal_heluo_models_table_exists(self):
        """personal_heluo_models 表存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema='public' AND table_name='personal_heluo_models'
        """)
        self.assertEqual(cur.fetchone()[0], 1)
        cur.close()
    
    def test_daily_state_table_exists(self):
        """daily_state 表存在。"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema='public' AND table_name='daily_state'
        """)
        self.assertEqual(cur.fetchone()[0], 1)
        cur.close()
    
    def test_sample_data_inserted(self):
        """样本数据已插入。"""
        cur = self.conn.cursor()
        
        # 检查用户数
        cur.execute("SELECT COUNT(*) FROM user_profiles")
        self.assertGreater(cur.fetchone()[0], 0)
        
        # 检查出生信息
        cur.execute("SELECT COUNT(*) FROM birth_profiles")
        self.assertGreater(cur.fetchone()[0], 0)
        
        # 检查个人模型
        cur.execute("SELECT COUNT(*) FROM personal_heluo_models")
        self.assertGreater(cur.fetchone()[0], 0)
        
        # 检查每日状态
        cur.execute("SELECT COUNT(*) FROM daily_state")
        self.assertGreater(cur.fetchone()[0], 0)
        
        cur.close()
    
    def test_user_with_anonymous_id(self):
        """用户有 anonymous_id。"""
        cur = self.conn.cursor()
        cur.execute("SELECT anonymous_id FROM user_profiles LIMIT 1")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertIsNotNone(row[0])
        cur.close()
    
    def test_birth_profile_has_true_solar_time(self):
        """出生信息包含真太阳时。"""
        cur = self.conn.cursor()
        cur.execute("SELECT true_solar_time FROM birth_profiles LIMIT 1")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertIsNotNone(row[0])
        cur.close()
    
    def test_heluo_model_has_benming_hexagram(self):
        """个人模型包含本命卦。"""
        cur = self.conn.cursor()
        cur.execute("SELECT benming_hexagram FROM personal_heluo_models LIMIT 1")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertIsNotNone(row[0])
        cur.close()
    
    def test_daily_state_has_energy_state(self):
        """每日状态包含能量状态。"""
        cur = self.conn.cursor()
        cur.execute("SELECT energy_state FROM daily_state ORDER BY state_date DESC LIMIT 1")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertIsNotNone(row[0])
        cur.close()
    
    def test_foreign_key_cascade(self):
        """外键级联删除测试。"""
        cur = self.conn.cursor()
        
        # 插入测试用户
        cur.execute("INSERT INTO user_profiles (anonymous_id) VALUES (%s) RETURNING id", ('cascade-test',))
        user_id = cur.fetchone()[0]
        
        # 插入关联数据
        cur.execute("INSERT INTO birth_profiles (user_id, birth_date) VALUES (%s, %s)", 
                    (user_id, date(2000, 1, 1)))
        cur.execute("INSERT INTO personal_heluo_models (user_id, benming_hexagram) VALUES (%s, %s)",
                    (user_id, '乾上乾下'))
        cur.execute("INSERT INTO daily_state (user_id, state_date, energy_state) VALUES (%s, %s, %s)",
                    (user_id, date.today(), '旺盛'))
        
        # 删除用户
        cur.execute("DELETE FROM user_profiles WHERE id = %s", (user_id,))
        
        # 验证关联数据已删除
        cur.execute("SELECT COUNT(*) FROM birth_profiles WHERE user_id = %s", (user_id,))
        self.assertEqual(cur.fetchone()[0], 0)
        
        cur.execute("SELECT COUNT(*) FROM personal_heluo_models WHERE user_id = %s", (user_id,))
        self.assertEqual(cur.fetchone()[0], 0)
        
        cur.execute("SELECT COUNT(*) FROM daily_state WHERE user_id = %s", (user_id,))
        self.assertEqual(cur.fetchone()[0], 0)
        
        cur.close()


if __name__ == "__main__":
    unittest.main()
