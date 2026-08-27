import sys; sys.path.insert(0,'src')
from tongshu.engines.time.resolver import TimeResolver
from tongshu.engines.bazi_adapter import BaziAdapter
from tongshu.engines.bazi_engine import BaziEngine
from datetime import date
r=TimeResolver()
a=BaziAdapter(BaziEngine())
for m,d in [(11,10),(11,15),(12,10),(1,15),(2,10)]:
    ctx23=r.resolve_context(birth_date=date(1990,m,d),hour=23,minute=30,timezone='Asia/Shanghai',location='beijing',gender='male')
    c23=a.compute(ctx23)
    ctx22=r.resolve_context(birth_date=date(1990,m,d),hour=22,minute=30,timezone='Asia/Shanghai',location='beijing',gender='male')
    c22=a.compute(ctx22)
    p22=c22.day_pillar.heavenly_stem+c22.day_pillar.earthly_branch
    p23=c23.day_pillar.heavenly_stem+c23.day_pillar.earthly_branch
    mark=' <<DIFF' if p22!=p23 else ''
    print(f'{m}-{d} 22:30 solar={ctx22.true_solar_datetime:%H:%M} date={ctx22.effective_date} pillar={p22}')
    print(f'{m}-{d} 23:30 solar={ctx23.true_solar_datetime:%H:%M} date={ctx23.effective_date} pillar={p23}{mark}')
    print()
