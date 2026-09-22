with open('engines/axis_xiuqi.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # B8：G7 日主有根→降档（不是硬闸，是减项）
    # 日主在地支见本气根（含库中余气）→ 化得不彻底→降MID
    day_wx = WUXING.get(ds, "")
    day_roots = sum(1 for b in br if WUXING.get(b) == day_wx)
    b8 = day_roots >= 1  # True=有根→降档'''

new = '''    # B8：G7 日主有根→降档（不是硬闸，是减项）
    # 日主在地支见本气根（含库中余气）→ 化得不彻底→降MID
    # 注意：日干原五行=化神五行时不算（如甲己化土，日干己土，化神也是土，见土根是化神有根，不是日主有根）
    day_wx = WUXING.get(ds, "")
    if day_wx != hx:
        day_roots = sum(1 for b in br if WUXING.get(b) == day_wx)
        b8 = day_roots >= 1  # True=有根→降档
    else:
        b8 = False  # 日干五行=化神五行，不存在"日主有根不降"的问题'''

content = content.replace(old, new)

with open('engines/axis_xiuqi.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
