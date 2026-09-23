with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 改import错误
old = '''    from spec.root_qi import STEM_WUXING, WUXING_OF as WUXING_OF_ROOT
    yin_wuxing = WUXING_OF_ROOT[day_wx]["印"]'''

new = '''    from spec.root_qi import STEM_WUXING
    yin_wuxing = WUXING_OF[day_wx]["印"]'''

content = content.replace(old, new)

# 改下面的cai_wuxing
old2 = '''    cai_wuxing = WUXING_OF_ROOT[day_wx]["财"]'''
new2 = '''    cai_wuxing = WUXING_OF[day_wx]["财"]'''

content = content.replace(old2, new2)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
