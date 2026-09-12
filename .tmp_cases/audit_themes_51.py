# -*- coding: utf-8 -*-
"""51 案例 12 主题批量验证：0 异常 + 枚举白名单 + 主题完整性(fail-closed)。"""
import sys, json
sys.path.insert(0, 'D:/shuntian')
sys.stdout.reconfigure(encoding='utf-8')
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
from src.tongshu.engines.blind_yingqi import BlindYingqiEngine
from src.tongshu.engines.blind_judgment import BlindJudgmentEngine
from src.tongshu.engines.blind_themes import BlindThemeEngine, THEME_DEFS

be = BaziEngine(); bb = BlindBaziEngine(be); by = BlindYingqiEngine(be)
jd = BlindJudgmentEngine(); th = BlindThemeEngine()

cases = json.load(open('D:/shuntian/.tmp_cases/blind_cases_engine_output.json', encoding='utf-8'))
VALID = {'ESTABLISHED', 'CANDIDATE', 'UNDETERMINED', 'NOT_APPLICABLE'}

errs = []; themes_seen = {}
for c in cases:
    key = c.get('birth') or (c.get('year'), c.get('month'), c.get('day'), c.get('hour'))
    if isinstance(key, list): key = tuple(key)
    gender = c.get('gender', 'male')
    try:
        ch = be.compute(key, gender=gender)
        br = bb.compute(key, gender=gender)
        yr = by.analyze(key, gender=gender, target_age=46)
        jr = jd.judge(ch, br, yr)
        res = th.aggregate(ch, br, yr, jr).to_dict()
        ids = [t['theme_id'] for t in res['themes']]
        states = [t['state'] for t in res['themes']]
        if len(ids) != 12:
            errs.append(f"{key}: 主题数={len(ids)}")
        for t in res['themes']:
            if t['state'] not in VALID:
                errs.append(f"{key} {t['theme_id']}: 非法枚举 {t['state']}")
            for e in t['entries']:
                if not e['source'] or not e['value']:
                    errs.append(f"{key} {t['theme_id']}: 空条目")
            themes_seen.setdefault(t['theme_id'], 0)
            themes_seen[t['theme_id']] += 1
    except Exception as ex:
        errs.append(f"{key}: 异常 {ex}")

print('案例数:', len(cases))
print('12主题覆盖:', sorted(themes_seen.keys()))
print('主题缺失:', [tid for tid, _ in THEME_DEFS if tid not in themes_seen])
print('错误数:', len(errs))
for e in errs[:30]:
    print(' -', e)
print('PASS' if not errs else 'FAIL')
