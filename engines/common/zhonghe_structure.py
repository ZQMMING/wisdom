# -*- coding: utf-8 -*-
"""全局中和 / 生化有情结构层 · task#48

"中和"在此是全局五行流通、生化有情、不偏枯、无战克的结构, 与七档"日主单端力量中和"是两个维度:
  - 七档中和 = 日主一端 ratio 中段;
  - 全局中和 = 五行齐备、五环相生链以"真有气"循环流通、日主有印比真根能受生、无克泄成势偏枯、
    天干无硬战克; 日主虽弱(单端 ratio 低)亦可全局中和纯粹
    (丙子庚寅辛巳戊子: 辛金寅月囚而财官印食循环、戊印透通根、庚劫扶、木嫩火虚, 端比仅0.10仍中和纯粹)。

必要结构(全部满足才 CANDIDATE):
  1. 五行(印/比劫/食伤/财/官杀)全出现有气(透干/本气根/成局);
  2. 五环相生链全通, 环上两神均"真有气"(本气根/成局/透干通根); 天干虚透截脚、地支无根者不任流通;
  3. 日主有真托: 本气根>=1, 或印透干通根, 或印本气根>=2; 虚浮孤印不算;
  4. 非已成偏格(专旺/从格/化气/母多灭子);
  5. 无克泄端成势偏枯: 食伤/财/官杀任一成三合三会局而日主端本气压不住;
  6. 天干无硬战克: 枭神夺食(偏印+食神同透)、伤官见官(伤官+正官同透)为原典明定之病。

中和之"和"非日主端与克泄端力量相等(端比重仅信息输出 #PCT-MARK, 不作否决);
一端独旺而克泄虚浮无根者, 虚浮之神不任流通, 自然在第2条断环。

边界: 只出 CANDIDATE; 纯粹/精神两足/富贵含审美成败不判; 不出用神/吉凶/STRONG/WEAK;
通关/合去/冲拔/贪合忘克等精细作用交 ACTIVITY 层; 不接 production_entry。

原典: 滴天髓·中和"既识中和之正理, 而于五行之妙, 有全能焉"; 流通"何处起根源, 流到何方住";
任注丙子庚寅"劫印相扶, 中和纯粹, 精神两足...日元足以用官";
反例甲子戊辰庚申壬午(申子辰水局、枭神夺食、官星伤、甲木假神)、庚寅壬午戊午丁巳(壬财虚透无根不能流至金)。
"""
from typing import Any, Dict, List


def _youqi(d):
    return int(d.get('stem_n', 0)) >= 1 or int(d.get('ben_n', 0)) >= 1 or int(d.get('ju_n', 0)) >= 1


def _zhenqi(d):
    if int(d.get('ben_n', 0)) >= 1 or int(d.get('ju_n', 0)) >= 1:
        return True
    if int(d.get('stem_n', 0)) >= 1 and (
            int(d.get('ben_n', 0)) + int(d.get('zhong_n', 0)) + int(d.get('yu_n', 0))) >= 1:
        return True
    return False


def build_zhonghe_structure(pillars, facts, wp, special=None):
    dm_wx = (wp or {}).get('daymaster_element')
    pw = (wp or {}).get('wuxing_power', {})
    out = {
        'module': 'ZHONGHE_STRUCTURE', 'patch': 'P160-ZHONGHE-STRUCT',
        'namespace': 'zhonghe.structure', 'daymaster_element': dm_wx,
        'wuxing_present': {}, 'shishen_wuxing': {},
        'circulation': {'links_passed': 0, 'chain': [], 'detail': {}},
        'tiangan_zhanke': [], 'duan_bi_ratio': None,
        'zhonghe_candidate': False, 'zhonghe_state': None, 'reject_reasons': [],
        'judgment_status': 'ZHONGHE_STRUCTURE_ONLY',
        'boundary_note': (
            '全局五行齐备+五环真有气流通+印比真根+无克泄成势偏枯/天干硬战克的中和纯粹结构候选(CANDIDATE); '
            '与七档日主单端中和相互独立(日主弱亦可全局中和, 端比重不作否决); 不判纯粹程度/格局高低/用神/吉凶/身强弱; '
            '专旺/从格/化气/母灭为偏格不标; 虚透截脚不任流通; 不接 production_entry'),
    }
    if not dm_wx or dm_wx not in pw:
        out['judgment_status'] = 'INSUFFICIENT_INPUT'
        return out

    from engines.common.wuxing_power import SHENG, SHENG_ME, KE, KE_ME, BRANCH_WX
    yin_wx, bi_wx, ss_wx, cai_wx, gs_wx = SHENG_ME[dm_wx], dm_wx, SHENG[dm_wx], KE[dm_wx], KE_ME[dm_wx]
    roles = {'官杀': gs_wx, '印': yin_wx, '比劫': bi_wx, '食伤': ss_wx, '财': cai_wx}
    out['shishen_wuxing'] = roles
    for role, wx in roles.items():
        d = pw.get(wx, {})
        out['wuxing_present'][role] = {
            'wuxing': wx, 'present_youqi': _youqi(d), 'zhenqi': _zhenqi(d),
            'stem_n': int(d.get('stem_n', 0)), 'ben_n': int(d.get('ben_n', 0)),
            'zhong_n': int(d.get('zhong_n', 0)), 'yu_n': int(d.get('yu_n', 0)),
            'ju_n': int(d.get('ju_n', 0)), 'ling_state': d.get('ling_state')}

    chain = [('官杀→印', gs_wx, yin_wx), ('印→身', yin_wx, bi_wx),
             ('身→食伤', bi_wx, ss_wx), ('食伤→财', ss_wx, cai_wx),
             ('财→官杀', cai_wx, gs_wx)]
    passed = 0
    for name, a, b in chain:
        ok = _zhenqi(pw.get(a, {})) and (b == dm_wx or _zhenqi(pw.get(b, {})))
        out['circulation']['detail'][name] = bool(ok)
        out['circulation']['chain'].append({'link': name, 'from': a, 'to': b, 'passed': bool(ok)})
        if ok:
            passed += 1
    out['circulation']['links_passed'] = passed

    stem_tg = {m.get('ten_god') for m in (facts or {}).get('ten_god_members', []) if m.get('type') == 'stem'}
    if '偏印' in stem_tg and '食神' in stem_tg:
        out['tiangan_zhanke'].append('枭神夺食(偏印与食神同透)')
    if '伤官' in stem_tg and '正官' in stem_tg:
        out['tiangan_zhanke'].append('伤官见官(伤官与正官同透)')

    def _tot(wx):
        return float(pw.get(wx, {}).get('total', 0) or 0)
    me_t = _tot(dm_wx) + _tot(yin_wx)
    opp_t = _tot(ss_wx) + _tot(cai_wx) + _tot(gs_wx)
    if me_t + opp_t > 0:
        out['duan_bi_ratio'] = round(me_t / (me_t + opp_t), 3)  # PCT-MARK 仅信息

    dm_d, yin_d = pw.get(dm_wx, {}), pw.get(yin_wx, {})
    reasons = []
    if not all(v['present_youqi'] for v in out['wuxing_present'].values()):
        reasons.append('五行(印比食财官)未全出现有气')
    if passed < 5:
        weak = [c['link'] for c in out['circulation']['chain'] if not c['passed']]
        reasons.append('相生五环未以真有气全通(通过%d/5, 断环:%s)' % (passed, '、'.join(weak)))
    yin_root = int(yin_d.get('ben_n', 0)) + int(yin_d.get('zhong_n', 0)) + int(yin_d.get('yu_n', 0))
    yin_tou_gen = int(yin_d.get('stem_n', 0)) >= 1 and yin_root >= 1
    if not (int(dm_d.get('ben_n', 0)) >= 1 or yin_tou_gen or int(yin_d.get('ben_n', 0)) >= 2):
        reasons.append('日主无本气根、印非透干通根且本气不成气(虚浮不受生)')
    if special and (special.get('cong_type') or special.get('zhuanwang')
                    or special.get('hua_qi') or special.get('mu_mie')):
        reasons.append('已成从格/专旺/化气/母灭偏格')
    me_ben = int(dm_d.get('ben_n', 0)) + int(yin_d.get('ben_n', 0))
    for role in ('食伤', '财', '官杀'):
        d = out['wuxing_present'][role]
        if d['ju_n'] >= 1 and d['ben_n'] > me_ben:
            reasons.append('%s成三合三会势而日主端本气压不住(成势偏枯)' % role)
            break
    # 紧邻六冲(年月/月日/日时)冲及日主本气禄/根 = 破禄争战, 非中和; 隔位力轻/合解/冲非本气不论
    pidx = ('year', 'month', 'day', 'hour')
    b2idx = {}
    for _i, _k in enumerate(pidx):
        b2idx.setdefault(pillars[_k][1], []).append(_i)
    for _pair in (facts or {}).get('combination_facts', {}).get('liuchong', []):
        _b1, _b2 = _pair[0], _pair[1]
        _hit = False
        for _i1 in b2idx.get(_b1, []):
            for _i2 in b2idx.get(_b2, []):
                if abs(_i1 - _i2) == 1 and (BRANCH_WX.get(_b1) == dm_wx or BRANCH_WX.get(_b2) == dm_wx):
                    _hit = True
        if _hit:
            reasons.append('紧邻六冲冲及日主本气禄/根(%s%s冲), 破禄争战非中和' % (_b1, _b2))
            break
    if out['tiangan_zhanke']:
        reasons.append('天干硬战克: ' + '、'.join(out['tiangan_zhanke']))

    out['reject_reasons'] = reasons
    if not reasons:
        out['zhonghe_candidate'] = True
        out['zhonghe_state'] = 'CANDIDATE'
    return out
