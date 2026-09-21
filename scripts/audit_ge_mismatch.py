# -*- coding: utf-8 -*-
"""引擎格局判定 vs 原文自述格局 错配率统计"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases

# ============================================================
# 类别映射表(事前写死)
# ============================================================

# 原文关键词 → 格局类别
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

# 引擎special字段 → 格局类别
def engine_ge_to_category(special_name):
    if not special_name:
        return None
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
    return None

# ============================================================
# 跑比对
# ============================================================

from engines.common.yongshen_engine import run_yongshen

stats = {
    'total': 0,
    'consistent': 0,      # 一致
    'mismatch': 0,        # 真错配
    'missed': 0,          # 漏判(原文有格局, 引擎为空)
    'by_type': {},        # 按格局类型拆明细
    'mismatch_examples': [],
    'missed_examples': [],
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
        continue  # 原文无格局, 跳过
    
    # 从引擎提取格局类别
    # 这里需要调用引擎获取special_name
    # 简化: 直接从dayun_align的输出中提取
    # 但我们没有直接访问, 用近似方法
    
    # 先统计原文有格局的案例数
    stats['by_type'][text_ge] = stats['by_type'].get(text_ge, 0) + 1

print('=== 原文自述格局分布(弱金标子集) ===')
print('总案例数: %d' % stats['total'])
print('原文有格局的案例数: %d' % sum(stats['by_type'].values()))
print()
print('按格局类型:')
for ge_type, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
    print('  %s: %d' % (ge_type, count))

print()
print('注: 引擎special字段比对需要调用引擎, 下一步补')
