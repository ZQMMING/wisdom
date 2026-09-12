# -*- coding: utf-8 -*-
"""盲派四柱案例 → 年柱锁年份 → 遍历候选年 → 批量 12 主题验证。"""
import sys, re
sys.path.insert(0, 'D:/shuntian')
sys.stdout.reconfigure(encoding='utf-8')

from src.tongshu.engines.bazi_engine import BaziEngine, pillar_to_chinese
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
from src.tongshu.engines.blind_yingqi import BlindYingqiEngine
from src.tongshu.engines.blind_judgment import BlindJudgmentEngine
from src.tongshu.engines.blind_themes import BlindThemeEngine, THEME_DEFS

STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"

# 年柱干支 → 候选年份（1930-2005）
def year_candidates(y_pillar):
    s, b = y_pillar[0], y_pillar[1]
    si, bi = STEMS.index(s), BRANCHES.index(b)
    # 干支序号 n = si = bi (mod 2 同奇偶)
    # 1900 年是庚子 (6,0): n = 6? 1900 庚子 = 干支序号 36 (0-based, 甲子=0)。庚=6, 子=0 → n=36
    # 通用: 找最小 n in [0,59] 使 n%10=si 且 n%12=bi
    n = None
    for k in range(60):
        if k % 10 == si and k % 12 == bi:
            n = k
            break
    # 1900-01-31 为庚子年（近似：立春分界忽略，用日历年匹配）
    # 干支年 n 对应公历年: year = 1900 + (n - 36) mod 60
    out = []
    for y in range(1930, 2006):
        if (y - 1900) % 60 == (n - 36) % 60:
            out.append(y)
    # 立春分界：公历年初出生年柱属上一年 → 补前后各1年候选
    ext = set(out)
    for y in out:
        ext.add(y - 1)
        ext.add(y + 1)
    return sorted(y for y in ext if 1930 <= y <= 2005)

# 时支 → 代表小时（子=0 避免晚子换日）
HOUR_MAP = {'子': 0, '丑': 1, '寅': 3, '卯': 5, '辰': 7, '巳': 9,
            '午': 11, '未': 13, '申': 15, '酉': 17, '戌': 19, '亥': 21}

def reverse_lookup(be, pillars):
    y_pillar, m_pillar, d_pillar, h_pillar = pillars
    hour = HOUR_MAP[h_pillar[1]]
    for y in year_candidates(y_pillar):
        for mo in range(1, 13):
            last = 31 if mo in (1, 3, 5, 7, 8, 10, 12) else (30 if mo != 2 else (29 if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0 else 28))
            for d in range(1, last + 1):
                try:
                    ch = be.compute((y, mo, d, hour), gender='male')
                    if (pillar_to_chinese(ch.year_pillar), pillar_to_chinese(ch.month_pillar),
                            pillar_to_chinese(ch.day_pillar), pillar_to_chinese(ch.hour_pillar)) == pillars:
                        return (y, mo, d, hour)
                except Exception:
                    pass
    return None

text = ''
for p in ['D:/顺天系统资料/盲派命理-案例资料集.md',
          'D:/顺天系统资料/盲派命理-个人案例详解集.md']:
    with open(p, encoding='utf-8') as f:
        text += f.read() + '\n'

pat = re.compile(r'(?P<gender>乾|坤)(?:造)?[:：]?\s*(?P<y>[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s*(?P<m>[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s*(?P<d>[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s*(?P<h>[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])')
cases, seen = [], set()
for mm in pat.finditer(text):
    key = (mm.group('y'), mm.group('m'), mm.group('d'), mm.group('h'))
    if key in seen:
        continue
    seen.add(key)
    cases.append({'pillars': key, 'gender': 'male' if mm.group('gender') == '乾' else 'female'})
    if len(cases) >= 60:
        break
print('四柱案例数:', len(cases))

be = BaziEngine()
bb = BlindBaziEngine(be); by = BlindYingqiEngine(be)
jd = BlindJudgmentEngine(); th = BlindThemeEngine()
VALID = {'ESTABLISHED', 'CANDIDATE', 'UNDETERMINED', 'NOT_APPLICABLE'}

errs, themes_seen, state_dist, matched = [], {}, {}, 0
for c in cases:
    key = reverse_lookup(be, c['pillars'])
    if key is None:
        errs.append(f"{c['pillars']}: 反推失败")
        continue
    matched += 1
    gender = c['gender']
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

print('反推匹配数:', matched, '/', len(cases))
print('12主题覆盖:', sorted(themes_seen.keys()))
print('主题缺失:', [tid for tid, _, _ in THEME_DEFS if tid not in themes_seen])
print('状态分布:')
for tid, _, _ in THEME_DEFS:
    print(' ', tid, state_dist.get(tid, {}))
print('错误数:', len(errs))
for e in errs[:30]:
    print(' -', e)
print('PASS' if not errs else 'FAIL')
