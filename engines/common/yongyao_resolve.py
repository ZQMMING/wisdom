# -*- coding: utf-8 -*-
"""用药裁决层 (yongyao_resolve) —— "算→辩→解"之"解".
辩层定主病, 本层按【离散图三边: 制/化/帮】列全药方, 并做友敌安全检查.

三边(全为五行确定性关系):
- 制: 克病五行者 KE_BACK[bw]          (如 食伤制杀/财破印/官杀制比劫)
- 化: 病五行所生 SHENG[bw] (泄病之气) (如 印化杀生身); 反生杀克身则剔除
- 帮: 比劫 dm + 印 SHENG_BACK[dm] 帮身 (如 比劫帮身/印生身); 是病则剔除

安全检查(布尔):
- 药==病五行, 或 药生病五行(帮病) → 剔除
- 化: 药克日主(化财生杀/化食伤生财反耗) → 剔除或降级
- 水泛木浮(bw水)特殊: 加火暖化寒湿 (DTS QI_HOU.008)

只裁决用药方向, 不判吉凶寿夭.
"""
from typing import Any, Dict, List

GAN_WX = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
          '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
SHENG_BACK = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}
KE_BACK = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
WX_GAN = {'木': ('甲', '乙'), '火': ('丙', '丁'), '土': ('戊', '己'),
          '金': ('庚', '辛'), '水': ('壬', '癸')}
ZHI_BEN_WX = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
              '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金',
              '戌': '土', '亥': '水'}


def _is_enemy_to_dm(wx: str, dm: str) -> bool:
    """药五行是否克/泄/耗日主(弱日主不宜): 克日主=官杀, 日主生=食伤, 日主克=财."""
    return KE_BACK.get(dm) == wx or SHENG.get(dm) == wx or KE.get(dm) == wx


def _safe(wx: str, bw: str) -> bool:
    """药是否帮病: 同病 或 生病."""
    if not wx or wx == bw:
        return False
    if SHENG.get(wx) == bw:      # wx 生 bw
        return False
    return True


def resolve_yongyao(facts: Dict[str, Any], debate: Dict[str, Any],
                    climate: Dict[str, Any] = None) -> Dict[str, Any]:
    primary = debate.get('primary_bing') or {}
    bw = primary.get('bing_wx', '')
    bid = primary.get('bing_id', '')
    _sec_wx = {s2.get('bing_wx') for s2 in (debate.get('secondary_bing') or []) if s2.get('bing_wx')}
    dm = GAN_WX.get(facts.get('day_stem', ''), '')
    _pl = facts.get('pillars')
    dm_ben = sum(1 for pos in ('year', 'month', 'day', 'hour')
                 if _pl and ZHI_BEN_WX.get(_pl[pos][1]) == dm) if _pl else 0

    rejected_climate = []
    if climate:
        for c in climate.get('climate_candidates', []):
            stem = c.get('stem', '')
            cwx = GAN_WX.get(stem, '')
            reason = None
            if cwx == bw:
                reason = '与主病同五行(%s), 用之添病' % bw
            elif SHENG_BACK.get(bw) == cwx:
                reason = '%s生%s(病), 为病之源' % (cwx, bw)
            if reason:
                rejected_climate.append({'stem': stem, 'wuxing': cwx, 'reason': reason})

    if not bw:
        return {'layer': 'YONGYAO_RESOLVE', 'state': 'NO_BING',
                'primary_medicine': None, 'auxiliary_medicine': [],
                'ji_shen': [], 'rejected_climate': rejected_climate,
                'boundary_note': '无主病, 不裁决用药'}

    edges = []   # 每条: 五行/gan/边类型/功能/是否采纳/剔除理由

    def add(wx, kind, func):
        gan = list(WX_GAN.get(wx, ()))
        ok = _safe(wx, bw)
        note = ''
        if not ok:
            note = '帮病(同病或生病), 剔除'
        elif wx in _sec_wx or SHENG.get(wx, '') in _sec_wx:
            ok = False
            _hit = sorted(x for x in (wx, SHENG.get(wx, '')) if x in _sec_wx)
            note = '帮次病(%s), 剔除' % '/'.join(_hit)
        elif kind == '化' and KE_BACK.get(dm) == wx:
            ok = False
            note = '化反克日主(生杀), 剔除'
        elif kind == '化' and KE.get(dm) == wx and dm_ben == 0:
            ok = False
            note = '化财而日主无本气根, 任不起财反成财多身弱, 剔除'
        edges.append({'wuxing': wx, 'gan': gan, 'kind': kind,
                      'function': func, 'accepted': ok, 'reject_reason': note})

    # 制
    add(KE_BACK.get(bw, ''), '制', '克病(%s)' % bw)
    # 化 (病所生, 泄病)
    add(SHENG.get(bw, ''), '化', '泄病之气(%s生? )' % bw)
    # 帮 (比劫 + 印)
    add(dm, '帮', '比劫帮身')
    add(SHENG_BACK.get(dm, ''), '帮', '印生身')
    # 水泛木浮特殊: 火暖化
    if bw == '水':
        add('火', '暖', '丙丁暖化寒湿')

    accepted = [e for e in edges if e['accepted']]
    # 去重(同五行保留kind最优: 制>化>帮/暖)
    seen = {}
    for e in accepted:
        if e['wuxing'] not in seen:
            seen[e['wuxing']] = e
    uniq = list(seen.values())

    # 药受制检查: 采纳药的天干是否被天干五合合绊(合而不化)
    th = facts.get('tian_he') or {}
    _pairs = th.get('he_pairs', [])

    def _gan_positions(wx):
        out = []
        if _pl:
            for pos in ('year', 'month', 'hour'):
                g = _pl[pos][0]
                if GAN_WX.get(g) == wx:
                    out.append((pos, g))
        return out

    medicine_blocked = []
    for e in uniq:
        for pos, g in _gan_positions(e['wuxing']):
            for pair in _pairs:
                if g in pair['stems']:
                    other = pair['stems'][0] if pair['stems'][1] == g else pair['stems'][1]
                    if pair['huashen_on_month_qi'] or th.get('has_long_chen'):
                        medicine_blocked.append({'wuxing': e['wuxing'], 'gan': g, 'pos': pos,
                            'with': other, 'state': '合而化', 'huashen': pair['huashen_wuxing'],
                            'note': '与%s合化%s, 不简单作绊' % (other, pair['huashen_wuxing'])})
                    else:
                        medicine_blocked.append({'wuxing': e['wuxing'], 'gan': g, 'pos': pos,
                            'with': other, 'state': '合绊(合而不化)', 'huashen': pair['huashen_wuxing'],
                            'note': '药%s被%s合绊, 制病力失; 需岁运解合, 或改取印化/比劫帮' % (g, other)})

    zhu = next((e for e in uniq if e['kind'] == '制'), None)
    if zhu is None and uniq:
        zhu = uniq[0]
    fu = [e for e in uniq if e is not zhu]

    ji = [bw]
    sb = SHENG_BACK.get(bw, '')
    if sb:
        ji.append(sb)

    primary_medicine = None
    if zhu:
        _zb = [b for b in medicine_blocked if b['wuxing'] == zhu['wuxing']
               and b['state'].startswith('合绊')]
        primary_medicine = {'wuxing': zhu['wuxing'], 'gan': zhu['gan'],
                            'function': zhu['function'], 'kind': '制',
                            'classic': '五行相克为基础关系; DTS FAN_JU.001',
                            'blocked': _zb[0] if _zb else None}
    aux = [{'wuxing': e['wuxing'], 'gan': e['gan'], 'kind': e['kind'],
            'function': e['function'],
            'classic': 'DTS QI_HOU.008 丙丁暖化/化杀生身为原典通例' if e['kind'] in ('暖',)
            else '原典病药通例(化/帮)'} for e in fu]

    return {
        'layer': 'YONGYAO_RESOLVE', 'state': 'YONGYAO_RESOLVED',
        'primary_bing': {'bing_id': bid, 'wuxing': bw},
        'primary_medicine': primary_medicine,
        'auxiliary_medicine': aux,
        'all_edges': edges,
        'medicine_blocked': medicine_blocked,
        'ji_shen': ji,
        'rejected_climate': rejected_climate,
        'rule': '制=克病; 化=泄病(克身则剔); 帮=比劫印帮身(是病则剔); 水泛加火暖',
        'boundary_note': '离散三边全列按主辅; 只裁用药方向不判吉凶; 化/帮为原典通例, 须看命局分寸',
        'evidence_refs': ['DTS PATHOLOGY_QI_HOU.008', 'DTS FAN_JU.001'],
    }
