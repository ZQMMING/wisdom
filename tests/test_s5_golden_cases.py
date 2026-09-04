"""S5-03 Golden Dataset 测试 (JSON-based, no DB required)"""
from __future__ import annotations
import unittest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

GOLDEN_PATH = Path(__file__).parent.parent / "dataset" / "golden_v1" / "golden_cases.json"


class TestGoldenDataset(unittest.TestCase):
    """测试 Golden Dataset 完整性（无DB依赖）。"""

    @classmethod
    def setUpClass(cls):
        cls.data = json.load(open(GOLDEN_PATH, encoding="utf-8"))
        cls.cases = cls.data.get("cases", [])

    def test_cases_count(self):
        """至少有40个案例。"""
        count = len(self.cases)
        self.assertGreaterEqual(count, 40, f"Expected >= 40 cases, got {count}")

    def test_cases_have_required_fields(self):
        """案例都有必需字段。"""
        empty = [c for c in self.cases if not c.get("gender") or not c.get("birth_date")]
        self.assertEqual(len(empty), 0, f"Cases missing required fields: {[c.get('case_id') for c in empty]}")

    def test_events_structure(self):
        """所有案例都有events列表。"""
        no_events = [c for c in self.cases if not isinstance(c.get("events"), list) or len(c["events"]) == 0]
        self.assertEqual(len(no_events), 0, f"Cases with no events: {[c.get('case_id') for c in no_events]}")

    def test_source_type_valid(self):
        """source_type有效。"""
        valid_types = {"historical", "modern", "ancient", "synthetic"}
        invalid = [c for c in self.cases if c.get("source_type") not in valid_types]
        self.assertEqual(len(invalid), 0, f"Invalid source_types: {set(c.get('source_type') for c in invalid)}")

    def test_event_dates_valid(self):
        """事件日期格式正确。"""
        import re
        bad_dates = []
        for c in self.cases:
            for e in c.get("events", []):
                if not re.match(r"\d{4}-\d{2}-\d{2}", e.get("date", "")):
                    bad_dates.append(f"{c['case_id']}: {e.get('date')}")
        self.assertEqual(len(bad_dates), 0, f"Invalid date formats: {bad_dates[:5]}")

    def test_evidence_grade_valid(self):
        """证据等级有效。"""
        valid_grades = {"A", "B", "C"}
        invalid = []
        for c in self.cases:
            for e in c.get("events", []):
                if e.get("evidence_grade") not in valid_grades:
                    invalid.append(f"{c['case_id']}: {e.get('evidence_grade')}")
        self.assertEqual(len(invalid), 0, f"Invalid evidence grades: {invalid[:5]}")

    def test_total_events(self):
        """总事件数 >= 500。"""
        total = sum(len(c.get("events", [])) for c in self.cases)
        self.assertGreaterEqual(total, 500, f"Expected >= 500 events, got {total}")

    def test_case_id_format(self):
        """case_id格式正确。"""
        import re
        bad = [c["case_id"] for c in self.cases if not re.match(r"GOLDEN-\d{3}", c["case_id"])]
        self.assertEqual(len(bad), 0, f"Invalid case_id format: {bad[:5]}")

    def test_gender_distribution(self):
        """性别分布合理。"""
        genders = [c.get("gender") for c in self.cases]
        self.assertIn("male", genders)
        self.assertIn("female", genders)

    def test_source_type_distribution(self):
        """source_type分布合理。"""
        from collections import Counter
        types = Counter(c.get("source_type") for c in self.cases)
        # Should have historical cases
        self.assertGreaterEqual(types.get("historical", 0), 10, "Should have >= 10 historical cases")


if __name__ == "__main__":
    unittest.main()
