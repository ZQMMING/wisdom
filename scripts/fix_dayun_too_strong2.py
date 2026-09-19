# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在格局判断部分增加用神本气根的判断 (使用正确的变量名primary)
old = """    # 阳刃格: 月令是阳刃(阳干的帝旺位)
    YANG_REN = {'甲':'卯', '丙':'午', '戊':'午', '庚':'酉', '壬':'子'}
    is_yangren_month = (dm in YANG_REN and month_branch_main == YANG_REN[dm])
    
    per_step = []"""

new = """    # 阳刃格: 月令是阳刃(阳干的帝旺位)
    YANG_REN = {'甲':'卯', '丙':'午', '戊':'午', '庚':'酉', '壬':'子'}
    is_yangren_month = (dm in YANG_REN and month_branch_main == YANG_REN[dm])
    
    # V4.1: 用神本气根判断 (用于用神过旺反忌)
    use_god_benqi_root = False
    if primary:
        for pos in ['year', 'month', 'day', 'hour']:
            branch = pillars[pos][1]
            hidden = HIDDEN_STEMS.get(branch, [])
            if hidden and WX.get(hidden[0], '') == primary:
                use_god_benqi_root = True
                break
    
    per_step = []"""
c = c.replace(old, new)

# 在has_xi/has_ji条件中增加用神过旺反忌的判断
old2 = """        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations or shangguan_peiyin_guanxi or pattern_xi)
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or 'GAN_PRIMARY_SHENG' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations or pattern_ji)"""

new2 = """        # V4.1: 用神过旺反忌判断
        # 如果原局已经有用神的本气根, 再行用神大运(天干地支都是用神五行), 可能反忌
        use_god_too_strong = False
        if use_god_benqi_root and primary:
            if gan_wx == primary and zhi_wx == primary:
                use_god_too_strong = True
        
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations or shangguan_peiyin_guanxi or pattern_xi)
        # 用神过旺反忌: 如果用神过旺, 则has_xi被覆盖
        if use_god_too_strong:
            has_xi = False
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or 'GAN_PRIMARY_SHENG' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations or pattern_ji or use_god_too_strong)"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.0'", "'module': 'DAYUN_XIJI_V4.1'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.1完成(增加用神过旺反忌判断:原局有用神本气根+大运干支都是用神五行则反忌)')
