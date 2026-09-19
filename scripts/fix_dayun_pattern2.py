# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在格局判断部分增加其他格局的判断
old = """    is_shangguan_peiyin = is_shangguan_month and len(yin_stems) > 0 and yin_has_root
    
    per_step = []"""

new = """    is_shangguan_peiyin = is_shangguan_month and len(yin_stems) > 0 and yin_has_root
    
    # V3.9: 其他格局判断 (基于子平真诠取运规则)
    # 正官格: 月令本气是正官(克日主的异性五行)
    is_zhengguan_month = False
    guan_wx = KE_ME.get(dm_wx_local, '')  # 克日主的五行=官杀
    if month_benqi_wx == guan_wx:
        dm_yang = dm in '甲丙戊庚壬'
        mb_yang = month_benqi in '甲丙戊庚壬'
        if dm_yang != mb_yang:  # 异性=正官
            is_zhengguan_month = True
    # 正官格用财: 财星透干有根
    cai_wx = KE.get(dm_wx_local, '')  # 日主克的五行=财
    cai_stems = []
    for pos in ['year', 'month', 'day', 'hour']:
        stem = pillars[pos][0]
        if WX.get(stem, '') == cai_wx:
            cai_stems.append(stem)
    cai_has_root = False
    for pos in ['year', 'month', 'day', 'hour']:
        branch = pillars[pos][1]
        hidden = HIDDEN_STEMS.get(branch, [])
        for h in hidden:
            if WX.get(h, '') == cai_wx:
                cai_has_root = True
                break
        if cai_has_root:
            break
    is_zhengguan_yongcai = is_zhengguan_month and len(cai_stems) > 0 and cai_has_root
    
    # 食神格: 月令本气是食神(日主生的同性五行)
    is_shishen_month = False
    if SHENG.get(dm_wx_local) == month_benqi_wx:
        dm_yang = dm in '甲丙戊庚壬'
        mb_yang = month_benqi in '甲丙戊庚壬'
        if dm_yang == mb_yang:  # 同性=食神
            is_shishen_month = True
    is_shishen_shengcai = is_shishen_month and len(cai_stems) > 0 and cai_has_root
    
    # 财格: 月令本气是财
    is_cai_month = (month_benqi_wx == cai_wx)
    # 财格生官: 官星透干有根
    guan_stems = []
    for pos in ['year', 'month', 'day', 'hour']:
        stem = pillars[pos][0]
        if WX.get(stem, '') == guan_wx:
            guan_stems.append(stem)
    guan_has_root = False
    for pos in ['year', 'month', 'day', 'hour']:
        branch = pillars[pos][1]
        hidden = HIDDEN_STEMS.get(branch, [])
        for h in hidden:
            if WX.get(h, '') == guan_wx:
                guan_has_root = True
                break
        if guan_has_root:
            break
    is_cai_shengguan = is_cai_month and len(guan_stems) > 0 and guan_has_root
    
    # 印格: 月令本气是印
    is_yin_month = (month_benqi_wx == yin_wx)
    # 印格用官: 官星透干有根
    is_yin_yongguan = is_yin_month and len(guan_stems) > 0 and guan_has_root
    
    # 阳刃格: 月令是阳刃(阳干的帝旺位)
    YANG_REN = {'甲':'卯', '丙':'午', '戊':'午', '庚':'酉', '壬':'子'}
    is_yangren_month = (dm in YANG_REN and month_branch_main == YANG_REN[dm])
    
    per_step = []"""
c = c.replace(old, new)

# 在has_xi/has_ji条件中增加其他格局的喜忌判断
old2 = """        # V3.8: 伤官佩印格中官星为喜 (官杀生印→印生身, 流通有情)
        shangguan_peiyin_guanxi = False
        if is_shangguan_peiyin:
            # 官星五行: 克日主的五行
            guan_wx = KE_ME.get(dm_wx_local, '')
            if gan_wx == guan_wx or zhi_wx == guan_wx:
                shangguan_peiyin_guanxi = True
        
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations or shangguan_peiyin_guanxi)
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or 'GAN_PRIMARY_SHENG' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations)"""

new2 = """        # V3.8: 伤官佩印格中官星为喜 (官杀生印→印生身, 流通有情)
        shangguan_peiyin_guanxi = False
        if is_shangguan_peiyin:
            if gan_wx == guan_wx or zhi_wx == guan_wx:
                shangguan_peiyin_guanxi = True
        
        # V3.9: 其他格局层面喜忌判断
        pattern_xi = False
        pattern_ji = False
        # 正官格用财: 食伤为忌(食伤克官星)
        if is_zhengguan_yongcai:
            shishang_wx = SHENG.get(dm_wx_local, '')
            if gan_wx == shishang_wx or zhi_wx == shishang_wx:
                pattern_ji = True
        # 食神格生财: 官煞为忌(官煞克食神)
        if is_shishen_shengcai:
            if gan_wx == guan_wx or zhi_wx == guan_wx:
                pattern_ji = True
        # 财格生官: 七煞伤官为忌
        if is_cai_shengguan:
            shishang_wx = SHENG.get(dm_wx_local, '')
            if gan_wx == shishang_wx or zhi_wx == shishang_wx:
                pattern_ji = True
        # 印格用官: 财运反吉(财生官→官生印)
        if is_yin_yongguan:
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_xi = True
        # 阳刃格: 财乡为喜(财生官煞制刃)
        if is_yangren_month:
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_xi = True
        
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations or shangguan_peiyin_guanxi or pattern_xi)
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or 'GAN_PRIMARY_SHENG' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations or pattern_ji)"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V3.8'", "'module': 'DAYUN_XIJI_V3.9'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V3.9完成(增加正官格/食神格/财格/印格/阳刃格的格局层面喜忌判断)')
