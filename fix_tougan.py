with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''def _tou_gan(stems: list, day_wx: str, shen_class: str) -> bool:
    """判某类十神是否在天干透出"""
    cls = SHISHEN_CLASSES[day_wx][shen_class]
    return any(s in cls for s in stems)'''

new = '''def _tou_gan(stems: list, day_wx: str, shen_class: str) -> bool:
    """判某类十神是否在天干透出"""
    from spec.root_qi import STEM_WUXING
    cls = SHISHEN_CLASSES[day_wx][shen_class]
    return any(STEM_WUXING[s] in cls for s in stems)'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
