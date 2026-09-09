"""R-04-P0-I-B: Production Behavior Regression

与 P0-I-A 完全分离：
- P0-I-A: Independent Correctness Oracle (零 sxtwl/BaziEngine 依赖)
- P0-I-B: Production Behavior (记录 BaziEngine 当前真实行为，用于发现 BUG)

本文件职责：
- 调用 Production BaziEngine → BaziAdapter → canonical_bazi_engine
- 输出 Production 当前实际计算的四柱
- 不做"对齐"，只做"快照"
- 与 Independent Oracle 对比时，FAIL 必须明确标注是 Production BUG
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def production_compute(civil_dt):
    """通过 BaziAdapter 调 Production BaziEngine，输出当前实际行为"""
    from tongshu.engines.time.resolver import TimeResolver
    from tongshu.engines.bazi_adapter import BaziAdapter

    civil_date = civil_dt.date()
    resolver = TimeResolver()
    ctx = resolver.resolve_context(
        birth_date=civil_date,
        hour=civil_dt.hour,
        minute=civil_dt.minute,
        timezone="Asia/Shanghai",
        location="Beijing",
        apparent_solar=False,  # 禁用真太阳时，与 Independent Oracle 一致
        gender="male",
    )

    adapter = BaziAdapter()
    chart = adapter.compute(ctx, gender="male")

    return {
        "year": (chart.year_pillar.heavenly_stem, chart.year_pillar.earthly_branch),
        "month": (chart.month_pillar.heavenly_stem, chart.month_pillar.earthly_branch),
        "day": (chart.day_pillar.heavenly_stem, chart.day_pillar.earthly_branch),
        "hour": (chart.hour_pillar.heavenly_stem, chart.hour_pillar.earthly_branch),
        "_ctx_effective_date": ctx.effective_date,
        "_ctx_effective_hour": ctx.effective_hour,
    }


if __name__ == "__main__":
    print("R-04-P0-I-B: Production Behavior Snapshot")
    print("=" * 60)
    test_cases = [
        ("立春前1秒", datetime(2024, 2, 4, 16, 26, 52, tzinfo=ZoneInfo("Asia/Shanghai"))),
        ("立春时刻", datetime(2024, 2, 4, 16, 26, 53, tzinfo=ZoneInfo("Asia/Shanghai"))),
        ("立春后1秒", datetime(2024, 2, 4, 16, 26, 54, tzinfo=ZoneInfo("Asia/Shanghai"))),
        ("立春前2天23:30 (BUG候选)", datetime(2024, 2, 3, 23, 30, tzinfo=ZoneInfo("Asia/Shanghai"))),
    ]
    for desc, civil_dt in test_cases:
        result = production_compute(civil_dt)
        print(f"{desc}: Y={result['year'][0]}{result['year'][1]} M={result['month'][0]}{result['month'][1]} D={result['day'][0]}{result['day'][1]} H={result['hour'][0]}{result['hour'][1]} eff={result['_ctx_effective_date']}/{result['_ctx_effective_hour']}")
