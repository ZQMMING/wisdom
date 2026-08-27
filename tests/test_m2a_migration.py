"""M2-A Passage Five-Layer Migration 测试 — schema v2.1 + data + loader + validator。

覆盖(KB_VALIDATION_SPEC V-5L + Spec Owner M2-A 验收 #2/#4/#5/#6/#7):
  1. 五层结构:20 条 passage 全有 source_layer(14 五经 + 6 河洛 P-HL,HL_H1_KICKOFF_AND_RULINGS.md H1-A);
     5 条 verified/cross_verified 的 classical_original.text 非空;15 条 pending 为空且 paraphrase 带 (待校,paraphrase) 前缀。
  2. 枚举规范化:全库无 legacy 取值(待校);BAZI-00x 4 条升 cross_verified。
  3. S1 反链 closure:concept.passage_refs ⇔ passage.concept_ids 双向对称;
     passage.principle_ids/concept_ids、concept.principle_ids/contexts 前向存在。
  4. V-5L 检测器:生产零违规;注入违例(原文非空但 verification=pending / 评注混入原文)→ 命中。
  5. legacy residue 识别:生产零残留;注入旧字段(original_text/待校/缺 source_layer)→ 命中。
  6. evidence v1.1:52 条过 schema;缺 source_layer / 未知 edition_id / 非工程种子缺 edition_id → 命中。
  7. 原子切换:loader 加载 v2.1 schema+data 零违规;旧 v2.0 形状 passages → KnowledgeLoadError。
  8. 回滚:_m2a_backup 齐全;旧 passages.v1 过 v2.0 schema(一致回滚点);legacy 扫描器命中旧数据。
"""

from __future__ import annotations
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import jsonschema

from tongshu.reasoning.knowledge_base import KbLoader, KnowledgeLoadError

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "backend" / "data"
DOCS = REPO / "docs"
BACKUP = DATA / "_m2a_backup"
DOCS_BACKUP = DOCS / "_m2a_backup"

VERIFIED = {"verified", "cross_verified"}
PENDING_PREFIX = "(待校,paraphrase)"


def _live_loader() -> KbLoader:
    return KbLoader(DATA, DOCS)


def _build_tree() -> Path:
    """拷贝生产 knowledge 树到临时目录(loader 需要全部 7 个文件)。"""
    tmp = Path(tempfile.mkdtemp(prefix="m2a_test_"))
    shutil.copytree(DATA / "knowledge", tmp / "knowledge")
    return tmp


class TestFiveLayerStructure(unittest.TestCase):
    def test_all_passages_have_five_layer_slots(self):
        kb = _live_loader()
        self.assertEqual(len(kb.passages), 38)
        for p in kb.passages:
            self.assertIn("source_layer", p)
            self.assertIn("classical_original", p)
            self.assertIn("paraphrase", p)
            self.assertIn("verification_status", p)
            self.assertNotIn("original_text", p, "五层化后不得残留 original_text")
            self.assertNotIn("normalized_text", p, "五层化后不得残留 normalized_text")

    def test_verified_have_original_pending_have_prefix(self):
        kb = _live_loader()
        n_verified = n_pending = 0
        for p in kb.passages:
            vs = p["verification_status"]
            co = p["classical_original"]
            para = p["paraphrase"]["text"]
            if vs in VERIFIED:
                n_verified += 1
                self.assertTrue((co["text"] or "").strip(), f"{p['passage_id']} verified 但原文空")
                self.assertEqual(co["verification"], vs)
            else:
                self.assertEqual(vs, "pending_verification")
                n_pending += 1
                self.assertEqual((co["text"] or "").strip(), "", f"{p['passage_id']} pending 不应有原文")
                self.assertTrue(para.startswith(PENDING_PREFIX), f"{p['passage_id']} 缺待校前缀")
        self.assertEqual(n_verified, 5)
        self.assertEqual(n_pending, 33)  # 15 base + 18 new passages from KB link closure

    def test_enum_normalization_no_legacy_values(self):
        # 枚举规范化:旧『待校』→ pending_verification;『verified』仍是合法新枚举值
        kb = _live_loader()
        for p in kb.passages:
            self.assertNotEqual(p["verification_status"], "待校")
            self.assertIn(p["verification_status"], {"verified", "cross_verified", "pending_verification", "disputed"})
        for c in kb.chapters:
            self.assertNotEqual(c.get("verification_status"), "待校")
            self.assertIn(c.get("verification_status"), {"verified", "cross_verified", "pending_verification", "disputed"})

    def test_bazi_cross_verified(self):
        # P0-15 cross_verified=true 的 BAZI-00x passage 升 cross_verified(迁移表 §6)
        kb = _live_loader()
        by_id = {p["passage_id"]: p for p in kb.passages}
        for pid in ("P-SMTH-SHIZI", "P-YHZP-DAYUN", "P-DTS-SHENGSHI", "P-YHZP-WUSHUDUN"):
            self.assertEqual(by_id[pid]["verification_status"], "cross_verified", pid)
            self.assertEqual(by_id[pid]["classical_original"]["verification"], "cross_verified", pid)


class TestS1Backlinks(unittest.TestCase):
    def test_concept_passage_bidirectional(self):
        kb = _live_loader()
        passage_by_id = {p["passage_id"]: p for p in kb.passages}
        for c in kb.concepts:
            cid = c["concept_id"]
            for ref in c.get("passage_refs", []):
                p = passage_by_id.get(ref)
                self.assertIsNotNone(p, f"concept {cid} -> 未知 passage {ref}")
                self.assertIn(cid, p.get("concept_ids", []),
                              f"concept {cid}->{ref} 反向缺 concept_ids")
        for p in kb.passages:
            for cid in p.get("concept_ids", []):
                c = kb.get("concept", cid)
                self.assertIsNotNone(c, f"passage {p['passage_id']} -> 未知 concept {cid}")
                self.assertIn(p["passage_id"], c.get("passage_refs", []),
                              f"passage {p['passage_id']}->{cid} 反向缺 passage_refs")

    def test_forward_existence(self):
        kb = _live_loader()
        principles = kb.ids("principle")
        concepts = kb.ids("concept")
        books = kb.ids("book")
        for p in kb.passages:
            for r in p.get("principle_ids", []):
                self.assertIn(r, principles, f"{p['passage_id']} -> 未知 principle {r}")
            for r in p.get("concept_ids", []):
                self.assertIn(r, concepts, f"{p['passage_id']} -> 未知 concept {r}")
        for c in kb.concepts:
            cid = c["concept_id"]
            for r in c.get("principle_ids", []):
                self.assertIn(r, principles, f"concept {cid} -> 未知 principle {r}")
            for ctx in c.get("contexts", []):
                self.assertIn(ctx["book_id"], books, f"concept {cid} -> context 未知 book")
                if ctx.get("principle_id"):
                    self.assertIn(ctx["principle_id"], principles,
                                  f"concept {cid} -> context 未知 principle")

    def test_r2_yongshen_chapter_link(self):
        # R2:用神凭《论用神》章节名显式链接(principle_id=null 合法)
        kb = _live_loader()
        yongshen = kb.get("concept", "用神")
        self.assertEqual(yongshen["passage_refs"], ["P-ZPZ-YONGSHEN"])
        ctx = yongshen["contexts"][0]
        self.assertEqual(ctx["book_id"], "ZIPING-ZHENQUAN")
        self.assertIsNone(ctx["principle_id"])


class TestV5L(unittest.TestCase):
    def test_production_zero_v5l(self):
        self.assertEqual(_live_loader().verify_link_closure(), [],
                         "生产数据 V-5L/closure 必须零违规")

    def test_detects_commentary_mixed_into_original(self):
        tmp = _build_tree()
        path = tmp / "knowledge" / "passages.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        p = next(x for x in d["items"] if x["passage_id"] == "P-ZPZ-YONGSHEN")
        p["classical_original"]["text"] += "任铁樵曰:此理甚明。"  # 评注混入原文 → V-5L④
        path.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        kb = KbLoader(tmp, DOCS)
        self.assertTrue(any("commentary markers" in v for v in kb.verify_link_closure()))
        shutil.rmtree(tmp)

    def test_detects_original_with_pending(self):
        tmp = _build_tree()
        path = tmp / "knowledge" / "passages.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        p = next(x for x in d["items"] if x["passage_id"] == "P-SMTH-JIANLU")
        p["classical_original"]["text"] = "甲禄在寅,乙禄在卯。"  # pending 但塞入原文 → V-5L①/⑤
        path.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        kb = KbLoader(tmp, DOCS)
        viol = kb.verify_link_closure()
        self.assertTrue(any("V-5L①" in v or "V-5L⑤" in v for v in viol))
        shutil.rmtree(tmp)


class TestLegacyResidue(unittest.TestCase):
    def test_production_zero_residue(self):
        self.assertEqual(KbLoader.verify_legacy_residue(DATA), [],
                         "生产数据不得有 v1/v2.0 残留")

    def test_detects_legacy_fields(self):
        tmp = _build_tree()
        path = tmp / "knowledge" / "passages.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        p = next(x for x in d["items"] if x["passage_id"] == "P-ZPZ-YONGSHEN")
        p["original_text"] = "八字用神,专求月令"
        p["verification_status"] = "待校"
        del p["source_layer"]  # 旧形状缺 source_layer
        path.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        findings = KbLoader.verify_legacy_residue(tmp)
        joined = "\n".join(findings)
        self.assertIn("original_text", joined)
        self.assertIn("待校", joined)
        self.assertIn("source_layer", joined)
        shutil.rmtree(tmp)

    def test_detects_evidence_without_source_layer(self):
        tmp = _build_tree()
        (tmp / "evidence").mkdir()
        ev = {"evidence_id": "E-OLD-001", "rule_refs": ["ZPZ-001"],
              "citation": {"original_text": "x", "language": "classical_chinese"},
              "evidence_strength": "primary", "version": "1.0.0"}
        (tmp / "evidence" / "E-OLD-001.json").write_text(
            json.dumps(ev, ensure_ascii=False), encoding="utf-8")
        findings = KbLoader.verify_legacy_residue(tmp)
        self.assertTrue(any("E-OLD-001" in f and "source_layer" in f for f in findings))
        shutil.rmtree(tmp)


class TestEvidenceMetadata(unittest.TestCase):
    def test_all_66_validate(self):
        kb = _live_loader()
        ev_dir = DATA / "evidence"
        self.assertEqual(len(list(ev_dir.glob("*.json"))), 86)  # 66 base + 20 KB link closure new
        self.assertEqual(kb.verify_evidence(DOCS / "evidence.schema.json"), [])

    def test_detects_unknown_edition_and_missing(self):
        tmp = _build_tree()
        (tmp / "evidence").mkdir()
        ev1 = {"evidence_id": "E-BAD1", "rule_refs": ["ZPZ-101"], "source_layer": "classical_original",
               "citation": {"original_text": "x", "language": "classical_chinese"},
               "edition_id": "EDITION-NOPE", "evidence_strength": "primary", "version": "1.0.0"}
        ev2 = {"evidence_id": "E-BAD2", "rule_refs": ["ZPZ-101"], "source_layer": "classical_original",
               "citation": {"original_text": "y", "language": "classical_chinese"},
               "evidence_strength": "primary", "version": "1.0.0"}
        (tmp / "evidence" / "E-BAD1.json").write_text(json.dumps(ev1, ensure_ascii=False), encoding="utf-8")
        (tmp / "evidence" / "E-BAD2.json").write_text(json.dumps(ev2, ensure_ascii=False), encoding="utf-8")
        kb = KbLoader(tmp, DOCS)
        findings = kb.verify_evidence(DOCS / "evidence.schema.json")
        self.assertTrue(any("unknown edition_id" in f for f in findings))
        self.assertTrue(any("missing edition_id" in f for f in findings))
        shutil.rmtree(tmp)


class TestAtomicSwitch(unittest.TestCase):
    def test_loader_loads_v21(self):
        # schema+data+loader 原子切换:生产 KbLoader 直接可用
        kb = _live_loader()
        self.assertEqual(kb.counts()["passage"], 38)

    def test_old_v20_shape_rejected(self):
        # 旧 v2.0 形状 passages → 硬错(禁止「schema v2.1 上线但数据仍 v2.0」中间态)
        tmp = _build_tree()
        old = json.loads((BACKUP / "knowledge" / "passages.v1.json").read_text(encoding="utf-8"))
        (tmp / "knowledge" / "passages.json").write_text(
            json.dumps(old, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(KnowledgeLoadError):
            KbLoader(tmp, DOCS)
        shutil.rmtree(tmp)


class TestRollback(unittest.TestCase):
    def test_backup_files_present(self):
        for f in ("passages.v1.json", "concepts.v1.json", "chapters.v1.json"):
            self.assertTrue((BACKUP / "knowledge" / f).is_file(), f)
        self.assertTrue((DOCS_BACKUP / "knowledge.schema.v2.0.json").is_file())
        self.assertTrue((DOCS_BACKUP / "evidence.schema.v1.0.json").is_file())
        self.assertEqual(len(list((BACKUP / "evidence").glob("*.json"))), 52)

    def test_old_data_valid_against_old_schema(self):
        # 回滚点一致性:旧 passages.v1 过 v2.0 schema(迁移前数据自身合法)
        schema = json.loads((DOCS_BACKUP / "knowledge.schema.v2.0.json").read_text(encoding="utf-8"))
        data = json.loads((BACKUP / "knowledge" / "passages.v1.json").read_text(encoding="utf-8"))
        jsonschema.validate(data, schema)

    def test_legacy_scanner_flags_backup_data(self):
        # 备份中的旧数据应被 legacy 扫描器识别(验证器可识别旧数据残留,验收 #4)
        tmp = _build_tree()
        old = json.loads((BACKUP / "knowledge" / "passages.v1.json").read_text(encoding="utf-8"))
        (tmp / "knowledge" / "passages.json").write_text(
            json.dumps(old, ensure_ascii=False), encoding="utf-8")
        findings = KbLoader.verify_legacy_residue(tmp)
        self.assertGreaterEqual(len(findings), 1, "旧数据应被识别为残留")
        shutil.rmtree(tmp)

    def test_backup_evidence_lack_source_layer(self):
        # 备份 evidence 为迁移前形状(无 source_layer)——回滚后 v1.0 schema 可接受
        schema = json.loads((DOCS_BACKUP / "evidence.schema.v1.0.json").read_text(encoding="utf-8"))
        for f in sorted((BACKUP / "evidence").glob("*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            self.assertNotIn("source_layer", d, f.name)
            jsonschema.validate(d, schema)


if __name__ == "__main__":
    unittest.main()
