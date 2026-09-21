# -*- coding: utf-8 -*-
"""账A关键词匹配器V2：包含词+排除词双表"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases
import json
import re

# 双表关键词匹配器V2
PATTERN_KEYWORDS = {
    "专旺格": {
        "include": [r"曲直", r"炎上", r"稼穑", r"从革", r"润下", r"一行得气", r"专旺"],
        "exclude": [r"偏枯", r"混乱", r"不成格"],
    },
    "从格": {
        "include": [r"从财", r"从杀", r"从儿", r"从官", r"弃命从", r"从势", r"从旺", r"从强", r"从化"],
        "exclude": [],
    },
    "化气格": {
        "include": [r"化气", r"格成.*化", r"[乙庚丁壬甲己丙戊].{0,3}合化"],
        "exclude": [r"从化", r"合去", r"化忌", r"变化", r"从杀", r"从财", r"合壬化木"],
    },
    "两神成象": {
        "include": [r"二人同心", r"两神成象", r"两气成象", r"两气"],
        "exclude": [],
    },
}

def classify_account_a(text):
    """用双表匹配器分类账A"""
    text = text[:300] if text else ''
    
    for pattern, kw in PATTERN_KEYWORDS.items():
        # 先检查排除词
        for ex in kw['exclude']:
            if re.search(ex, text):
                return None  # 命中排除词，不算
        
        # 再检查包含词
        for inc in kw['include']:
            if re.search(inc, text):
                return pattern
    
    return None  # 都没命中

# 重跑账A
print('=== 账A关键词匹配器V2结果 ===')
print()

account_a = {}
account_b_count = 0

for idx, (li, fp, dy, txt) in enumerate(cases, 1):
    pattern = classify_account_a(txt)
    if pattern:
        if pattern not in account_a:
            account_a[pattern] = []
        account_a[pattern].append(idx)
    else:
        account_b_count += 1

print('账A（原文自述格局）：')
total_a = 0
for pattern, ids in account_a.items():
    print('  %s: %d条' % (pattern, len(ids)))
    total_a += len(ids)
print('  合计: %d条' % total_a)
print()
print('账B（原文无格局）: %d条' % account_b_count)
print()

# 读基线
baseline = json.load(open('baseline_special_20260922.json', encoding='utf-8'))
special_by_key = {}
for b in baseline:
    key = b['key']
    special_by_key[key] = b.get('special', '')

# 化气格判断
def is_huaqi(special):
    return '化' in special and '气格' in special

# 专旺格判断
def is_zhuanwang(special):
    return any(x in special for x in ['曲直格', '炎上格', '稼穑格', '从革格', '润下格'])

# 从格判断
def is_cong(special):
    return any(x in special for x in ['从财格', '从杀格', '从儿格', '从官格', '从势格'])

# 重算账A一致率
print('=== 账A一致率（V2匹配器）===')
print()

for pattern, ids in account_a.items():
    kept = 0
    lost = 0
    for idx in ids:
        # 找key
        for i, (li, fp, dy, txt) in enumerate(cases, 1):
            if i == idx:
                key = ''.join(g+z for g,z in fp)
                sp = special_by_key.get(key, '')
                
                if pattern == '化气格' and is_huaqi(sp):
                    kept += 1
                elif pattern == '专旺格' and is_zhuanwang(sp):
                    kept += 1
                elif pattern == '从格' and is_cong(sp):
                    kept += 1
                else:
                    lost += 1
                break
    
    print('%s: kept=%d / total=%d (%.1f%%)' % (pattern, kept, len(ids), kept/len(ids)*100))
