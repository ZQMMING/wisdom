# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.8简化: B0通用调候不检查力量，直接用调候候选第一优先
old = """        # B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，B1只针对仲冬仲夏不够)
        # 如果有明确调候候选hou且第一候选有根/有气，优先走调候路径
        # 注意: ben()/stem()/ling()/cs()参数是十神类型不是五行，改用wuxing_power检查
        if primary is None and hou and hou[0]:
            _h0 = hou[0]
            _h0_pow = wuxing_power.get('wuxing_power', {}).get(_h0, {})
            _h0_usable = (int(_h0_pow.get('ben_n', 0)) >= 1 or
                          int(_h0_pow.get('stem_n', 0)) >= 1 or
                          _h0_pow.get('ling_state', '') in ('旺', '相') or
                          int(_h0_pow.get('ju_n', 0)) >= 1 or
                          int(_h0_pow.get('zhong_n', 0)) >= 1 or
                          int(_h0_pow.get('yu_n', 0)) >= 1)
            if _h0_usable:
                P(_h0,'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先，候神有根/有气可用)')"""

new = """        # B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，B1只针对仲冬仲夏不够)
        # 有明确调候候选hou时直接用第一优先(QTBJ调候是月令核心需求，优先级最高)
        if primary is None and hou and hou[0]:
            P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.8简化完成(B0通用调候直接用第一候选)')
