with open('engines/special_pan.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 加import
content = content.replace(
    'from engines.zhengge_quge import l1_quge',
    'from engines.zhengge_quge import l1_quge\nfrom engines.zhengge_xiangshen import l2_xiangshen, l3_chengbai, zhengge_grade'
)

# 改正格族兜底
old = '''    ge, quge_reason = l1_quge(stems, branches, day_stem)
    if ge is None:
        return ("正格", "REJECT", quge_reason)
    
    return (f"正格·{ge}", "MID_1", f"{quge_reason}")'''

new = '''    ge, quge_reason = l1_quge(stems, branches, day_stem)
    if ge is None:
        return ("正格", "REJECT", quge_reason)
    
    day_wx = STEM_WUXING[day_stem]
    xiangshen, xs_reason = l2_xiangshen(ge, day_wx, stems, branches)
    poges, cb_reason = l3_chengbai(ge, day_wx, stems, branches)
    grade, demote, grade_reason = zhengge_grade(ge, xiangshen, poges, day_wx, stems, branches, branches[1])
    
    return (f"正格·{ge}", grade, f"{quge_reason} | {xs_reason} | {cb_reason} | {grade_reason}")'''

content = content.replace(old, new)

with open('engines/special_pan.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
