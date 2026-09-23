with open('test_huaqi.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'run("丙辛化水(丙子辛卯丙申辛卯)", "丙", ["子", "卯", "申", "卯"], ["丙", "辛", "丙", "辛"])',
    'run("丙辛化水(丙子辛卯丙申辛卯)", "丙", ["子", "子", "申", "卯"], ["丙", "辛", "丙", "辛"])'
)

with open('test_huaqi.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
