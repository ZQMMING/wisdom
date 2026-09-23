with open('engines/zhuanwang_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 改——日干也算克财
old = '''            # 2. 被比劫紧贴克
            bei_ke = False
            for j, s2 in enumerate(stems):
                if j == 2: continue
                if abs(i - j) == 1 and STEM_WUXING.get(s2) in bi_cls:
                    bei_ke = True
                    break'''

new = '''            # 2. 被比劫紧贴克（日干也算，因为日干本身就是比劫）
            bei_ke = False
            for j, s2 in enumerate(stems):
                if abs(i - j) == 1 and STEM_WUXING.get(s2) in bi_cls:
                    bei_ke = True
                    break'''

content = content.replace(old, new)

with open('engines/zhuanwang_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
