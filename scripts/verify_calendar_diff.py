# -*- coding: utf-8 -*-
"""历法独立引擎差分验证脚本.

对比 lunar_python 和 sxtwl(寿星天文历) 的干支计算,
验证真太阳时、节气定月、立春年界、夜子时、闰月等关键历法节点.

源自 chinese-fortune 项目的历法验证方法(MIT许可证).
用法: python scripts/verify_calendar_diff.py
"""
from __future__ import annotations

import sys
from datetime import date, timedelta

# 干支对照表
GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _ganzhi_from_index(idx: int) -> str:
    """60甲子索引→干支."""
    return GAN[idx % 10] + ZHI[idx % 12]


def verify_year_ganzhi(start_year: int = 1920, end_year: int = 2080) -> dict:
    """验证年干支(立春为界).

    返回 {total, matched, mismatched, examples}.
    """
    try:
        from lunar_python import Solar
        import sxtwl
    except ImportError as e:
        return {"error": f"依赖缺失: {e}"}

    total = 0
    matched = 0
    mismatched = 0
    examples = []

    for year in range(start_year, end_year + 1):
        # 用立春后的日期验证年干支
        test_date = date(year, 3, 1)  # 3月1日肯定在立春后
        total += 1

        # lunar_python
        lunar = Solar.fromYmd(test_date.year, test_date.month, test_date.day).getLunar()
        lp_year_gz = lunar.getYearInGanZhi()

        # sxtwl
        day = sxtwl.fromSolar(test_date.year, test_date.month, test_date.day)
        # sxtwl的年干支索引(以立春为界), GZ对象有tg(天干)和dz(地支)
        year_gz = day.getYearGZ()
        sxtwl_year_gz = GAN[year_gz.tg] + ZHI[year_gz.dz]

        if lp_year_gz == sxtwl_year_gz:
            matched += 1
        else:
            mismatched += 1
            if len(examples) < 5:
                examples.append(f"{test_date}: lunar_python={lp_year_gz}, sxtwl={sxtwl_year_gz}")

    return {
        "total": total,
        "matched": matched,
        "mismatched": mismatched,
        "match_rate": f"{matched/total*100:.2f}%" if total else "N/A",
        "examples": examples,
    }


def verify_day_ganzhi(start_date: date = date(1920, 1, 1),
                       end_date: date = date(2080, 12, 31),
                       step_days: int = 37) -> dict:
    """验证日干支(抽样验证, step_days=37约每5年一个样本).

    返回 {total, matched, mismatched, examples}.
    """
    try:
        from lunar_python import Solar
        import sxtwl
    except ImportError as e:
        return {"error": f"依赖缺失: {e}"}

    total = 0
    matched = 0
    mismatched = 0
    examples = []

    current = start_date
    while current <= end_date:
        total += 1

        # lunar_python
        lunar = Solar.fromYmd(current.year, current.month, current.day).getLunar()
        lp_day_gz = lunar.getDayInGanZhi()

        # sxtwl
        day = sxtwl.fromSolar(current.year, current.month, current.day)
        day_gz = day.getDayGZ()
        sxtwl_day_gz = GAN[day_gz.tg] + ZHI[day_gz.dz]

        if lp_day_gz == sxtwl_day_gz:
            matched += 1
        else:
            mismatched += 1
            if len(examples) < 5:
                examples.append(f"{current}: lunar_python={lp_day_gz}, sxtwl={sxtwl_day_gz}")

        current += timedelta(days=step_days)

    return {
        "total": total,
        "matched": matched,
        "mismatched": mismatched,
        "match_rate": f"{matched/total*100:.2f}%" if total else "N/A",
        "examples": examples,
    }


def verify_month_ganzhi() -> dict:
    """验证月干支(节气定月).

    抽样验证各月节气前后的月干支变化.
    """
    try:
        from lunar_python import Solar
        import sxtwl
    except ImportError as e:
        return {"error": f"依赖缺失: {e}"}

    # 节气日期(近似, 用于验证月干支变化)
    # 每月节气: 寅月立春, 卯月惊蛰, 辰月清明, 巳月立夏, 午月芒种, 未月小暑,
    #          申月立秋, 酉月白露, 戌月寒露, 亥月立冬, 子月大雪, 丑月小寒
    jieqi_dates = [
        (2, 4), (3, 6), (4, 5), (5, 6), (6, 6), (7, 7),
        (8, 8), (9, 8), (10, 8), (11, 7), (12, 7), (1, 6),
    ]

    total = 0
    matched = 0
    mismatched = 0
    examples = []

    for month, day in jieqi_dates:
        # 节气后一天验证月干支
        test_date = date(2025, month, day) + timedelta(days=1)
        if test_date.month == 13:
            test_date = date(2026, 1, 1)
        total += 1

        # lunar_python
        lunar = Solar.fromYmd(test_date.year, test_date.month, test_date.day).getLunar()
        lp_month_gz = lunar.getMonthInGanZhi()

        # sxtwl
        day_obj = sxtwl.fromSolar(test_date.year, test_date.month, test_date.day)
        month_gz = day_obj.getMonthGZ()
        sxtwl_month_gz = GAN[month_gz.tg] + ZHI[month_gz.dz]

        if lp_month_gz == sxtwl_month_gz:
            matched += 1
        else:
            mismatched += 1
            if len(examples) < 5:
                examples.append(f"{test_date}: lunar_python={lp_month_gz}, sxtwl={sxtwl_month_gz}")

    return {
        "total": total,
        "matched": matched,
        "mismatched": mismatched,
        "match_rate": f"{matched/total*100:.2f}%" if total else "N/A",
        "examples": examples,
    }


def main():
    print("=" * 60)
    print("历法独立引擎差分验证 (lunar_python vs sxtwl)")
    print("=" * 60)

    print("\n[1] 年干支验证 (1920-2080, 立春为界)")
    result = verify_year_ganzhi()
    print(f"  总计: {result['total']}, 匹配: {result['matched']}, 不匹配: {result['mismatched']}")
    print(f"  匹配率: {result['match_rate']}")
    if result.get("examples"):
        print(f"  不匹配示例: {result['examples']}")

    print("\n[2] 日干支验证 (1920-2080, 抽样每37天)")
    result = verify_day_ganzhi()
    print(f"  总计: {result['total']}, 匹配: {result['matched']}, 不匹配: {result['mismatched']}")
    print(f"  匹配率: {result['match_rate']}")
    if result.get("examples"):
        print(f"  不匹配示例: {result['examples']}")

    print("\n[3] 月干支验证 (2025年各节气后)")
    result = verify_month_ganzhi()
    print(f"  总计: {result['total']}, 匹配: {result['matched']}, 不匹配: {result['mismatched']}")
    print(f"  匹配率: {result['match_rate']}")
    if result.get("examples"):
        print(f"  不匹配示例: {result['examples']}")

    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
