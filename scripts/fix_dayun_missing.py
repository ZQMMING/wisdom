# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在用神力量计算后增加原局缺少五行计算
old = """    # V2.7: 计算用神在原局中的力量占比 # PCT-MARK: 用神力量占比, 用于判断用神强弱
    primary_power_ratio = 0.0
    if wpo and primary and 'wuxing_power' in wpo:
        wp = wpo['wuxing_power']
        total_all = sum(v.get('total', 0) for v in wp.values())
        if total_all > 0:
            primary_power_ratio = wp.get(primary, {}).get('total', 0) / total_all
    
    per_step = []"""
new = """    # V2.7: 计算用神在原局中的力量占比 # PCT-MARK: 用神力量占比, 用于判断用神强弱
    primary_power_ratio = 0.0
    # V2.9: 计算原局缺少的五行(力量为0或极低)
    missing_wuxing = []
    if wpo and 'wuxing_power' in wpo:
        wp = wpo['wuxing_power']
        total_all = sum(v.get('total', 0) for v in wp.values())
        if total_all > 0:
            primary_power_ratio = wp.get(primary, {}).get('total', 0) / total_all
            for wx, v in wp.items():
                if v.get('total', 0) < 0.5:  # 力量极低, 视为缺少
                    missing_wuxing.append(wx)
    
    per_step = []"""
c = c.replace(old, new)

# 在综合判断前增加大运补充缺少五行判断
old2 = """        # V2.8: 用神力量修正扩大范围 # PCT-MARK: 用神弱(<15%)时生扶更喜, 用神强(>30%)时克泄可能为喜
        primary_weak = primary_power_ratio < 0.15 if primary_power_ratio > 0 else False
        primary_strong = primary_power_ratio > 0.30 if primary_power_ratio > 0 else False
        
        # 综合判断: 用神力量+计数+关系综合决定"""
new2 = """        # V2.8: 用神力量修正扩大范围 # PCT-MARK: 用神弱(<15%)时生扶更喜, 用神强(>30%)时克泄可能为喜
        primary_weak = primary_power_ratio < 0.15 if primary_power_ratio > 0 else False
        primary_strong = primary_power_ratio > 0.30 if primary_power_ratio > 0 else False
        
        # V2.9: 大运补充原局缺少五行判断
        dayun_gan_wx = GAN_WX.get(gan, '')
        dayun_zhi_wx = ZHI_WX.get(zhi, '')
        dayun_supports_missing = (dayun_gan_wx in missing_wuxing) or (dayun_zhi_wx in missing_wuxing)
        
        # 综合判断: 用神力量+计数+关系+缺少五行综合决定"""
c = c.replace(old2, new2)

# 修改综合判断逻辑, 增加缺少五行判断
old3 = """        elif has_xi:
            # 只有生扶: 用神强时可能过犹不及, 但仍以生扶为喜(保守)
            xiji_label = 'SUPPORT_USE_GOD'
        elif has_ji:
            # 只有克泄: 用神强时可能是抑制过强(为喜), 用神弱时为忌
            if primary_strong:
                xiji_label = 'SUPPORT_USE_GOD'  # 用神强, 克泄抑制过强, 反为喜
            else:
                xiji_label = 'SUPPRESS_USE_GOD'
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
new3 = """        elif has_xi:
            # 只有生扶: 用神强时可能过犹不及, 但仍以生扶为喜(保守)
            xiji_label = 'SUPPORT_USE_GOD'
        elif has_ji:
            # 只有克泄: 用神强时可能是抑制过强(为喜), 用神弱时为忌
            if primary_strong:
                xiji_label = 'SUPPORT_USE_GOD'  # 用神强, 克泄抑制过强, 反为喜
            else:
                xiji_label = 'SUPPRESS_USE_GOD'
        elif dayun_supports_missing:
            # 大运补充原局缺少五行, 为喜
            xiji_label = 'SUPPORT_USE_GOD'
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
c = c.replace(old3, new3)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V2.8'", "'module': 'DAYUN_XIJI_V2.9'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V2.9优化完成(增加大运补充原局缺少五行判断)')
