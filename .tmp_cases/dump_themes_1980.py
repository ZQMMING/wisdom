# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, 'D:/shuntian')
sys.stdout.reconfigure(encoding='utf-8')
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
from src.tongshu.engines.blind_yingqi import BlindYingqiEngine
from src.tongshu.engines.blind_judgment import BlindJudgmentEngine
from src.tongshu.engines.blind_themes import BlindThemeEngine

be = BaziEngine(); bb = BlindBaziEngine(be); by = BlindYingqiEngine(be)
jd = BlindJudgmentEngine(); th = BlindThemeEngine()

b = (1980, 6, 22, 10)
ch = be.compute(b, gender='male')
br = bb.compute(b, gender='male')
yr = by.analyze(b, gender='male', target_age=46)
jr = jd.judge(ch, br, yr)
res = th.aggregate(ch, br, yr, jr)

print('=== 1980 12主题输出（引擎原始）===')
for t in res.to_dict()['themes']:
    vals = []
    for e in t['entries']:
        src = e['source'].split('.')[-1]
        vals.append(src + '=' + e['value'])
    print(t['theme_id'], '[%s]' % t['theme_name'], t['state'], '||', '; '.join(vals))
