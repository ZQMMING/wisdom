with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # 旺神不纯：他神泄气
    if family == "官杀" and shi_dict.get("食伤", 0) > 0:
        n += 1
    if family == "财" and shi_dict.get("官杀", 0) > 0:
        n += 1
    if family == "食伤" and shi_dict.get("官杀", 0) > 0:
        n += 1
    if family == "印比" and (shi_dict.get("财", 0) > 0 or shi_dict.get("官杀", 0) > 0):
        n += 1'''

new = '''    # 旺神不纯：他神泄气
    if family == "官杀" and shi_dict.get("食伤", 0) > 0:
        n += 1
    if family == "财" and shi_dict.get("官杀", 0) > 0:
        n += 1
    if family == "食伤" and shi_dict.get("财", 0) > 0:  # 食伤生财，财星泄食伤
        n += 1
    if family == "印比" and (shi_dict.get("财", 0) > 0 or shi_dict.get("官杀", 0) > 0):
        n += 1'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
