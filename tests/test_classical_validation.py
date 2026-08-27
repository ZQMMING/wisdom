# -*- coding: utf-8 -*-
"""古籍引用交叉验证测试 — classical_validation."""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.assertion.contract import Assertion, AssertionType, Direction
from tongshu.assertion.classical_validation import (
    validate_assertion_refs, cross_validate_systems, _cited_classics,
)


def _mk_assertion(subject, refs=()):
    return Assertion(
        subject=subject,
        assertion_type=AssertionType.STRUCTURAL,
        direction=Direction.POSITIVE,
        classical_refs=tuple(refs),
    )


class TestCitedClassics(unittest.TestCase):
    """古籍名识别测试."""

    def test_滴天髓_带篇名(self):
        """《滴天髓·篇》能识别为《滴天髓》."""
        refs = ("《滴天髓·通神论·衰旺》: 能知衰旺",)
        cited = _cited_classics(refs)
        self.assertIn("《滴天髓》", cited)

    def test_渊海子平(self):
        refs = ("《渊海子平·论偏财》: 偏财为我克之神",)
        cited = _cited_classics(refs)
        self.assertIn("《渊海子平》", cited)

    def test_周易_卦辞(self):
        refs = ("《周易》卦辞",)
        cited = _cited_classics(refs)
        self.assertIn("《周易》", cited)

    def test_紫微天纪(self):
        refs = ("倪海厦《天纪》: 看一个宫一定看三方四正与对面",)
        cited = _cited_classics(refs)
        self.assertIn("倪海厦《天纪》", cited)

    def test_河洛理数(self):
        refs = ("《河洛理数》: 先天卦为本命",)
        cited = _cited_classics(refs)
        self.assertIn("《河洛理数》", cited)


class TestValidateAssertionRefs(unittest.TestCase):
    """单断言古籍引用验证测试."""

    def test_has_valid_refs(self):
        a = _mk_assertion("ziwei", ("倪海厦《天纪》: 三方四正",))
        r = validate_assertion_refs(a)
        self.assertTrue(r.has_refs)
        self.assertTrue(r.all_valid)
        self.assertEqual(r.validity_score, 1.0)

    def test_no_refs(self):
        a = _mk_assertion("ziwei", ())
        r = validate_assertion_refs(a)
        self.assertFalse(r.has_refs)
        self.assertEqual(r.validity_score, 0.0)


class TestCrossValidateSystems(unittest.TestCase):
    """多体系古籍交叉验证测试."""

    def test_all_referenced(self):
        assertions = [
            _mk_assertion("ziwei", ("倪海厦《天纪》",)),
            _mk_assertion("blind", ("盲派口诀",)),
            _mk_assertion("heluo", ("《河洛理数》",)),
            _mk_assertion("ziping", ("《滴天髓》",)),
        ]
        r = cross_validate_systems(assertions)
        self.assertEqual(r["ref_coverage"], 1.0)
        self.assertEqual(r["systems_with_refs"], 4)
        self.assertEqual(r["unreferenced_systems"], [])
        self.assertIn("交叉验证充分", r["verdict"])

    def test_partial_referenced(self):
        assertions = [
            _mk_assertion("ziwei", ("倪海厦《天纪》",)),
            _mk_assertion("blind", ()),
        ]
        r = cross_validate_systems(assertions)
        self.assertEqual(r["ref_coverage"], 0.5)
        self.assertEqual(r["unreferenced_systems"], ["blind"])
        self.assertIn("部分体系", r["verdict"])

    def test_no_systems(self):
        r = cross_validate_systems([])
        self.assertEqual(r["systems_total"], 0)
        self.assertEqual(r["verdict"], "no systems")


if __name__ == "__main__":
    unittest.main()
