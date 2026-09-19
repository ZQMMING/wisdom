# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 1. 修改函数签名, 增加wpo参数
c = c.replace(
    "def build_dayun_xiji(\n    pillars: Dict[str, list],\n    yongshen_result: Dict[str, Any],\n    dayun_list: List[str],\n) -> Dict[str, Any]:",
    "def build_dayun_xiji(\n    pillars: Dict[str, list],\n    yongshen_result: Dict[str, Any],\n    dayun_list: List[str],\n    wpo: Dict[str, Any] = None,\n) -> Dict[str, Any]:"
)

# 2. 在函数开头增加用神力量计算
old2 = """    primary = yongshen_result.get('yongshen_primary') or ''
    secondary = yongshen_result.get('yongshen_secondary') or []
    avoid = yongshen_result.get('yongshen_avoid') or []
    
    per_step = []"""
new2 = """    primary = yongshen_result.get('yongshen_primary') or ''
    secondary = yongshen_result.get('yongshen_secondary') or []
    avoid = yongshen_result.get('yongshen_avoid') or []
    
    # V2.7: 计算用神在原局中的力量占比 # PCT-MARK: 用神力量占比, 用于判断用神强弱
    primary_power_ratio = 0.0
    if wpo and primary and 'wuxing_power' in wpo:
        wp = wpo['wuxing_power']
        total_all = sum(v.get('total', 0) for v in wp.values())
        if total_all > 0:
            primary_power_ratio = wp.get(primary, {}).get('total', 0) / total_all
    
    per_step = []"""
c = c.replace(old2, new2)

# 3. 修改综合喜忌标签逻辑, 增加用神力量修正
old3 = """        # 综合判断: 如果生扶和克泄同时存在, 用计数决定
        if has_xi and has_ji:
            if xi_count > ji_count:
                xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
            elif ji_count > xi_count:
                xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
            else:
                # 计数相等时, 生扶优先(保守)
                xiji_label = 'SUPPORT_USE_GOD'
        elif has_xi:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif has_ji:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
new3 = """        # V2.7: 用神力量修正 # PCT-MARK: 用神弱(<15%)时生扶更喜, 用神强(>30%)时克泄更喜
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
c = c.replace(old3, new3)

# 4. 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V2.6'", "'module': 'DAYUN_XIJI_V2.7'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V2.7重新应用完成(用神力量修正)')
