# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 移除对ten_god的引用
old = """        dayun_wx_list = [gan_wx, zhi_wx] if gan_wx and zhi_wx else ([gan_wx] if gan_wx else ([zhi_wx] if zhi_wx else []))
        # 大运十神列表(用于关键短语匹配)
        dayun_tg_list = [ten_god] if ten_god and ten_god != '未知' else []"""
new = """        dayun_wx_list = [gan_wx, zhi_wx] if gan_wx and zhi_wx else ([gan_wx] if gan_wx else ([zhi_wx] if zhi_wx else []))"""
c = c.replace(old, new)

# 移除十神匹配逻辑
old2 = """                    # 检查十神匹配
                    for tg in dayun_tg_list:
                        if tg in after or tg[:1] in after:
                            phrase_xi = True
                            break
                    # 检查天干地支匹配"""
new2 = """                    # 检查天干地支匹配"""
c = c.replace(old2, new2)

old3 = """                    for tg in dayun_tg_list:
                        if tg in after or tg[:1] in after:
                            phrase_ji = True
                            break
                    if gan in after or zhi in after or gz in after:"""
new3 = """                    if gan in after or zhi in after or gz in after:"""
c = c.replace(old3, new3)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('修复ten_god未定义bug')
