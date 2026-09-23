with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # 找主势
    sorted_shis = sorted(shi_dict.items(), key=lambda kv: kv[1], reverse=True)
    main_family = sorted_shis[0][0]
    main_val = sorted_shis[0][1]
    second_val = sorted_shis[1][1] if len(sorted_shis) > 1 else 0
    
    # 新增：主势/第二势比值≥5才算从格（绝对碾压）
    ratio = main_val / second_val if second_val > 0 else 999
    if ratio < 5 and main_family != "印比":  # F4从强特殊，后面单独处理
        return None  # 主势未绝对碾压，退回正格

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
