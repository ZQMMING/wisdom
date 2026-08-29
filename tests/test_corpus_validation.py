"""P0-3.1 Cross-Validation 引擎单元测试。"""
import sys
from pathlib import Path

sys.path.insert(0, r"D:\shuntian\backend\src")

from tongshu.corpus.adapter import FiveClassicsCorpusAdapter
from tongshu.corpus.validation import (
    CrossValidator,
    normalize_text,
    sha256_text,
    PassageDataLoader,
)


class TestNormalizeText:
    def test_remove_whitespace_and_punctuation(self):
        assert normalize_text("甲木参天，脱胎要火。") == "甲木参天脱胎要火"

    def test_traditional_to_simplified(self):
        assert normalize_text("阴阳") == "阴阳"
        assert normalize_text("氣") == "气"

    def test_empty(self):
        assert normalize_text("") == ""
        assert normalize_text(None) == ""


class TestSha256:
    def test_deterministic(self):
        assert sha256_text("甲木参天") == sha256_text("甲木参天")

    def test_differs_for_diff_text(self):
        assert sha256_text("甲木参天") != sha256_text("乙木虽柔")

    def test_stable_length(self):
        assert len(sha256_text("任意文本")) == 16


class TestCrossValidator:
    @classmethod
    def setup_class(cls):
        cls.adapter = FiveClassicsCorpusAdapter()
        cls.adapter.load()
        cls.validator = CrossValidator(cls.adapter)
        cls.loader = cls.adapter.passage_loader if hasattr(cls.adapter, "passage_loader") else PassageDataLoader()

    def test_dts_exact_match(self):
        entry = self.adapter.get_entry_by_id("十干体性_甲")
        assert entry is not None
        result = self.validator.validate_entry(entry)
        assert result.verification_status == "EXACT_MATCH"
        assert result.matched_passage_id  # 应有命中段落
        assert result.source_hash  # 应有哈希

    def test_dts_ri_zhu_shuai_wang(self):
        entry = self.adapter.get_entry_by_id("日主衰旺论")
        assert entry is not None
        result = self.validator.validate_entry(entry)
        assert result.verification_status == "EXACT_MATCH"

    def test_qtbj_exact_match(self):
        entry = self.adapter.get_entry_by_id("甲日_寅月")
        assert entry is not None
        result = self.validator.validate_entry(entry)
        assert result.verification_status == "EXACT_MATCH"

    def test_yhzp_exact_match(self):
        entry = self.adapter.get_entry_by_id("天干体象_甲_11")
        assert entry is not None
        result = self.validator.validate_entry(entry)
        assert result.verification_status == "EXACT_MATCH"

    def test_smth_modern_text_not_found(self):
        # 三命通会强弱条目是现代整理语句，应判定 NOT_FOUND
        entry = self.adapter.get_entry_by_id("强弱_得令")
        assert entry is not None
        result = self.validator.validate_entry(entry)
        assert result.verification_status == "NOT_FOUND"

    def test_ziping_derived_text(self):
        # 子平真诠正官格无原文，应判定 DERIVED_TEXT
        entry = self.adapter.get_entry_by_id("正官格")
        assert entry is not None
        assert entry.verification_status == "DERIVED_TEXT"
        result = self.validator.validate_entry(entry)
        assert result.verification_status == "DERIVED_TEXT"

    def test_validate_entries_batch(self):
        entries = self.adapter.get_entries_by_classic("di_tian_sui")
        results = self.validator.validate_entries(entries)
        assert len(results) == len(entries)
        summary = self.validator.get_summary(results)
        assert summary["total"] == len(entries)
        assert "by_status" in summary

    def test_passage_loader(self):
        loader = PassageDataLoader()
        loader.load()
        stats = loader.get_statistics()
        assert "di_tian_sui" in stats
        assert stats["di_tian_sui"]["passage_count"] > 0
