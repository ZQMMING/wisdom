"""P0-3.2 全量 Evidence Classification 单元测试。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tongshu.corpus.adapter import FiveClassicsCorpusAdapter
from tongshu.corpus.validation import CrossValidator


class TestFullClassification:
    @classmethod
    def setup_class(cls):
        cls.adapter = FiveClassicsCorpusAdapter()
        cls.adapter.load()
        cls.validator = CrossValidator(cls.adapter)
        cls.all_entries = cls.adapter.get_all_entries()
        cls.all_results = cls.validator.validate_entries(cls.all_entries)

    def test_all_entries_covered(self):
        assert len(self.all_results) == 376

    def test_all_have_evidence_class(self):
        classes = set(r.evidence_class for r in self.all_results)
        # 五分类子集
        assert classes.issubset({"EXACT_PRIMARY", "PARTIAL", "DERIVED_TEXT", "NOT_FOUND", "CONFLICT"})

    def test_majority_exact_primary(self):
        exact = [r for r in self.all_results if r.evidence_class == "EXACT_PRIMARY"]
        assert len(exact) > 300  # 绝大多数是原典逐字

    def test_derived_text_isolated(self):
        derived = [r for r in self.all_results if r.evidence_class == "DERIVED_TEXT"]
        # 子平真诠格局条目全部隔离
        zz_derived = [r for r in derived if r.classic_id == "ziping_zhenquan"]
        assert len(zz_derived) == 14  # 14个格局条目无原文
        # 三命通会宫位条目隔离
        smth_derived = [r for r in derived if r.classic_id == "sanming_tonghui"]
        assert len(smth_derived) == 4  # 年柱/月柱/日柱/时柱

    def test_dts_all_exact(self):
        dts_results = [r for r in self.all_results if r.classic_id == "di_tian_sui"]
        assert len(dts_results) == 19
        assert all(r.evidence_class == "EXACT_PRIMARY" for r in dts_results)

    def test_qtbj_mostly_exact(self):
        qtbj_results = [r for r in self.all_results if r.classic_id == "qiongtong_baojian"]
        assert len(qtbj_results) == 120
        exact = [r for r in qtbj_results if r.evidence_class == "EXACT_PRIMARY"]
        assert len(exact) >= 118

    def test_yhzp_mostly_exact(self):
        yhzp_results = [r for r in self.all_results if r.classic_id == "yuanhai_ziping"]
        assert len(yhzp_results) == 187
        exact = [r for r in yhzp_results if r.evidence_class == "EXACT_PRIMARY"]
        assert len(exact) >= 185

    def test_smth_mostly_not_found(self):
        # 三命通会绝大多数条目是现代整理语句，NOT_FOUND
        smth_results = [r for r in self.all_results if r.classic_id == "sanming_tonghui"]
        nf = [r for r in smth_results if r.evidence_class == "NOT_FOUND"]
        assert len(nf) >= 23

    def test_get_summary_has_by_class(self):
        summary = self.validator.get_summary(self.all_results)
        assert "by_class" in summary
        assert summary["total"] == 376
        assert sum(summary["by_class"].values()) == 376

    def test_source_hash_present_for_all(self):
        for r in self.all_results:
            assert r.source_hash, f"missing hash for {r.entry_id}"

    def test_matched_passage_for_exact(self):
        for r in self.all_results:
            if r.evidence_class == "EXACT_PRIMARY":
                assert r.matched_passage_id, f"EXACT without passage: {r.entry_id}"
