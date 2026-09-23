with open('engines/special_pan.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'cong_result = cong_ge_pan(shi_dict, stems, day_stem, branches[1], root_qi_val)',
    'cong_result = cong_ge_pan(shi_dict, stems, day_stem, branches[1], root_qi_val, branches=branches)'
)

with open('engines/special_pan.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
