# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在用神力量修正部分增加精细的用神过旺反忌判断
old = """        # V2.7: 用神力量修正 # PCT-MARK: 用神弱(<15%)时生扶更喜, 用神强(>30%)时克泄可能为喜
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
                xiji_label = 'SUPPRESS_USE_GOD'"""

new = """        # V2.7: 用神力量修正 # PCT-MARK: 用神弱(<15%)时生扶更喜, 用神强(>30%)时克泄可能为喜
        primary_weak = primary_power_ratio < 0.15 if primary_power_ratio > 0 else False
        primary_strong = primary_power_ratio > 0.30 if primary_power_ratio > 0 else False
        
        # V4.2: 精细的用神过旺反忌判断 (基于滴天髓"偏之又偏,以其无情也"和"实所当益者而益之,反害")
        # 条件: 1)原局用神非常旺(>40%); 2)大运干支都是用神五行; 3)原局日主也旺(>30%)
        daymaster_power_ratio = 0.0
        if wpo and 'wuxing_power' in wpo:
            wp = wpo['wuxing_power']
            total_all = sum(v.get('total', 0) for v in wp.values())
            if total_all > 0:
                daymaster_power_ratio = wp.get(dmw, {}).get('total', 0) / total_all
        # 大运干支都是用神五行
        dayun_all_primary = bool(primary) and gan_wx == primary and zhi_wx == primary
        # 用神过旺反忌的精细条件
        primary_too_strong_reverse = (primary_power_ratio > 0.40 and daymaster_power_ratio > 0.30 
                                       and dayun_all_primary and primary_strong)
        
        if has_xi and has_ji:
            # 生扶和克泄同时存在: 用神弱则生扶, 用神强则克泄, 否则生扶优先
            if primary_weak:
                xiji_label = 'SUPPORT_USE_GOD'
            elif primary_strong or primary_too_strong_reverse:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'
        elif has_xi:
            # 只有生扶: 用神过旺反忌时, 生扶反而为忌
            if primary_too_strong_reverse:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'
        elif has_ji:
            # 只有克泄: 用神强时可能是抑制过强(为喜)
            if primary_strong or primary_too_strong_reverse:
                xiji_label = 'SUPPORT_USE_GOD'
            else:
                xiji_label = 'SUPPRESS_USE_GOD'"""
c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.1'", "'module': 'DAYUN_XIJI_V4.2'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.2完成(精细的用神过旺反忌判断: 用神>40%+日主>30%+大运干支都是用神五行)')
