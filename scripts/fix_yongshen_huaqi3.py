# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.5: 假化(CANDIDATE)不触发化气格路径，只有真化(CONFIRMED)才触发
# 问题: QT-0040戊子庚申乙丑壬午被判为假化(CANDIDATE)，但hua_youqing=True导致触发化气格路径用金
# 原文说"专用午中一点丁火"，应该用丁火调候制杀，不是化金气格
# 优化: 只有hua_conf(CONFIRMED)才触发化气格路径，假化(CANDIDATE)走正常扶抑/调候路径

old = """    # ---------- A 化气 / 从顺 / 专旺 / 成象 ----------
    if hua_conf or hua_youqing:"""

new = """    # ---------- A 化气 / 从顺 / 专旺 / 成象 ----------
    # V4.5: 只有真化(CONFIRMED)才触发化气格路径，假化(CANDIDATE)走正常扶抑/调候路径
    if hua_conf:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.5完成(假化CANDIDATE不触发化气格路径，只有真化CONFIRMED才触发)')
