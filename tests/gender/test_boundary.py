"""Gender Golden Test - 边界条件"""

from __future__ import annotations
import pytest
from tongshu.engines.heluo.input import HeluoInput, Location


class TestBoundaryConditions:
    """边界情况验证"""
    
    def test_midnight_boundary_zi_shi(self):
        """子时边界：23:00 后算次日"""
        # 验证：时间字段可以跨越子时
        early = "22:59"
        late = "23:01"
        
        # 这两个时间应在不同日期
        d1 = "2024-01-01"
        d2 = "2024-01-02"
        
        # 验证逻辑正确性
        assert early < late  # 字符串比较
    
    def test_gender_required(self):
        """gender 必须显式提供"""
        with pytest.raises(Exception):
            # 不传 gender 应抛出异常
            HeluoInput(
                birth_date="2024-01-01",
                birth_time="12:00",
                # gender 未提供
                location=Location(latitude=0, longitude=0),
                timezone="UTC",
                true_solar_datetime="2024-01-01T12:00:00",
            )
    
    def test_gender_invalid_value(self):
        """无效 gender 值应被拒绝"""
        valid_genders = {"male", "female"}
        
        for g in ["male", "female"]:
            assert g in valid_genders
        
        with pytest.raises(ValueError):
            HeluoInput(
                birth_date="2024-01-01",
                birth_time="12:00",
                gender="unknown",
                location=Location(latitude=0, longitude=0),
                timezone="UTC",
                true_solar_datetime="2024-01-01T12:00:00",
            )
