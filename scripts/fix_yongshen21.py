# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在仲冬调候路径前增加水专旺(比劫成势+食伤透干)时用木泄秀, 不走调候火(甲申丙子癸亥癸亥润下格用甲木泄秀)
old = """        # B6 调候兜底 / 扶抑
        # 印旺+财有气时优先财破印, 优先于仲冬调候(案例5丙申己亥庚辰戊寅亥月印旺用木破印, 不走调候火)"""
new = """        # B6 调候兜底 / 扶抑
        # 水专旺(比劫成势+食伤透干)时用木泄秀, 不走调候火(甲申丙子癸亥癸亥润下格用甲木泄秀, 忌火调候激旺)
        _shui_zhuanwang = (cs(t['bi']) or ben(t['bi'])>=3) and stem(t['shi'])>=1 and dmw=='水'
        if primary is None and _shui_zhuanwang:
            P(t['shi'],'ZHUANWANG','润下水专旺成势，食伤木透干顺泄秀为奋发之机(水生木)，忌火调候激旺'); S(t['cai'],'木生火暖局')
        # 印旺+财有气时优先财破印, 优先于仲冬调候(案例5丙申己亥庚辰戊寅亥月印旺用木破印, 不走调候火)"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('水专旺用木泄秀修复完成')
