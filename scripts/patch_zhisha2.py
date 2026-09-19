# -*- coding: utf-8 -*-
# gs_bing 制化块两修:
# (1) zhi_ok 增"食伤透干坐中气长生根 + 日主有本气禄根能任制"一路(L753 庚申庚辰甲戌丙寅:
#     丙火独透坐寅长生、甲归时禄, 制杀扶身; 原只认本气根/成局致误取印待运 P水, 应 P火食伤制杀)
# (2) 专食伤"枭印夺食A印"仅限身旺能任; 身弱(无本气根)杀成局时食伤制杀与印化杀并行,
#     印化杀扶身同为喜、不夺食(L756 壬子壬子丙戌戊戌: 戊土制杀 P, 乙卯印杀印相生仕郡守)。
#     身旺专食伤A印保持(L1744 壬申印夺食不禄, 甲生寅月有本气禄 ben(dmw)>=1)。
import io
fp=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(fp,encoding='utf-8').read()

# (1) zhi_ok 增中气长生根+身本气禄
old1="                zhi_ok=stem(t['shi'])>=1 and qi(t['shi']) and (tier in WANG_TIER or ben(t['shi'])>=1 or cs(t['shi']) or _dm_root_ok)"
assert s.count(old1)==1, ('1',s.count(old1))
new1="""                zhi_ok=stem(t['shi'])>=1 and qi(t['shi']) and (tier in WANG_TIER or ben(t['shi'])>=1 or cs(t['shi']) or _dm_root_ok
                         or (stem(t['shi'])>=1 and d(t['shi']).get('zhong_n',0)>=1 and ben(dmw)>=1))"""
s=s.replace(old1,new1)

# (2) line321 专食伤前插身弱杀成局制化并行
old2="""                elif zhi_ok and (ben(t['shi'])>=1 or cs(t['shi'])):
                    # 食伤自有本气根/成势, 制杀有力专美(儿能救母 L1744甲申丙寅甲申庚午): 枭印夺食破格忌印, 食伤生财喜财, 比劫帮身任制
                    P(t['shi'],'BINGYAO','食伤透根制杀有力(儿能救母)，专食伤制杀'); S(t['cai'],'食伤生财、制杀后官为用'); S(t['bi'],'帮身任制'); A(t['yin'],'枭印夺食破格'); _zhuan_shi=True"""
assert s.count(old2)==1, ('2',s.count(old2))
new2="""                elif zhi_ok and (ben(t['shi'])>=1 or cs(t['shi'])) and tier in SHUAI_TIER and ben(dmw)==0 \\
                        and (ben(t['guan'])>=2 or cs(t['guan']) or (stem(t['guan'])>=2 and ben(t['guan'])>=1)):
                    # 身弱(无本气根)杀成局、食伤制杀: 制化并行, 印化杀扶身同为喜(不夺食), 比劫帮身(L756 戊土制杀、乙卯印杀印相生仕郡守)
                    P(t['shi'],'BINGYAO','身弱杀成局、食伤制杀，制化并行'); S(t['yin'],'印化杀扶身(制化并行不夺食)')
                    S(t['bi'],'帮身任制'); S(t['cai'],'食伤生财'); _zhuan_shi=True
                elif zhi_ok and (ben(t['shi'])>=1 or cs(t['shi'])):
                    # 食伤自有本气根/成势, 制杀有力专美(儿能救母 L1744甲申丙寅甲申庚午): 枭印夺食破格忌印, 食伤生财喜财, 比劫帮身任制
                    P(t['shi'],'BINGYAO','食伤透根制杀有力(儿能救母)，专食伤制杀'); S(t['cai'],'食伤生财、制杀后官为用'); S(t['bi'],'帮身任制'); A(t['yin'],'枭印夺食破格'); _zhuan_shi=True"""
s=s.replace(old2,new2)

io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched zhisha2 (L753 zhongqi root + L756 zhihua bingxing)')
