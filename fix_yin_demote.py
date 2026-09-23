with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 天干透逆神检查里，印虚透被制不算减项
old = '''    # 天干透一粒虚浮逆神（中等减项）
    if stems is not None:
        from spec.root_qi import STEM_WUXING
        from engines.cong_ge_gates import SHISHEN_CLASSES
        # 检查是否有逆神透干（不是印比，不是所从之神）
        reverse_shen = {
            "官杀": ["食伤", "印"],  # 从杀忌食伤、印
            "财": ["比", "印", "官杀"],  # 从财忌比劫、印、官杀
            "食伤": ["印", "官杀"],  # 从儿忌印、官杀
            "印比": ["官杀", "财"],  # 从强忌官杀、财
        }
        for shen in reverse_shen.get(family, []):
            cls = SHISHEN_CLASSES[day_wx][shen]
            for i, s in enumerate(stems):
                if i == 2:  # 跳过日干
                    continue
                if STEM_WUXING.get(s) in cls:
                    n += 1
                    break  # 每类逆神只算一次'''

new = '''    # 天干透一粒虚浮逆神（中等减项）
    if stems is not None:
        from spec.root_qi import STEM_WUXING
        from engines.cong_ge_gates import SHISHEN_CLASSES
        # 检查是否有逆神透干（不是印比，不是所从之神）
        reverse_shen = {
            "官杀": ["食伤", "印"],  # 从杀忌食伤、印
            "财": ["比", "印", "官杀"],  # 从财忌比劫、印、官杀
            "食伤": ["印", "官杀"],  # 从儿忌印、官杀
            "印比": ["官杀", "财"],  # 从强忌官杀、财
        }
        for shen in reverse_shen.get(family, []):
            # 印透干：虚透被制不算减项
            if shen == "印":
                # 检查是否虚透被制
                yin_xu = _yin_xu_tou_bei_zhi(stems, None, day_wx)
                if yin_xu:
                    continue  # 虚透被制，不算减项
            cls = SHISHEN_CLASSES[day_wx][shen]
            for i, s in enumerate(stems):
                if i == 2:  # 跳过日干
                    continue
                if STEM_WUXING.get(s) in cls:
                    n += 1
                    break  # 每类逆神只算一次'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
