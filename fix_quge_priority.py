with open('engines/zhengge_quge.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # 1. 月令藏干透干 → 取透干为格
    month_canggan = BRANCH_CANGGAN[month_branch]
    for cg in month_canggan:
        if not cg: continue
        cg_wx = STEM_WUXING[cg]
        for i, s in enumerate(stems):
            if i == 2: continue  # 跳过日干
            if s == cg:
                shishen = _get_shishen(day_wx, cg_wx)
                if shishen != "比劫":
                    return (shishen, f"月令{month_branch}藏{cg}透干取格")

    # 2. 月令藏干不透，本气非比劫 → 取本气为格
    month_benqi = month_canggan[0]
    if month_benqi:
        benqi_wx = STEM_WUXING[month_benqi]
        shishen = _get_shishen(day_wx, benqi_wx)
        if shishen != "比劫":
            return (shishen, f"月令{month_branch}本气{month_benqi}不透取格")'''

new = '''    month_canggan = BRANCH_CANGGAN[month_branch]
    month_benqi = month_canggan[0]

    # 1. 月令本气透干 → 取本气为格（最高优先级）
    if month_benqi:
        for i, s in enumerate(stems):
            if i == 2: continue
            if s == month_benqi:
                benqi_wx = STEM_WUXING[month_benqi]
                shishen = _get_shishen(day_wx, benqi_wx)
                if shishen != "比劫":
                    return (shishen, f"月令{month_branch}本气{month_benqi}透干取格")

    # 2. 月令本气不透，但本气是比劫 → 看时支（跳过本气）
    # 3. 月令本气不透，本气非比劫 → 优先取本气为格（本气>中气/余气透干）
    if month_benqi:
        benqi_wx = STEM_WUXING[month_benqi]
        shishen_benqi = _get_shishen(day_wx, benqi_wx)
        if shishen_benqi != "比劫":
            return (shishen_benqi, f"月令{month_branch}本气{month_benqi}不透取格（本气优先）")'''

content = content.replace(old, new)

with open('engines/zhengge_quge.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
