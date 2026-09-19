# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.15: 回退V4.14的本气根条件，回到V4.12状态(B0在前面，从格排除，无力量条件)
old = """    # ---------- B0 通用调候(QTBJ穷通宝鉴，调候候选第一优先有本气根时优先) ----------
    # 只在调候候选第一优先有本气根(ben_n>=1)时才触发，避免DTS/SFTK案例(调候候选虚透无根)误走调候
    if primary is None and hou and hou[0] and not (cong or cong_shun):
        _h0_pow = wuxing_power.get('wuxing_power', {}).get(hou[0], {})
        if int(_h0_pow.get('ben_n', 0)) >= 1:
            P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先，候神有本气根)')
    # ---------- B 正格 ----------
    if zheng:"""

new = """    # ---------- B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，正格适用) ----------
    # 有明确调候候选hou时直接用第一优先(QTBJ调候是月令核心需求，优先级最高)
    # 排除: 从格(cong or cong_shun)不走通用调候，应该走从格路径
    if primary is None and hou and hou[0] and not (cong or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')
    # ---------- B 正格 ----------
    if zheng:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.15完成(回退本气根条件，回到V4.12状态)')
