with open('engines/zhuanwang_grade.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修——SHISHEN_CLASSES用五行键
content = content.replace(
    'cai_cls = SHISHEN_CLASSES[day_stem]["财"]',
    'cai_cls = SHISHEN_CLASSES[day_wx]["财"]'
)
content = content.replace(
    'guan_sha_cls = SHISHEN_CLASSES[day_stem]["官杀"]',
    'guan_sha_cls = SHISHEN_CLASSES[day_wx]["官杀"]'
)

with open('engines/zhuanwang_grade.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
