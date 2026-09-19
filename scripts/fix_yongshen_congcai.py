# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.17: 从财格优化：财太旺(ben>=3或成势)时用官杀泄财
# 问题: QT-0058甲辰甲戌甲辰甲戌从财格，财土太旺(地支辰戌辰戌)，原文用金(官杀泄财)
old = """        if '从财' in cong:
            if t['cai']=='水' and (mz in ('亥','子','丑','辰') or cold):
                P(t['cai'],'CONG_SHUN','寒湿虚身从水财，顺其寒湿水势'); S(t['shi'],'金食伤生水')
            elif qi(t['shi']):
                P(t['shi'],'CONG_SHUN','从财喜食伤吐秀生财(从财必要食伤)'); S(t['cai'],'顺财')
            else:
                P(t['cai'],'CONG_SHUN','从财无食伤，顺财'); S(t['shi'],'食伤生财')"""

new = """        if '从财' in cong:
            # 从财格：财太旺(ben>=3或成势)时用官杀泄财，否则用财或食伤
            _cai_taiwang = ben(t['cai'])>=3 or cs(t['cai'])
            if _cai_taiwang:
                P(t['guan'],'CONG_SHUN','从财格财星太旺成势，用官杀泄财为用'); S(t['cai'],'财旺生官杀')
            elif t['cai']=='水' and (mz in ('亥','子','丑','辰') or cold):
                P(t['cai'],'CONG_SHUN','寒湿虚身从水财，顺其寒湿水势'); S(t['shi'],'金食伤生水')
            elif qi(t['shi']):
                P(t['shi'],'CONG_SHUN','从财喜食伤吐秀生财(从财必要食伤)'); S(t['cai'],'顺财')
            else:
                P(t['cai'],'CONG_SHUN','从财无食伤，顺财'); S(t['shi'],'食伤生财')"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.17完成(从财格优化：财太旺用官杀泄财)')
