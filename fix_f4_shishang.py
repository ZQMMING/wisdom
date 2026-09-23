with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        # 新增：印比占比≥75%（8字里至少6个是印比）
        yin_wx = WUXING_OF[day_wx]["印"]
        bi_wx = day_wx  # 比劫=日主同五行
        yin_bi_count = 0
        for s in stems:
            if STEM_WUXING.get(s) in {yin_wx, bi_wx}:
                yin_bi_count += 1
        for b in branches:
            from spec.root_qi import BENQI
            if BENQI.get(b) in {yin_wx, bi_wx}:
                yin_bi_count += 1
        if yin_bi_count < 6:  # <75%（6/8=75%）
            return None  # 印比未到满盘，退回正格'''

new = '''        # 新增：印比占比≥75%（8字里至少6个是印比）
        yin_wx = WUXING_OF[day_wx]["印"]
        bi_wx = day_wx  # 比劫=日主同五行
        yin_bi_count = 0
        for s in stems:
            if STEM_WUXING.get(s) in {yin_wx, bi_wx}:
                yin_bi_count += 1
        for b in branches:
            from spec.root_qi import BENQI
            if BENQI.get(b) in {yin_wx, bi_wx}:
                yin_bi_count += 1
        if yin_bi_count < 6:  # <75%（6/8=75%）
            return None  # 印比未到满盘，退回正格
        
        # 新增：地支不能有食伤成势（≥2个）或食伤与印星相冲
        shi_wx = WUXING_OF[day_wx]["食伤"]
        shi_count = 0
        for b in branches:
            from spec.root_qi import BENQI
            if BENQI.get(b) == shi_wx:
                shi_count += 1
        if shi_count >= 2:
            return None  # 食伤成势，不满足从强
        
        # 新增：食伤与印星相冲（子午冲/卯酉冲等）
        LIU_CHONG = {"子": "午", "午": "子", "卯": "酉", "酉": "卯", "寅": "申", "申": "寅", "巳": "亥", "亥": "巳", "辰": "戌", "戌": "辰", "丑": "未", "未": "丑"}
        has_chong = False
        for i, b1 in enumerate(branches):
            for b2 in branches[i+1:]:
                if LIU_CHONG.get(b1) == b2:
                    # 检查冲的双方是否是印和食伤
                    b1_wx = STEM_WUXING.get(BENQI.get(b1, ""), "")
                    b2_wx = STEM_WUXING.get(BENQI.get(b2, ""), "")
                    if {b1_wx, b2_wx} == {yin_wx, shi_wx}:
                        has_chong = True
                        break
            if has_chong: break
        if has_chong:
            return None  # 食伤与印星相冲，气势不纯'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
