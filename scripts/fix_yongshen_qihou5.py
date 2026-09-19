# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.10: B0通用调候增加从格排除条件，从格(cong_shun)不走通用调候，应该走从格路径
# 问题: QT-0058从财格、QT-0252从儿格、QT-0282从杀格都走了调候路径，而不是从格路径

old = """    # ---------- B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，所有格局都适用) ----------
    # 有明确调候候选hou时直接用第一优先(QTBJ调候是月令核心需求，优先级最高)
    if primary is None and hou and hou[0]:
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""

new = """    # ---------- B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，正格适用) ----------
    # 有明确调候候选hou时直接用第一优先(QTBJ调候是月令核心需求，优先级最高)
    # 排除: 从格(cong_shun)不走通用调候，应该走从格路径
    if primary is None and hou and hou[0] and not cong_shun:
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.10完成(B0通用调候增加从格排除条件)')
