"""KB Reader(C4)只读模块测试。

依赖本地 PostgreSQL `shuntian_kb`(建库交接基线 known-good-db-baseline-20260820)。
shuntian_kb 不可达时整模块跳过 —— 不破坏无 DB 基线。
只读纪律:本测试额外含一个**源码静态守卫** —— kb_reader.py 一旦出现
UPDATE/INSERT/DELETE/DROP/ALTER 立即失败,防止"只读模块"日后被偷塞写方法。

运行(backend/):
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python -m unittest tests.test_kb_reader -v
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

import psycopg2

from tongshu.db import kb_reader

REPO = Path(__file__).resolve().parents[2]
KB_READER_PATH = REPO / "backend" / "src" / "tongshu" / "db" / "kb_reader.py"

# 已知锚点(shuntian_kb 建库基线实测存在)
KNOWN_RULE_ID = "ZPZ-101"
KNOWN_EVIDENCE_ID = "E-ZPZ-101-001"
KNOWN_PASSAGE_IDS = ["PZZQ_031_P001", "P-ZPZ-YONGSHEN"]
EXPECTED_ACTIVE_GOLDEN = 20  # GOLDEN-001..020(契约 §2.4 可执行基线)
EXPECTED_ALL_GOLDEN = 35     # 20 active + 14 DRAFT(GOLD_EXP_/GOLD_MAP_) + 1 HL-G-R-0001(河洛研究级,HL_H1_KICKOFF_AND_RULINGS.md ⑥,active_only 过滤)


def _kb_available() -> tuple[bool, str]:
    try:
        conn = psycopg2.connect(kb_reader.kb_dsn(), connect_timeout=3)
        conn.close()
        return True, ""
    except Exception as exc:  # noqa: BLE001 — 探测要吞掉任意连接异常
        return False, str(exc)[:200]


@unittest.skipUnless(*_kb_available())
class KbReaderQueryTest(unittest.TestCase):
    """四查询函数 + 空输入 + active_only 过滤。"""

    def test_query_rules_by_id(self) -> None:
        rows = kb_reader.query_rules([KNOWN_RULE_ID])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["rule_id"], KNOWN_RULE_ID)
        # 关键字段都在(source_refs 承载证据引用,见 rules 表 DDL)
        for field in ("rule_id", "rule_text", "rule_status", "domain", "source_refs"):
            self.assertIn(field, rows[0])

    def test_query_rules_empty(self) -> None:
        self.assertEqual(kb_reader.query_rules([]), [])
        self.assertEqual(kb_reader.query_rules(["NO-SUCH-RULE-999"]), [])

    def test_query_evidence_by_id(self) -> None:
        rows = kb_reader.query_evidence([KNOWN_EVIDENCE_ID])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["evidence_id"], KNOWN_EVIDENCE_ID)
        self.assertIn("verification_status", rows[0])

    def test_query_passages_by_ids(self) -> None:
        rows = kb_reader.query_passages(KNOWN_PASSAGE_IDS)
        got = {r["passage_id"] for r in rows}
        self.assertEqual(got, set(KNOWN_PASSAGE_IDS))
        self.assertTrue(all("original_text" in r for r in rows))

    def test_query_golden_active_only(self) -> None:
        rows = kb_reader.query_golden_cases(active_only=True)
        self.assertEqual(len(rows), EXPECTED_ACTIVE_GOLDEN)
        self.assertEqual(rows[0]["case_id"], "GOLDEN-001")
        self.assertEqual(rows[-1]["case_id"], "GOLDEN-020")
        self.assertTrue(all(r["verification_status"] == "active" for r in rows))

    def test_query_golden_all(self) -> None:
        rows = kb_reader.query_golden_cases(active_only=False)
        self.assertEqual(len(rows), EXPECTED_ALL_GOLDEN)

    def test_with_kb_conn_roundtrip(self) -> None:
        with kb_reader.with_kb_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT current_database()")
            self.assertEqual(cur.fetchone()[0], "shuntian_kb")


@unittest.skipUnless(*_kb_available())
class KbReaderReadOnlyGuardTest(unittest.TestCase):
    """源码静态守卫:kb_reader.py 的可执行代码不得含写 SQL,只读红线结构性固化。

    用 AST 遍历代码字符串字面量(跳过模块 docstring —— 它文本里就写着
    "没有任何 UPDATE / INSERT / DELETE",那是纪律声明,不是代码)。凡后续有人
    往代码里塞真实写语句,必然以字符串字面量出现,守卫即失败。
    """

    WRITE_SQL_KEYWORDS = ("UPDATE ", "INSERT INTO", "DELETE FROM", "DROP ", "ALTER ")

    @staticmethod
    def _module_docstring_node(tree: ast.Module) -> ast.Constant | None:
        first = tree.body[0] if tree.body else None
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            return first.value
        return None

    def test_module_code_has_no_write_sql(self) -> None:
        tree = ast.parse(KB_READER_PATH.read_text(encoding="utf-8"))
        doc_node = self._module_docstring_node(tree)
        hits = []
        for node in ast.walk(tree):
            if node is doc_node:
                continue
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for kw in self.WRITE_SQL_KEYWORDS:
                    if kw in node.value:
                        hits.append((kw, node.value[:60]))
        self.assertEqual(hits, [], f"kb_reader.py 代码内含写 SQL: {hits}")

    def test_module_uses_cursor_and_execute_for_reads(self) -> None:
        src = KB_READER_PATH.read_text(encoding="utf-8")
        # 读路径确实存在(execute/cursor),确保守卫不是空转
        self.assertIn("cur.execute", src)
        self.assertIn("RealDictCursor", src)


if __name__ == "__main__":
    unittest.main()
