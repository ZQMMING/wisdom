"""Gender Golden Test - 完整链路验证"""

from __future__ import annotations
import pytest
from tongshu.engines.heluo import HeluoCanonical


class TestFullChainGenderSensitivity:
    """完整计算链验证"""
    
    JIXIAOLAN_BAZI = [("甲", "辰"), ("辛", "未"), ("丙", "戌"), ("甲", "午")]
    
    def test_male_female_different_results(self):
        """相同八字不同性别 → 完整链路结果不同"""
        c = HeluoCanonical()
        
        # 男性
        male_result = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="male",
            birth_hour="午",
            era="zhong",
        )
        
        # 女性
        female_result = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="female",
            birth_hour="午",
            era="zhong",
        )
        
        # 先天卦应不同
        assert male_result.prenatal.hexagram_name != female_result.prenatal.hexagram_name
        
        # 后天卦应不同
        assert male_result.postnatal.hexagram_name != female_result.postnatal.hexagram_name
        
        # 元堂应不同
        assert male_result.yuantang.yuantang != female_result.yuantang.yuantang
    
    def test_interpretation_based_on_structure_not_gender(self):
        """解释层基于结构差异，而非直接基于 gender"""
        c = HeluoCanonical()
        
        male_result = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="male",
            birth_hour="午",
            era="zhong",
        )
        
        # 解释层应消费结构分析结果，而非 gender
        # 这里验证：male_result 包含结构信息
        assert hasattr(male_result, 'prenatal')
        assert hasattr(male_result, 'postnatal')
        assert hasattr(male_result, 'yuantang')
