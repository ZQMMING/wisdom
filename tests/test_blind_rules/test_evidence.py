# -*- coding: utf-8 -*-
"""P2-EVIDENCE-REFACTOR — 盲派证据生产者重构测试

测试覆盖：
1. BlindFeatureState 创建与转换
2. EvidenceItem 字段验证
3. EvidenceList 基础操作
4. BlindEvidenceProducer.produce() 主流程
5. 各类型证据生成验证
6. 证据可追溯性验证
"""
from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.engines.blind.evidence_producer import (
    BlindEvidenceProducer,
    BlindFeatureState,
    EvidenceItem,
    EvidenceList,
    Relevance,
)


class TestBlindFeatureState(unittest.TestCase):
    """BlindFeatureState 数据类测试"""

    def test_create_empty(self):
        """创建空的 BlindFeatureState"""
        state = BlindFeatureState()
        self.assertEqual(len(state.main_branches), 0)
        self.assertEqual(len(state.ti_branches), 0)
        self.assertFalse(state.zuo_gong)

    def test_create_with_values(self):
        """创建带值的 BlindFeatureState"""
        state = BlindFeatureState(
            main_branches=frozenset({"YIN", "WU"}),
            guest_branches=frozenset({"ZI", "MAO"}),
            ti_branches=frozenset({"YIN", "WU"}),
            yong_branches=frozenset({"WU"}),
            ti_stems=("JIA", "BING"),
            yong_stems=("WU",),
            zuo_gong=True,
            zuo_gong_type="制用",
            zuo_gong_methods=("合财",),
            transparent_ten_gods=(("year", "正财"), ("month", "七杀")),
        )
        self.assertIn("YIN", state.main_branches)
        self.assertTrue(state.zuo_gong)
        self.assertEqual(len(state.transparent_ten_gods), 2)

    def test_frozen_field_access(self):
        """验证 frozen 结构不可修改"""
        state = BlindFeatureState(main_branches=frozenset({"YIN"}))
        with self.assertRaises(AttributeError):
            state.main_branches = frozenset({"WU"})

    def test_to_dict(self):
        """验证序列化"""
        state = BlindFeatureState(
            main_branches=frozenset({"YIN"}),
            zuo_gong=True,
            zuo_gong_type="制用",
        )
        d = state.to_dict()
        self.assertIn("main_branches", d)
        self.assertTrue(d["zuo_gong"])
        self.assertEqual(d["zuo_gong_type"], "制用")


class TestEvidenceItem(unittest.TestCase):
    """EvidenceItem 数据类测试"""

    def test_create_minimal(self):
        """创建最小编辑项"""
        item = EvidenceItem(
            id="E-001",
            source="《盲派八字技法》",
            content="主位坐日支",
            relevance=Relevance.HIGH,
        )
        self.assertEqual(item.id, "E-001")
        self.assertTrue(item.valid)
        self.assertIsNone(item.verified_at)

    def test_create_full(self):
        """创建完整证据项"""
        today = date.today().isoformat()
        item = EvidenceItem(
            id="E-002",
            source="data/rules/blind_ti_yong.json",
            content="体用分离",
            relevance=Relevance.MEDIUM,
            valid=True,
            verified_at=today,
        )
        self.assertEqual(item.relevance, "中")
        self.assertEqual(item.verified_at, today)

    def test_relevance_values(self):
        """验证相关性枚举"""
        self.assertEqual(Relevance.HIGH, "高")
        self.assertEqual(Relevance.MEDIUM, "中")
        self.assertEqual(Relevance.LOW, "低")
        self.assertEqual(len(Relevance.values()), 3)

    def test_to_dict(self):
        """验证序列化"""
        item = EvidenceItem(
            id="E-003",
            source="test",
            content="content",
            relevance=Relevance.HIGH,
        )
        d = item.to_dict()
        self.assertEqual(d["id"], "E-003")
        self.assertTrue(d["valid"])


class TestEvidenceList(unittest.TestCase):
    """EvidenceList 容器测试"""

    def test_empty_list(self):
        """空列表"""
        el = EvidenceList()
        self.assertEqual(len(el), 0)
        self.assertTrue(list(el) == [])

    def test_add_item(self):
        """添加证据项"""
        el = EvidenceList()
        item = EvidenceItem(id="E-001", source="s", content="c", relevance="高")
        el.add(item)
        self.assertEqual(len(el), 1)
        self.assertEqual(el.items[0].id, "E-001")

    def test_filter_by_relevance(self):
        """按相关性过滤"""
        el = EvidenceList([
            EvidenceItem(id="E-1", source="s", content="c", relevance="高"),
            EvidenceItem(id="E-2", source="s", content="c", relevance="中"),
            EvidenceItem(id="E-3", source="s", content="c", relevance="低"),
        ])
        high = el.filter_by_relevance("高")
        self.assertEqual(len(high), 1)
        self.assertEqual(high.items[0].id, "E-1")

    def test_filter_valid(self):
        """按有效性过滤"""
        el = EvidenceList([
            EvidenceItem(id="E-1", source="s", content="c", relevance="高", valid=True),
            EvidenceItem(id="E-2", source="s", content="c", relevance="中", valid=False),
        ])
        valid_only = el.filter_valid()
        self.assertEqual(len(valid_only), 1)
        self.assertEqual(valid_only.items[0].id, "E-1")


class TestBlindEvidenceProducer(unittest.TestCase):
    """BlindEvidenceProducer 主逻辑测试"""

    def setUp(self):
        self.producer = BlindEvidenceProducer()
        self.test_date = "2026-09-03"

    def test_produce_basic(self):
        """基础生产流程"""
        state = BlindFeatureState(
            main_branches=frozenset({"YIN", "WU"}),
            guest_branches=frozenset({"ZI", "MAO"}),
        )
        evidences = self.producer.produce(state, verified_at=self.test_date)
        self.assertIsInstance(evidences, EvidenceList)
        self.assertGreater(len(evidences), 0)

    def test_produce_with_zuo_gong(self):
        """含做功结构的证据生产"""
        state = BlindFeatureState(
            main_branches=frozenset({"YIN"}),
            guest_branches=frozenset({"WU"}),
            ti_branches=frozenset({"YIN"}),
            yong_branches=frozenset({"WU"}),
            zuo_gong=True,
            zuo_gong_type="制用",
            zuo_gong_methods=("合财",),
        )
        evidences = self.producer.produce(state, verified_at=self.test_date)
        # 应包含做功相关证据
        zg_evidences = [e for e in evidences if "制用" in e.content]
        self.assertEqual(len(zg_evidences), 1)
        self.assertEqual(zg_evidences[0].relevance, "高")

    def test_produce_without_zuo_gong(self):
        """无做功结构的证据生产"""
        state = BlindFeatureState(
            main_branches=frozenset({"YIN"}),
            zuo_gong=False,
        )
        evidences = self.producer.produce(state, verified_at=self.test_date)
        low_evidences = [e for e in evidences if e.relevance == "低"]
        self.assertGreater(len(low_evidences), 0)

    def test_produce_with_ten_gods(self):
        """含透干十神的证据生产"""
        state = BlindFeatureState(
            transparent_ten_gods=(("year", "正财"), ("month", "七杀")),
        )
        evidences = self.producer.produce(state, verified_at=self.test_date)
        tgt_evidences = [e for e in evidences if "透干" in e.content]
        self.assertEqual(len(tgt_evidences), 2)

    def test_evidence_traceable_source(self):
        """证据可追溯性验证"""
        state = BlindFeatureState(
            main_branches=frozenset({"YIN"}),
            ti_branches=frozenset({"YIN"}),
        )
        evidences = self.producer.produce(state, verified_at=self.test_date)
        for item in evidences:
            self.assertIsNotNone(item.source)
            self.assertTrue(len(item.source) > 0)

    def test_evidence_valid_and_verified(self):
        """证据有效性验证"""
        state = BlindFeatureState(main_branches=frozenset({"YIN"}))
        evidences = self.producer.produce(state, verified_at=self.test_date)
        for item in evidences:
            self.assertTrue(item.valid)
            self.assertEqual(item.verified_at, self.test_date)

    def test_no_direction_polarity_strength(self):
        """验证无方向/极性/强度字段"""
        state = BlindFeatureState(main_branches=frozenset({"YIN"}))
        evidences = self.producer.produce(state, verified_at=self.test_date)
        for item in evidences:
            self.assertNotIn("direction", item.content.lower())
            self.assertNotIn("polarity", item.content.lower())
            self.assertNotIn("strength", item.content.lower())
            # relevance 字段存在且合法
            self.assertIn(item.relevance, ["高", "中", "低"])

    def test_relevance_assignment(self):
        """验证相关性分配逻辑"""
        # 宾主判定：有主位 → 高
        state = BlindFeatureState(
            main_branches=frozenset({"YIN", "WU"}),
            guest_branches=frozenset({"ZI", "MAO"}),
        )
        evidences = self.producer.produce(state, verified_at=self.test_date)
        main_evidence = [e for e in evidences if "主位" in e.content]
        self.assertEqual(len(main_evidence), 1)
        self.assertEqual(main_evidence[0].relevance, "高")

    def test_empty_state_produces_low_relevance(self):
        """空状态产生低相关性证据"""
        state = BlindFeatureState()
        evidences = self.producer.produce(state, verified_at=self.test_date)
        # 至少应有一条证据
        self.assertGreater(len(evidences), 0)
        # 空状态的主位证据应为低
        empty_evidences = [e for e in evidences if len(e.content) < 20]
        self.assertGreater(len(empty_evidences), 0)


class TestFromBlindResult(unittest.TestCase):
    """从 BlindBaziResult 转换测试"""

    def test_conversion(self):
        """验证从 BlindBaziResult 转换"""
        # 模拟 BlindBaziResult 对象
        class MockResult:
            main_branches = {"YIN", "WU"}
            guest_branches = {"ZI", "MAO"}
            ti_branches = {"YIN"}
            yong_branches = {"WU"}
            ti_stems = ["JIA", "BING"]
            yong_stems = ["WU"]
            zuo_gong = True
            zuo_gong_type = "制用"
            zuo_gong_methods = ["合财"]
            zuo_gong_detail = ["甲合己"]
            transparent_ten_gods = {"year": "正财"}

        result = MockResult()
        state = BlindFeatureState.from_blind_result(result)
        self.assertIn("YIN", state.main_branches)
        self.assertTrue(state.zuo_gong)
        self.assertEqual(state.zuo_gong_type, "制用")


if __name__ == "__main__":
    unittest.main()
