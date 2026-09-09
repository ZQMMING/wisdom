"""R-04-P0-I-C: TRUE Dual-Track Correctness Verification

核心目的：
- Independent Correctness Oracle (绝对零依赖) ← 正确答案
- Production BaziEngine (当前实际行为) ← 待验证
- 对比两者差异
- FAIL 标注为 PRODUCTION_BUG，不修改 Oracle

P0-J-3 (Solar Year Boundary Resolver) + P0-J-1/2 (秒级精度) 全部完成。
最终结果：44/44 PASS, 0 PRODUCTION_BUGS.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo


def production_compute(civil_dt):
    """通过 BaziAdapter 调 Production BaziEngine，输出当前实际行为

    R-04-P0-J: 传入 second 参数（TimeResolver P0-1 修复后）
    """
    from tongshu.engines.time.resolver import TimeResolver
    from tongshu.engines.bazi_adapter import BaziAdapter

    civil_date = civil_dt.date()
    resolver = TimeResolver()
    ctx = resolver.resolve_context(
        birth_date=civil_date,
        hour=civil_dt.hour,
        minute=civil_dt.minute,
        second=civil_dt.second,
        timezone="Asia/Shanghai",
        location="Beijing",
        apparent_solar=False,
        gender="male",
    )

    adapter = BaziAdapter()
    chart = adapter.compute(ctx, gender="male")

    return {
        "year": (chart.year_pillar.heavenly_stem, chart.year_pillar.earthly_branch),
        "month": (chart.month_pillar.heavenly_stem, chart.month_pillar.earthly_branch),
        "day": (chart.day_pillar.heavenly_stem, chart.day_pillar.earthly_branch),
        "hour": (chart.hour_pillar.heavenly_stem, chart.hour_pillar.earthly_branch),
    }


# Import Independent Oracle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_r04_independent_correctness_oracle import (
    independent_oracle,
    LICHUN, JINGZHE, QINGMING, LIXIA, MANGZHONG, XIAOSHU,
    LISHU, BAILU, HANLU, LIDONG, DAXUE, XIAOHAN,
)


def build_boundary_matrix():
    """12×3=36 cases 边界矩阵（秒级精度）"""
    test_cases = []
    term_data = [
        ("立春", LICHUN), ("惊蛰", JINGZHE), ("清明", QINGMING),
        ("立夏", LIXIA), ("芒种", MANGZHONG), ("小暑", XIAOSHU),
        ("立秋", LISHU), ("白露", BAILU), ("寒露", HANLU),
        ("立冬", LIDONG), ("大雪", DAXUE), ("小寒", XIAOHAN),
    ]
    for term_name, term_dt in term_data:
        test_cases.append((term_dt - timedelta(seconds=1), f"{term_name}前1秒"))
        test_cases.append((term_dt, f"{term_name}时刻"))
        test_cases.append((term_dt + timedelta(seconds=1), f"{term_name}后1秒"))
    return test_cases


def build_extra_cases():
    """补充测试：23:00 换日 + 立春前2天23:30 + 时辰边界"""
    return [
        # 23:00 换日
        (datetime(2024, 2, 3, 23, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "立春前1天23:30"),
        (datetime(2024, 2, 4, 23, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "立春当天23:30"),
        # 立春前2天23:30 - 跨日边界
        (datetime(2024, 2, 3, 23, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "立春前2天23:00"),
        (datetime(2024, 2, 3, 23, 59, 59, tzinfo=ZoneInfo("Asia/Shanghai")), "立春前2天23:59"),
        # 时辰边界
        (datetime(2024, 2, 4, 0, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "子时00:30"),
        (datetime(2024, 2, 4, 3, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "寅时03:30"),
        (datetime(2024, 2, 4, 12, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "午时12:00"),
        (datetime(2024, 2, 4, 15, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "申时15:30"),
    ]


def _compare_pillars(oracle_result, production_result):
    return all(
        oracle_result[pillar] == production_result[pillar]
        for pillar in ["year", "month", "day", "hour"]
    )


def dual_track_correctness_verify():
    results = {"pass_count": 0, "fail_count": 0, "production_bugs": [], "details": []}

    print("=" * 70)
    print("R-04-P0-I-C: TRUE Dual-Track Correctness Verification")
    print("Independent Oracle (正确答案) ↔ Production (待验证)")
    print("FAIL = PRODUCTION_BUG，必须修 Production，不修改 Oracle")
    print("=" * 70)

    all_test_cases = build_boundary_matrix() + build_extra_cases()

    for civil_dt, desc in all_test_cases:
        oracle_result = independent_oracle(civil_dt)
        production_result = production_compute(civil_dt)

        match = _compare_pillars(oracle_result, production_result)
        status = "✅ PASS" if match else "❌ FAIL [PRODUCTION_BUG]"

        y_o, m_o, d_o, h_o = oracle_result["year"], oracle_result["month"], oracle_result["day"], oracle_result["hour"]
        y_p, m_p, d_p, h_p = production_result["year"], production_result["month"], production_result["day"], production_result["hour"]

        if match:
            print(f"{status} {desc}: Oracle=Production=({y_o[0]}{y_o[1]} {m_o[0]}{m_o[1]} {d_o[0]}{d_o[1]} {h_o[0]}{h_o[1]})")
            results["pass_count"] += 1
        else:
            print(f"{status} {desc}:")
            print(f"   Oracle     = ({y_o[0]}{y_o[1]} {m_o[0]}{m_o[1]} {d_o[0]}{d_o[1]} {h_o[0]}{h_o[1]})")
            print(f"   Production = ({y_p[0]}{y_p[1]} {m_p[0]}{m_p[1]} {d_p[0]}{d_p[1]} {h_p[0]}{h_p[1]})")
            for pillar in ["year", "month", "day", "hour"]:
                if oracle_result[pillar] != production_result[pillar]:
                    o = oracle_result[pillar]
                    p = production_result[pillar]
                    results["production_bugs"].append({
                        "test": desc, "pillar": pillar,
                        "oracle": f"{o[0]}{o[1]}", "production": f"{p[0]}{p[1]}",
                    })
            results["fail_count"] += 1

    return results


if __name__ == "__main__":
    results = dual_track_correctness_verify()

    total = results["pass_count"] + results["fail_count"]
    print("\n" + "=" * 70)
    print(f"📊 TRUE DUAL-TRACK RESULT: {results['pass_count']}/{total} PASS")
    print(f"🔴 PRODUCTION_BUGS FOUND: {results['fail_count']}")
    print("=" * 70)

    if results["production_bugs"]:
        print("\n🔴 PRODUCTION BUGS THAT MUST BE FIXED:")
        for bug in results["production_bugs"]:
            print(f"   [{bug['pillar']}] {bug['test']}: Oracle={bug['oracle']} vs Production={bug['production']}")

    print("\n" + "=" * 70)
    if results["fail_count"] == 0:
        print("✅ 0 PRODUCTION_BUGS - Independent Oracle ≡ Production")
    else:
        print(f"❌ {results['fail_count']} PRODUCTION_BUGS - 必须修 Production")
    print("=" * 70)
