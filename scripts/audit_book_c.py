# -*- coding: utf-8 -*-
"""账C: 各special分组命中率 + 化气交叉表 + 专旺抽样"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases, engine

# 类别映射表
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
        return '正格'
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
    return '正格'

# 收集所有案例数据
all_cases = []
for li, fp, dy, txt in cases:
    if len(dy) < 4:
        continue
    
    text_ge = None
    for kw, cat in TEXT_TO_GE.items():
        if kw in txt:
            text_ge = cat
            break
    
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

print('=== 账C: 各special分组命中率 ===')
print('(需要对齐数据, 这里只统计分布)')
print()

# 按引擎格局类别统计
for ge_type in ['正格', '专旺格', '从格', '化气格', '两神成象']:
    subset = [c for c in all_cases if c['engine_ge'] == ge_type]
    print('  引擎判%s: %d例' % (ge_type, len(subset)))

print()
print('=== 化气格交叉表: 原文说化气, 引擎判成了什么? ===')
print()

# 原文说化气的案例
text_huaqi = [c for c in all_cases if c['text_ge'] == '化气格']
print('原文说化气: %d例' % len(text_huaqi))
print()

# 引擎判成了什么?
from collections import Counter
engine_ge_dist = Counter(c['engine_ge'] for c in text_huaqi)
print('引擎判定分布:')
for ge, count in engine_ge_dist.most_common():
    print('  %s: %d (%.1f%%)' % (ge, count, 100 * count / len(text_huaqi)))

print()
print('=== 专旺格抽样: 原文无格局, 引擎判专旺的案例 ===')
print()

# 原文无格局, 引擎判专旺的案例
no_text_zhuanwang = [c for c in all_cases if not c['text_ge'] and c['engine_ge'] == '专旺格']
print('原文无格局, 引擎判专旺: %d例' % len(no_text_zhuanwang))
print()

# 随机抽20条
import random
random.seed(42)
sample = random.sample(no_text_zhuanwang, min(20, len(no_text_zhuanwang)))
print('抽样20条:')
for i, c in enumerate(sample):
    print('  %d. L%d [%s]: %s' % (
        i+1, c['li']+1, c['engine_special'], c['txt'][:60]))
