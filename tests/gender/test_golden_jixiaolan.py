"""Gender Golden Test - 纪晓岚案例"""

from __future__ import annotations
import pytest
from tongshu.engines.heluo import HeluoCanonical


class TestJixiaolanGenderDivergence:
    """纪晓岚同八字不同性别 → 卦象必须不同"""
    
    JIXIAOLAN_BAZI = [("甲", "辰"), ("辛", "未"), ("丙", "戌"), ("甲", "午")]
    
    def test_male_prenatal_is_ditian_tai(self):
        """阳年男命 → 地天泰"""
        c = HeluoCanonical()
        result = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="male",
            birth_hour="午",
            era="zhong",
        )
        assert result.prenatal.hexagram_name == "地天泰"
    
    def test_female_prenatal_is_tiandi_pi(self):
        """阳年女命 → 天地否"""
        c = HeluoCanonical()
        result = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="female",
            birth_hour="午",
            era="zhong",
        )
        assert result.prenatal.hexagram_name == "天地否"
    
    def test_gender_divergence(self):
        """完整链路：相同八字不同性别 → 结果必须不同"""
        c = HeluoCanonical()
        
        male = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="male",
            birth_hour="午",
            era="zhong",
        )
        female = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="female",
            birth_hour="午",
            era="zhong",
        )
        
        assert male.prenatal.hexagram_name != female.prenatal.hexagram_name
        assert male.postnatal.hexagram_name != female.postnatal.hexagram_name
    
    def test_postnatal_divergence(self):
        """后天卦也受性别影响"""
        c = HeluoCanonical()
        
        male = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="male",
            birth_hour="午",
            era="zhong",
        )
        female = c.calculate(
            bazi=self.JIXIAOLAN_BAZI,
            gender="female",
            birth_hour="午",
            era="zhong",
        )
        
        assert male.postnatal.hexagram_name != female.postnatal.hexagram_name
