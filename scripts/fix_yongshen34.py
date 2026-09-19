# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在官杀制化路径else分支中增加: 比劫成势+官杀虚透只有余气根+财星有藏干根→用财(丁巳癸丑丁卯丙午)
old = """                    else:
                        if _tigang_buzhao:
                            P(t['yin'],'BINGYAO','提纲不照：月令本气不透，印星透干有根为用(透金为用神)'); S(t['bi'],'比劫帮身')
                        else:
                            P(t['guan'],'BINGYAO','身旺官杀透，任官杀克身成权(待根/财滋)'); S(t['cai'],'财滋官杀')"""

new = """                    else:
                        if _tigang_buzhao:
                            P(t['yin'],'BINGYAO','提纲不照：月令本气不透，印星透干有根为用(透金为用神)'); S(t['bi'],'比劫帮身')
                        elif ben(t['guan'])==0 and d(t['guan'])['zhong_n']==0 and d(t['guan'])['yu_n']>=1 \
                                and (cs(t['bi']) or ben(t['bi'])>=2 or (ben(t['bi'])>=1 and stem(t['bi'])>=1)) \
                                and (d(t['cai'])['zhong_n']>=1 or d(t['cai'])['yu_n']>=1 or ben(t['cai'])>=1):
                            # 比劫成势+官杀虚透只有余气根+财星有藏干根: 用财泄比劫生官杀(丁巳癸丑丁卯丙午: 必以丑中辛金为用, 泄劫生财)
                            P(t['cai'],'BINGYAO','比劫成势官杀虚透只有余气根，财星有藏干根，用财泄比劫生官杀(丑中辛金为用)'); S(t['guan'],'财生官杀'); S(t['shi'],'食伤生财')
                        else:
                            P(t['guan'],'BINGYAO','身旺官杀透，任官杀克身成权(待根/财滋)'); S(t['cai'],'财滋官杀')"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('官杀制化路径else分支增加比劫成势财星藏干根用财完成')
