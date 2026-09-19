# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在per_step中增加语义类型字段
old = """        per_step.append({
            'ganzhi': gz,
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': gan_wx,
            'zhi_wuxing': zhi_wx,
            'ten_god': ten_god,
            'relations': relations,
            'xiji_label': xiji_label,
            'xiji_labels': xiji_labels,
            'xiji_labels': xiji_labels,
        })"""

new = """        # V4.6: 语义类型标记 - 区分"大运提供"与"大运互动"
        # DAYUN_PROVISION: 大运透干/通根直接提供了命局所需 (天干是用神/地支是用神/藏干是用神)
        # DAYUN_INTERACTION: 大运通过冲/合/刑/害等互动关系影响命局 (冲用神/合用神/刑用神)
        # MIXED: 同时存在提供和互动
        provision_relations = ['GAN_PRIMARY', 'ZHI_PRIMARY', 'GAN_SHENG_PRIMARY', 'ZHI_HIDDEN_BENQI_PRIMARY', 
                                'ZHI_HIDDEN_ZHONGQI_PRIMARY', 'ZHI_HIDDEN_YUQI_PRIMARY', 'GAN_SECONDARY', 'ZHI_SECONDARY']
        interaction_relations = ['CHONG_', 'HE_', 'HAI_', 'XING_', 'PO_', 'WUHE_', 'SANHE_', 'SANHUI_', 'BANHE_', 'LIUHE_']
        has_provision = any(any(pr in r for pr in provision_relations) for r in relations)
        has_interaction = any(any(ir in r for ir in interaction_relations) for r in relations)
        if has_provision and has_interaction:
            semantic_type = 'MIXED'
        elif has_provision:
            semantic_type = 'DAYUN_PROVISION'
        elif has_interaction:
            semantic_type = 'DAYUN_INTERACTION'
        else:
            semantic_type = 'NEUTRAL'
        
        # 大运提供了哪些命局所需
        dayun_provides = []
        if 'GAN_PRIMARY' in relations:
            dayun_provides.append(f'天干透{primary}')
        if 'ZHI_PRIMARY' in relations:
            dayun_provides.append(f'地支坐{primary}')
        if hidden_primary_any:
            dayun_provides.append(f'地支藏{primary}')
        if 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            dayun_provides.append('提供喜神')
        
        # 大运破坏了哪些命局所需
        dayun_suppresses = []
        if chong_primary_any:
            dayun_suppresses.append(f'冲{primary}')
        if he_primary_any:
            dayun_suppresses.append(f'合{primary}')
        if hai_primary_any:
            dayun_suppresses.append(f'害{primary}')
        if xing_primary_any:
            dayun_suppresses.append(f'刑{primary}')
        if 'GAN_KE_PRIMARY' in relations:
            dayun_suppresses.append(f'天干克{primary}')
        if 'GAN_PRIMARY_SHENG' in relations:
            dayun_suppresses.append(f'{primary}生天干(泄)')
        
        per_step.append({
            'ganzhi': gz,
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': gan_wx,
            'zhi_wuxing': zhi_wx,
            'ten_god': ten_god,
            'relations': relations,
            'xiji_label': xiji_label,
            'xiji_labels': xiji_labels,
            'semantic_type': semantic_type,  # 语义类型: DAYUN_PROVISION/DAYUN_INTERACTION/MIXED/NEUTRAL
            'dayun_provides': dayun_provides,  # 大运提供了哪些命局所需
            'dayun_suppresses': dayun_suppresses,  # 大运破坏了哪些命局所需
        })"""
c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.5'", "'module': 'DAYUN_XIJI_V4.6'")

# 修改boundary_note
old2 = """        'boundary_note': '大运喜忌结构层: 基于用神/喜神/忌神与大运干支的关系输出结构标签; 非吉凶裁决; 吉凶前端拦截; 冲合/调候/通关等深层作用待后续扩展',"""
new2 = """        'boundary_note': '大运喜忌结构层V4.6: 区分原局喜忌(命局需要什么)与大运喜忌(大运提供/破坏了什么); semantic_type标记DAYUN_PROVISION/DAYUN_INTERACTION/MIXED; 非吉凶裁决; 吉凶前端拦截',"""
c = c.replace(old2, new2)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.6完成(增加语义类型标记: 区分DAYUN_PROVISION大运提供与DAYUN_INTERACTION大运互动)')
