# -*- coding: utf-8 -*-
"""PATCH-138 PZZQ Producer v1
消费L0 facts -> 月令入口 -> pattern_candidates. 不判成格/破格/用神.
"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import ten_god

# 十神 -> 格局类型名(事实映射, 非吉凶)
TEN_GOD_TO_PATTERN = {
    '正官': '正官', '七杀': '七杀', '正财': '正财', '偏财': '偏财',
    '正印': '正印', '偏印': '偏印', '食神': '食神', '伤官': '伤官',
    '比肩': '建禄', '劫财': '月劫',
}


def produce_pattern_candidates(facts):
    dg = facts['day_stem']
    out = {'status': 'PRODUCED', 'pattern_candidates': [], 'source': []}
    mhs = facts['month_hidden_stems']
    transparent = facts['month_transparent']

    chosen = []
    if transparent:
        for s in transparent:
            tg = ten_god(dg, s)
            chosen.append((s, tg, 'transparent'))
        out['source'].append('month_transparent')
    else:
        # 不透: 取月令本气(藏干首位)
        s = mhs[0]
        tg = ten_god(dg, s)
        chosen.append((s, tg, 'month_benqi'))
        out['source'].append('month_benqi')

    for s, tg, how in chosen:
        out['pattern_candidates'].append({
            'pattern_type': TEN_GOD_TO_PATTERN.get(tg, tg),
            'ten_god': tg,
            'month_stem': s,
            'basis': how,
            'status': 'CANDIDATE',
        })
    return out


if __name__ == '__main__':
    import io, json
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    from engines.common.l0_fact_builder import build
    gc001 = {'year': ['癸','亥'], 'month': ['壬','戌'], 'day': ['乙','未'], 'hour': ['壬','午']}
    facts = build(gc001)
    print('GC-001 pattern_candidates:', json.dumps(produce_pattern_candidates(facts), ensure_ascii=False))
    # 乙日酉月透辛 -> 七杀候选
    f2 = {'year': ['甲','子'], 'month': ['辛','酉'], 'day': ['乙','卯'], 'hour': ['丁','亥']}
    print('乙酉透辛:', json.dumps(produce_pattern_candidates(build(f2)), ensure_ascii=False))
