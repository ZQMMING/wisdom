"""端到端流程测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest
from tongshu.engines.heluo import HeluoCanonical
from tongshu.api.profile import resolve_profile, ProfileStatus
from tongshu.engines.time_resolver import TimeResolver


class TestProfileLifecycle(unittest.TestCase):
    """Profile生命周期测试。"""
    
    def test_valid_full_profile_male(self):
        """男性完整资料 → VALID。"""
        resolver = TimeResolver()
        result = resolve_profile(
            gender="male",
            timezone="Asia/Shanghai",
            calendar_system="solar",
            location="Beijing",
            time_resolver=resolver,
        )
        self.assertEqual(result.status, ProfileStatus.VALID)
    
    def test_valid_full_profile_female(self):
        """女性完整资料 → VALID。"""
        resolver = TimeResolver()
        result = resolve_profile(
            gender="female",
            timezone="Asia/Shanghai",
            calendar_system="solar",
            location="Beijing",
            time_resolver=resolver,
        )
        self.assertEqual(result.status, ProfileStatus.VALID)
    
    def test_insufficient_missing_gender(self):
        """缺少gender → INSUFFICIENT。"""
        resolver = TimeResolver()
        result = resolve_profile(
            timezone="Asia/Shanghai",
            calendar_system="solar",
            location="Beijing",
            time_resolver=resolver,
        )
        self.assertEqual(result.status, ProfileStatus.INSUFFICIENT)
        self.assertIn('gender', result.missing_fields)
    
    def test_invalid_gender_rejected(self):
        """无效性别应拒绝。"""
        from tongshu.api.errors import OTCGApiError
        resolver = TimeResolver()
        with self.assertRaises(OTCGApiError):
            resolve_profile(
                gender="unknown",
                timezone="Asia/Shanghai",
                calendar_system="solar",
                location="Beijing",
                time_resolver=resolver,
            )
    
    def test_none_when_no_profile(self):
        """无资料 → NONE。"""
        resolver = TimeResolver()
        result = resolve_profile(
            gender=None,
            timezone=None,
            calendar_system=None,
            location=None,
            time_resolver=resolver,
        )
        self.assertEqual(result.status, ProfileStatus.NONE)
    
    def test_lunar_unsupported(self):
        """农历不支持。"""
        from tongshu.api.errors import OTCGApiError
        resolver = TimeResolver()
        with self.assertRaises(OTCGApiError):
            resolve_profile(
                gender="male",
                timezone="Asia/Shanghai",
                calendar_system="lunar",
                location="Beijing",
                time_resolver=resolver,
            )


class TestGoldenCaseVerification(unittest.TestCase):
    """黄金案例验证。"""
    
    JIXIAOLAN_BAZI = [("甲", "辰"), ("辛", "未"), ("丙", "戌"), ("甲", "午")]
    
    def test_male_prenatal_is_ditian_tai(self):
        """阳年男命 → 地天泰。"""
        c = HeluoCanonical()
        result = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="male",
            birth_hour="午",
            era="zhong",
        )
        self.assertEqual(result.prenatal.hexagram_name, "地天泰")
    
    def test_female_prenatal_is_tiandi_pi(self):
        """阳年女命 → 天地否。"""
        c = HeluoCanonical()
        result = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="female",
            birth_hour="午",
            era="zhong",
        )
        self.assertEqual(result.prenatal.hexagram_name, "天地否")
    
    def test_gender_divergence(self):
        """同八字不同性别 → 结果必须不同。"""
        c = HeluoCanonical()
        male = c.calculate(bazi=self.JIXIAOLAN_BAZI, gender="male", birth_hour="午", era="zhong")
        female = c.calculate(bazi=self.JIXIAOLAN_BAZI, gender="female", birth_hour="午", era="zhong")
        self.assertNotEqual(male.prenatal.hexagram_name, female.prenatal.hexagram_name)
    
    def test_all_golden_cases_pass(self):
        """所有黄金案例通过。"""
        c = HeluoCanonical()
        results = c.run_all_golden_cases()
        for case, passed in results.items():
            self.assertTrue(passed, f"{case} 未通过")


class TestEdgeCases(unittest.TestCase):
    """边界情况测试。"""
    
    def test_midnight_boundary(self):
        """子时边界处理。"""
        c = HeluoCanonical()
        result = c.calculate(
            bazi=[("甲", "辰"), ("辛", "未"), ("丙", "戌"), ("甲", "子")],
            gender="male",
            birth_hour="子",
            era="zhong",
        )
        self.assertIsNotNone(result.prenatal.hexagram_name)
    
    def test_invalid_bazi_length(self):
        """非法八字长度。"""
        c = HeluoCanonical()
        with self.assertRaises(ValueError):
            c.calculate(bazi=[("甲", "辰")], gender="male", birth_hour="子")


if __name__ == '__main__':
    unittest.main()
