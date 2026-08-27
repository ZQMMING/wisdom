"""Gender Golden Test - 河洛路径分歧验证"""

from __future__ import annotations
import pytest
from tongshu.engines.heluo.yuan_tang import find_yuantang
from tongshu.engines.heluo.postnatal import compute_postnatal


class TestYuantangGenderDivergence:
    """元堂定位受 gender 影响"""
    
    def test_pure_qian_male_vs_female(self):
        """纯阳卦：乾卦元堂男女不同"""
        # 乾卦纯阳：[1,1,1,1,1,1]
        male_yt = find_yuantang([1,1,1,1,1,1], "子", "male", "乾为天")
        female_yt = find_yuantang([1,1,1,1,1,1], "子", "female", "乾为天")
        
        assert male_yt.yuantang != female_yt.yuantang
    
    def test_pure_kun_male_vs_female(self):
        """纯阴卦：坤卦元堂男女不同"""
        # 坤卦纯阴：[-1,-1,-1,-1,-1,-1]
        male_yt = find_yuantang([-1,-1,-1,-1,-1,-1], "子", "male", "坤为地")
        female_yt = find_yuantang([-1,-1,-1,-1,-1,-1], "子", "female", "坤为地")
        
        assert male_yt.yuantang != female_yt.yuantang


class TestPostnatalGenderDivergence:
    """后天卦计算受性别影响"""
    
    def test_different_prenatal_leads_different_postnatal(self):
        """不同先天卦 → 不同后天卦"""
        # 地天泰 vs 天地否 → 后天卦应不同
        tai_lines = [1, 1, 1, -1, -1, -1]  # 地天泰
        pi_lines = [-1, -1, -1, 1, 1, 1]   # 天地否
        
        tai_result = compute_postnatal(tai_lines, yuantang_index=3)
        pi_result = compute_postnatal(pi_lines, yuantang_index=2)
        
        assert tai_result.hexagram_name != pi_result.hexagram_name
