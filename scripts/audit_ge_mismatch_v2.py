# -*- coding: utf-8 -*-
"""引擎格局判定 vs 原文自述格局 错配率统计"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')

# 复用dayun_align的排盘和引擎调用
from scripts.dayun_align import cases, pai_pan, get_wangshuai, get_qiangruo

# 原文关键词 → 格局类别
TEXT_TO_GE = {
    '从势': '从格', '从财': '从格', '从杀': '从格', '从官': '从格',
    '从儿': '从格', '弃命从': '从格', '顺其气势': '从格', '顺其性': '从格',
    '曲直': '专旺格', '炎上': '专旺格', '稼穑': '专旺格', '从革': '专旺格',
    '润下': '专旺格', '一行得气': '专旺格', '专旺': '专旺格',
    '化气': '化气格', '化木': '化气格', '化火': '化气格', '化土': '化气格',
    '化金': '化气格', '化水': '化气格', '化出': '化气格',
    '二人同心': '两神成象', '两神成象': '两神成象', '两气成象': '两神成象',
}

def engine_ge_to_category(special_name):
    if not special_name:
        return None
    if any(x in special_name for x in ['从财格', '从杀格', '从官格', '从儿格', '从势格']):
        return '从格'
    if any(x in special_name for x in ['曲直格', '炎上格', '稼穑格', '从革格', '润下格']):
        return '专旺格'
    if '化' in special_name and '气格' in special_name:
        return '化气格'
    if '两气成象' in special_name:
        return '两神成象'
    if '正格' in special_name:
        return '正格'
    return None

stats = {
    'total': 0,
    'text_has_ge': 0,
    'consistent': 0,
    'mismatch': 0,
    'missed': 0,
    'by_type': {},
    'mismatch_list': [],
    'missed_list': [],
}

for li, fp, dy, txt in cases:
    if len(dy) < 4:
        continue
    stats['total'] += 1
    
    # 从原文提取格局类别
    text_ge = None
    for kw, cat in TEXT_TO_GE.items():
        if kw in txt:
            text_ge = cat
            break
    
    if not text_ge:
        continue
    
    stats['text_has_ge'] += 1
    stats['by_type'].setdefault(text_ge, {'total': 0, 'consistent': 0, 'mismatch': 0, 'missed': 0})
    stats['by_type'][text_ge]['total'] += 1
    
    # 调用引擎获取special
    try:
        p = pai_pan(fp)
        wp = get_wangshuai(p)
        qr = get_qiangruo(p, wp)
        from engines.common.yongshen_engine import build_yongshen_engine
        from engines.common.special_pattern import build_special_patterns
        # 简化: 只获取special字段
        # 这里需要完整的引擎调用, 先跳过
        engine_special = None  # 简化
    except:
        engine_special = None
    
    # 暂时只统计原文格局分布
    # 引擎special比对需要完整引擎调用

print('=== 原文自述格局分布 ===')
print('总案例数: %d' % stats['total'])
print('原文有格局: %d (%.1f%%)' % (
    stats['text_has_ge'],
    100 * stats['text_has_ge'] / max(stats['total'], 1)))
print()
print('按格局类型:')
for ge_type, data in sorted(stats['by_type'].items(), key=lambda x: -x[1]['total']):
    print('  %s: %d' % (ge_type, data['total']))
print()
print('注: 引擎special比对需要完整引擎调用, 下一步补')
