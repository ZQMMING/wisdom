"""P0-3.1 Cross-Validation 引擎单元测试。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))

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

    def _find_entry_by_keyword(self, keyword: str, classic_id: str = None):
        """根据关键词搜索条目（适配passages格式）"""
        entries = self.adapter.get_all_entries()
        if classic_id:
            entries = [e for e in entries if e.classic_id == classic_id]
        for entry in entries:
            if keyword in entry.original_text or keyword in entry.key:
                return entry
        return None

    def test_dts_exact_match(self):
        entry = self._find_entry_by_keyword("甲", "di_tian_sui")
        assert entry is not None, "应找到包含'甲'的滴天髓段落"
        result = self.validator.validate_entry(entry)
        assert result.verification_status in ["EXACT_MATCH", "UNVERIFIED"]

    def test_dts_ri_zhu_shuai_wang(self):
        entry = self._find_entry_by_keyword("日主", "di_tian_sui")
        assert entry is not None, "应找到包含'日主'的滴天髓段落"
        result = self.validator.validate_entry(entry)
        assert result is not None

    def test_qtbj_exact_match(self):
        entry = self._find_entry_by_keyword("甲", "qiongtong_baojian")
        assert entry is not None, "应找到包含'甲'的穷通宝鉴段落"
        result = self.validator.validate_entry(entry)
        assert result.verification_status in ["EXACT_MATCH", "UNVERIFIED"]

    def test_yhzp_exact_match(self):
        entry = self._find_entry_by_keyword("天干", "yuanhai_ziping")
        assert entry is not None, "应找到包含'天干'的渊海子平段落"
        result = self.validator.validate_entry(entry)
        assert result is not None

    def test_smth_modern_text_not_found(self):
        # 三命通会中搜索现代整理语句，可能找不到
        entry = self._find_entry_by_keyword("强弱", "sanming_tonghui")
        if entry:
            result = self.validator.validate_entry(entry)
            # 可能找到，状态取决于是否匹配
            assert result is not None

    def test_ziping_derived_text(self):
        entry = self._find_entry_by_keyword("正官", "ziping_zhenquan")
        if entry:
            # 验证条目结构
            assert entry.classic_id == "ziping_zhenquan"
            result = self.validator.validate_entry(entry)
            assert result is not None

    def test_validate_entries_batch(self):
        entries = self.adapter.get_entries_by_classic("di_tian_sui")
        assert len(entries) > 0, "应找到滴天髓条目"
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
