# -*- coding: utf-8 -*-
"""PATCH-178 运x原局结构 Relation (纯结构事实, 不判喜忌/吉凶/成格/用神)

输入: yun={'decade':[干,支],'year':[干,支]}; pillars 四柱
输出: 关系列表, 每条带 provenance。Relation Fact ≠ 作用成立 ≠ 成格 ≠ 喜忌吉凶。
"""
HIDDEN = __import__('json').load(
    open(__import__('pathlib').Path(__file__).resolve().parents[2]/'registries/zhi_hidden_stems_v1.json', encoding='utf-8'))['hidden_stems']

LIUHE = {'子':'丑','丑':'子','寅':'亥','亥':'寅','卯':'戌','戌':'卯','辰':'酉','酉':'辰','巳':'申','申':'巳','午':'未','未':'午'}
LIUCHONG = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅','卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}
WUHE = {frozenset(['甲','己']):'甲己合', frozenset(['乙','庚']):'乙庚合', frozenset(['丙','辛']):'丙辛合',
        frozenset(['丁','壬']):'丁壬合', frozenset(['戊','癸']):'戊癸合'}
SANHE = [{'p':['申','子','辰'],'n':'申子辰水局'},{'p':['寅','午','戌'],'n':'寅午戌火局'},
         {'p':['巳','酉','丑'],'n':'巳酉丑金局'},{'p':['亥','卯','未'],'n':'亥卯未木局'}]
SANHUI = [{'p':['寅','卯','辰'],'n':'寅卯辰东方木'},{'p':['巳','午','未'],'n':'巳午未南方火'},
          {'p':['申','酉','戌'],'n':'申酉戌西方金'},{'p':['亥','子','丑'],'n':'亥子丑北方水'}]

PILLAR_POS = ['year','month','day','hour']


def _record(yun_type, yun_stem, yun_branch, rel_type, natal_pillar, detail):
    return {'yun_type': yun_type, 'yun_stem': yun_stem, 'yun_branch': yun_branch,
            'relation': rel_type, 'natal_pillar': natal_pillar, **detail}


def yun_natal_relations(yun, pillars):
    """yun: {'decade':[干,支],'year':[干,支]} (可缺)。返回结构关系列表。"""
    out = []
    nat_stems = {k: pillars[k][0] for k in PILLAR_POS}
    nat_branches = {k: pillars[k][1] for k in PILLAR_POS}
    for ytype, yv in (yun or {}).items():
        if not yv or len(yv) < 2:
            continue
        ystem, ybranch = yv[0], yv[1]
        # 1. 运干 x 命局天干: 五合
        for pos, nst in nat_stems.items():
            key = frozenset([ystem, nst])
            if key in WUHE:
                out.append(_record(ytype, ystem, ybranch, '天干五合', pos,
                                   {'stems': [ystem, nst], 'he': WUHE[key]}))
        # 2. 运支 x 命局地支: 六合/六冲
        for pos, nbr in nat_branches.items():
            if LIUHE.get(ybranch) == nbr:
                out.append(_record(ytype, ystem, ybranch, '地支六合', pos, {'branches': [ybranch, nbr]}))
            if LIUCHONG.get(ybranch) == nbr:
                out.append(_record(ytype, ystem, ybranch, '地支六冲', pos, {'branches': [ybranch, nbr], 'position': pos}))
        # 3. 运支参与 三合/三会 (运支 + 命局支集合)
        nat_zset = set(nat_branches.values())
        for s in SANHE:
            if ybranch in s['p'] and set(s['p']) - {ybranch} <= nat_zset:
                out.append(_record(ytype, ystem, ybranch, '三合', None,
                                   {'branches': s['p'], 'group': s['n'], 'note': '运支参与候选, 非成格'}))
        for s in SANHUI:
            if ybranch in s['p'] and set(s['p']) - {ybranch} <= nat_zset:
                out.append(_record(ytype, ystem, ybranch, '三会', None,
                                   {'branches': s['p'], 'group': s['n']}))
        # 4. 运干透命局藏干 (透清)
        for pos, nbr in nat_branches.items():
            if ystem in HIDDEN[nbr]:
                out.append(_record(ytype, ystem, ybranch, '透清', pos,
                                   {'stem': ystem, 'branch': nbr, 'note': '运干透命局藏干, 非用神成立'}))
    return out
