# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改_has_negation函数, 增加更长的否定短语排除
old = """def _has_negation(sent, keyword_pos):
    \"\"\"检查关键词前是否有否定词.\"\"\"
    for i in range(max(0, keyword_pos-2), keyword_pos):
        if sent[i] in NEGATION_PREFIX:
            return True
    return False"""

new = """def _has_negation(sent, keyword_pos):
    \"\"\"检查关键词前是否有否定词或否定短语.\"\"\"
    # 检查关键词前2个字符是否有否定词
    for i in range(max(0, keyword_pos-2), keyword_pos):
        if sent[i] in NEGATION_PREFIX:
            return True
    # 检查更长的否定短语
    neg_phrases = ['不以为', '不足为', '未足为', '不可为', '不能为', '不必为', '不可以', '未可以', '不啻', '无非', '不过']
    for phrase in neg_phrases:
        if keyword_pos >= len(phrase):
            if sent[keyword_pos-len(phrase):keyword_pos] == phrase:
                return True
    return False"""

c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('大运喜忌原文提取否定词排除优化完成')
