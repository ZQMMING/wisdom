with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # 旺神不纯：他神泄气（余气级别不算，阈值0.5）
    PURITY_THRESHOLD = 0.5  # 余气=0.5不算杂气
    if family == "官杀" and shi_dict.get("食伤", 0) > PURITY_THRESHOLD:
        n += 1
    if family == "财" and shi_dict.get("官杀", 0) > PURITY_THRESHOLD:
        n += 1
    if family == "食伤" and shi_dict.get("财", 0) > PURITY_THRESHOLD:  # 食伤生财，财星泄食伤
        n += 1
    if family == "印比" and (shi_dict.get("财", 0) > PURITY_THRESHOLD or shi_dict.get("官杀", 0) > PURITY_THRESHOLD):
        n += 1'''

new = '''    # 旺神不纯：他神泄气（余气级别不算，阈值0.5）
    PURITY_THRESHOLD = 0.5  # 余气=0.5不算杂气
    if family == "官杀" and shi_dict.get("食伤", 0) > PURITY_THRESHOLD:
        n += 1
    if family == "财" and shi_dict.get("官杀", 0) > PURITY_THRESHOLD:
        n += 1
    # 从儿族：财星是喜神（吾儿又见儿），不算泄气减项
    if family == "印比" and (shi_dict.get("财", 0) > PURITY_THRESHOLD or shi_dict.get("官杀", 0) > PURITY_THRESHOLD):
        n += 1'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
