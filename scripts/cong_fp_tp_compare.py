# -*- coding: utf-8 -*-
"""从格FP vs TP结构签名对照表"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases
import json
import re

# 读基线
baseline = json.load(open('baseline_special_20260922.json', encoding='utf-8'))
special_by_key = {}
for b in baseline:
    key = b['key']
    special_by_key[key] = b.get('special', '')

# 从格判断
def is_cong(special):
    return any(x in special for x in ['从财格', '从杀格', '从儿格', '从官格', '从势格'])

# 专旺格判断
def is_zhuanwang(special):
    return any(x in special for x in ['曲直格', '炎上格', '稼穑格', '从革格', '润下格'])

# 化气格判断
def is_huaqi(special):
    return '化' in special and '气格' in special

# 从格关键词
CONG_INCLUDE = [r"从财", r"从杀", r"从儿", r"从官", r"弃命从", r"从势", r"从旺", r"从强", r"从化"]

# 收集TP（账A·从格且引擎判从格）和FP（账B·从格）
tp_list = []
fp_list = []

for idx, (li, fp, dy, txt) in enumerate(cases, 1):
    text = txt[:300] if txt else ''
    
    # 检查是否命中从格关键词
    hit = False
    for kw in CONG_INCLUDE:
        if re.search(kw, text):
            hit = True
            break
    
    # 用key匹配基线
    key = ''.join(g+z for g,z in fp)
    sp = special_by_key.get(key, '')
    
    if hit and is_cong(sp):
        # TP：原文说从格，引擎也判从格
        tp_list.append((idx, key, sp, text, fp))
    elif not hit and is_cong(sp):
        # FP：原文没说从格，引擎判从格
        fp_list.append((idx, key, sp, text, fp))

print('TP（账A·从格一致）:', len(tp_list), '条')
print('FP（账B·从格）:', len(fp_list), '条')
print()

# 结构签名分析
def analyze_structure(fp_list):
    """分析八字结构签名"""
    # 天干
    tiangan = [fp[0] for fp in fp_list]
    # 地支
    dizhi = [fp[1] for fp in fp_list]
    
    # 统计五行分布
    wuxing_count = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    
    # 天干五行
    gan_wuxing = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
                  '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
    # 地支五行
    zhi_wuxing = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
                  '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'}
    
    for gan in tiangan:
        wuxing_count[gan_wuxing[gan]] += 1
    for zhi in dizhi:
        wuxing_count[zhi_wuxing[zhi]] += 1
    
    return wuxing_count

print('=== TP结构签名 ===')
tp_wx = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
for idx, key, sp, text, fp in tp_list:
    wx = analyze_structure(fp)
    for k in tp_wx:
        tp_wx[k] += wx[k]

total_tp = sum(tp_wx.values())
for k, v in tp_wx.items():
    print('  %s: %d (%.1f%%)' % (k, v, v/total_tp*100))

print()
print('=== FP结构签名 ===')
fp_wx = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
for idx, key, sp, text, fp in fp_list:
    wx = analyze_structure(fp)
    for k in fp_wx:
        fp_wx[k] += wx[k]

total_fp = sum(fp_wx.values())
for k, v in fp_wx.items():
    print('  %s: %d (%.1f%%)' % (k, v, v/total_fp*100))

print()
print('=== 对比 ===')
print('TP最旺五行:', max(tp_wx, key=tp_wx.get))
print('FP最旺五行:', max(fp_wx, key=fp_wx.get))
