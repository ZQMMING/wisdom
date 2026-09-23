import re

with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'conf = "MID" if demote > 0 else "CONFIRMED"'
new = '''if demote == 0:
            conf = "CONFIRMED"
        elif demote == 1:
            conf = "MID_1"
        elif demote == 2:
            conf = "MID_2"
        else:
            conf = "REJECT"'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
