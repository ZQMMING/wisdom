"""P0-02 修复测试：classical_text.py 知识库加载。

验证：
- CLASSICAL_TEXTS 不再是空字典，至少覆盖 64 卦卦辞 + 大象辞。
- get_classical_text() 返回真实原文（非空字符串）。
- load_from_kb() 从 KbLoader.passages 筛选易经原文并覆盖内嵌数据。
- 未知卦名返回空 ClassicalText 而非抛异常（向后兼容）。
- 约束：不修改 KbLoader，只读取 passages 数据。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import unittest

from tongshu.engines.yi import classical_text
from tongshu.engines.yi.classical_text import (
    get_all_hexagram_names,
    get_classical_text,
    get_coverage_stats,
    load_classical_database,
    load_from_kb,
)


class _FakeKbLoader:
    """最小 KbLoader 替身（只暴露 passages 属性，用于测试筛选逻辑）。

    不修改真实 KbLoader —— 真实 KbLoader 当前知识库无易经 64 卦数据，
    因此内嵌数据兜底保证至少覆盖 64 卦卦辞 + 大象辞。
    """

    def __init__(self, passages):
        self.passages = passages


class TestClassicalTextEmbeddedCoverage(unittest.TestCase):
    def setUp(self):
        classical_text._KB_TEXTS.clear()

    def test_64_hexagrams_covered(self):
        names = get_all_hexagram_names()
        self.assertEqual(len(names), 64)
        # 抽查几个关键卦名
        for name in ("乾为天", "坤为地", "地天泰", "天地否", "水火既济", "火水未济"):
            self.assertIn(name, names)

    def test_gua_ci_and_da_xiang_ci_full_coverage(self):
        stats = get_coverage_stats()
        self.assertEqual(stats["total_hexagrams"], 64)
        self.assertEqual(stats["gua_ci_coverage"], 64)
        self.assertEqual(stats["da_xiang_ci_coverage"], 64)

    def test_get_classical_text_returns_original_not_empty(self):
        ct = get_classical_text("乾为天")
        self.assertEqual(ct.gua_ci, "元亨利贞。")
        self.assertEqual(ct.da_xiang_ci, "天行健，君子以自强不息。")
        self.assertTrue(ct.gua_ci_source)


class TestClassicalTextKbLoading(unittest.TestCase):
    def setUp(self):
        classical_text._KB_TEXTS.clear()

    def test_load_from_kb_merges_yi_passage(self):
        kb = _FakeKbLoader([
            {"passage_id": "P-YI-001", "book_id": "ZHOUYI",
             "classical_original": {"text": "乾为天卦辞：元亨利贞。"}},
        ])
        merged = load_from_kb(kb)
        self.assertEqual(merged, 1)
        # KbLoader 筛选结果应覆盖内嵌卦辞
        self.assertEqual(get_classical_text("乾为天").gua_ci, "乾为天卦辞：元亨利贞。")

    def test_load_from_kb_ignores_non_yi_passage(self):
        kb = _FakeKbLoader([
            {"passage_id": "P-BAZI-001", "book_id": "DITIANSUI",
             "classical_original": {"text": "滴天髓原文，与易经无关。"}},
        ])
        merged = load_from_kb(kb)
        self.assertEqual(merged, 0)
        # 未命中时仍走内嵌数据
        self.assertEqual(get_classical_text("乾为天").gua_ci, "元亨利贞。")

    def test_load_classical_database_with_kb_loader(self):
        kb = _FakeKbLoader([
            {"passage_id": "P-YI-002", "book_id": "ZHOUYI",
             "classical_original": {"text": "坤为地大象：地势坤，君子以厚德载物。"}},
        ])
        load_classical_database(kb_loader=kb)
        self.assertEqual(
            get_classical_text("坤为地").da_xiang_ci,
            "坤为地大象：地势坤，君子以厚德载物。",
        )

    def test_alias_resolution(self):
        # 简称 "泰" 应解析到 "地天泰"
        ct = get_classical_text("泰")
        self.assertEqual(ct.hexagram_name, "地天泰")
        self.assertEqual(ct.gua_ci, "小往大来，吉亨。")

    def test_unknown_hexagram_returns_empty_not_raise(self):
        ct = get_classical_text("不存在的卦")
        self.assertEqual(ct.gua_ci, "")
        self.assertEqual(ct.da_xiang_ci, "")


if __name__ == "__main__":
    unittest.main()
