# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复1: 身旺扶抑路径中的条件, 把zhong_n==0去掉, 改为ben==0且有中气/余气根
old1 = """            elif stem(t['guan'])>=1 and ben(t['guan'])==0 and d(t['guan'])['zhong_n']==0 and d(t['guan'])['yu_n']>=1                     and (cs(t['bi']) or ben(t['bi'])>=2 or (ben(t['bi'])>=1 and stem(t['bi'])>=1))                     and (d(t['cai'])['zhong_n']>=1 or d(t['cai'])['yu_n']>=1 or ben(t['cai'])>=1):"""
new1 = """            elif stem(t['guan'])>=1 and ben(t['guan'])==0 and (d(t['guan'])['zhong_n']>=1 or d(t['guan'])['yu_n']>=1) \
                    and (cs(t['bi']) or ben(t['bi'])>=2 or (ben(t['bi'])>=1 and stem(t['bi'])>=1)) \
                    and (d(t['cai'])['zhong_n']>=1 or d(t['cai'])['yu_n']>=1 or ben(t['cai'])>=1):"""
content = content.replace(old1, new1)

# 修复2: 官杀制化路径else分支中的条件, 同样修改
old2 = """                        elif ben(t['guan'])==0 and d(t['guan'])['zhong_n']==0 and d(t['guan'])['yu_n']>=1 \\
                                and (cs(t['bi']) or ben(t['bi'])>=2 or (ben(t['bi'])>=1 and stem(t['bi'])>=1)) \\
                                and (d(t['cai'])['zhong_n']>=1 or d(t['cai'])['yu_n']>=1 or ben(t['cai'])>=1):"""
new2 = """                        elif ben(t['guan'])==0 and (d(t['guan'])['zhong_n']>=1 or d(t['guan'])['yu_n']>=1) \\
                                and (cs(t['bi']) or ben(t['bi'])>=2 or (ben(t['bi'])>=1 and stem(t['bi'])>=1)) \\
                                and (d(t['cai'])['zhong_n']>=1 or d(t['cai'])['yu_n']>=1 or ben(t['cai'])>=1):"""
content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('官杀无本气根条件修复完成(ben==0且有中气/余气根)')
