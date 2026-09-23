with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'yin_xu = _yin_xu_tou_bei_zhi(stems, None, day_wx)',
    'yin_xu = _yin_xu_tou_bei_zhi(stems, [], day_wx)'
)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
