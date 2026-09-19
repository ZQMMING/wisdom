# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.8: 增加通用调候路径(QTBJ穷通宝鉴覆盖所有月份，B1只针对仲冬仲夏不够)
# 在B1仲冬调候前面增加：如果有明确调候候选hou且第一候选有根/有气，优先走调候路径
# 问题: QT-0147丁亥丁未乙酉丁亥(未月)原文"专此壬水为用"，但引擎走通关用金
#       QT-0168庚辰丙戌乙亥庚辰(戌月)原文"只能用丙火"，但引擎走病药用水

old = """        # B1 仲冬调候(火透: 杀重则制杀调候合一, 否则身有气寒木向阳; 印重破印让位)"""

new = """        # B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，B1只针对仲冬仲夏不够)
        # 如果有明确调候候选hou且第一候选有根/有气，优先走调候路径
        if primary is None and hou and hou[0]:
            _h0 = hou[0]
            _h0_usable = ben(_h0)>=1 or stem(_h0)>=1 or ling(_h0) in ('旺','相') or cs(_h0)
            if _h0_usable:
                P(_h0,'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先，候神有根/有气可用)')
        # B1 仲冬调候(火透: 杀重则制杀调候合一, 否则身有气寒木向阳; 印重破印让位)"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.8完成(增加通用调候路径B0，QTBJ所有月份调候候选优先)')
