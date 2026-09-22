import json

with open('tests/cases_l1_v1.json', 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

# 找到G2条目结束的位置，补上provenance_note和}
# 第360行（索引359）是rationale_quote，后面缺provenance_note和}
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if i == 359:  # rationale_quote那行
        new_lines.append('    "provenance_note": "润下格财星不忌实证：亥子丑三会水+丁火财星透干，润下格只忌土官杀，不忌财"\n')
        new_lines.append('  },\n')

with open('tests/cases_l1_v1.json', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# 验证
with open('tests/cases_l1_v1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'JSON valid, cases: {len(data)}')
