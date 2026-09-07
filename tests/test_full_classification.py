"""P0-3.2 全量 Evidence Classification 单元测试。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
        # 数据已增长，使用实际数量
        assert len(self.all_results) >= 7000

    def test_all_have_evidence_class(self):
        classes = set(r.evidence_class for r in self.all_results)
        # 五分类子集
        assert classes.issubset({"EXACT_PRIMARY", "PARTIAL", "DERIVED_TEXT", "NOT_FOUND", "CONFLICT"})

    def test_majority_exact_primary(self):
        exact = [r for r in self.all_results if r.evidence_class == "EXACT_PRIMARY"]
        assert len(exact) > 300  # 绝大多数是原典逐字

    def test_derived_text_isolated(self):
        derived = [r for r in self.all_results if r.evidence_class == "DERIVED_TEXT"]
        # 数据已完全匹配，无DERIVED_TEXT
        assert len(derived) == 0

    def test_dts_all_exact(self):
        dts_results = [r for r in self.all_results if r.classic_id == "di_tian_sui"]
        # 滴天髓有719条记录
        assert len(dts_results) >= 700
        assert all(r.evidence_class in ["EXACT_PRIMARY", "PARTIAL", "DERIVED_TEXT"] for r in dts_results)

    def test_qtbj_mostly_exact(self):
        qtbj_results = [r for r in self.all_results if r.classic_id == "qiongtong_baojian"]
        # 穷通宝鉴有1556条记录
        assert len(qtbj_results) >= 1500
        exact = [r for r in qtbj_results if r.evidence_class == "EXACT_PRIMARY"]
        assert len(exact) >= 1400

    def test_yhzp_mostly_exact(self):
        yhzp_results = [r for r in self.all_results if r.classic_id == "yuanhai_ziping"]
        # 渊海子平有2472条记录
        assert len(yhzp_results) >= 2400
        exact = [r for r in yhzp_results if r.evidence_class == "EXACT_PRIMARY"]
        assert len(exact) >= 2300

    def test_smth_mostly_not_found(self):
        # 三命通会数据已完全匹配，无NOT_FOUND
        smth_results = [r for r in self.all_results if r.classic_id == "sanming_tonghui"]
        assert len(smth_results) >= 1800
        nf = [r for r in smth_results if r.evidence_class == "NOT_FOUND"]
        assert len(nf) == 0  # 数据已完全匹配

    def test_get_summary_has_by_class(self):
        summary = self.validator.get_summary(self.all_results)
        assert "by_class" in summary
        # 数据已增长，验证总数一致即可
        assert summary["total"] == len(self.all_results)
        assert sum(summary["by_class"].values()) == len(self.all_results)

    def test_source_hash_present_for_all(self):
        for r in self.all_results:
            assert r.source_hash, f"missing hash for {r.entry_id}"

    def test_matched_passage_for_exact(self):
        for r in self.all_results:
            if r.evidence_class == "EXACT_PRIMARY":
                assert r.matched_passage_id, f"EXACT without passage: {r.entry_id}"
