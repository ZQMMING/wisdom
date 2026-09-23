with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 简化_yin_xu_tou_bei_zhi——不查藏干，直接看地支本气
old_func = '''
def _yin_xu_tou_bei_zhi(stems, branches, day_wx):
    """判印星是否虚透被制（无根+被克）"""
    from spec.root_qi import STEM_WUXING
    yin_wuxing = WUXING_OF[day_wx]["印"]
    
    # 找透干的印星
    yin_stems = []
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) == yin_wuxing:
            yin_stems.append((i, s))
    
    if not yin_stems:
        return False
    
    # 检查印星是否无根
    yin_root = 0
    for b in branches:
        from spec.root_qi import CANGGAN
        if b in CANGGAN:
            for cg in CANGGAN[b]:
                if STEM_WUXING.get(cg[0]) == yin_wuxing:
                    yin_root += cg[1]
    
    if yin_root >= 0.5:
        return False  # 有根，破格
    
    # 检查是否被克：财星克印
    cai_wuxing = WUXING_OF[day_wx]["财"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) == cai_wuxing:
            for yin_i, yin_s in yin_stems:
                if abs(i - yin_i) == 1:  # 紧贴
                    return True
    
    return False
'''

new_func = '''
def _yin_xu_tou_bei_zhi(stems, branches, day_wx):
    """判印星是否虚透被制（无根+被克）"""
    from spec.root_qi import STEM_WUXING, BENQI
    yin_wuxing = WUXING_OF[day_wx]["印"]
    
    # 找透干的印星
    yin_stems = []
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) == yin_wuxing:
            yin_stems.append((i, s))
    
    if not yin_stems:
        return False
    
    # 检查印星是否有本气根（地支本气=印星）
    has_root = False
    for b in branches:
        if BENQI.get(b) == yin_wuxing:
            has_root = True
            break
    
    if has_root:
        return False  # 有本气根，破格
    
    # 检查是否被克：财星克印（紧贴）
    cai_wuxing = WUXING_OF[day_wx]["财"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) == cai_wuxing:
            for yin_i, yin_s in yin_stems:
                if abs(i - yin_i) == 1:  # 紧贴
                    return True
    
    return False
'''

content = content.replace(old_func, new_func)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
