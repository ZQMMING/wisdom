# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

old = """                elif zhi_ok and (ben(t['shi'])>=1 or cs(t['shi'])):
                    # 食伤自有本气根/成势, 制杀有力专美(儿能救母 L1744甲申丙寅甲申庚午): 枭印夺食破格忌印, 食伤生财喜财, 比劫帮身任制
                    P(t['shi'],'BINGYAO','食伤透根制杀有力(儿能救母)，专食伤制杀'); S(t['cai'],'食伤生财、制杀后官为用'); S(t['bi'],'帮身任制'); A(t['yin'],'枭印夺食破格'); _zhuan_shi=True"""

new = """                elif zhi_ok and (ben(t['shi'])>=1 or cs(t['shi'])) and not (cs(t['guan']) and ben(dmw)>=1 and stem(t['bi'])==0):
                    # 食伤自有本气根/成势, 制杀有力专美(儿能救母 L1744甲申丙寅甲申庚午): 枭印夺食破格忌印, 食伤生财喜财, 比劫帮身任制
                    # 排除: 官杀成势且日主有本气根但无比劫透干, 此时应优先比劫帮身任官杀(原文"用神必在酉金")
                    P(t['shi'],'BINGYAO','食伤透根制杀有力(儿能救母)，专食伤制杀'); S(t['cai'],'食伤生财、制杀后官为用'); S(t['bi'],'帮身任制'); A(t['yin'],'枭印夺食破格'); _zhuan_shi=True
                elif zhi_ok and cs(t['guan']) and ben(dmw)>=1 and stem(t['bi'])==0:
                    # 官杀成势+日主有本气根+无比劫透干: 比劫帮身任官杀为用(原文"用神必在酉金" 丁巳壬子辛巳丁酉)
                    P(t['bi'],'BINGYAO','官杀成势日主有根但无比劫透干，比劫帮身任官杀为用'); S(t['yin'],'印化杀生身'); S(t['shi'],'食伤制杀为喜'); A(t['cai'],'财生官杀助旺')"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('用神引擎案例1修复完成')
