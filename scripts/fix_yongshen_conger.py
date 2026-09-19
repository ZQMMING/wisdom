# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.16: 从儿格用神优化：财星无本气根且无透干时用食伤，否则用财
# 问题: QT-0252丁丑丁未丙午己丑从儿格，财金太弱(无本气根无透干)，原文用土(食伤)
old = """        elif '从儿' in cong:
            P(t['cai'],'CONG_SHUN','从儿儿又见儿，食伤生财，以财为用'); S(t['shi'],'顺食伤格神')"""

new = """        elif '从儿' in cong:
            # 从儿格：财星有根/透干用财，财星太弱用食伤顺泄
            _cai_usable = ben(t['cai'])>=1 or stem(t['cai'])>=1 or cs(t['cai'])
            if _cai_usable:
                P(t['cai'],'CONG_SHUN','从儿儿又见儿，食伤生财，以财为用'); S(t['shi'],'顺食伤格神')
            else:
                P(t['shi'],'CONG_SHUN','从儿格财星太弱(无根无透)，顺食伤泄秀为用'); S(t['cai'],'食伤生财(待运)')"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.16完成(从儿格用神优化：财星太弱用食伤)')
