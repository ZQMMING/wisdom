# -*- coding: utf-8 -*-
"""從殺/曲直/炎上 三格判定函数"""
import sys
sys.path.insert(0, r'engines\common')
from gc002_builder import paipan, HIDDEN

ELEM = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土',
        '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
GAN = '甲乙丙丁戊己庚辛壬癸'
BENQI = {k: v[0] for k, v in HIDDEN.items()}
gen = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}


def ten_lists(day):
    de = ELEM[day]
    me_ke = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '木'}[de]
    yang_day = GAN.index(day) % 2 == 0
    def li(elem, same):
        return [s for s in GAN if ELEM[s] == elem and (GAN.index(s) % 2 == 0) == same]
    return {'sha': li(me_ke, yang_day), 'guan': li(me_ke, not yang_day),
            'shi_shang': [s for s in GAN if ELEM[s] == gen[de]], 'sha_elem': me_ke}


def cong_sha_rule(c):
    """從殺格 SFTK-012-002 A"""
    day = c['dm']; stems = c['stems']; br = c['br']
    tl = ten_lists(day)
    de = ELEM[day]
    yin = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}[de]
    rootless = all(ELEM[h] != de for b in br for h in HIDDEN[b])
    no_fu = all(ELEM[s] not in (de, yin) for s in stems)
    benqi = BENQI[c['month']]
    sha_dang = benqi in tl['sha'] or benqi in tl['guan']
    no_shang = not any(s in tl['shi_shang'] for s in stems)
    sha_root = any(ELEM[h] == tl['sha_elem'] for b in br for h in HIDDEN[b])
    mixed = any(s in tl['guan'] for s in stems) and any(s in tl['sha'] for s in stems)
    if rootless and no_fu and sha_dang and no_shang and sha_root:
        ctx = '官杀混杂(官留杀从杀论)' if mixed else '纯杀从杀'
        return {'pattern_state': 'DETERMINED(從殺格)', 'pattern_success_state': 'SUCCESS(棄命從殺)',
                'condition_context': f'日主无根无食制，官杀成势；{ctx}',
                'evidence': ['SFTK-012-002'], 'note': '從殺成：舍命從殺；忌根運制殺運'}
    return None


def quzhi_rule(c):
    """曲直格 YHZP-101-010 A：甲乙日+木局/木方+不见庚辛"""
    day = c['dm']; stems = c['stems']; br_set = set(c['br'])
    if ELEM[day] != '木':
        return None
    sanhe = all(x in br_set for x in ['亥', '卯', '未'])
    sanhui = all(x in br_set for x in ['寅', '卯', '辰'])
    no_gengxin = not any(s in ('庚', '辛') for s in stems)
    if (sanhe or sanhui) and no_gengxin:
        return {'pattern_state': 'DETERMINED(曲直格)', 'pattern_success_state': 'SUCCESS(木局從木)',
                'condition_context': '甲乙日木局/木方全，不见庚辛',
                'evidence': ['YHZP-101-010'], 'note': '曲直成：從木運；忌西方金運'}
    return None


def yan_shang_rule(c):
    """炎上格 YHZP-101-006 A：丙丁日+火局/火方"""
    day = c['dm']; br_set = set(c['br'])
    if ELEM[day] != '火':
        return None
    sanhe = all(x in br_set for x in ['寅', '午', '戌'])
    sanhui = all(x in br_set for x in ['巳', '午', '未'])
    if sanhe or sanhui:
        return {'pattern_state': 'DETERMINED(炎上格)', 'pattern_success_state': 'SUCCESS(火局從火)',
                'condition_context': '丙丁日火局/火方全',
                'evidence': ['YHZP-101-006'], 'note': '炎上成：從火運；忌水鄉金地'}
    return None


if __name__ == '__main__':
    cases = [
        ('GC-009 從殺', 1983, 12, 0, cong_sha_rule),
        ('GC-010 曲直', 1985, 7, 22, quzhi_rule),
        ('GC-011 炎上', 1989, 2, 14, yan_shang_rule),
    ]
    for name, y, m, h, rule in cases:
        p = paipan(y, m, 15, h)
        c = {'dm': p['day_master'], 'stems': [p['stems']['年'], p['stems']['月'], p['stems']['时']],
             'br': list(p['branches'].values()), 'month': p['month_order']}
        r = rule(c)
        print(f'{name}: {p["pillars"]} 日主={p["day_master"]}')
        print(f'  → {r}')
