# -*- coding: utf-8 -*-
"""三笔账: 错配率+幻觉率+各special分组命中率"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases, engine

# ============================================================
# 类别映射表(事前写死)
# ============================================================

# 原文关键词 → 格局类别
# 注意: "二人同心"归两神成象(《滴天髓》形象章, 非从化章)
TEXT_TO_GE = {
    # 从格
    '从势': '从格', '从财': '从格', '从杀': '从格', '从官': '从格',
    '从儿': '从格', '弃命从': '从格', '顺其气势': '从格', '顺其性': '从格',
    # 专旺格
    '曲直': '专旺格', '炎上': '专旺格', '稼穑': '专旺格', '从革': '专旺格',
    '润下': '专旺格', '一行得气': '专旺格', '专旺': '专旺格',
    # 化气格
    '化气': '化气格', '化木': '化气格', '化火': '化气格', '化土': '化气格',
    '化金': '化气格', '化水': '化气格', '化出': '化气格',
    # 两神成象
    '二人同心': '两神成象', '两神成象': '两神成象', '两气成象': '两神成象',
}

def engine_ge_to_category(special_name):
    """引擎special字段 → 格局类别"""
    if not special_name:
        return '正格'
    # 从格
    if any(x in special_name for x in ['从财格', '从杀格', '从官格', '从儿格', '从势格']):
        return '从格'
    # 专旺格
    if any(x in special_name for x in ['曲直格', '炎上格', '稼穑格', '从革格', '润下格']):
        return '专旺格'
    # 化气格
    if '化' in special_name and '气格' in special_name:
        return '化气格'
    # 两神成象
    if '两气成象' in special_name:
        return '两神成象'
    # 正格
    if '正格' in special_name:
        return '正格'
    return '正格'

# ============================================================
# 跑三笔账
# ============================================================

# 账A: 错配四格表
# 账B: 幻觉率(原文无格局, 引擎有特殊格局)
# 账C: 各special分组命中率

# 先收集所有案例的数据
all_cases = []
for li, fp, dy, txt in cases:
    if len(dy) < 4:
        continue
    
    # 从原文提取格局类别
    text_ge = None
    for kw, cat in TEXT_TO_GE.items():
        if kw in txt:
            text_ge = cat
            break
    
    # 从引擎提取格局类别
    try:
        p, f, ye, tp0, wp, th = engine(fp)
        engine_special = ye.get('special') or ''
        engine_ge = engine_ge_to_category(engine_special)
    except:
        engine_special = ''
        engine_ge = '正格'
    
    all_cases.append({
        'li': li,
        'text_ge': text_ge,
        'engine_special': engine_special,
        'engine_ge': engine_ge,
        'txt': txt,
    })

print('=== 三笔账统计 ===')
print('总案例数: %d' % len(all_cases))
print()

# ============================================================
# 账A: 错配四格表(按类型拆分)
# ============================================================
print('=== 账A: 错配四格表(原文有格局的子集) ===')
text_ge_cases = [c for c in all_cases if c['text_ge']]
print('原文有格局: %d' % len(text_ge_cases))
print()

# 按格局类型拆分
for ge_type in ['从格', '专旺格', '化气格', '两神成象']:
    subset = [c for c in text_ge_cases if c['text_ge'] == ge_type]
    if not subset:
        continue
    
    consistent = sum(1 for c in subset if c['engine_ge'] == ge_type)
    mismatch = sum(1 for c in subset if c['engine_ge'] != ge_type and c['engine_ge'] != '正格')
    missed = sum(1 for c in subset if c['engine_ge'] == '正格')
    
    print('  [%s]' % ge_type)
    print('    总数: %d' % len(subset))
    print('    一致: %d (%.1f%%)' % (consistent, 100 * consistent / len(subset)))
    print('    真错配: %d (%.1f%%)' % (mismatch, 100 * mismatch / len(subset)))
    print('    漏判(原文有, 引擎判正格): %d (%.1f%%)' % (missed, 100 * missed / len(subset)))
    print()

# ============================================================
# 账B: 幻觉率(原文无格局, 引擎有特殊格局)
# ============================================================
print('=== 账B: 幻觉率(原文无格局, 引擎有特殊格局) ===')
no_text_ge_cases = [c for c in all_cases if not c['text_ge']]
print('原文无格局: %d' % len(no_text_ge_cases))
print()

for ge_type in ['正格', '专旺格', '从格', '化气格', '两神成象']:
    subset = [c for c in no_text_ge_cases if c['engine_ge'] == ge_type]
    print('  引擎判%s: %d (%.1f%%)' % (
        ge_type, len(subset), 100 * len(subset) / len(no_text_ge_cases)))

print()

# ============================================================
# 账C: 各special分组命中率
# ============================================================
print('=== 账C: 各special分组命中率 ===')
print('(需要对齐数据, 这里只统计分布)')
print()

# 按引擎格局类别统计
for ge_type in ['正格', '专旺格', '从格', '化气格', '两神成象']:
    subset = [c for c in all_cases if c['engine_ge'] == ge_type]
    print('  引擎判%s: %d例' % (ge_type, len(subset)))
