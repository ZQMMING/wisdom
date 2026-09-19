# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.23: B0调候路径增加候选存在性检查：第一候选不存在(无透干无本气根)时用第二候选
# 问题: QT-0684申月壬水第一调候候选戊土，但命局无戊土，原文"无戊土止水，专用丙火"
old = """    if primary is None and hou and hou[0] and not (cong or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""

new = """    if primary is None and hou and hou[0] and not (cong or cong_shun):
        # V4.23: 第一调候候选不存在(无透干无本气根)时用第二候选
        _h0_exists = stem(hou[0])>=1 or ben(hou[0])>=1 or cs(hou[0]) or ling(hou[0]) in ('旺','相')
        _use_hou = hou[0]
        if not _h0_exists and len(hou)>=2 and hou[1]:
            _h1_exists = stem(hou[1])>=1 or ben(hou[1])>=1 or cs(hou[1]) or ling(hou[1]) in ('旺','相')
            if _h1_exists:
                _use_hou = hou[1]
        P(_use_hou,'QIHOU','通用调候候神(《穷通宝鉴》月令调候，候选不存在时取下一候选)')"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.23完成(B0调候候选不存在时用下一候选)')
