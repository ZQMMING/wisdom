with open('engines/axis_xiuqi.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'HUA_SHEN = {"甲己": "土", "乙庚": "金", "丙辛": "水", "丁壬": "木", "戊癸": "火"}'
new = '''HUA_SHEN = {"甲己": "土", "己甲": "土", "乙庚": "金", "庚乙": "金",
            "丙辛": "水", "辛丙": "水", "丁壬": "木", "壬丁": "木",
            "戊癸": "火", "癸戊": "火"}'''

content = content.replace(old, new)

with open('engines/axis_xiuqi.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('fixed')
