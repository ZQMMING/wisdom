with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找F1从杀的位置
for i, line in enumerate(lines):
    if 'F1 从杀' in line and 'main_family == "官杀"' in lines[i+1]:
        # 在印透化煞后面加比值条件
        # 找"# 减项计数"的位置
        for j in range(i, min(i+10, len(lines))):
            if '# 减项计数' in lines[j] and 'demote' in lines[j+1]:
                # 在j行前面插入比值条件
                indent = '        '
                new_code = [
                    indent + '# 官杀/第二势比值>=5才算真从杀（绝对碾压）\n',
                    indent + 'guansha_val = shi_dict.get("官杀", 0)\n',
                    indent + 'second_val = 0\n',
                    indent + 'for f, v in shi_dict.items():\n',
                    indent + '    if f != "官杀" and v > second_val:\n',
                    indent + '        second_val = v\n',
                    indent + 'if second_val > 0 and guansha_val / second_val < 5:\n',
                    indent + '    return None  # 官杀未绝对碾压，退回正格\n',
                    '\n',
                ]
                lines = lines[:j] + new_code + lines[j:]
                break
        break

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done")
