# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在大运喜忌输出中增加理论来源标签
old = """    return {
        'module': 'DAYUN_XIJI_V4.6',
        'namespace': 'dayun_xiji_structure',
        'day_master': dm,
        'daymaster_wuxing': dmw,
        'yongshen_primary': primary,
        'yongshen_secondary': secondary,
        'yongshen_avoid': avoid,
        'per_step': per_step,
        'judgment_status': 'DAYUN_XIJI_STRUCTURE_ONLY',"""

new = """    # V4.7: 冲突保留输出 - 多源透明, 保留理论分歧
    # 获取用神引擎的理论来源标签
    theory_source = yongshen_result.get('theory_source', 'THEORY_ZIPING')
    # 获取所有候选用神及其理论来源
    yongshen_candidates = yongshen_result.get('yongshen_candidates', [])
    
    return {
        'module': 'DAYUN_XIJI_V4.7',
        'namespace': 'dayun_xiji_structure',
        'day_master': dm,
        'daymaster_wuxing': dmw,
        'yongshen_primary': primary,
        'yongshen_secondary': secondary,
        'yongshen_avoid': avoid,
        'theory_source': theory_source,  # 理论来源标签 (ZIPING/QIONGTONG/SHENFENG)
        'yongshen_candidates': yongshen_candidates,  # 所有候选用神(多源透明)
        'per_step': per_step,
        'judgment_status': 'DAYUN_XIJI_STRUCTURE_ONLY',"""
c = c.replace(old, new)

# 修改boundary_note
old2 = """        'boundary_note': '大运喜忌结构层V4.6: 区分原局喜忌(命局需要什么)与大运喜忌(大运提供/破坏了什么); semantic_type标记DAYUN_PROVISION/DAYUN_INTERACTION/MIXED; 非吉凶裁决; 吉凶前端拦截',"""
new2 = """        'boundary_note': '大运喜忌结构层V4.7: 冲突保留输出-多源透明保留理论分歧; 区分原局喜忌与大运喜忌; semantic_type标记DAYUN_PROVISION/DAYUN_INTERACTION/MIXED; theory_source标记ZIPING/QIONGTONG/SHENFENG; 不强行裁决唯一答案, 保留多源结论; 非吉凶裁决; 吉凶前端拦截',"""
c = c.replace(old2, new2)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.7完成(冲突保留输出: 增加theory_source和yongshen_candidates字段, 多源透明保留理论分歧)')
