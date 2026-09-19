# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改综合喜忌标签逻辑, 扩大用神力量修正范围
old = """        # V2.7: 用神力量修正 # PCT-MARK: 用神弱(<15%)时生扶更喜, 用神强(>30%)时克泄更喜
        primary_weak = primary_power_ratio < 0.15 if primary_power_ratio > 0 else False
        primary_strong = primary_power_ratio > 0.30 if primary_power_ratio > 0 else False
        
        # 综合判断: 如果生扶和克泄同时存在, 用计数+用神力量决定
        if has_xi and has_ji:
            if xi_count > ji_count:
                xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
            elif ji_count > xi_count:
                xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
            else:
                # 计数相等时, 用神弱则生扶, 用神强则克泄, 否则生扶优先
                if primary_weak:
                    xiji_label = 'SUPPORT_USE_GOD'
                elif primary_strong:
                    xiji_label = 'SUPPRESS_USE_GOD'
                else:
                    xiji_label = 'SUPPORT_USE_GOD'
        elif has_xi:
            xiji_label = 'SUPPORT_USE_GOD'
        elif has_ji:
            xiji_label = 'SUPPRESS_USE_GOD'
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""

new = """        # V2.8: 用神力量修正扩大范围 # PCT-MARK: 用神弱(<15%)时生扶更喜, 用神强(>30%)时克泄可能为喜
        primary_weak = primary_power_ratio < 0.15 if primary_power_ratio > 0 else False
        primary_strong = primary_power_ratio > 0.30 if primary_power_ratio > 0 else False
        
        # 综合判断: 用神力量+计数+关系综合决定
        if has_xi and has_ji:
            if xi_count > ji_count:
                # 生扶关系多: 用神强时可能过犹不及, 但仍以生扶为喜(保守)
                xiji_label = 'SUPPORT_USE_GOD'
            elif ji_count > xi_count:
                # 克泄关系多: 用神强时可能是抑制过强(为喜), 用神弱时为忌
                if primary_strong:
                    xiji_label = 'SUPPORT_USE_GOD'  # 用神强, 克泄抑制过强, 反为喜
                else:
                    xiji_label = 'SUPPRESS_USE_GOD'
            else:
                # 计数相等时, 用神弱则生扶, 用神强则克泄, 否则生扶优先
                if primary_weak:
                    xiji_label = 'SUPPORT_USE_GOD'
                elif primary_strong:
                    xiji_label = 'SUPPRESS_USE_GOD'
                else:
                    xiji_label = 'SUPPORT_USE_GOD'
        elif has_xi:
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
c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V2.7'", "'module': 'DAYUN_XIJI_V2.8'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V2.8优化完成(用神力量修正扩大范围)')
