with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # F4 从强：印比势最大 ∧ root_qi==0
    if main_family == "印比":
        if root_qi_val > 0:
            return None  # 交给专旺型
        # F4从强：只要求root_qi==0，不要求无气（印比是所从之神）
        demote = _demote_count(shi_dict, "印比", month_branch, day_wx, stems)'''

new = '''    # F4 从强：印比势最大 ∧ root_qi==0 ∧ 印比占比≥75%
    if main_family == "印比":
        if root_qi_val > 0:
            return None  # 交给专旺型
        
        # 新增：印比占比≥75%（8字里至少6个是印比）
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
        
        # F4从强：只要求root_qi==0，不要求无气（印比是所从之神）
        demote = _demote_count(shi_dict, "印比", month_branch, day_wx, stems)'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
