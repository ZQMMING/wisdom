"""Gender Golden Test 共享 fixture"""

from __future__ import annotations
import pytest
from datetime import date, time
from tongshu.engines.heluo import HeluoCanonical
from tongshu.engines.heluo.input import HeluoInput


@pytest.fixture
def jixiaolan_input():
    """纪晓岚案例输入（同八字不同性别）"""
    return HeluoInput(
        birth_date=date(1724, 7, 2),
        birth_time=time(12, 0),
        gender="male",
        calendar_system="zhongyuan",
        location={"latitude": 39.90, "longitude": 116.40},
        timezone="Asia/Shanghai",
    )


@pytest.fixture
def jixiaolan_input_female(jixiaolan_input):
    """纪晓岚女性版本"""
    return jixiaolan_input.model_copy(update={"gender": "female"})


@pytest.fixture
def heluo_canonical():
    """河洛引擎单例"""
    return HeluoCanonical()
