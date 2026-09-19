# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在大运改善五行平衡度判断后增加大运对用神力量影响判断
old = """        # V3.0: 大运加入后五行平衡度计算 # PCT-MARK: 大运加入后五行力量占比标准差
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
new = """        # V3.0: 大运加入后五行平衡度计算 # PCT-MARK: 大运加入后五行力量占比标准差
        dayun_improves_balance = False
        # V3.1: 大运对用神力量影响判断 # PCT-MARK: 大运加入后用神力量变化率
        dayun_boosts_primary = False
        dayun_suppresses_primary = False
        if wpo and 'wuxing_power' in wpo and primary:
            wp = wpo['wuxing_power']
            primary_total = wp.get(primary, {}).get('total', 0)
            if primary_total > 0:
                # 模拟大运加入对用神力量的影响
                primary_delta = 0.0
                # 大运天干/地支是用神五行 -> 增加用神力量
                if dayun_gan_wx == primary:
                    primary_delta += 1.0
                if dayun_zhi_wx == primary:
                    primary_delta += 1.5
                # 大运天干/地支是克用神的五行 -> 减少用神力量
                ke_primary = {'木':'金', '火':'水', '土':'木', '金':'火', '水':'土'}.get(primary, '')
                if dayun_gan_wx == ke_primary:
                    primary_delta -= 0.8
                if dayun_zhi_wx == ke_primary:
                    primary_delta -= 1.2
                # 大运天干/地支是用神生的五行(泄) -> 减少用神力量
                xie_primary = {'木':'火', '火':'土', '土':'金', '金':'水', '水':'木'}.get(primary, '')
                if dayun_gan_wx == xie_primary:
                    primary_delta -= 0.5
                if dayun_zhi_wx == xie_primary:
                    primary_delta -= 0.8
                dayun_boosts_primary = primary_delta > 0.3
                dayun_suppresses_primary = primary_delta < -0.3
        
        # 综合判断: 用神力量+计数+关系+缺少五行+五行平衡度+用神力量变化综合决定"""
c = c.replace(old, new)

# 修改综合判断逻辑, 增加用神力量变化判断
old2 = """        elif dayun_improves_balance:
            # 大运改善原局五行平衡度, 为喜
            xiji_label = 'SUPPORT_USE_GOD'
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
new2 = """        elif dayun_boosts_primary:
            # 大运增加用神力量, 为喜
            xiji_label = 'SUPPORT_USE_GOD'
        elif dayun_suppresses_primary:
            # 大运减少用神力量, 为忌
            xiji_label = 'SUPPRESS_USE_GOD'
        elif dayun_improves_balance:
            # 大运改善原局五行平衡度, 为喜
            xiji_label = 'SUPPORT_USE_GOD'
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V3.0'", "'module': 'DAYUN_XIJI_V3.1'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V3.1优化完成(增加大运对用神力量影响判断)')
