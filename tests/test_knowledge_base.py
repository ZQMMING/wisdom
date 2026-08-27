"""Knowledge Base(KbLoader)测试 — P1-01 D1/D2b。

覆盖:
  1. 加载 data/knowledge/*.json 经 docs/knowledge.schema.json 校验(格式错误硬错)。
  2. 实体计数与按 id 访问。
  3. verify_link_closure() 闭合 §8.2 链(含 55 条规则的 KB 链接,零违规)。
  4. schema 校验失败 = KnowledgeLoadError(绝不静默)。
"""

from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from tongshu.reasoning.knowledge_base import KbLoader, KnowledgeLoadError
from tongshu.reasoning.rule_loader import RuleLoader

REPO = Path(__file__).resolve().parents[2]


def _loader() -> KbLoader:
    return KbLoader(REPO / "backend" / "data", REPO / "docs")


class TestKbLoadAndAccess(unittest.TestCase):
    def test_counts(self):
        kb = _loader()
        # H1-A(2026-08-21,HL_H1_KICKOFF_AND_RULINGS.md):+河洛理数 → book/edition 7,chapter +6,passage +6
        self.assertEqual(kb.counts(), {
            "book": 9,
            "edition": 9,
            "source_copy": 0,
            "chapter": 335,
            "passage": 38,
            "concept": 29,
            "principle": 18,
        })

    def test_index_access(self):
        kb = _loader()
        # get / ids / __getitem__
        self.assertEqual(kb.get("book", "ZIPING-ZHENQUAN")["title"], "子平真诠")
        self.assertIsNone(kb.get("passage", "NOPE"))
        self.assertIn("ZIPING-ZHENQUAN", kb.ids("book"))
        self.assertIn("P-ZPZ-YONGSHEN", kb.ids("passage"))
        self.assertEqual(len(kb["principle"]), 18)
        self.assertIn("GOV-001", {p["principle_id"] for p in kb.principles})

    def test_passage_entities(self):
        kb = _loader()
        by_id = {p["passage_id"]: p for p in kb.passages}
        self.assertEqual(by_id["P-SMTH-TIANYI"]["verification_status"], "pending_verification")
        self.assertEqual(by_id["P-YHZP-DAYUN"]["verification_status"], "cross_verified")
        self.assertEqual(by_id["P-YHZP-WUSHUDUN"]["book_id"], "YUANHAI-ZIPING")


class TestKbLinkClosure(unittest.TestCase):
    def test_closure_zero_violations_with_rules(self):
        kb = _loader()
        rl = RuleLoader(REPO / "backend" / "data", REPO / "docs")
        violations = kb.verify_link_closure(rl.rules)
        self.assertEqual(violations, [], f"link closure broken: {violations}")

    def test_closure_detects_dangling_rule_link(self):
        kb = _loader()
        violations = kb.verify_link_closure(
            [{"rule_id": "T-001", "book_id": "NO-SUCH-BOOK"}]
        )
        self.assertTrue(any("NO-SUCH-BOOK" in v for v in violations))


class TestKbSchemaEnforcement(unittest.TestCase):
    def test_malformed_kb_raises(self):
        # 坏文件 → KnowledgeLoadError(加载即校验,不静默)。
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "knowledge").mkdir()
            (d / "knowledge" / "books.json").write_text(
                json.dumps({"kind": "book", "items": [{"book_id": "X"}]}),
                encoding="utf-8",
            )
            (d / "knowledge.schema.json").write_text(
                (REPO / "docs" / "knowledge.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            with self.assertRaises(KnowledgeLoadError):
                KbLoader(d, d)

    def test_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "knowledge").mkdir()
            (d / "knowledge.schema.json").write_text(
                (REPO / "docs" / "knowledge.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            with self.assertRaises(KnowledgeLoadError):
                KbLoader(d, d)


if __name__ == "__main__":
    unittest.main()
