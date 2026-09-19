# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在函数开头增加用神十神类型计算
old = """    primary = yongshen_result.get('yongshen_primary') or ''
    secondary = yongshen_result.get('yongshen_secondary') or []
    avoid = yongshen_result.get('yongshen_avoid') or []"""

new = """    primary = yongshen_result.get('yongshen_primary') or ''
    secondary = yongshen_result.get('yongshen_secondary') or []
    avoid = yongshen_result.get('yongshen_avoid') or []
    
    # V3.3: 计算用神的十神类型(通过日主天干和用神五行)
    primary_ten_god_type = ''
    if primary and dm:
        dmw = WX.get(dm, '')
        primary_wx = primary
        dm_yang = dm in '甲丙戊庚壬'
        if primary_wx == dmw:
            primary_ten_god_type = '比劫'
        elif SHENG.get(primary_wx) == dmw:
            primary_ten_god_type = '印'
        elif SHENG.get(dmw) == primary_wx:
            primary_ten_god_type = '食伤'
        elif KE.get(dmw) == primary_wx:
            primary_ten_god_type = '财'
        elif KE_ME.get(dmw) == primary_wx:
            primary_ten_god_type = '官杀'"""
c = c.replace(old, new)

# 在综合判断逻辑中增加十神关系判断
old2 = """        # V3.2: 多标签输出 - 一个大运可能同时具有多种喜忌属性
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any)
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any)
        xiji_labels = []"""

new2 = """        # V3.3: 十神关系判断 - 大运十神与用神十神的生克关系
        ten_god_xi = False
        ten_god_ji = False
        if primary_ten_god_type and ten_god != '未知':
            # 十神生克关系: 比劫生食伤, 食伤生财, 财生官杀, 官杀生印, 印生比劫
            sheng_chain = {'比劫': '食伤', '食伤': '财', '财': '官杀', '官杀': '印', '印': '比劫'}
            ke_chain = {'比劫': '财', '财': '印', '印': '食伤', '食伤': '官杀', '官杀': '比劫'}
            # 大运十神生用神十神 -> 喜
            if sheng_chain.get(ten_god) == primary_ten_god_type:
                ten_god_xi = True
            # 大运十神克用神十神 -> 忌
            if ke_chain.get(ten_god) == primary_ten_god_type:
                ten_god_ji = True
        
        # V3.2: 多标签输出 - 一个大运可能同时具有多种喜忌属性
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi)
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji)
        xiji_labels = []"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V3.2'", "'module': 'DAYUN_XIJI_V3.3'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V3.3优化完成(增加十神关系判断)')
