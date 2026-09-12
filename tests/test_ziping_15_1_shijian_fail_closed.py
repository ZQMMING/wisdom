"""BZ-FNDR-15.3 (⑮-1 A1+A2): SHIJIAN fail-closed + SHISHEN/SHIJIAN P1-REVIEW 标记.

User 裁决 (2026-09-10):
  A1: SHIJIAN 无 event_signals -> UNKNOWN (不是 EVENT_ABSENT).
  A2: SHISHEN + SHIJIAN 加 STATUS=P1-REVIEW / PRODUCTION_READY=False.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.reasoning.judgment import (
    SHIJIANJudgment, SHISHENJudgment,
    JudgmentConclusion, JudgmentDomain,
)


def _sample_ctx():
    return {"natal": {"pillars": [
        {"position": "YEAR", "heavenly_stem": "GUI", "earthly_branch": "HAI"},
        {"position": "MONTH", "heavenly_stem": "REN", "earthly_branch": "XU"},
        {"position": "DAY", "heavenly_stem": "YI", "earthly_branch": "WEI"},
        {"position": "HOUR", "heavenly_stem": "REN", "earthly_branch": "WU"},
    ], "day_master": "YI"}}


class TestSHIJIANFailClosed(unittest.TestCase):
    """A1: SHIJIAN 无 event_signals 必须 UNKNOWN (fail-closed).

    原 EVENT_ABSENT 是 fail-open: "无输入证据" 却输出积极结论 ("无事件") 是伪判定.
    """

    def test_no_signals_returns_unknown(self):
        """无 signals → UNKNOWN (不是 EVENT_ABSENT)."""
        s = SHIJIANJudgment.judge([], _sample_ctx())
        self.assertEqual(
            s.conclusion, JudgmentConclusion.UNKNOWN,
            f"⑮-1 A1: 无 event_signals 应 UNKNOWN, 实际 = {s.conclusion.name}",
        )

    def test_no_event_signals_returns_unknown(self):
        """有 signals 但无 event_types → UNKNOWN."""
        s = SHIJIANJudgment.judge(
            [{"id": "x", "ontology_type": "TEN_GOD", "value": "正官"}],
            _sample_ctx(),
        )
        self.assertEqual(
            s.conclusion, JudgmentConclusion.UNKNOWN,
            f"⑮-1 A1: 有 signals 但无 event_signals 应 UNKNOWN, 实际 = {s.conclusion.name}",
        )

    def test_with_event_signals_returns_event_exist(self):
        """有 event_signals → EVENT_EXIST (积极结论合法)."""
        s = SHIJIANJudgment.judge(
            [{"id": "e1", "event_types": ["career_change"]}],
            _sample_ctx(),
        )
        self.assertEqual(
            s.conclusion, JudgmentConclusion.EVENT_EXIST,
            f"⑮-1 A1: 有 event_signals 应 EVENT_EXIST, 实际 = {s.conclusion.name}",
        )


class TestDeprecationMarkers(unittest.TestCase):
    """A2: SHISHEN + SHIJIAN 必须有 STATUS='P1-REVIEW' / PRODUCTION_READY=False.

    User 裁决: "当前生产路径未具备完整输入, 因此禁止把该域的默认结果当成生产判断.
                但 SHISHEN 本身不是废弃方法, 是子平体系的基础组成部分."
    """

    def test_shishen_is_p1_review(self):
        self.assertEqual(
            getattr(SHISHENJudgment, "STATUS", None), "P1-REVIEW",
            "SHISHEN.STATUS 必须 = 'P1-REVIEW' (⑮-1 A2)",
        )
        self.assertEqual(
            getattr(SHISHENJudgment, "PRODUCTION_READY", None), False,
            "SHISHEN.PRODUCTION_READY 必须 = False (⑮-1 A2)",
        )

    def test_shijian_is_p1_review(self):
        self.assertEqual(
            getattr(SHIJIANJudgment, "STATUS", None), "P1-REVIEW",
            "SHIJIAN.STATUS 必须 = 'P1-REVIEW' (⑮-1 A2)",
        )
        self.assertEqual(
            getattr(SHIJIANJudgment, "PRODUCTION_READY", None), False,
            "SHIJIAN.PRODUCTION_READY 必须 = False (⑮-1 A2)",
        )

    def test_core_domains_have_no_p1_review_marker(self):
        """核心三域 (WANGSHUAI / GEJU / YONGSHEN) 不应有 P1-REVIEW 标记
        — 它们是生产就绪的, 不应被错误地标 P1-REVIEW.
        """
        from tongshu.reasoning.judgment import (
            WANGSHUAIJudgment, GEJUJudgment, YONGSHENJudgment,
        )
        for cls in (WANGSHUAIJudgment, GEJUJudgment, YONGSHENJudgment):
            # 核心域不应有 STATUS='P1-REVIEW' (否则是误标)
            self.assertNotEqual(
                getattr(cls, "STATUS", None), "P1-REVIEW",
                f"{cls.__name__} 不应被标 P1-REVIEW (是生产就绪域)",
            )


if __name__ == "__main__":
    unittest.main()
