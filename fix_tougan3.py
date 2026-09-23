with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''def _tou_gan(stems: list, day_wx: str, shen_class: str, exclude_day=True) -> bool:
    """判某类十神是否在天干透出（默认排除日干自身）"""
    from spec.root_qi import STEM_WUXING
    cls = SHISHEN_CLASSES[day_wx][shen_class]
    check_stems = stems[1:] if exclude_day else stems  # 排除日干
    return any(STEM_WUXING[s] in cls for s in check_stems)'''

new = '''def _tou_gan(stems: list, day_wx: str, shen_class: str, exclude_day=True) -> bool:
    """判某类十神是否在天干透出（默认排除日干自身）
    stems顺序：年干、月干、日干、时干
    """
    from spec.root_qi import STEM_WUXING
    cls = SHISHEN_CLASSES[day_wx][shen_class]
    if exclude_day:
        # 排除日干（stems[2]）
        check_stems = [s for i, s in enumerate(stems) if i != 2]
    else:
        check_stems = stems
    return any(STEM_WUXING[s] in cls for s in check_stems)'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
