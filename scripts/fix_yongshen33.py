# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在第478行官杀条件前增加: 比劫成势+官杀只有余气根+财星有藏干根→用财泄比劫生官杀(丁巳癸丑丁卯丙午: 丑中辛金为用)
old = """            elif stem(t['guan'])>=1 and (ben(t['guan'])>=1 or ling(t['guan']) in ('旺','相') or d(t['guan'])['zhong_n']+d(t['guan'])['yu_n']>=1):
                P(t['guan'],'FUYI','身旺官杀透干有根/有气，用官杀克身成权')"""

new = """            elif stem(t['guan'])>=1 and ben(t['guan'])==0 and d(t['guan'])['zhong_n']==0 and d(t['guan'])['yu_n']>=1 \
                    and (cs(t['bi']) or ben(t['bi'])>=2 or (ben(t['bi'])>=1 and stem(t['bi'])>=1)) \
                    and (d(t['cai'])['zhong_n']>=1 or d(t['cai'])['yu_n']>=1 or ben(t['cai'])>=1):
                # 比劫成势+官杀虚透只有余气根+财星有藏干根: 用财泄比劫生官杀(丁巳癸丑丁卯丙午: 必以丑中辛金为用, 泄劫生财)
                P(t['cai'],'BINGYAO','比劫成势官杀虚透只有余气根，财星有藏干根，用财泄比劫生官杀(丑中辛金为用)'); S(t['guan'],'财生官杀'); S(t['shi'],'食伤生财')
            elif stem(t['guan'])>=1 and (ben(t['guan'])>=1 or ling(t['guan']) in ('旺','相') or d(t['guan'])['zhong_n']+d(t['guan'])['yu_n']>=1):
                P(t['guan'],'FUYI','身旺官杀透干有根/有气，用官杀克身成权')"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('比劫成势官杀虚透财星藏干根用财修复完成')
