# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.3: 修复调候候选选择逻辑 - 保留顺序，取第一个(最优先)，而不是sorted按Unicode编码排序
# 问题: 第62行hou是set，丢失了调候候选的顺序；第508/522行sorted(hou)[0]按Unicode编码排序选择，不是按调候优先级
# 例如QT-0137调候候选=['癸','丙']，sorted后选了'水'但原文用神是'火'

# 1. 第62行: set改成list，保留顺序
old1 = "    hou={WX[c.get('stem')] for c in (climate.get('climate_candidates') or []) if c.get('stem') in WX}"
new1 = "    hou=[WX[c.get('stem')] for c in (climate.get('climate_candidates') or []) if c.get('stem') in WX]"
c = c.replace(old1, new1)

# 2. 第508行: sorted(hou)[0]改成hou[0]
old2 = "            elif hou: P(sorted(hou)[0],'QIHOU','中和取调候/相神，扶抑不强')"
new2 = "            elif hou: P(hou[0],'QIHOU','中和取调候/相神，扶抑不强(取调候候选第一优先)')"
c = c.replace(old2, new2)

# 3. 第522行: sorted(hou)[0]改成hou[0]
old3 = "                P(sorted(hou)[0],'QIHOU','兜底取调候候神(所有结构化路径未命中)')"
new3 = "                P(hou[0],'QIHOU','兜底取调候候神(所有结构化路径未命中，取调候候选第一优先)')"
c = c.replace(old3, new3)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.3完成(修复调候候选选择逻辑: 保留顺序取第一优先，而非sorted按Unicode编码排序)')
