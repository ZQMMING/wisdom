with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# F2从财印透硬闸加例外
old_f2 = '''    # F2 从财
    if main_family == "财":
        if _tou_gan(stems, day_wx, "比"):
            return ("从财", "REJECT", "F2①·比劫争财")
        if _tou_gan(stems, day_wx, "印"):
            return ("从财", "REJECT", "F2②·印透生身")'''

new_f2 = '''    # F2 从财
    if main_family == "财":
        if _tou_gan(stems, day_wx, "比"):
            return ("从财", "REJECT", "F2①·比劫争财")
        # 印透硬闸：印虚透被制不算破格（印无根+被克）
        if _tou_gan(stems, day_wx, "印") and not _yin_xu_tou_bei_zhi(stems, branches, day_wx):
            return ("从财", "REJECT", "F2②·印透生身")'''

content = content.replace(old_f2, new_f2)

# 在_tou_gan函数后面加_yin_xu_tou_bei_zhi函数
old_tougan_end = '''def _tou_gan(stems, day_wx, shen_class):
    """判某类十神是否在天干透出（含日干自身）"""
    cls = SHISHEN_CLASSES[day_wx][shen_class]
    return any(STEM_WUXING.get(s) in cls for i, s in enumerate(stems) if i != 2)'''

# 找_tou_gan函数定义位置
import re
# 找_yin_xu_tou_bei_zhi应该加在哪
# 直接加在文件开头的import后面

# 先加函数定义
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
        return False  # 没透印，不算
    
    # 检查印星是否无根（地支无本气/中气/余气根）
    yin_root = 0
    for b in branches:
        from spec.root_qi import CANGGAN
        if b in CANGGAN:
            for cg in CANGGAN[b]:
                if STEM_WUXING.get(cg[0]) == yin_wuxing:
                    yin_root += cg[1]
    
    # 无根（root=0或<0.5算虚浮）
    if yin_root >= 0.5:
        return False  # 有根，破格
    
    # 检查是否被克：天干有克印星的五行
    # 印星生身，克印的是财星
    cai_wuxing = WUXING_OF[day_wx]["财"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) == cai_wuxing:
            # 财星克印，紧贴？
            for yin_i, yin_s in yin_stems:
                if abs(i - yin_i) == 1:  # 紧贴
                    return True  # 印虚透被制
    
    return False

'''

# 加在_tou_gan函数后面
content = content.replace(
    'def _tou_gan(stems, day_wx, shen_class):',
    new_func + 'def _tou_gan(stems, day_wx, shen_class):'
)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
