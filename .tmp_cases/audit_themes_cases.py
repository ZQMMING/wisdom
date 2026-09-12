# -*- coding: utf-8 -*-
"""从盲派案例库提取带生辰案例，批量跑 12 主题。"""
import sys, re, json
sys.path.insert(0, 'D:/shuntian')
sys.stdout.reconfigure(encoding='utf-8')
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
from src.tongshu.engines.blind_yingqi import BlindYingqiEngine
from src.tongshu.engines.blind_judgment import BlindJudgmentEngine
from src.tongshu.engines.blind_themes import BlindThemeEngine, THEME_DEFS

# 读取案例库
text = ''
for p in ['D:/顺天系统资料/盲派命理-案例资料集.md',
          'D:/顺天系统资料/盲派命理-个人案例详解集.md']:
    with open(p, encoding='utf-8') as f:
        text += f.read() + '\n'

# 提取公历日期 + 时辰 + 性别
pat = re.compile(r'(?P<gender>乾|坤|男|女)[^0-9\n]{0,20}?公历\s*(?P<y>19\d{2}|20\d{2})[年/\-\.](?P<m>\d{1,2})[月/\-\.](?P<d>\d{1,2})日?\s*(?P<h>\d{1,2})[：:点时]', re.S)
cases = []
seen = set()
for m in pat.finditer(text):
    g = m.group('gender')
    gen = 'male' if g in ('乾', '男') else 'female'
    key = (int(m.group('y')), int(m.group('m')), int(m.group('d')), int(m.group('h')))
    if key in seen:
        continue
    seen.add(key)
    cases.append({'birth': key, 'gender': gen})
    if len(cases) >= 60:
        break

print('提取案例数:', len(cases))

be = BaziEngine(); bb = BlindBaziEngine(be); by = BlindYingqiEngine(be)
jd = BlindJudgmentEngine(); th = BlindThemeEngine()
VALID = {'ESTABLISHED', 'CANDIDATE', 'UNDETERMINED', 'NOT_APPLICABLE'}

errs = []; themes_seen = {}; state_dist = {}
for c in cases:
    key = c['birth']; gender = c['gender']
    try:
        ch = be.compute(key, gender=gender)
        br = bb.compute(key, gender=gender)
        yr = by.analyze(key, gender=gender, target_age=46)
        jr = jd.judge(ch, br, yr)
        res = th.aggregate(ch, br, yr, jr).to_dict()
        ids = [t['theme_id'] for t in res['themes']]
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
            state_dist.setdefault(t['theme_id'], {})
            state_dist[t['theme_id']][t['state']] = state_dist[t['theme_id']].get(t['state'], 0) + 1
    except Exception as ex:
        errs.append(f"{key}: 异常 {type(ex).__name__}: {ex}")

print('12主题覆盖:', sorted(themes_seen.keys()))
print('主题缺失:', [tid for tid, _, _ in THEME_DEFS if tid not in themes_seen])
print('状态分布:')
for tid, _, _ in THEME_DEFS:
    print(' ', tid, state_dist.get(tid, {}))
print('错误数:', len(errs))
for e in errs[:30]:
    print(' -', e)
print('PASS' if not errs else 'FAIL')
