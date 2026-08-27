"""M1 Edition Registry 测试 — 最小数据完整性(EDITION_REGISTRY_SPEC ED-V-1..6 + R1 原子切换)。
注(2026-08-21):H1-A 依 HL_H1_KICKOFF_AND_RULINGS.md 增河洛理数 → 7 固化版本/20 passage。

覆盖:
  1. editions.json 七条固化版本(含 HELUO-LISHU),过 v2.0 schema($defs.edition);KbLoader 加载无错。
  2. 每 book 至多 1 条 pinned;books.pinned_edition_id 与 pinned 双向一致(ED-V-2/3)。
  3. 20 条 passage 全部 edition_id 解析到同书固化版本(M1 任务 6 确定性映射)。
  4. layer_structure 键 ⊆ 五层且含 classical_original(ED-V-4)。
  5. commentator 非空 ⇔ commentary 层(ED-V-5)。
  6. basis(具体版次)诚实:pending_verification,status=review,零推断成 verified 史实。
  7. edition_id pattern ^EDITION-[A-Z][A-Z0-9-]{3,31}$。
  8. CAL 历法源不入五经 KB 主链;QTB excludes 造化玄钥/元钥(D-03,ED-V-6)。
  9. ZW 安星诀 edition 登记;P-ZW passages 保持 pending_verification paraphrase;ZW-405..408 规则仍 active。
  10. verify_link_closure() 零违规(含 55 条规则的 KB 链接)。
"""

from __future__ import annotations
import unittest
from pathlib import Path

from tongshu.reasoning.knowledge_base import KbLoader
from tongshu.reasoning.rule_loader import RuleLoader

REPO = Path(__file__).resolve().parents[2]

EDITION_IDS = [
    "EDITION-DITIANSUI-RENTIEQIAO",
    "EDITION-ZIPING-ZHENQUAN-XULEWU",
    "EDITION-SANMING-TONGHUI-SHIERJUAN",
    "EDITION-YUANHAI-ZIPING-ZENGBU",
    "EDITION-QIONGTONG-BAOJIAN-YUXUNTAI",
    "EDITION-ZIWEI-DOUSHU-ANXINGJUE",
    # H1-A(2026-08-21,HL_H1_KICKOFF_AND_RULINGS.md ①/③):河洛理数研究底稿版本。
    # 身份=公开书目事实(verification_status=verified);OCR 未对印刷版复核→basis_verification=pending、status=review。
    "EDITION-HELUO-LISHU-NA09030",
    # KB link closure(2026-08-26): +黄帝内经/五行精纪 DEFAULT 通行本(basis pending)
    "EDITION-HUANGDI-NEIJING-DEFAULT",
    "EDITION-WUXINGJINGJI-DEFAULT",
]

ALLOWED_LAYERS = {
    "classical_original", "commentary", "paraphrase",
    "engineering_seed", "secondary_reference",
}


def _loader() -> KbLoader:
    return KbLoader(REPO / "backend" / "data", REPO / "docs")


class TestEditionRegistryData(unittest.TestCase):
    def test_six_pinned_editions(self):
        kb = _loader()
        self.assertEqual([e["edition_id"] for e in kb.editions], EDITION_IDS)
        self.assertTrue(all(e["pinned"] for e in kb.editions))

    def test_edition_id_pattern(self):
        import re
        pat = re.compile(r"^EDITION-[A-Z][A-Z0-9-]{3,31}$")
        for e in _loader().editions:
            self.assertRegex(e["edition_id"], pat, e["edition_id"])
            self.assertIsInstance(e["title"], str)
            self.assertGreater(len(e["title"]), 0)

    def test_pinned_unique_and_book_link(self):
        kb = _loader()
        books = {b["book_id"]: b for b in kb.books}
        by_id = {e["edition_id"]: e for e in kb.editions}
        # ED-V-2: 每 book 至多 1 条 pinned(数据层面直接断言唯一)
        self.assertEqual(len(kb.editions), len({e["book_id"] for e in kb.editions}))
        # ED-V-3: book.pinned_edition_id 指向同书 pinned edition
        for bid, b in books.items():
            peid = b["pinned_edition_id"]
            self.assertIn(peid, by_id, f"book {bid} pinned_edition_id 无对应 edition")
            self.assertEqual(by_id[peid]["book_id"], bid, f"book {bid} 的 pinned edition 属不同书")
            self.assertTrue(by_id[peid]["pinned"], f"book {bid} 的 pinned_edition_id 非 pinned")

    def test_passage_edition_mapping(self):
        kb = _loader()
        books = {b["book_id"]: b for b in kb.books}
        by_id = {e["edition_id"]: e for e in kb.editions}
        self.assertEqual(len(kb.passages), 38)  # 20 五经+河洛 + 18 新域(GW/HH/MK/SX/LM/TF 等 link closure)
        for p in kb.passages:
            self.assertIn("edition_id", p, f"passage {p['passage_id']} 缺 edition_id(M1 任务 6)")
            eid = p["edition_id"]
            self.assertIn(eid, by_id, f"passage {p['passage_id']} edition_id 无对应 edition")
            self.assertEqual(
                by_id[eid]["book_id"], p["book_id"],
                f"passage {p['passage_id']} 的 edition 属不同书",
            )
            self.assertEqual(
                eid, books[p["book_id"]]["pinned_edition_id"],
                f"passage {p['passage_id']} edition_id != 该书固化版本",
            )

    def test_layer_structure_valid(self):
        for e in _loader().editions:
            ls = e["layer_structure"]
            self.assertLessEqual(set(ls), ALLOWED_LAYERS, e["edition_id"])
            self.assertIn("classical_original", ls, e["edition_id"])
            # ED-V-5: commentator 非空 ⇔ commentary 层
            self.assertEqual(
                bool(e.get("commentator")), "commentary" in ls,
                f"edition {e['edition_id']} commentator/commentary 层不一致",
            )

    def test_basis_honest(self):
        # 具体版次一律 pending,禁止模型推断成 verified 史实(SPEC OWNER 特别禁止)
        for e in _loader().editions:
            self.assertEqual(
                e.get("basis_verification"), "pending_verification",
                f"edition {e['edition_id']} 具体版次必须 pending_verification",
            )
            self.assertEqual(e["status"], "review", "basis 待核验 → status=review(§4)")
            self.assertEqual(e["verification_status"], "verified", "版本身份=公开书目+Spec Owner 固化")


class TestEditionBoundaries(unittest.TestCase):
    def test_cal_not_in_main_chain(self):
        kb = _loader()
        # CAL 历法权威源不得进入五经 KB 主链(KB_STATUS §4 R7)
        self.assertFalse(any(e["source_type"] == "calendrical_authority" for e in kb.editions))
        self.assertFalse(any(b["source_type"] == "calendrical_authority" for b in kb.books))
        self.assertFalse(any("CAL" in e["edition_id"] for e in kb.editions))

    def test_qtb_excludes_yuanyao(self):
        # D-03: 造化玄钥/元钥 仅 bibliographic note,不进入正文来源(ED-V-6)
        qtb = [e for e in _loader().editions if e["book_id"] == "QIONGTONG-BAOJIAN"]
        self.assertEqual(len(qtb), 1)
        self.assertIn("造化玄钥", qtb[0]["excludes"])
        self.assertIn("造化元钥", qtb[0]["excludes"])
        for p in _loader().passages:
            text = (p.get("source_reference") or "") + (p.get("edition") or "")
            self.assertNotIn("造化玄钥", text)
            self.assertNotIn("造化元钥", text)

    def test_zw_unchanged(self):
        # U-6: 安星诀证据层标 engineering_seed;ZW passages 保持待校 paraphrase;规则不动
        kb = _loader()
        zw_ed = [e for e in kb.editions if e["book_id"] == "ZIWEI-DOUSHU"]
        self.assertEqual(len(zw_ed), 1)
        self.assertIn("口诀", zw_ed[0]["layer_structure"]["classical_original"])
        for p in kb.passages:
            if p["book_id"] == "ZIWEI-DOUSHU":
                self.assertEqual(p["verification_status"], "pending_verification")
                self.assertTrue(p["paraphrase"]["text"].startswith("(待校,paraphrase)"))
        rl = RuleLoader(REPO / "backend" / "data", REPO / "docs")
        zw_rules = [r for r in rl.rules if r["rule_id"].startswith("ZW-405") or r["rule_id"].startswith("ZW-40")]
        self.assertEqual(len(zw_rules), 4)
        self.assertTrue(all(r["status"] == "active" for r in zw_rules))


class TestEditionClosure(unittest.TestCase):
    def test_closure_zero_violations_with_rules(self):
        kb = _loader()
        rl = RuleLoader(REPO / "backend" / "data", REPO / "docs")
        violations = kb.verify_link_closure(rl.rules)
        self.assertEqual(violations, [], f"link closure broken: {violations}")


class TestSourceCopyStructure(unittest.TestCase):
    """M1 授权 item #4/#8:SOURCE_COPY 可扩展关联结构(结构就位、数据诚实为空)。"""

    def test_source_copy_loads_empty(self):
        # KbLoader 加载 source_copies.json(kind=source_copy,空 items)经 schema 校验无错
        kb = _loader()
        self.assertEqual(kb.counts()["source_copy"], 0)
        self.assertEqual(kb.source_copies, [])

    def test_extensible_links_optional_and_absent(self):
        # passage.source_copy_id / edition.source_copies 为可选且当前不填——零虚构副本
        kb = _loader()
        for p in kb.passages:
            self.assertNotIn("source_copy_id", p, f"passage {p['passage_id']} 不得虚构 source_copy_id")
        for e in kb.editions:
            self.assertNotIn("source_copies", e, f"edition {e['edition_id']} 不得虚构 source_copies")

    def test_closure_zero_violations_with_source_copy(self):
        kb = _loader()
        rl = RuleLoader(REPO / "backend" / "data", REPO / "docs")
        self.assertEqual(kb.verify_link_closure(rl.rules), [])


if __name__ == "__main__":
    unittest.main()
