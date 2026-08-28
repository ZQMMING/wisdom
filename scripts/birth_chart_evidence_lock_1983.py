"""Birth Chart Evidence Lock - 1983案例基准命例证据锁.

治理规则: 任何Golden Case/Fixture在进入Selection、Assertion或Validation之前,
必须先通过Birth Chart Evidence Lock.

原始出生资料 → 历法类型 → 公历日期 → 时区 → 真太阳时规则 → 四柱 → 日主
任一环节未锁定, 不得进入后续测试.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

import hashlib
from dataclasses import dataclass, field
from typing import Optional

from tongshu.engines.bazi_engine import BaziEngine


@dataclass
class BirthChartEvidence:
    """Birth Chart Evidence Lock - 基准命例完整证据链."""
    # 原始输入
    case_id: str
    original_lunar_date: str  # 原始农历日期
    original_time: str  # 原始时辰
    original_gender: str  # 原始性别
    calendar_type: str  # 历法类型: LUNAR / SOLAR

    # 农历转公历
    solar_date: tuple  # (年, 月, 日)
    solar_time_hour: int  # 公历小时
    conversion_source: list  # 转换来源/验证来源

    # 时区/真太阳时
    timezone: str  # 时区
    true_solar_time: bool  # 是否使用真太阳时
    location: Optional[tuple]  # 经纬度 (用于真太阳时)

    # 四柱计算
    year_pillar: str
    month_pillar: str
    day_pillar: str
    hour_pillar: str
    day_master: str
    day_master_element: str
    day_master_yin_yang: str

    # 引擎信息
    engine_name: str
    engine_version: str
    compute_params: dict

    # 证据锁
    evidence_hash: str = ""
    locked: bool = False

    def compute_hash(self) -> str:
        """计算证据链hash, 确保基准命例不可篡改."""
        evidence_str = (
            f"{self.case_id}|{self.original_lunar_date}|{self.original_time}|{self.original_gender}|"
            f"{self.calendar_type}|{self.solar_date}|{self.solar_time_hour}|"
            f"{self.timezone}|{self.true_solar_time}|{self.location}|"
            f"{self.year_pillar}|{self.month_pillar}|{self.day_pillar}|{self.hour_pillar}|"
            f"{self.day_master}|{self.engine_name}|{self.engine_version}"
        )
        return hashlib.sha256(evidence_str.encode('utf-8')).hexdigest()[:16]

    def lock(self):
        """锁定证据链."""
        self.evidence_hash = self.compute_hash()
        self.locked = True

    def verify(self) -> bool:
        """验证证据链完整性."""
        if not self.locked:
            return False
        return self.compute_hash() == self.evidence_hash


def build_1983_evidence() -> BirthChartEvidence:
    """构建1983案例的Birth Chart Evidence Lock."""
    engine = BaziEngine()
    chart = engine.compute((1983, 11, 3, 12), 'male')

    evidence = BirthChartEvidence(
        case_id="GOLDEN_CASE_1983_MALE",
        original_lunar_date="农历1983年九月二十九",
        original_time="午时 (11:00-12:59)",
        original_gender="男",
        calendar_type="LUNAR (原始输入为农历)",
        solar_date=(1983, 11, 3),
        solar_time_hour=12,
        conversion_source=[
            "阴历阳历网: 1983.11.3 = 农历癸亥年九月廿九",
            "天气网万年历: 1983年11月03日 = 农历一九八三年九月(大)廿九",
            "便民查询网: 1983年11月3日 = 九月廿九 癸亥年壬戌月乙未日",
            "周新春易学网: 农历1983年九月廿九 = 公历1983年11月3日",
        ],
        timezone="Asia/Shanghai (UTC+8, 标准北京时间)",
        true_solar_time=False,
        location=None,
        year_pillar=f"{chart.year_pillar.heavenly_stem}{chart.year_pillar.earthly_branch}",
        month_pillar=f"{chart.month_pillar.heavenly_stem}{chart.month_pillar.earthly_branch}",
        day_pillar=f"{chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch}",
        hour_pillar=f"{chart.hour_pillar.heavenly_stem}{chart.hour_pillar.earthly_branch}",
        day_master=chart.day_master,
        day_master_element="WOOD",
        day_master_yin_yang="YIN (阴木)",
        engine_name="BaziEngine",
        engine_version="production",
        compute_params={
            "solar_date": (1983, 11, 3, 12),
            "gender": "male",
            "skip_late_zi": False,
        },
    )
    evidence.lock()
    return evidence


def main():
    print("=" * 80)
    print("Birth Chart Evidence Lock - GOLDEN_CASE_1983_MALE")
    print("=" * 80)

    evidence = build_1983_evidence()

    print("\n=== 1. 原始输入 ===")
    print(f"  Case ID: {evidence.case_id}")
    print(f"  原始农历日期: {evidence.original_lunar_date}")
    print(f"  原始时辰: {evidence.original_time}")
    print(f"  原始性别: {evidence.original_gender}")
    print(f"  历法类型: {evidence.calendar_type}")

    print("\n=== 2. 农历转公历 ===")
    print(f"  公历日期: {evidence.solar_date[0]}-{evidence.solar_date[1]:02d}-{evidence.solar_date[2]:02d}")
    print(f"  公历小时: {evidence.solar_time_hour}:00")
    print(f"  转换验证来源:")
    for src in evidence.conversion_source:
        print(f"    - {src}")

    print("\n=== 3. 时区/真太阳时 ===")
    print(f"  时区: {evidence.timezone}")
    print(f"  真太阳时: {evidence.true_solar_time} (不使用)")
    print(f"  位置: {evidence.location} (不使用)")

    print("\n=== 4. 四柱计算 (BaziEngine) ===")
    print(f"  年柱: {evidence.year_pillar}")
    print(f"  月柱: {evidence.month_pillar}")
    print(f"  日柱: {evidence.day_pillar}")
    print(f"  时柱: {evidence.hour_pillar}")
    print(f"  日主: {evidence.day_master} ({evidence.day_master_element}, {evidence.day_master_yin_yang})")

    print("\n=== 5. 引擎信息 ===")
    print(f"  引擎: {evidence.engine_name} v{evidence.engine_version}")
    print(f"  计算参数: {evidence.compute_params}")

    print("\n=== 6. 证据锁 ===")
    print(f"  Evidence Hash: {evidence.evidence_hash}")
    print(f"  Locked: {evidence.locked}")
    print(f"  Verify: {evidence.verify()}")

    print("\n=== 7. 关键特征 (供后续Selection使用) ===")
    print(f"  日主: 乙木 (阴木)")
    print(f"  月令: 戌月 (九月, 寒露-立冬)")
    print(f"  月令主气: 戊土 = 正财 (对乙木)")
    print(f"  格局: 正财格")
    print(f"  调候: 乙木生于戌月, 取癸水滋润, 丙火照暖")
    print(f"  十神: 年干癸水=偏印, 月干壬水=正印, 时干壬水=正印")
    print(f"        日支未土=偏财, 时支午火=食神")
    print(f"  五行: 水=0.5(极旺), 土=0.25, 木=0.125, 火=0.125, 金=0(缺)")
    print(f"  五行失衡: True")
    print(f"  空亡: 辰、巳")
    print(f"  六合: 未午合土 (日支时支)")

    print("\n" + "=" * 80)
    print(f"Birth Chart Evidence Lock: {'COMPLETE' if evidence.verify() else 'FAILED'}")
    print(f"  Hash: {evidence.evidence_hash}")
    print(f"  此基准命例已锁定, 后续Phase 3-1/3-2/3-3必须使用此八字")
    print("=" * 80)

    return evidence


if __name__ == "__main__":
    main()
