# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在仲冬调候路径增加水专旺排除条件
old = """        if primary is None and mz in MIDWINTER and stem('火')>=1 \\
                and not (cs(t['yin']) and not cs(t['guan']) and stem(t['guan'])==0 and cai_usable) \\
                and not (cs(t['shi']) and (cs(dmw) or ben(dmw)>=1 or stem(dmw)>=1)) \\
                and ('火' in (t['shi'],t['yin']) or tier in WANG_TIER or cs(dmw) or cs(t['guan'])):"""
new = """        _shui_zw_noqihou = dmw=='水' and (ben(t['bi'])>=3 or (ben(t['bi'])>=2 and stem(t['bi'])>=1)) and stem(t['shi'])>=1
        if primary is None and mz in MIDWINTER and stem('火')>=1 \\
                and not (cs(t['yin']) and not cs(t['guan']) and stem(t['guan'])==0 and cai_usable) \\
                and not (cs(t['shi']) and (cs(dmw) or ben(dmw)>=1 or stem(dmw)>=1)) \\
                and not _shui_zw_noqihou \\
                and ('火' in (t['shi'],t['yin']) or tier in WANG_TIER or cs(dmw) or cs(t['guan'])):"""

content = content.replace(old, new)

# 移除后面的调试print和重复的水专旺条件(因为现在在第305行就排除了)
old2 = """        # 水专旺(比劫成势+食伤透干)时用木泄秀, 不走调候火(甲申丙子癸亥癸亥润下格用甲木泄秀, 忌火调候激旺)
        _shui_zhuanwang = (ben(t['bi'])>=3 or (ben(t['bi'])>=2 and stem(t['bi'])>=1)) and stem(t['shi'])>=1 and dmw=='水'
        if dm=='癸' and mz=='子': print(f'DEBUG shui_zhuanwang: ben_bi={ben(t["bi"])}, stem_bi={stem(t["bi"])}, stem_shi={stem(t["shi"])}, dmw={dmw}, cond={_shui_zhuanwang}, primary={primary}')
        if primary is None and _shui_zhuanwang:
            P(t['shi'],'ZHUANWANG','润下水专旺成势，食伤木透干顺泄秀为奋发之机(水生木)，忌火调候激旺'); S(t['cai'],'木生火暖局')"""
new2 = """        # 水专旺(比劫成势+食伤透干)时用木泄秀(甲申丙子癸亥癸亥润下格用甲木泄秀, 仲冬调候已排除)
        _shui_zhuanwang = (ben(t['bi'])>=3 or (ben(t['bi'])>=2 and stem(t['bi'])>=1)) and stem(t['shi'])>=1 and dmw=='水'
        if primary is None and _shui_zhuanwang:
            P(t['shi'],'ZHUANWANG','润下水专旺成势，食伤木透干顺泄秀为奋发之机(水生木)'); S(t['cai'],'木生火暖局')"""

content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('仲冬调候水专旺排除+移除调试print完成')
