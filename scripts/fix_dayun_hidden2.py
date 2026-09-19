# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改大运藏干判断, 区分本气/中气/余气
old = """        # V1.9: 大运藏干判断 (大运地支藏干中有用神/忌神)
        zhi_hidden = HIDDEN_STEMS.get(zhi, [])
        zhi_hidden_wx = [WX.get(s, '') for s in zhi_hidden]
        if primary in zhi_hidden_wx:
            relations.append('ZHI_HIDDEN_PRIMARY')  # 大运藏干中有用神, 喜
        if avoid and avoid[0] in zhi_hidden_wx:
            relations.append('ZHI_HIDDEN_AVOID')  # 大运藏干中有忌神, 忌"""
new = """        # V2.0: 大运藏干判断 (区分本气/中气/余气权重)
        zhi_hidden = HIDDEN_STEMS.get(zhi, [])
        zhi_hidden_wx = [WX.get(s, '') for s in zhi_hidden]
        # 本气(第1个)权重最高, 中气(第2个)次之, 余气(第3个)最小
        if len(zhi_hidden_wx) >= 1 and zhi_hidden_wx[0] == primary:
            relations.append('ZHI_HIDDEN_BENQI_PRIMARY')  # 大运藏干本气是用神, 喜(强)
        elif len(zhi_hidden_wx) >= 2 and zhi_hidden_wx[1] == primary:
            relations.append('ZHI_HIDDEN_ZHONGQI_PRIMARY')  # 大运藏干中气是用神, 喜(中)
        elif len(zhi_hidden_wx) >= 3 and zhi_hidden_wx[2] == primary:
            relations.append('ZHI_HIDDEN_YUQI_PRIMARY')  # 大运藏干余气是用神, 喜(弱)
        if avoid:
            if len(zhi_hidden_wx) >= 1 and zhi_hidden_wx[0] == avoid[0]:
                relations.append('ZHI_HIDDEN_BENQI_AVOID')  # 大运藏干本气是忌神, 忌(强)
            elif len(zhi_hidden_wx) >= 2 and zhi_hidden_wx[1] == avoid[0]:
                relations.append('ZHI_HIDDEN_ZHONGQI_AVOID')  # 大运藏干中气是忌神, 忌(中)
            elif len(zhi_hidden_wx) >= 3 and zhi_hidden_wx[2] == avoid[0]:
                relations.append('ZHI_HIDDEN_YUQI_AVOID')  # 大运藏干余气是忌神, 忌(弱)"""
c = c.replace(old, new)

# 修改综合喜忌标签逻辑, 增加大运藏干本气/中气/余气判断
old2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'ZHI_HIDDEN_PRIMARY' in relations or chong_avoid_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'ZHI_HIDDEN_AVOID' in relations or chong_primary_any:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
new2 = """        hidden_primary_any = any('ZHI_HIDDEN_' in r and '_PRIMARY' in r for r in relations)
        hidden_avoid_any = any('ZHI_HIDDEN_' in r and '_AVOID' in r for r in relations)
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or hidden_avoid_any or chong_primary_any:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V1.9'", "'module': 'DAYUN_XIJI_V2.0'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V2.0优化完成(大运藏干本气/中气/余气区分)')
