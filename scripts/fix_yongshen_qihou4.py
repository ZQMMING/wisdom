# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.9: 把B0通用调候移到if zheng:外面，让所有格局(包括假化CANDIDATE)都能走通用调候
# 问题: QT-0040化气格CANDIDATE导致zheng=False，B0在if zheng:块内没执行，用神为空

# 先删除if zheng:块内的B0
old_in_zheng = """        # B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，B1只针对仲冬仲夏不够)
        # 有明确调候候选hou时直接用第一优先(QTBJ调候是月令核心需求，优先级最高)
        if primary is None and hou and hou[0]:
            P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')
        # B1 仲冬调候"""

new_in_zheng = """        # B1 仲冬调候"""
c = c.replace(old_in_zheng, new_in_zheng)

# 在if zheng:前面增加B0通用调候(在A部分之后，B正格之前)
old_before_zheng = """    # ---------- B 正格 ----------
    if zheng:"""

new_before_zheng = """    # ---------- B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，所有格局都适用) ----------
    # 有明确调候候选hou时直接用第一优先(QTBJ调候是月令核心需求，优先级最高)
    if primary is None and hou and hou[0]:
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')
    # ---------- B 正格 ----------
    if zheng:"""
c = c.replace(old_before_zheng, new_before_zheng)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.9完成(B0通用调候移到if zheng:外面，所有格局都适用)')
