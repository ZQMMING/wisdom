with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # F1/F2/F3需要无气检查（无比印透干），F4从强不需要
    if not 无气(stems, day_stem):
        # 有比印透干，只有F4从强能进，其他都退回正格
        if main_family != "印比":
            return None  # 主势不是印比，有比印透干→不从，退回正格
    
    # F1 从杀
    if main_family == "官杀":'''

new = '''    # F1 从杀
    if main_family == "官杀":'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
