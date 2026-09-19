# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 1. 在zhi_ok之前定义_tigang_buzhao变量
old1 = """                yin_he = d(t['yin']).get('banhe_n',0)>=1 or BRANCH_WX.get(dz)==t['yin']
                hua_ok=stem(t['yin'])>=1 or ling(t['yin'])=='旺' or ben(t['yin'])>=2 or (ben(t['yin'])>=1 and yin_he)
                _zhuan_shi=False"""
new1 = """                yin_he = d(t['yin']).get('banhe_n',0)>=1 or BRANCH_WX.get(dz)==t['yin']
                hua_ok=stem(t['yin'])>=1 or ling(t['yin'])=='旺' or ben(t['yin'])>=2 or (ben(t['yin'])>=1 and yin_he)
                _zhuan_shi=False
                # 提纲不照: 月干不是月令本气五行, 印星透干有根(庚申戊寅壬子甲辰: 寅月本气甲木不透(月干戊), 庚金透干为用)
                _month_stem_tg = pillars['month'][0]
                _month_benqi_wx_tg = BRANCH_WX.get(mz)
                _tigang_buzhao = bool(_month_benqi_wx_tg) and _ganwx.get(_month_stem_tg)!=_month_benqi_wx_tg and stem(t['yin'])>=1 and (ben(t['yin'])>=1 or ling(t['yin']) in ('旺','相'))"""
content = content.replace(old1, new1)

# 2. 修改else分支, 增加提纲不照用印
old2 = """                    else:
                        P(t['guan'],'BINGYAO','身旺官杀透，任官杀克身成权(待根/财滋)'); S(t['cai'],'财滋官杀')"""
new2 = """                    else:
                        if _tigang_buzhao:
                            P(t['yin'],'BINGYAO','提纲不照：月令本气不透，印星透干有根为用(透金为用神)'); S(t['bi'],'比劫帮身')
                        else:
                            P(t['guan'],'BINGYAO','身旺官杀透，任官杀克身成权(待根/财滋)'); S(t['cai'],'财滋官杀')"""
content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('提纲不照变量定义和else分支修复完成')
