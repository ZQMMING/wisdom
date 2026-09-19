# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复案例2: 官杀不成势且食伤太旺(ben>=3)时, 应用印制食伤扶身, 而非食伤制杀
old1 = """                elif zhi_ok and (ben(t['shi'])>=1 or cs(t['shi'])) and not (cs(t['guan']) and ben(dmw)>=1 and stem(t['bi'])==0):
                    # 食伤自有本气根/成势, 制杀有力专美(儿能救母 L1744甲申丙寅甲申庚午): 枭印夺食破格忌印, 食伤生财喜财, 比劫帮身任制
                    # 排除: 官杀成势且日主有本气根但无比劫透干, 此时应优先比劫帮身任官杀(原文"用神必在酉金")
                    P(t['shi'],'BINGYAO','食伤透根制杀有力(儿能救母)，专食伤制杀'); S(t['cai'],'食伤生财、制杀后官为用'); S(t['bi'],'帮身任制'); A(t['yin'],'枭印夺食破格'); _zhuan_shi=True"""

new1 = """                elif zhi_ok and (ben(t['shi'])>=1 or cs(t['shi'])) and not (cs(t['guan']) and ben(dmw)>=1 and stem(t['bi'])==0) and not (not cs(t['guan']) and ben(t['shi'])>=3):
                    # 食伤自有本气根/成势, 制杀有力专美(儿能救母 L1744甲申丙寅甲申庚午): 枭印夺食破格忌印, 食伤生财喜财, 比劫帮身任制
                    # 排除1: 官杀成势且日主有本气根但无比劫透干, 此时应优先比劫帮身任官杀(原文"用神必在酉金")
                    # 排除2: 官杀不成势且食伤太旺(ben>=3), 此时应用印制食伤扶身(原文"用神在土不在火也" 丁亥壬子庚子辛巳)
                    P(t['shi'],'BINGYAO','食伤透根制杀有力(儿能救母)，专食伤制杀'); S(t['cai'],'食伤生财、制杀后官为用'); S(t['bi'],'帮身任制'); A(t['yin'],'枭印夺食破格'); _zhuan_shi=True
                elif zhi_ok and not cs(t['guan']) and ben(t['shi'])>=3:
                    # 官杀不成势+食伤太旺(ben>=3): 印制食伤扶身为用(原文"用神在土，不在火也" 丁亥壬子庚子辛巳)
                    P(t['yin'],'BINGYAO','官杀不成势食伤太旺，印制食伤扶身为用'); S(t['bi'],'比劫帮身'); A(t['shi'],'食伤太旺为病'); A(t['cai'],'财生官杀')"""

content = content.replace(old1, new1)

# 修复案例5: hua_ok(印化杀)路径应增加官杀重的判断, 官杀不重时不应印化杀
old2 = """                elif hua_ok:
                    P(t['yin'],'BINGYAO','官杀重身弱/中和，印化杀生身(杀印相生)'); S(t['bi'])"""

new2 = """                elif hua_ok and (cs(t['guan']) or stem(t['guan'])>=2 or (stem(t['guan'])>=1 and ben(t['guan'])>=1)):
                    # 官杀重+印透有气: 印化杀生身(杀印相生)
                    P(t['yin'],'BINGYAO','官杀重身弱/中和，印化杀生身(杀印相生)'); S(t['bi'])"""

content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('用神引擎案例2+案例5修复完成')
