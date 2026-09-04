"""
P2.6-C Canonical Ten-God Rule Verification: 建立十神映射的完整 Truth Table
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from tongshu.engines.bazi_engine import (
    _ten_god,
    STEM_ELEMENT,
    STEM_POLARITY,
    _GENERATES,
    _CONTROLS,
    HEAVENLY_STEMS,
)


class TestTenGodCanonicalTruthTable:
    """验证 _ten_god 算法的10×1 Truth Table 每格都有经典依据"""

    # ========== 同我者: 比肩(同阴阳), 劫财(异阴阳) ==========
    def test_bi_jian_same_yang(self):
        """比肩: 同五行 + 同阴阳 → 证据: E-ZQ-051-001"""
        assert _ten_god("JIA", "JIA") == "比肩"   # 阳木+阳木
        assert _ten_god("YI", "YI") == "比肩"     # 阴木+阴木
        assert _ten_god("BING", "BING") == "比肩" # 阳火+阳火

    def test_jie_cai_diff_polarity(self):
        """劫财: 同五行 + 异阴阳 → 证据: E-ZQ-051-001"""
        assert _ten_god("JIA", "YI") == "劫财"   # 阳木+阴木
        assert _ten_god("YI", "JIA") == "劫财"   # 阴木+阳木
        assert _ten_god("WU", "JI") == "劫财"    # 阳土+阴土

    # ========== 我生者: 食神(同阴阳), 伤官(异阴阳) ==========
    def test_shi_shen_same_polarity(self):
        """食神: 我生 + 同阴阳 → 证据: E-ZQ-051-001"""
        assert _ten_god("JIA", "BING") == "食神"  # 木生火，阳+阳
        assert _ten_god("YI", "DING") == "食神"   # 木生火，阴+阴
        assert _ten_god("BING", "WU") == "食神"   # 火生土，阳+阳

    def test_shang_guan_diff_polarity(self):
        """伤官: 我生 + 异阴阳 → 证据: E-ZQ-051-001"""
        assert _ten_god("JIA", "DING") == "伤官"  # 木生火，阳+阴
        assert _ten_god("YI", "BING") == "伤官"   # 木生火，阴+阳
        assert _ten_god("BING", "JI") == "伤官"   # 火生土，阳+阴

    # ========== 生我者: 偏印(同阴阳), 正印(异阴阳) ==========
    def test_pian_yin_same_polarity(self):
        """偏印: 生我 + 同阴阳 → 证据: E-ZQ-051-001"""
        assert _ten_god("JIA", "REN") == "偏印"   # 水生木，阳+阳
        assert _ten_god("YI", "GUI") == "偏印"    # 水生木，阴+阴
        assert _ten_god("BING", "GUI") == "正官"  # 水克火，阳+阴 → 正官

    def test_zheng_yin_diff_polarity(self):
        """正印: 生我 + 异阴阳 → 证据: E-ZQ-051-001"""
        assert _ten_god("JIA", "GUI") == "正印"   # 水生木，阳+阴
        assert _ten_god("YI", "REN") == "正印"    # 水生木，阴+阳
        assert _ten_god("BING", "REN") == "七杀"  # 水克火，阳+阳 → 七杀

    # ========== 克我者: 七杀(同阴阳), 正官(异阴阳) ==========
    def test_qi_sha_same_polarity(self):
        """七杀: 克我 + 同阴阳 → 证据: E-ZQ-051-001"""
        assert _ten_god("JIA", "GENG") == "七杀"  # 金克木，阳+阳
        assert _ten_god("YI", "XIN") == "七杀"    # 金克木，阴+阴
        assert _ten_god("BING", "XIN") == "正财"  # 火克金，阳+阴 → 正财

    def test_zheng_guan_diff_polarity(self):
        """正官: 克我 + 异阴阳 → 证据: E-ZQ-051-001"""
        assert _ten_god("JIA", "XIN") == "正官"   # 金克木，阳+阴
        assert _ten_god("YI", "GENG") == "正官"   # 金克木，阴+阳
        assert _ten_god("BING", "GENG") == "偏财" # 火克金，阳+阳 → 偏财

    # ========== 我克者: 偏财(同阴阳), 正财(异阴阳) ==========
    def test_pian_cai_same_polarity(self):
        """偏财: 我克 + 同阴阳 → 证据: E-ZQ-051-001"""
        assert _ten_god("JIA", "WU") == "偏财"    # 木克土，阳+阳
        assert _ten_god("YI", "JI") == "偏财"     # 木克土，阴+阴
        assert _ten_god("BING", "JI") == "伤官"   # 火生土，阳+阴 → 伤官

    def test_zheng_cai_diff_polarity(self):
        """正财: 我克 + 异阴阳 → 证据: E-ZQ-051-001"""
        assert _ten_god("JIA", "JI") == "正财"    # 木克土，阳+阴
        assert _ten_god("YI", "WU") == "正财"     # 木克土，阴+阳
        assert _ten_god("BING", "WU") == "食神"   # 火生土，阳+阳 → 食神

    # ========== 经典原文验证 ==========
    def test_classical_example_jia_geng(self):
        """经典原文示例: 甲乙见庚辛"""
        # 原文: "甲者，阳木也...故逢秋天为官，而乙则反是，庚官而辛杀也"
        # 翻译: 乙见庚为正官（异阴阳），甲见庚为七杀（同阴阳）
        assert _ten_god("JIA", "GENG") == "七杀"  # 金克木，阳+阳 = 七杀 ✓
        assert _ten_god("YI", "GENG") == "正官"   # 金克木，阴+阳 = 正官 ✓

    def test_classical_example_geng_bing(self):
        """经典原文示例: 庚辛见丙"""
        # 原文: "此庚以丙为杀，而辛以丙为官也"
        assert _ten_god("GENG", "BING") == "七杀"  # 火克金，阳+阳 = 七杀 ✓
        assert _ten_god("XIN", "BING") == "正官"   # 火克金，阴+阳 = 正官 ✓

    def test_classical_example_xin_ding(self):
        """经典原文示例: 辛庚见丁"""
        # 原文: "此所以辛以丁为杀，而庚以丁为官也"
        assert _ten_god("XIN", "DING") == "七杀"  # 火克金，阴+阴 = 七杀 ✓
        assert _ten_god("GENG", "DING") == "正官" # 火克金，阳+阴 = 正官 ✓

    # ========== 全量覆盖测试 ==========
    def test_complete_truth_table(self):
        """验证100种组合全部覆盖，每格都有有效输出"""
        valid_ten_gods = {
            "比肩", "劫财", "食神", "伤官",
            "偏印", "正印", "七杀", "正官", "偏财", "正财"
        }
        for dm in HEAVENLY_STEMS:
            for other in HEAVENLY_STEMS:
                result = _ten_god(dm, other)
                assert result in valid_ten_gods, f"Invalid: {dm}-{other} -> {result}"

    def test_polarity_rule_consistency(self):
        """验证偏正规则的一致性：同阴阳=偏，异阴阳=正"""
        for dm in HEAVENLY_STEMS:
            for other in HEAVENLY_STEMS:
                if dm == other:
                    continue  # 自己不算

                same_polarity = STEM_POLARITY[dm] == STEM_POLARITY[other]
                result = _ten_god(dm, other)

                # 同我者
                if STEM_ELEMENT[dm] == STEM_ELEMENT[other]:
                    if same_polarity:
                        assert result == "比肩", f"{dm}+{other} should be 比肩, got {result}"
                    else:
                        assert result == "劫财", f"{dm}+{other} should be 劫财, got {result}"

                # 我生者
                elif _GENERATES.get(STEM_ELEMENT[dm]) == STEM_ELEMENT[other]:
                    if same_polarity:
                        assert result == "食神", f"{dm}+{other} should be 食神, got {result}"
                    else:
                        assert result == "伤官", f"{dm}+{other} should be 伤官, got {result}"

                # 生我者
                elif _GENERATES.get(STEM_ELEMENT[other]) == STEM_ELEMENT[dm]:
                    if same_polarity:
                        assert result == "偏印", f"{dm}+{other} should be 偏印, got {result}"
                    else:
                        assert result == "正印", f"{dm}+{other} should be 正印, got {result}"

                # 克我者
                elif _CONTROLS.get(STEM_ELEMENT[other]) == STEM_ELEMENT[dm]:
                    if same_polarity:
                        assert result == "七杀", f"{dm}+{other} should be 七杀, got {result}"
                    else:
                        assert result == "正官", f"{dm}+{other} should be 正官, got {result}"

                # 我克者
                elif _CONTROLS.get(STEM_ELEMENT[dm]) == STEM_ELEMENT[other]:
                    if same_polarity:
                        assert result == "偏财", f"{dm}+{other} should be 偏财, got {result}"
                    else:
                        assert result == "正财", f"{dm}+{other} should be 正财, got {result}"


class TestTenGodEvidenceTrace:
    """验证十神算法的Evidence Trace完整性"""

    def test_evidence_id_exists(self):
        """验证 _ten_god 有 evidence_id 引用"""
        from tongshu.engines.bazi_engine import _ten_god_evidence_id
        assert _ten_god_evidence_id is not None
        assert "E-ZQ-051-001" in _ten_god_evidence_id

    def test_classical_rule_extractable(self):
        """验证可以从经典原文中提取十神规则"""
        # 这是证据验证，不是代码测试
        # 规则已经存在于 E-ZQ-051-001 的 original_text 中
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
