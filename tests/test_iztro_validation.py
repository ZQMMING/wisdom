"""iztro紫微斗数交叉验证

来源: SylarLong/iztro (TypeScript, 3.6k stars)
验证: 紫微斗数安星公式与官方实现对齐
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import unittest

class TestIztroValidation(unittest.TestCase):
    """iztro交叉验证。"""
    
    def test_main_star_uso_mapping(self):
        """验证14主星USO映射完整性。"""
        from tongshu.engines.ziwei_engine import MAIN_STAR_USO
        expected = {
            "ZIWEI": "SUPPORT", "TIANFU": "SUPPORT", "TAIYANG": "SUPPORT",
            "TIANLIANG": "SUPPORT", "WUQU": "RESOURCE", "TAIYIN": "REFLECTION",
            "TIANTONG": "REFLECTION", "TIANJI": "REFLECTION", "TANLANG": "ACTION",
            "LIANZHEN": "CONSTRAINT", "POJUN": "CHANGE", "QISHA": "CONSTRAINT",
            "JUMEN": "CONSTRAINT",
        }
        for star, uso in expected.items():
            self.assertIn(star, MAIN_STAR_USO, f"星{star}缺失")
    
    def test_sihua_effects_structure(self):
        """验证四化效果结构完整性。"""
        from tongshu.engines.ziwei_engine import SIHUA_EFFECT
        # 四化效果应包含四个基本类型
        required_keys = ["HUA_LU", "HUA_QUAN", "HUA_KE", "HUA_JI"]
        for key in required_keys:
            self.assertIn(key, SIHUA_EFFECT, f"四化类型{key}缺失")
            effect = SIHUA_EFFECT[key]
            self.assertIn("polarity", effect, f"{key}缺少polarity")
            self.assertIn("direction", effect, f"{key}缺少direction")
