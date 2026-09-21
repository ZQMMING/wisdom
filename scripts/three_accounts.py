# -*- coding: utf-8 -*-
"""三笔账：账A（原文自述格局）/ 账B（原文无格局）/ 账C（各special分组命中率）"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases

# 原文自述格局关键词
SPECIAL_KEYWORDS = {
    '专旺': ['曲直', '炎上', '稼穑', '从革', '润下', '一行得气', '专旺'],
    '从格': ['从财', '从杀', '从儿', '从官', '弃命从', '从势', '从旺', '从强'],
    '化气': ['化气', '化木', '化火', '化土', '化金', '化水', '乙庚化', '甲己化', '丙辛化', '丁壬化', '戊癸化'],
    '两神成象': ['二人同心', '两神成象', '两气成象', '两气'],
}

# 扫原文，找自述格局
account_a = {k: [] for k in SPECIAL_KEYWORDS}  # 账A：原文自述格局
account_b = []  # 账B：原文无格局

for idx, (li, fp, dy, txt) in enumerate(cases, 1):
    text = txt[:200] if txt else ''
    has_special = False
    for cat, kws in SPECIAL_KEYWORDS.items():
        for kw in kws:
            if kw in text:
                account_a[cat].append(idx)
                has_special = True
                break
        if has_special:
            break
    if not has_special:
        account_b.append(idx)

print('=== 账A（原文自述格局）===')
for cat, cases_list in account_a.items():
    print('  %s: %d条' % (cat, len(cases_list)))
print('  合计: %d条' % sum(len(v) for v in account_a.values()))
print()
print('=== 账B（原文无格局）===')
print('  合计: %d条' % len(account_b))
print()

# 专旺格判断
def is_zhuanwang(special):
    return any(x in special for x in ['曲直格', '炎上格', '稼穑格', '从革格', '润下格'])

# 读基线
import json
baseline = json.load(open('baseline_special_20260922.json', encoding='utf-8'))
special_map = {b['li']: b.get('special', '') for b in baseline}

# 账A·专旺格
zhuanwang_a = account_a['专旺']
kept_tp = sum(1 for idx in zhuanwang_a if is_zhuanwang(special_map.get(idx, '')))
lost_tp = len(zhuanwang_a) - kept_tp
print('=== 账A·专旺格 ===')
print('  总数: %d条' % len(zhuanwang_a))
print('  仍判专旺（kept_tp）: %d条' % kept_tp)
print('  流失（lost_tp）: %d条' % lost_tp)
print()

# 账B·专旺格
zhuanwang_b = [idx for idx in account_b if is_zhuanwang(special_map.get(idx, ''))]
remaining_fp = len(zhuanwang_b)
killed_fp = len(account_b) - remaining_fp  # 不对，应该是账B中原文无格局但引擎判专旺的
print('=== 账B·专旺格 ===')
print('  账B总数: %d条' % len(account_b))
print('  其中判专旺（remaining_fp）: %d条' % remaining_fp)
print()

# 净变化
print('=== 净变化 ===')
print('  拦假例（killed_fp）: 待对比旧基线')
print('  误杀真例（lost_tp）: %d条' % lost_tp)
print('  净收益 = killed_fp - lost_tp')
