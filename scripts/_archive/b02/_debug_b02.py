import sys, os; sys.path.insert(0,'src')
os.environ['TONGSHU_ALLOW_ZIWEI_STUB'] = '1'
from datetime import date
from tongshu.engines.time.resolver import TimeResolver
from tongshu.engines.ziwei_adapter import ZiweiAdapter
from tongshu.engines.ziwei_engine import ZiweiEngine
from lunar_python import Solar

r = TimeResolver()
ctx = r.resolve_context(
    birth_date=date(1984,12,7), hour=16, minute=0,
    timezone='Asia/Shanghai', location='beijing', gender='male'
)

# Old way: solar date passed as lunar
engine = ZiweiEngine(node_modules_dir=Path('node_modules')) if False else ZiweiEngine()
old_chart = engine.compute((1984, 12, 7), 16, gender='male')

# New way: adapter converts solar->lunar
adapter = ZiweiAdapter(engine)
new_chart = adapter.compute(ctx, gender='male')

# What lunar date is it?
solar = Solar.fromYmdHms(1984, 12, 7, 16, 0, 0)
lunar = solar.getLunar()
print(f"Solar 1984-12-07 -> Lunar {lunar.getYear()}-{lunar.getMonth()}-{lunar.getDay()}")
print(f"Old ziwei input: (1984, 12, 7)")
print(f"New ziwei input: ({lunar.getYear()}, {lunar.getMonth()}, {lunar.getDay()})")

# Compare charts
old_sig = engine.extract_baseline_signal(old_chart, 0)
new_sig = engine.extract_baseline_signal(new_chart, 0)
print(f"\nOld signal: {old_sig.ontology_type if old_sig else None} dir={old_sig.direction if old_sig else None}")
print(f"New signal: {new_sig.ontology_type if new_sig else None} dir={new_sig.direction if new_sig else None}")
