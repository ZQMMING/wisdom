# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.2: 修复身旺时"杀印相生"路径过于激进的问题
# 原著依据:
# 1. 《子平真诠》徐乐吾注: "身弱用官，宜於印化；身強用官，宜用財生"
# 2. 《滴天髓》任铁樵注: "杀即官也，身旺者以杀为官；官即杀也，身弱者以官为杀"
# 3. 《子平真诠》论印绶: "有印透官者，身强用官，喜财生官"
# 结论: 身旺时应该用官(或财生官)，杀印相生只适用于身弱杀重

old = """                    elif gs_rooted and hua_ok and (cs(t['guan']) or stem(t['guan'])>=2):
                        P(t['yin'],'BINGYAO','身旺而官杀成势有根、印透有气，杀印相生权自我操'); S(t['guan'])"""

new = """                    elif gs_rooted and hua_ok and (cs(t['guan']) or stem(t['guan'])>=2) and tier not in WANG_TIER:
                        # V4.2: 身旺时不触发"杀印相生"，优先用官(原著: 身強用官宜用財生，身弱用官宜於印化)
                        P(t['yin'],'BINGYAO','官杀成势有根、印透有气，杀印相生权自我操(身弱/中和适用)'); S(t['guan'])"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.2完成(修复身旺时杀印相生路径过于激进: 身旺时不触发杀印相生，优先用官)')
