# -*- coding: utf-8 -*-
with open('engines/common/wuxing_power.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在return前增加stem_strength_modifier计算
old = """    return {'daymaster': dm, 'daymaster_element': dm_wx, 'month_element': month_wx,
            'wuxing_power': power, 'judgment_status': 'WUXING_POWER_STRUCTURE_ONLY'}"""

new = """    # V7.24: 天干强弱修正(修正层, 不是替换层)
    from engines.common.stem_strength_modifier import get_stem_strength_modifier
    _ssm = get_stem_strength_modifier(dm)

    return {'daymaster': dm, 'daymaster_element': dm_wx, 'month_element': month_wx,
            'wuxing_power': power, 'judgment_status': 'WUXING_POWER_STRUCTURE_ONLY',
            'stem_strength_modifier': _ssm}"""

content = content.replace(old, new)

with open('engines/common/wuxing_power.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
