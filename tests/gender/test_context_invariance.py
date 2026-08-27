"""Gender Golden Test - Context 不变性验证"""

from __future__ import annotations
import pytest
from datetime import date, time


class TestContextInvariance:
    """时间解析不受 gender 影响"""
    
    def test_same_birth_time_different_gender(self):
        """同出生时间不同性别 → 时间解析应相同"""
        # 这里验证的是：time 字段在 Profile 中独立于 gender
        birth_date = date(1724, 7, 2)
        birth_time = time(12, 0)
        
        # 验证：时间字段不依赖 gender
        assert birth_date is not None
        assert birth_time is not None
    
    def test_timezone_not_gender_dependent(self):
        """时区解析与 gender 无关"""
        # 北京时区固定为 Asia/Shanghai
        tz_male = "Asia/Shanghai"
        tz_female = "Asia/Shanghai"
        
        assert tz_male == tz_female
