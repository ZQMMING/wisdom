# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_accuracy3.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在章节标题截断后, 增加"何知其人"截断
old = """    # 遇到章节标题时截断(避免包含下一章内容)
    chapter_match = re.search(r'={3,}\\s*[^=]+\\s*={3,}', context)
    if chapter_match:
        context = context[:chapter_match.start()]"""

new = """    # 遇到章节标题时截断(避免包含下一章内容)
    chapter_match = re.search(r'={3,}\\s*[^=]+\\s*={3,}', context)
    if chapter_match:
        context = context[:chapter_match.start()]
    # 遇到"何知其人"时截断(何知章是下一章, 不是命例断语)
    hezhi_match = re.search(r'何知其人', context)
    if hezhi_match:
        context = context[:hezhi_match.start()]"""

c = c.replace(old, new)
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('对齐脚本增加何知其人截断完成')
