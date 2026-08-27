"""Phase 8-B: Relationship Timeline 测试"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.services.relationship_timeline import (
    RelationshipTimeline,
    RelationshipRecord,
    DailyRelationshipState,
    get_timeline
)


class TestRelationshipTimeline(unittest.TestCase):
    """关系时间线测试。"""
    
    def setUp(self):
        self.timeline = RelationshipTimeline()
        self.base_date = date(2026, 8, 1)
    
    def test_add_and_get_record(self):
        """添加和获取记录。"""
        record = RelationshipRecord(
            record_id="r1",
            relationship_id="rel_001",
            date=self.base_date,
            state_title="稳定期",
            interaction_pattern="相生",
            sync_phase="协同期",
            strength_level="strong",
            summary="关系平稳"
        )
        
        self.timeline.add_record(record)
        history = self.timeline.get_history("rel_001", limit=10)
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["date"], "2026-08-01")
        self.assertEqual(history[0]["state"], "稳定期")
    
    def test_limit_parameter(self):
        """limit参数生效。"""
        for i in range(5):
            record = RelationshipRecord(
                record_id=f"r{i}",
                relationship_id="rel_001",
                date=self.base_date,
                state_title="测试",
                interaction_pattern="中性",
                sync_phase="平稳",
                strength_level="medium",
                summary="测试"
            )
            self.timeline.add_record(record)
        
        history = self.timeline.get_history("rel_001", limit=3)
        self.assertEqual(len(history), 3)
    
    def test_empty_history(self):
        """空历史记录。"""
        history = self.timeline.get_history("nonexistent")
        self.assertEqual(len(history), 0)


class TestDailyRelationshipState(unittest.TestCase):
    """双人每日状态测试。"""
    
    def setUp(self):
        self.timeline = RelationshipTimeline()
    
    def test_both_stable(self):
        """双方稳定状态。"""
        result = self.timeline.compute_daily_state("stable", "stable")
        
        self.assertEqual(result.interaction, "协同期")
        self.assertIn("深入沟通", result.suitable_actions)
        self.assertIn("保持节奏", result.attention_points)
    
    def test_one_expanding(self):
        """一方扩张状态。"""
        result = self.timeline.compute_daily_state("expanding", "stable")
        
        self.assertEqual(result.interaction, "引领期")
        self.assertIn("主动推进", result.suitable_actions)
    
    def test_both_adjusting(self):
        """双方调整状态。"""
        result = self.timeline.compute_daily_state("adjusting", "adjusting")
        
        self.assertEqual(result.interaction, "调整期")
        self.assertIn("各自沉淀", result.suitable_actions)
    
    def test_default_case(self):
        """默认情况。"""
        result = self.timeline.compute_daily_state("unknown", "unknown")
        
        self.assertEqual(result.interaction, "neutral")
        self.assertTrue(len(result.suitable_actions) > 0)
    
    def test_custom_date(self):
        """自定义日期。"""
        custom_date = date(2026, 12, 31)
        result = self.timeline.compute_daily_state("stable", "stable", custom_date)
        
        self.assertEqual(result.date, custom_date)
    
    def test_output_fields(self):
        """输出字段完整性。"""
        result = self.timeline.compute_daily_state("stable", "stable")
        
        self.assertIsInstance(result, DailyRelationshipState)
        self.assertIsInstance(result.suitable_actions, list)
        self.assertIsInstance(result.attention_points, list)


class TestSingleton(unittest.TestCase):
    """单例模式测试。"""
    
    def test_singleton(self):
        """全局单例一致性。"""
        tl1 = get_timeline()
        tl2 = get_timeline()
        self.assertIs(tl1, tl2)


if __name__ == '__main__':
    unittest.main()