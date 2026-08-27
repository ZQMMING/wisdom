import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"
from datetime import date
from tongshu.engines.time.resolver import TimeResolver
from tongshu.engines.bazi_adapter import BaziAdapter
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.ziwei_adapter import ZiweiAdapter
from tongshu.engines.ziwei_engine import ZiweiEngine

r = TimeResolver()
ba = BaziAdapter(BaziEngine())
zw = ZiweiAdapter(ZiweiEngine())

for loc in ["guangzhou", "chengdu", "beijing"]:
    print(f"--- {loc} ---")
    for h, m in [(22, 59), (23, 30)]:
        ctx = r.resolve_context(
            birth_date=date(1990, 11, 10), hour=h, minute=m,
            timezone="Asia/Shanghai", location=loc, gender="male",
        )
        chart = ba.compute(ctx, gender="male")
        dp = f"{chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch}"
        zw_chart = zw.compute(ctx, gender="male")
        print(f"  {h:02d}:{m:02d} | solar={ctx.true_solar_datetime.strftime('%H:%M:%S')} | bazi_view={ctx.bazi_view} | zw_view={ctx.ziwei_view} | dp={dp} | zw_star={zw_chart.soul_palace_main_star}")
