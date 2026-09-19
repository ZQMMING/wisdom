# -*- coding: utf-8 -*-
import re

path = r'D:\shuntian-ziping-p0\scripts\kw_stats_v5.py'
content = open(path, encoding='utf-8').read()

# 加check_shenqiang函数
old = """def check_shenruo(r):"""
new = """def check_shenqiang(r):
    qs=r['queries']
    if 'HEAVY-ROOT' in qs or 'YIN-PARTY' in qs or 'BIJIE-PARTY' in qs or 'JIWANG-HUAIJI' in qs:
        return True
    # 双墓库根(如己丑月+日丑): 原典可作身强
    if r['root_class']=='LIGHT' and 'LIGHT-ROOT' in qs:
        # 检查是否有两个墓库根
        return False
    return False

def check_shenruo(r):"""
content = content.replace(old, new)

# 修改checks里身强的engine_qs为None，使用check_shenqiang
old = """    ('身强', ['HEAVY-ROOT', 'YIN-PARTY', 'BIJIE-PARTY'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '身强者', '身强敌杀', '身强财弱', '身强杀浅', '微论身强身弱']),"""
new = """    ('身强', None, ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '身强者', '身强敌杀', '身强财弱', '身强杀浅', '微论身强身弱']),"""
content = content.replace(old, new)

# 修改处理逻辑，支持check_shenqiang
old = """            if engine_qs is None:
                if check_shenruo(r):
                    kw_stats[kw]['match']+=1
                else:
                    kw_stats[kw]['mismatch']+=1"""
new = """            if engine_qs is None:
                if kw == '身强':
                    if check_shenqiang(r):
                        kw_stats[kw]['match']+=1
                    else:
                        kw_stats[kw]['mismatch']+=1
                else:
                    if check_shenruo(r):
                        kw_stats[kw]['match']+=1
                    else:
                        kw_stats[kw]['mismatch']+=1"""
content = content.replace(old, new)

open(path, 'w', encoding='utf-8', newline='\n').write(content)
print('done')
