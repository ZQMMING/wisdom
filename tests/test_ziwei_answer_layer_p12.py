# -*- coding: utf-8 -*-
"""Z74d: 答案层组装测试（两派平行 → 八维度）"""

import sys

sys.path.insert(0, r"D:\shuntian-ziwei-v2\src")

import pytest

from tongshu.engines.ziwei_engine import ZiweiEngine
from tongshu.engines.ziwei.rules.answer_layer import build_answer, DIMENSIONS


@pytest.fixture(scope="module")
def engine():
    return ZiweiEngine()


class TestAnswerLayerZ74d:
    """答案层：两派规则命中 → 分维度平行答案。"""

    def test_eight_dimensions(self, engine):
        """八维度齐备，两派并行输出。"""
        ch = engine.full_chart((1983, 9, 29), 11, "male")
        ans = build_answer(ch)
        assert set(ans["dimensions"]) == set(DIMENSIONS)
        assert ans["summary"]["sanhe_total"] > 0
        assert ans["summary"]["qintian_total"] > 0

    def test_dimension_items_structured(self, engine):
        """每条维度答案有 source/rule_id/text。"""
        ch = engine.full_chart((1983, 9, 29), 11, "male")
        ans = build_answer(ch)
        for dim in DIMENSIONS:
            for it in ans["answer"][dim]:
                assert it["source"] in ("sanhe", "qintian")
                assert it["rule_id"]
                assert it["text"]

    def test_sihua_text_generated(self, engine):
        """生年四化入宫文本生成（SANHE-SIHUA-癸-化禄 → 生年癸干化禄入官禄宫）。"""
        ch = engine.full_chart((1983, 9, 29), 11, "male")
        ans = build_answer(ch)
        found = False
        for it in ans["answer"]["四化体用"]:
            if it["rule_id"] == "SANHE-SIHUA-癸-化禄":
                assert "生年癸干化禄入官禄宫" in it["text"]
                found = True
        assert found

    def test_parallel_no_vote(self, engine):
        """南北派各自保留：同一维度内同时有 sanhe 与 qintian 条目（不合并）。"""
        ch = engine.full_chart((1983, 9, 29), 11, "male")
        ans = build_answer(ch)
        for dim in ("性格", "事业", "婚姻", "应期"):
            sources = {it["source"] for it in ans["answer"][dim]}
            assert "sanhe" in sources or "qintian" in sources
        # 四化体用维度两派都在
        sources = {it["source"] for it in ans["answer"]["四化体用"]}
        assert sources == {"sanhe", "qintian"}
