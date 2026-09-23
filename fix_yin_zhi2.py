with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找_cong_ge_pan函数定义
old = 'def cong_ge_pan(shi_dict: dict, stems: list, day_stem: str, month_branch: str, root_qi_val: float):'

new_func = '''
def _yin_xu_tou_bei_zhi(stems, branches, day_wx):
    """判印星是否虚透被制（无根+被克）"""
    from spec.root_qi import STEM_WUXING, WUXING_OF as WUXING_OF_ROOT
    yin_wuxing = WUXING_OF_ROOT[day_wx]["印"]
    
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
    cai_wuxing = WUXING_OF_ROOT[day_wx]["财"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) == cai_wuxing:
            for yin_i, yin_s in yin_stems:
                if abs(i - yin_i) == 1:  # 紧贴
                    return True
    
    return False


def cong_ge_pan(shi_dict: dict, stems: list, day_stem: str, month_branch: str, root_qi_val: float):'''

content = content.replace(old, new_func)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
