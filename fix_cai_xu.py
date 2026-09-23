with open('engines/zhuanwang_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # 硬闸④：财不透干
    cai_cls = SHISHEN_CLASSES[day_wx]["财"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) in cai_cls:
            return False, f"F0·财透干破格（{s}）"

    return True, f"专旺·印比势{yin_bi_shi:.2f}占优"'''

new = '''    # 硬闸④：财不透干（财虚透被制例外：无根+被比劫紧贴克）
    cai_cls = SHISHEN_CLASSES[day_wx]["财"]
    bi_cls = SHISHEN_CLASSES[day_wx]["比"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) in cai_cls:
            # 检查财星是否虚透被制
            # 1. 财星无根：地支无本气根
            cai_root = False
            cai_wx = WUXING_OF[day_wx]["财"]
            for b in branches:
                from spec.root_qi import BENQI
                if BENQI.get(b) == cai_wx:
                    cai_root = True
                    break
            if cai_root:
                return False, f"F0·财透干有根破格（{s}）"
            
            # 2. 被比劫紧贴克
            bei_ke = False
            for j, s2 in enumerate(stems):
                if j == 2: continue
                if abs(i - j) == 1 and STEM_WUXING.get(s2) in bi_cls:
                    bei_ke = True
                    break
            if not bei_ke:
                return False, f"F0·财透干无制破格（{s}）"
            # 财虚透被制 → 放行，算减项

    return True, f"专旺·印比势{yin_bi_shi:.2f}占优"'''

content = content.replace(old, new)

with open('engines/zhuanwang_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
