# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.28: B0调候路径增加调候候选力量检查：ling是死/囚/绝时不触发，走正格路径
# 问题: DT-0263调候火ling=死，SF-0083调候木ling=囚，力量弱不应走调候
old = """    # V4.27: B0调候路径只排除真从(CONFIRMED)和cong_shun，不排除假从(CANDIDATE)
    _cong_confirmed = bool(cong) and (cong_state or '') == 'CONFIRMED'
    if primary is None and hou and hou[0] and not (_cong_confirmed or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""

new = """    # V4.27: B0调候路径只排除真从(CONFIRMED)和cong_shun，不排除假从(CANDIDATE)
    # V4.28: 调候候选ling是死/囚/绝时不触发B0，走正格路径(调候候神太弱)
    _cong_confirmed = bool(cong) and (cong_state or '') == 'CONFIRMED'
    _hou_ling = ling(hou[0]) if hou and hou[0] else ''
    _hou_tooweak = _hou_ling in ('死','囚','绝')
    if primary is None and hou and hou[0] and not (_cong_confirmed or cong_shun) and not _hou_tooweak:
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.28完成(B0调候候选ling死/囚/绝时不触发)')
