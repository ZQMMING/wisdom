# -*- coding: utf-8 -*-
"""ZiweiMethodProfile 测试（Z10）。

覆盖：
- MethodId / RuleType / ConfidenceLevel 枚举值
- EvidenceRef / RuleSpec 数据结构
- 四化表差异（戊干科星）
- 各流派特征（自化/立极/空宫/流昌流曲/小限）
- 流派注册表（get_profile / list_available_methods）
- 抽象基类不可直接实例化
- sihua_differs 检测
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.ziwei_method_profile import (
    MethodId,
    RuleType,
    ConfidenceLevel,
    EvidenceRef,
    RuleSpec,
    ZiweiMethodProfile,
    SanheProfile,
    ZhongzhouProfile,
    FeixingProfile,
    QintianProfile,
    get_profile,
    list_available_methods,
    sihua_differs,
    SIHUA_TABLE_CLASSIC,
    SIHUA_TABLE_ZHONGZHOU,
)


class TestEnumValues(unittest.TestCase):
    """枚举值完整性测试。"""

    def test_method_id_values(self):
        """四个流派全部定义。"""
        ids = [m.value for m in MethodId]
        self.assertIn("sanhe", ids)
        self.assertIn("zhongzhou", ids)
        self.assertIn("feixing", ids)
        self.assertIn("qintian", ids)
        self.assertEqual(len(ids), 4)

    def test_method_id_labels_zh(self):
        """每个 MethodId 有中文字符标签。"""
        for mid in MethodId:
            self.assertTrue(isinstance(mid.label_zh, str))
            self.assertNotEqual(mid.label_zh, "")

    def test_rule_type_values(self):
        """五种规则类型全部定义。"""
        types = [t.value for t in RuleType]
        expected = {"pattern", "sihua", "palace", "interaction", "cycle"}
        self.assertEqual(set(types), expected)

    def test_confidence_level_values(self):
        """四种置信度全部定义。"""
        levels = [l.value for l in ConfidenceLevel]
        expected = {"high", "medium", "low", "unknown"}
        self.assertEqual(set(levels), expected)


class TestDataStructures(unittest.TestCase):
    """数据结构测试。"""

    def test_evidence_ref_creation(self):
        """EvidenceRef 可正确创建。"""
        ref = EvidenceRef(
            rule_id="ZW-TEST-001",
            source_work="紫微斗数全书",
            source_chapter="紫微星",
            verification_status="canonical",
        )
        self.assertEqual(ref.rule_id, "ZW-TEST-001")
        self.assertEqual(ref.verification_status, "canonical")

    def test_rule_spec_creation(self):
        """RuleSpec 可正确创建。"""
        spec = RuleSpec(
            rule_id="SANHE-PATTERN-001",
            method_id=MethodId.SANHE,
            rule_type=RuleType.PATTERN,
            condition={"star_combo": ["武曲", "贪狼"]},
            operation={"action": "recognize"},
            confidence=ConfidenceLevel.MEDIUM,
        )
        self.assertEqual(spec.method_id, MethodId.SANHE)
        self.assertTrue(spec.matches({"star_combo": ["武曲", "贪狼"]}))
        self.assertFalse(spec.matches({"star_combo": ["紫微", "天府"]}))


class TestSiHuaTables(unittest.TestCase):
    """四化表差异测试。"""

    def test_classic_wu_stem_ke(self):
        """三合派戊干科星=右弼。"""
        _, _, ke, _ = SIHUA_TABLE_CLASSIC["戊"]
        self.assertEqual(ke, "右弼")

    def test_zhongzhou_wu_stem_ke(self):
        """中州派戊干科星=太阳。"""
        _, _, ke, _ = SIHUA_TABLE_ZHONGZHOU["戊"]
        self.assertEqual(ke, "太阳")

    def test_tables_differ_on_wu(self):
        """两个四化表在戊干上有差异。"""
        self.assertNotEqual(SIHUA_TABLE_CLASSIC["戊"], SIHUA_TABLE_ZHONGZHOU["戊"])

    def test_tables_identical_elsewhere(self):
        """除戊干外，两个四化表完全一致。"""
        for stem in SIHUA_TABLE_CLASSIC:
            if stem == "戊":
                continue
            self.assertEqual(
                SIHUA_TABLE_CLASSIC[stem],
                SIHUA_TABLE_ZHONGZHOU[stem],
                f"{stem} 四化应相同"
            )


class TestProfileFeatures(unittest.TestCase):
    """各流派特征对比测试。"""

    def _profiles(self):
        return {
            MethodId.SANHE: SanheProfile(),
            MethodId.ZHONGZHOU: ZhongzhouProfile(),
            MethodId.FEIXING: FeixingProfile(),
            MethodId.QINTIAN: QintianProfile(),
        }

    def test_sihua_table_assignment(self):
        """各派别使用正确的四化表。"""
        p = self._profiles()
        self.assertEqual(p[MethodId.SANHE].SIHUA_TABLE, SIHUA_TABLE_CLASSIC)
        self.assertEqual(p[MethodId.ZHONGZHOU].SIHUA_TABLE, SIHUA_TABLE_ZHONGZHOU)
        self.assertEqual(p[MethodId.FEIXING].SIHUA_TABLE, SIHUA_TABLE_CLASSIC)
        self.assertEqual(p[MethodId.QINTIAN].SIHUA_TABLE, SIHUA_TABLE_CLASSIC)

    def test_self_mutagen_feature(self):
        """飞星和钦天门支持自化；三合和中州不支持。"""
        p = self._profiles()
        self.assertFalse(p[MethodId.SANHE].supports_self_mutagen())
        self.assertFalse(p[MethodId.ZHONGZHOU].supports_self_mutagen())
        self.assertTrue(p[MethodId.FEIXING].supports_self_mutagen())
        self.assertTrue(p[MethodId.QINTIAN].supports_self_mutagen())

    def test_liji_feature(self):
        """仅钦天门支持立极宫。"""
        p = self._profiles()
        for mid in (MethodId.SANHE, MethodId.ZHONGZHOU, MethodId.FEIXING):
            self.assertFalse(p[mid].supports_liji())
        self.assertTrue(p[MethodId.QINTIAN].supports_liji())

    def test_xiao_xian_feature(self):
        """三合和中州支持小限；飞星不支持；钦天门部分支持。"""
        p = self._profiles()
        self.assertTrue(p[MethodId.SANHE].supports_xiao_xian())
        self.assertTrue(p[MethodId.ZHONGZHOU].supports_xiao_xian())
        self.assertFalse(p[MethodId.FEIXING].supports_xiao_xian())
        self.assertTrue(p[MethodId.QINTIAN].supports_xiao_xian())

    def test_empty_palace_policy(self):
        """中州派空宫策略最完整。"""
        p = self._profiles()
        self.assertEqual(p[MethodId.ZHONGZHOU].get_empty_palace_policy(), "full")
        for mid in (MethodId.SANHE, MethodId.FEIXING, MethodId.QINTIAN):
            self.assertEqual(p[mid].get_empty_palace_policy(), "partial")

    def test_liu_chang_liu_qu(self):
        """仅中州派支持流昌流曲。"""
        p = self._profiles()
        self.assertTrue(p[MethodId.ZHONGZHOU].supports_liu_chang_liu_qu())
        for mid in (MethodId.SANHE, MethodId.FEIXING, MethodId.QINTIAN):
            self.assertFalse(p[mid].supports_liu_chang_liu_qu())

    def test_w_stem_ke_diff(self):
        """戊干四化科星：三合=右弼，中州=太阳，飞星=右弼。"""
        p = self._profiles()
        _, _, ke_sanhe, _ = p[MethodId.SANHE].get_sihua_for_stem("戊")
        _, _, ke_zz, _ = p[MethodId.ZHONGZHOU].get_sihua_for_stem("戊")
        _, _, ke_fx, _ = p[MethodId.FEIXING].get_sihua_for_stem("戊")
        self.assertEqual(ke_sanhe, "右弼")
        self.assertEqual(ke_zz, "太阳")
        self.assertEqual(ke_fx, "右弼")


class TestRegistry(unittest.TestCase):
    """流派注册表测试。"""

    def test_get_profile(self):
        """get_profile 返回正确类型的实例。"""
        for mid in MethodId:
            profile = get_profile(mid)
            self.assertIsInstance(profile, ZiweiMethodProfile)
            self.assertEqual(profile.METHOD_ID, mid)

    def test_list_available_methods(self):
        """list_available_methods 返回四个流派的描述。"""
        methods = list_available_methods()
        self.assertEqual(len(methods), 4)
        ids = {m["method_id"] for m in methods}
        self.assertEqual(ids, {"sanhe", "zhongzhou", "feixing", "qintian"})

    def test_unknown_method_raises(self):
        """未知 MethodId 抛出 ValueError。"""
        import enum
        fake_id = enum.Enum("FakeMethod", {"FAKE": "fake"})
        with self.assertRaises(ValueError):
            get_profile(fake_id("fake"))


class TestAbstractBase(unittest.TestCase):
    """抽象基类测试。"""

    def test_cannot_instantiate_base(self):
        """ZiweiMethodProfile 不能直接实例化。"""
        with self.assertRaises(TypeError):
            ZiweiMethodProfile()


class TestSihuaDiffers(unittest.TestCase):
    """sihua_differs 函数测试。"""

    def test_sanh_vs_zhongzhou_differs(self):
        """三合派与中州派四化表存在差异。"""
        self.assertTrue(sihua_differs(MethodId.SANHE, MethodId.ZHONGZHOU))

    def test_sanh_vs_feixing_no_diff(self):
        """三合派与飞星派四化表无差异。"""
        self.assertFalse(sihua_differs(MethodId.SANHE, MethodId.FEIXING))

    def test_same_method_no_diff(self):
        """同一派别无差异。"""
        self.assertFalse(sihua_differs(MethodId.SANHE, MethodId.SANHE))


if __name__ == "__main__":
    unittest.main()
