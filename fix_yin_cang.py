with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # 找主势
    main_family = max(shi_dict.items(), key=lambda kv: kv[1])[0]

    # 印藏支检查：F1/F2/F3（非印比主势）地支有印藏→日主有气，退回正格
    if main_family != "印比":
        yin_wx_map = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
        yin_wx = yin_wx_map.get(day_wx, "")
        from spec.root_qi import BRANCH_CANGGAN
        for b in branches or []:
            canggan = BRANCH_CANGGAN.get(b, [])
            for cg in canggan:
                if cg and STEM_WUXING.get(cg) == yin_wx:
                    return None  # 印藏支→日主有气，不从，退回正格
                    break
            else:
                continue
            break

    # F1 从杀
    if main_family == "官杀":'''

new = '''    # 找主势
    main_family = max(shi_dict.items(), key=lambda kv: kv[1])[0]

    # F1 从杀
    if main_family == "官杀":'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
