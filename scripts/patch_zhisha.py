# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()

old1=("                if tier in WANG_TIER:\n"
      "                    if zhi_ok:\n"
      "                        P(t['shi'],'BINGYAO','官杀成势身旺，食伤制杀')\n")
new1=("                _zhuan_shi=False\n"
      "                if tier in WANG_TIER:\n"
      "                    if zhi_ok and ben(t['guan'])==0 and ling(t['shi'])=='旺':\n"
      "                        # 身旺(旺极/太旺)+食伤当令+官杀虚透无根=伤官去官/食伤泄秀(L1080戊午壬戌丁卯癸卯):\n"
      "                        # 比劫生食伤顺泄帮身、食伤生财为喜; 虚官被去岁运犯旺、印克食伤(莫作用印)为忌\n"
      "                        P(t['shi'],'BINGYAO','身旺食伤当令、官杀虚透无根，伤官去官、食伤泄秀生财'); S(t['bi'],'比劫生食伤帮身任泄'); S(t['cai'],'食伤生财'); A(t['guan'],'虚官被去、岁运犯旺凶'); A(t['yin'],'印克食伤、莫作用印'); _zhuan_shi=True\n"
      "                    elif zhi_ok:\n"
      "                        P(t['shi'],'BINGYAO','官杀成势身旺，食伤制杀')\n")
assert s.count(old1)==1,('o1',s.count(old1)); s=s.replace(old1,new1)

old2=("                elif zhi_ok:\n"
      "                    P(t['shi'],'BINGYAO','印无力而食伤透根，食伤制杀'); S(t['yin'])\n")
new2=("                elif zhi_ok and (ben(t['shi'])>=1 or cs(t['shi'])):\n"
      "                    # 食伤自有本气根/成势, 制杀有力专美(儿能救母 L1744甲申丙寅甲申庚午): 枭印夺食破格忌印, 食伤生财喜财, 比劫帮身任制\n"
      "                    P(t['shi'],'BINGYAO','食伤透根制杀有力(儿能救母)，专食伤制杀'); S(t['cai'],'食伤生财、制杀后官为用'); S(t['bi'],'帮身任制'); A(t['yin'],'枭印夺食破格'); _zhuan_shi=True\n"
      "                elif zhi_ok:\n"
      "                    P(t['shi'],'BINGYAO','印无力而食伤无根，食伤制杀待印化'); S(t['yin'])\n")
assert s.count(old2)==1,('o2',s.count(old2)); s=s.replace(old2,new2)

old3="                if primary!=t['cai']: A(t['cai'])  # 财滋弱杀以财为用不忌财; 余制化忌财坏印生杀\n"
new3="                if primary!=t['cai'] and not _zhuan_shi: A(t['cai'])  # 财滋弱杀以财为用不忌财; 制杀专食伤/伤官去官则食伤生财喜财; 余制化忌财坏印生杀\n"
assert s.count(old3)==1,('o3',s.count(old3)); s=s.replace(old3,new3)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('伤官去官/食伤制杀专食伤细分 done')
