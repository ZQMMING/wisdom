# -*- coding: utf-8 -*-
"""检查A: 调候在金标里出现多少次
检查B: 136条关系案例的命中率是多少
"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')

from scripts.dayun_align import cases

# ============================================================
# 检查A: 调候关键词统计
# ============================================================
TIAOHOU_KEYWORDS = [
    '寒', '暖', '燥', '湿',
    '调候', '水火既济',
    '丙火', '癸水',
    '冬生', '夏生',
    '寒木', '暖土', '燥土', '湿土',
    '水冷', '火炎', '金寒', '木凋',
    '解冻', '解冻除寒',
    '滋湿', '调候为急',
    '金水相涵', '木火通明',
    '水旺火熄', '火炎土燥',
    '水冷金寒', '木火通明',
    '丙癸', '丁甲',
    '寒极', '暖极',
    '得寒', '得暖',
    '受寒', '受热',
]

stats_a = {
    'total': 0,
    'has_tiaohou': 0,
    'by_keyword': {},
}

for li, fp, dy, txt in cases:
    if len(dy) < 4:
        continue
    stats_a['total'] += 1
    
    has_th = False
    for kw in TIAOHOU_KEYWORDS:
        if kw in txt:
            has_th = True
            stats_a['by_keyword'][kw] = stats_a['by_keyword'].get(kw, 0) + 1
    
    if has_th:
        stats_a['has_tiaohou'] += 1

print('=== 检查A: 调候在金标里出现多少次 ===')
print('总案例数: %d' % stats_a['total'])
print('提到调候的案例数: %d (%.1f%%)' % (
    stats_a['has_tiaohou'],
    100 * stats_a['has_tiaohou'] / max(stats_a['total'], 1)))
print()
print('按关键词分布(前20):')
for kw, count in sorted(stats_a['by_keyword'].items(), key=lambda x: -x[1])[:20]:
    print('  %s: %d' % (kw, count))
print()

# ============================================================
# 检查B: 136条关系案例的命中率
# ============================================================
RELATION_KEYWORDS = {
    '六合': ['合去', '合住', '合绊', '合化', '合局', '合而', '合之', '合为'],
    '三合三会': ['三合', '三会', '会局', '合局'],
    '六冲': ['冲去', '冲散', '冲开', '冲克', '冲战', '冲之', '冲而', '相冲'],
    '三刑': ['三刑', '刑伤', '刑出', '刑入', '刑至'],
    '六害': ['六害', '害之', '相害'],
    '六破': ['破之', '相破', '破出', '破入'],
    '暗会拱合': ['暗会', '暗拱', '拱合', '拱出'],
    '天干合': ['合官', '合煞', '合财', '合印', '合食', '合伤', '合比', '合劫'],
}

def has_relation(txt):
    for rel_type, keywords in RELATION_KEYWORDS.items():
        for kw in keywords:
            if kw in txt:
                return True
    return False

# 重跑对齐, 分关系/非关系组统计
from scripts.dayun_align import main as align_main
import io
import contextlib

# 先收集所有案例的对齐结果
align_output = io.StringIO()
with contextlib.redirect_stdout(align_output):
    align_main()

# 解析对齐结果
align_results = {}
for line in align_output.getvalue().split('\n'):
    if line.startswith(' L') and '运' in line:
        # 解析案例行
        parts = line.strip().split()
        li_str = parts[0].replace('L', '')
        try:
            li = int(li_str)
            align_results[li] = line
        except:
            pass

# 统计关系组命中率
relation_judgable = 0
relation_agree = 0
no_relation_judgable = 0
no_relation_agree = 0

for li, fp, dy, txt in cases:
    if len(dy) < 4:
        continue
    
    # 判断是否可判
    if 'fav' not in txt and 'av' not in txt:
        continue
    
    # 检查是否提到关系
    rel = has_relation(txt)
    
    # 检查对齐结果
    li_int = li + 1
    if li_int in align_results:
        line = align_results[li_int]
        # 简化: 如果行里有"原文ji"或"原文xiong", 就算可判
        if '原文' in line:
            if rel:
                relation_judgable += 1
                # 简化判断: 如果引擎判断和原文判断一致
                # 这里不精确, 只是粗略统计
            else:
                no_relation_judgable += 1

print('=== 检查B: 关系案例 vs 非关系案例命中率 ===')
print('(粗略统计, 精确数字需完整重跑对齐)')
print('关系案例可判数: %d' % relation_judgable)
print('非关系案例可判数: %d' % no_relation_judgable)
print()
print('注: 精确命中率需重跑dayun_align并按是否提到关系分组')
