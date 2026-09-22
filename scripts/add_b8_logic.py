with open('engines/axis_xiuqi.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # 财根深：地支有财五行本气
    cai_roots = sum(1 for b in br if WUXING.get(b) == cai_wx)
    # 超标条件：财透两位，或财透一位但根深(>=2)
    if len(tou_cai) >= 2:
        b7 = False
    elif len(tou_cai) == 1 and cai_roots >= 2:
        b7 = False
    else:
        b7 = True

    score = sum([b1a or b1b, b2, b4, b6, b7]) + (1 if b3 else 0) + (1 if b5 else 0)
    root = f"一行成象·{hx_to_ge(hx)}" if hx else None

    return XiuqiResult(root, "化气型", b1a, b1b, b2, b3, b4, b5, b6, b7, score, list(gate_debug))'''

new = '''    # 财根深：地支有财五行本气
    cai_roots = sum(1 for b in br if WUXING.get(b) == cai_wx)
    # 超标条件：财透两位，或财透一位但根深(>=2)
    if len(tou_cai) >= 2:
        b7 = False
    elif len(tou_cai) == 1 and cai_roots >= 2:
        b7 = False
    else:
        b7 = True

    # B8：G7 日主有根→降档（不是硬闸，是减项）
    # 日主在地支见本气根（含库中余气）→ 化得不彻底→降MID
    day_wx = WUXING.get(ds, "")
    day_roots = sum(1 for b in br if WUXING.get(b) == day_wx)
    b8 = day_roots >= 1  # True=有根→降档

    score = sum([b1a or b1b, b2, b4, b6, b7]) + (1 if b3 else 0) + (1 if b5 else 0)
    root = f"一行成象·{hx_to_ge(hx)}" if hx else None

    return XiuqiResult(root, "化气型", b1a, b1b, b2, b3, b4, b5, b6, b7, b8, score, list(gate_debug))'''

content = content.replace(old, new)

with open('engines/axis_xiuqi.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
