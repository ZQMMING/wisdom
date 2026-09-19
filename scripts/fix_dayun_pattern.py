# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在函数开头增加格局判断
old = """    per_step = []
    for gz in dayun_list:"""

new = """    # V3.8: 格局层面喜忌判断 (基于子平真诠各格局取运规则)
    # 判断伤官佩印格: 月令伤官 + 印星透干有根
    month_branch_main = pillars['month'][1]
    month_hidden = HIDDEN_STEMS.get(month_branch_main, [])
    # 月令本气对应的十神
    dm_wx_local = WX.get(dm, '')
    month_benqi = month_hidden[0] if month_hidden else ''
    month_benqi_wx = WX.get(month_benqi, '')
    # 判断月令是否是伤官(日主生的异性五行)
    is_shangguan_month = False
    if month_benqi_wx and dm_wx_local:
        # 伤官: 日主生的异性五行 (如甲木生丁火=伤官, 甲木生丙火=食神)
        if SHENG.get(dm_wx_local) == month_benqi_wx:
            dm_yang = dm in '甲丙戊庚壬'
            mb_yang = month_benqi in '甲丙戊庚壬'
            if dm_yang != mb_yang:  # 异性=伤官
                is_shangguan_month = True
    # 判断印星是否透干有根
    yin_stems = []
    yin_wx = SHENG_ME.get(dm_wx_local, '')  # 生日主的五行=印
    for pos in ['year', 'month', 'day', 'hour']:
        stem = pillars[pos][0]
        if WX.get(stem, '') == yin_wx:
            yin_stems.append(stem)
    # 印星有根: 地支中有印星五行的藏干
    yin_has_root = False
    for pos in ['year', 'month', 'day', 'hour']:
        branch = pillars[pos][1]
        hidden = HIDDEN_STEMS.get(branch, [])
        for h in hidden:
            if WX.get(h, '') == yin_wx:
                yin_has_root = True
                break
        if yin_has_root:
            break
    is_shangguan_peiyin = is_shangguan_month and len(yin_stems) > 0 and yin_has_root
    
    per_step = []
    for gz in dayun_list:"""
c = c.replace(old, new)

# 在has_xi条件中增加伤官佩印格官星为喜的判断
old2 = """        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations)"""
new2 = """        # V3.8: 伤官佩印格中官星为喜 (官杀生印→印生身, 流通有情)
        shangguan_peiyin_guanxi = False
        if is_shangguan_peiyin:
            # 官星五行: 克日主的五行
            guan_wx = KE_ME.get(dm_wx_local, '')
            if gan_wx == guan_wx or zhi_wx == guan_wx:
                shangguan_peiyin_guanxi = True
        
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations or shangguan_peiyin_guanxi)"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V3.7'", "'module': 'DAYUN_XIJI_V3.8'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V3.8完成(增加伤官佩印格官星为喜的格局层面判断)')
