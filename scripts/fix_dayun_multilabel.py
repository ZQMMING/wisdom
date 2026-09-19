# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改综合判断逻辑, 增加多标签输出
old = """        # 综合判断: 用神力量+计数+关系+缺少五行+五行平衡度+用神力量变化综合决定
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
        elif dayun_boosts_primary:
            # 大运增加用神力量, 为喜
            xiji_label = 'SUPPORT_USE_GOD'
        elif dayun_suppresses_primary:
            # 大运减少用神力量, 为忌
            xiji_label = 'SUPPRESS_USE_GOD'
        elif dayun_supports_missing:
            # 大运补充原局缺少五行, 为喜
            xiji_label = 'SUPPORT_USE_GOD'
        elif dayun_improves_balance:
            # 大运改善原局五行平衡度, 为喜
            xiji_label = 'SUPPORT_USE_GOD'
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""

new = """        # V3.2: 多标签输出 - 一个大运可能同时具有多种喜忌属性
        xiji_labels = []
        if has_xi or dayun_boosts_primary or dayun_supports_missing or dayun_improves_balance:
            xiji_labels.append('SUPPORT_USE_GOD')
        if has_ji or dayun_suppresses_primary:
            # 用神强时克泄可能是抑制过强(为喜), 但仍记录克泄标签
            xiji_labels.append('SUPPRESS_USE_GOD')
        if 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_labels.append('SUPPORT_XI_SHEN')
        if not xiji_labels:
            xiji_labels.append('NEUTRAL')
        
        # 主标签(用于向后兼容): 用神力量+计数+关系综合决定
        if has_xi and has_ji:
            if xi_count > ji_count:
                xiji_label = 'SUPPORT_USE_GOD'
            elif ji_count > xi_count:
                if primary_strong:
                    xiji_label = 'SUPPORT_USE_GOD'
                else:
                    xiji_label = 'SUPPRESS_USE_GOD'
            else:
                if primary_weak:
                    xiji_label = 'SUPPORT_USE_GOD'
                elif primary_strong:
                    xiji_label = 'SUPPRESS_USE_GOD'
                else:
                    xiji_label = 'SUPPORT_USE_GOD'
        elif has_xi:
            xiji_label = 'SUPPORT_USE_GOD'
        elif has_ji:
            if primary_strong:
                xiji_label = 'SUPPORT_USE_GOD'
            else:
                xiji_label = 'SUPPRESS_USE_GOD'
        elif dayun_boosts_primary:
            xiji_label = 'SUPPORT_USE_GOD'
        elif dayun_suppresses_primary:
            xiji_label = 'SUPPRESS_USE_GOD'
        elif dayun_supports_missing:
            xiji_label = 'SUPPORT_USE_GOD'
        elif dayun_improves_balance:
            xiji_label = 'SUPPORT_USE_GOD'
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'
        else:
            xiji_label = 'NEUTRAL'"""
c = c.replace(old, new)

# 修改输出结构, 增加xiji_labels字段
old2 = """            'xiji_label': xiji_label,"""
new2 = """            'xiji_label': xiji_label,
            'xiji_labels': xiji_labels,"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V3.1'", "'module': 'DAYUN_XIJI_V3.2'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V3.2优化完成(增加多标签输出)')
