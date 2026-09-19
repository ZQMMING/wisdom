# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.14: 回退V4.13，B0放回前面，但增加力量条件：只在调候候选第一优先有本气根时才触发
# 问题: B0在前面导致DTS/SFTK案例(调候候选无本气根)误走调候
# 优化: B0在前面，但只在调候候选第一优先有本气根(ben_n>=1)时才触发

# 1. 删除B正格后面的B0兜底
old_after = """        # B0 通用调候兜底(QTBJ穷通宝鉴覆盖所有月份，正格路径未命中时走调候)
        if primary is None and hou and hou[0]:
            P(hou[0],'QIHOU','通用调候候神兜底(正格路径未命中，取《穷通宝鉴》月令调候第一优先)')
        # B6 调候兜底 / 扶抑"""

new_after = """        # B6 调候兜底 / 扶抑"""
c = c.replace(old_after, new_after)

# 2. 在B正格前面增加B0(带力量条件)
old_before = """    # ---------- B 正格 ----------
    if zheng:"""

new_before = """    # ---------- B0 通用调候(QTBJ穷通宝鉴，调候候选第一优先有本气根时优先) ----------
    # 只在调候候选第一优先有本气根(ben_n>=1)时才触发，避免DTS/SFTK案例(调候候选虚透无根)误走调候
    if primary is None and hou and hou[0] and not (cong or cong_shun):
        _h0_pow = wuxing_power.get('wuxing_power', {}).get(hou[0], {})
        if int(_h0_pow.get('ben_n', 0)) >= 1:
            P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先，候神有本气根)')
    # ---------- B 正格 ----------
    if zheng:"""
c = c.replace(old_before, new_before)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.14完成(回退V4.13，B0放回前面但增加本气根条件)')
