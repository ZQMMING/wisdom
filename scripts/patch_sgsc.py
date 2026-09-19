# -*- coding: utf-8 -*-
# 伤官生财顺用: 食伤当令+身有重根(燥厚)+财透有根 -> 伤官生财、财生官流通, 财喜不忌
# 原典: 《子平真诠》伤官格喜财(伤官生财); 《滴天髓》L887 壬戌己酉戊戌乙卯
#   "戊日酉月土金伤官,地支两戌燥而且厚,妙年干壬水,润土泄金而生木,足以用官;壬子早遂仕路,甲寅乙卯仕至侍郎"
# 区别于 line329 制化忌财(财坏印生杀): 那是印化杀路径; 伤官当令身旺顺泄生财不忌财。
import io
fp=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(fp,encoding='utf-8').read()
old="""                elif ben(dmw)>=2 and not hua_ok:
                    P(t['shi'],'BINGYAO','官杀重而身有重根、印无气，食伤制杀为美(生局须食)'); S(t['yin'])"""
assert s.count(old)==1, s.count(old)
new="""                elif ben(dmw)>=2 and not hua_ok and ling(t['shi'])=='旺' and stem(t['cai'])>=1 \\
                        and (dry or ben(t['cai'])>=1 or cs(t['cai'])):
                    # 伤官当令身旺(燥厚)、财透有根: 伤官生财顺用, 财泄食伤生官、润燥通关(L887 壬水润土泄金生木用官)
                    P(t['shi'],'BINGYAO','伤官当令身旺、财透，伤官生财、财生官流通(燥厚喜财润燥)')
                    S(t['cai'],'伤官生财、润燥'); S(t['guan'],'财生官'); _zhuan_shi=True
                elif ben(dmw)>=2 and not hua_ok:
                    P(t['shi'],'BINGYAO','官杀重而身有重根、印无气，食伤制杀为美(生局须食)'); S(t['yin'])"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched shangguan shengcai')
