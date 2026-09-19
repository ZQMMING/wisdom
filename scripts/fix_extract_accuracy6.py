# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在上下文判断中增加更严格的语义角色标注
# 只有明确包含大运引导词或完整大运干支的句子才计入喜忌判断
old = """            # 检查句子中是否有大运引导词或完整大运干支
            has_guide = any(gw in sent for gw in dayun_guide_words)
            has_full_gz = gz in sent
            # 如果没有大运引导词且没有完整大运干支, 则排除(可能是命例总体评价)
            if not has_guide and not has_full_gz and len(sent) > 10:
                continue
            for kw in XI_KEYWORDS:"""

new = """            # 检查句子中是否有大运引导词或完整大运干支
            has_guide = any(gw in sent for gw in dayun_guide_words)
            has_full_gz = gz in sent
            # V5: 更严格的语义角色标注 - 区分"原局喜忌"与"大运喜忌"
            # 原局喜忌的典型表达: "此造喜X"、"所喜者X"、"喜用X"、"为喜X"等 (没有大运引导词)
            # 大运喜忌的典型表达: "运行X地"、"交X运"、"至X运"、"行X运"等 (有大运引导词)
            # 只有明确包含大运引导词或完整大运干支的句子才计入大运喜忌判断
            # 原局喜忌的句子标记为ORIGINAL_BUREAU, 不与大运喜忌对齐
            is_original_bureau = False
            if not has_guide and not has_full_gz:
                # 检查是否是原局喜忌的典型表达
                original_bureau_patterns = ['此造', '此命', '此局', '所喜', '所忌', '喜用', '为喜', '为忌', '喜神', '忌神', '用神', '相神']
                if any(pattern in sent for pattern in original_bureau_patterns) and len(sent) > 10:
                    is_original_bureau = True
            # 如果是原局喜忌或没有大运引导词且没有完整大运干支, 则排除
            if is_original_bureau or (not has_guide and not has_full_gz and len(sent) > 10):
                continue
            for kw in XI_KEYWORDS:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_dayun_xiji_accuracy.py V5优化完成(更严格区分原局喜忌与大运喜忌: 原局喜忌典型表达排除)')
