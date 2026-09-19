# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.13: 把B0通用调候从B正格前面移到B正格后面(兜底位置)
# 问题: B0在B正格前面导致DTS/SFTK案例误走调候，正格路径(扶抑/病药/通关)没有机会触发
# 优化: 正格路径先触发，只有正格没命中时才走调候兜底(QTBJ调候仍可通过B1仲冬仲夏触发)

# 1. 删除B正格前面的B0
old_before = """    # ---------- B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，正格适用) ----------
    # 有明确调候候选hou时直接用第一优先(QTBJ调候是月令核心需求，优先级最高)
    # 排除: 从格(cong_shun)不走通用调候，应该走从格路径
    if primary is None and hou and hou[0] and not (cong or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')
    # ---------- B 正格 ----------
    if zheng:"""

new_before = """    # ---------- B 正格 ----------
    if zheng:"""
c = c.replace(old_before, new_before)

# 2. 在B6调候兜底/扶抑前面增加B0通用调候(作为兜底)
# 先找到B6的位置
old_b6 = """        # B6 调候兜底 / 扶抑"""

new_b6 = """        # B0 通用调候兜底(QTBJ穷通宝鉴覆盖所有月份，正格路径未命中时走调候)
        if primary is None and hou and hou[0]:
            P(hou[0],'QIHOU','通用调候候神兜底(正格路径未命中，取《穷通宝鉴》月令调候第一优先)')
        # B6 调候兜底 / 扶抑"""
c = c.replace(old_b6, new_b6)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.13完成(B0通用调候移到B正格后面作为兜底)')
