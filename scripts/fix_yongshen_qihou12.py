# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.25: B0调候路径使用原始climate_candidates检查具体天干是否透干
# 问题: QT-0684申月壬水第一调候候选戊土，但命局无戊土透干(地支丑是己土)，原文"无戊土止水，专用丙火"
old = """    if primary is None and hou and hou[0] and not (cong or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""

new = """    if primary is None and hou and hou[0] and not (cong or cong_shun):
        # V4.25: 使用原始climate_candidates检查具体天干是否透干，第一候选天干没透干时用第二候选
        _clc_list = climate.get('climate_candidates') or []
        _use_hou_wx = hou[0]
        if _clc_list:
            _c0 = _clc_list[0].get('stem','') if len(_clc_list)>=1 else ''
            _c0_tougan = _c0 and _c0 in [pillars[k][0] for k in ('year','month','hour')]
            if not _c0_tougan and len(_clc_list)>=2:
                _c1 = _clc_list[1].get('stem','')
                _c1_tougan = _c1 and _c1 in [pillars[k][0] for k in ('year','month','hour')]
                if _c1_tougan:
                    _use_hou_wx = WX.get(_c1, hou[1] if len(hou)>=2 else hou[0])
        P(_use_hou_wx,'QIHOU','通用调候候神(《穷通宝鉴》月令调候，候选天干未透干时取下一候选)')"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.25完成(B0调候候选天干未透干时用下一候选)')
