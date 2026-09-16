# -*- coding: utf-8 -*-
"""Z74c: 流月应期层测试（QTN-CMB-054/055）"""

import sys

sys.path.insert(0, r"D:\shuntian-ziwei-v2\src")

import pytest

from tongshu.engines.ziwei_engine import ZiweiEngine
from tongshu.engines.ziwei.rules.qintian.combinations import PRODUCTION_DETECTORS


@pytest.fixture(scope="module")
def engine():
    return ZiweiEngine()


class TestQtnCmbZ74c:
    """流月四化应用（斗君）+ 流月化忌入天刑（应期到月）。"""

    def test_rules_registered(self):
        ids = [d.__name__ for d in PRODUCTION_DETECTORS]
        assert any("054_liuyue" in n for n in ids)
        assert any("055_liuyue_ji_tianxing" in n for n in ids)

    def test_054_liuyue_sihua_data(self, engine):
        """1983 盘流月 1 → 斗君（仆役酉）起正月，辛干文昌忌。"""
        ch = engine.full_chart((1983, 9, 29), 11, "male", flow_month=1)
        res = [c for c in PRODUCTION_DETECTORS if False]
        from tongshu.engines.ziwei.rules.qintian.combinations import detect_all_production
        hits = detect_all_production(ch)
        r54 = next((c for c in hits if c.rule_id == "QTN-CMB-054"), None)
        assert r54 is not None
        f = r54.facts
        assert f["flow_month"] == 1
        assert f["doujun_palace"] == "仆役"
        assert f["month_branch"] == "酉"
        assert f["liuyue_sihua"]["ji"] == "文昌"

    def test_054_fail_closed_no_month(self, engine):
        """无 flow_month（0）→ 054/055 fail-closed 不触发。"""
        ch = engine.full_chart((1983, 9, 29), 11, "male")
        from tongshu.engines.ziwei.rules.qintian.combinations import detect_all_production
        hits = detect_all_production(ch)
        assert not any(c.rule_id in ("QTN-CMB-054", "QTN-CMB-055") for c in hits)

    def test_055_liuyue_ji_tianxing(self, engine):
        """1983 盘流月 10 → 戊干天机忌入天刑宫 → 该月官非（斗君顺行验证）。"""
        ch = engine.full_chart((1983, 9, 29), 11, "male", flow_month=10)
        from tongshu.engines.ziwei.rules.qintian.combinations import detect_all_production
        hits = detect_all_production(ch)
        r55 = next((c for c in hits if c.rule_id == "QTN-CMB-055"), None)
        assert r55 is not None
        assert r55.facts["flow_month"] == 10
        assert r55.facts["month_stem"] == "戊"
        assert r55.facts["ji_star"] == "天机"
        assert "tianxing_palace" in r55.facts

    def test_case38_liuyue_data(self, engine):
        """#38 车祸（丙戌年四月）：流月 4 → 兄弟宫乙干太阴忌（数据层可用）。"""
        ch = engine.full_chart((1954, 9, 30), 20, "male", flow_month=4)
        from tongshu.engines.ziwei.rules.qintian.combinations import detect_all_production
        hits = detect_all_production(ch)
        r54 = next((c for c in hits if c.rule_id == "QTN-CMB-054"), None)
        assert r54 is not None
        f = r54.facts
        assert f["month_palace"] == "兄弟"
        assert f["month_stem"] == "乙"
        assert f["liuyue_sihua"]["ji"] == "太阴"
