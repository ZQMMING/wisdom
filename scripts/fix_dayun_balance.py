# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在原局缺少五行计算后增加五行平衡度计算
old = """    # V2.9: 计算原局缺少的五行(力量为0或极低)
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
new = """    # V2.9: 计算原局缺少的五行(力量为0或极低)
    missing_wuxing = []
    # V3.0: 计算原局五行平衡度(标准差) # PCT-MARK: 五行力量占比标准差, 用于判断五行平衡度
    original_balance = 0.0
    if wpo and 'wuxing_power' in wpo:
        wp = wpo['wuxing_power']
        total_all = sum(v.get('total', 0) for v in wp.values())
        if total_all > 0:
            primary_power_ratio = wp.get(primary, {}).get('total', 0) / total_all
            ratios = [v.get('total', 0) / total_all for v in wp.values()]
            mean_ratio = sum(ratios) / len(ratios)
            original_balance = (sum((r - mean_ratio) ** 2 for r in ratios) / len(ratios)) ** 0.5
            for wx, v in wp.items():
                if v.get('total', 0) < 0.5:  # 力量极低, 视为缺少
                    missing_wuxing.append(wx)
    
    per_step = []"""
c = c.replace(old, new)

# 在大运补充缺少五行判断后增加大运加入后五行平衡度计算
old2 = """        # V2.9: 大运补充原局缺少五行判断
        dayun_gan_wx = GAN_WX.get(gan, '')
        dayun_zhi_wx = ZHI_WX.get(zhi, '')
        dayun_supports_missing = (dayun_gan_wx in missing_wuxing) or (dayun_zhi_wx in missing_wuxing)
        
        # 综合判断: 用神力量+计数+关系+缺少五行综合决定"""
new2 = """        # V2.9: 大运补充原局缺少五行判断
        dayun_gan_wx = GAN_WX.get(gan, '')
        dayun_zhi_wx = ZHI_WX.get(zhi, '')
        dayun_supports_missing = (dayun_gan_wx in missing_wuxing) or (dayun_zhi_wx in missing_wuxing)
        
        # V3.0: 大运加入后五行平衡度计算 # PCT-MARK: 大运加入后五行力量占比标准差
        dayun_improves_balance = False
        if wpo and 'wuxing_power' in wpo and original_balance > 0:
            wp = wpo['wuxing_power']
            total_all = sum(v.get('total', 0) for v in wp.values())
            if total_all > 0:
                # 模拟大运加入: 天干力量+1, 地支力量+1.5(地支力量通常大于天干)
                new_totals = {}
                for wx, v in wp.items():
                    new_totals[wx] = v.get('total', 0)
                if dayun_gan_wx:
                    new_totals[dayun_gan_wx] = new_totals.get(dayun_gan_wx, 0) + 1.0
                if dayun_zhi_wx:
                    new_totals[dayun_zhi_wx] = new_totals.get(dayun_zhi_wx, 0) + 1.5
                new_total_all = sum(new_totals.values())
                if new_total_all > 0:
                    new_ratios = [t / new_total_all for t in new_totals.values()]
                    new_mean = sum(new_ratios) / len(new_ratios)
                    new_balance = (sum((r - new_mean) ** 2 for r in new_ratios) / len(new_ratios)) ** 0.5
                    dayun_improves_balance = new_balance < original_balance
        
        # 综合判断: 用神力量+计数+关系+缺少五行+五行平衡度综合决定"""
c = c.replace(old2, new2)

# 修改综合判断逻辑, 增加五行平衡度判断
old3 = """        elif dayun_supports_missing:
            # 大运补充原局缺少五行, 为喜
            xiji_label = 'SUPPORT_USE_GOD'
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
new3 = """        elif dayun_supports_missing:
            # 大运补充原局缺少五行, 为喜
            xiji_label = 'SUPPORT_USE_GOD'
        elif dayun_improves_balance:
            # 大运改善原局五行平衡度, 为喜
            xiji_label = 'SUPPORT_USE_GOD'
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
c = c.replace(old3, new3)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V2.9'", "'module': 'DAYUN_XIJI_V3.0'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V3.0优化完成(增加大运改善五行平衡度判断)')
