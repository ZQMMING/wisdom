# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在用神十神类型计算后增加用神力量占比计算
old = """        elif KE_ME.get(dmw) == primary_wx:
            primary_ten_god_type = '官杀'
    
    per_step = []"""
new = """        elif KE_ME.get(dmw) == primary_wx:
            primary_ten_god_type = '官杀'
    
    # V2.7: 计算用神在原局中的力量占比 # PCT-MARK: 用神力量占比, 用于判断用神强弱
    primary_power_ratio = 0.0
    if wpo and primary and 'wuxing_power' in wpo:
        wp = wpo['wuxing_power']
        total_all = sum(v.get('total', 0) for v in wp.values())
        if total_all > 0:
            primary_power_ratio = wp.get(primary, {}).get('total', 0) / total_all
    
    per_step = []"""
c = c.replace(old, new)

# 在主标签判断逻辑中增加用神力量修正
old2 = """        if has_xi:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif has_ji:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
new2 = """        # V2.7: 用神力量修正 # PCT-MARK: 用神弱(<15%)时生扶更喜, 用神强(>30%)时克泄可能为喜
        primary_weak = primary_power_ratio < 0.15 if primary_power_ratio > 0 else False
        primary_strong = primary_power_ratio > 0.30 if primary_power_ratio > 0 else False
        
        if has_xi and has_ji:
            # 生扶和克泄同时存在: 用神弱则生扶, 用神强则克泄, 否则生扶优先
            if primary_weak:
                xiji_label = 'SUPPORT_USE_GOD'
            elif primary_strong:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'
        elif has_xi:
            xiji_label = 'SUPPORT_USE_GOD'
        elif has_ji:
            # 只有克泄: 用神强时可能是抑制过强(为喜)
            if primary_strong:
                xiji_label = 'SUPPORT_USE_GOD'
            else:
                xiji_label = 'SUPPRESS_USE_GOD'
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V3.3'", "'module': 'DAYUN_XIJI_V3.4'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V3.4优化完成(增加用神力量修正)')
