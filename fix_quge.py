with open('engines/special_pan.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 加import
content = content.replace(
    'from engines.zhengge_gates import zhengge_f0',
    'from engines.zhengge_gates import zhengge_f0\nfrom engines.zhengge_quge import l1_quge'
)

# 改正格族兜底
content = content.replace(
    '''    # 第四步：正格族（兜底）
    f0_ok, f0_reason = zhengge_f0(branches)
    if not f0_ok:
        return ("正格", "REJECT", f0_reason)
    
    # TODO: 接入L1/L2/L3
    return ("正格", "MID_1", "正格·F0通过待L1/L2/L3")''',
    '''    # 第四步：正格族（兜底）
    f0_ok, f0_reason = zhengge_f0(branches)
    if not f0_ok:
        return ("正格", "REJECT", f0_reason)
    
    ge, quge_reason = l1_quge(stems, branches, day_stem)
    if ge is None:
        return ("正格", "REJECT", quge_reason)
    
    return (f"正格·{ge}", "MID_1", f"{quge_reason}")'''
)

with open('engines/special_pan.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
