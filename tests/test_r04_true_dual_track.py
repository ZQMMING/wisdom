"""R-04-P0-I-C: True Dual-Track Correctness Verification

核心目的：
- Independent Correctness Oracle (绝对零依赖) ← 正确答案
- Production BaziEngine (当前实际行为) ← 可能存在 BUG
- 对比两者差异
- FAIL 标注为 PRODUCTION_BUG，不修改 Oracle

V2 严格审计级测试设计：
- Independent Oracle 给出的答案是正确答案（基于经典公式 + 权威锚点）
- Production 必须与 Independent Oracle 完全一致才算 PASS
- 不一致 = PRODUCTION_BUG，必须修 Production
- 绝对禁止修改 Oracle 去迎合 Production
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Import Independent Oracle (零依赖)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_r04_independent_correctness_oracle import (
    independent_oracle,
    LICHUN, JINGZHE, QINGMING, LIXIA, MANGZHONG, XIAOSHU,
    LISHU, BAILU, HANLU, LIDONG, DAXUE, XIAOHAN, LICHUN_2025,
)

# Import Production Behavior
from test_r04_production_behavior import production_compute


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
        # 立春前2天23:30 - User 标记的 BUG 候选
        (datetime(2024, 2, 3, 23, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "立春前2天23:00"),
        (datetime(2024, 2, 3, 23, 59, 59, tzinfo=ZoneInfo("Asia/Shanghai")), "立春前2天23:59"),
        # 时辰边界
        (datetime(2024, 2, 4, 0, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "子时00:30"),
        (datetime(2024, 2, 4, 3, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "寅时03:30"),
        (datetime(2024, 2, 4, 12, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "午时12:00"),
        (datetime(2024, 2, 4, 15, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai")), "申时15:30"),
    ]


def dual_track_correctness_verify():
    """真双轨正确性验证
    
    Independent Oracle = 正确答案
    Production = 待验证对象
    FAIL = PRODUCTION_BUG，必须修 Production
    """
    results = {
        "pass_count": 0,
        "fail_count": 0,
        "production_bugs": [],
        "details": [],
    }

    print("=" * 70)
    print("R-04-P0-I-C: TRUE Dual-Track Correctness Verification")
    print("Independent Oracle (正确答案) ↔ Production (待验证)")
    print("FAIL = PRODUCTION_BUG，必须修 Production，不修改 Oracle")
    print("=" * 70)

    all_test_cases = build_boundary_matrix() + build_extra_cases()

    for civil_dt, desc in all_test_cases:
        oracle_result = independent_oracle(civil_dt)
        production_result = production_compute(civil_dt)

        match = oracle_result == production_result
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
            bug_found = False
            for pillar in ["year", "month", "day", "hour"]:
                if oracle_result[pillar] != production_result[pillar]:
                    o = oracle_result[pillar]
                    p = production_result[pillar]
                    bug = {
                        "test": desc,
                        "pillar": pillar,
                        "oracle": f"{o[0]}{o[1]}",
                        "production": f"{p[0]}{p[1]}",
                    }
                    results["production_bugs"].append(bug)
                    bug_found = True
            if not bug_found:
                # 子字典都一致，但 match=False（可能是 _ctx_effective_date 等字段差异）
                print(f"   (差异在非四柱字段，例如 _ctx_*)")
            results["fail_count"] += 1

        results["details"].append({
            "test": desc,
            "status": "PASS" if match else "FAIL_PRODUCTION_BUG",
        })

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
