# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 替换parse_dayun_xiji_from_text函数, 增加大运引导词匹配和上下文窗口
old = """def parse_dayun_xiji_from_text(text, dayun_list):
    \"\"\"从断语文本中提取大运喜忌判断.\"\"\"
    results = {}
    for gz in dayun_list:
        gan = gz[0]
        zhi = gz[1]
        sentences = re.split(r'[，。；！？\\n]', text)
        for sent in sentences:
            if gan in sent or zhi in sent:
                xi_score = 0
                ji_score = 0
                for kw in XI_KEYWORDS:
                    pos = sent.find(kw)
                    if pos >= 0 and not _has_negation(sent, pos):
                        xi_score += 1
                for kw in JI_KEYWORDS:
                    pos = sent.find(kw)
                    if pos >= 0:
                        ji_score += 1
                if xi_score > ji_score:
                    results[gz] = 'XI'
                elif ji_score > xi_score:
                    results[gz] = 'JI'
                elif xi_score > 0:
                    results[gz] = 'MIXED'
    return results"""

new = """def parse_dayun_xiji_from_text(text, dayun_list):
    \"\"\"从断语文本中提取大运喜忌判断 V2.
    优化: 1)增加大运引导词匹配(交/至/行/逢/入X运); 2)扩大上下文窗口(前后各2句); 3)排除否定词.
    \"\"\"
    results = {}
    sentences = re.split(r'[，。；！？\\n]', text)
    for gz in dayun_list:
        gan = gz[0]
        zhi = gz[1]
        # 大运引导词: 交/至/行/逢/入/到/走/上 + 天干/地支 + 运
        dayun_patterns = [
            f'交{gan}', f'交{zhi}', f'交{gz}',
            f'至{gan}', f'至{zhi}', f'至{gz}',
            f'行{gan}', f'行{zhi}', f'行{gz}',
            f'逢{gan}', f'逢{zhi}', f'逢{gz}',
            f'入{gan}', f'入{zhi}', f'入{gz}',
            f'{gan}运', f'{zhi}运', f'{gz}运',
            gan, zhi,  # 兜底: 直接匹配天干/地支
        ]
        matched_indices = []
        for i, sent in enumerate(sentences):
            if any(p in sent for p in dayun_patterns):
                matched_indices.append(i)
        # 对每个匹配的句子, 取前后各2句作为上下文
        context_sents = set()
        for idx in matched_indices:
            for j in range(max(0, idx-2), min(len(sentences), idx+3)):
                context_sents.add(j)
        # 在上下文中判断喜忌
        xi_score = 0
        ji_score = 0
        for idx in context_sents:
            sent = sentences[idx]
            for kw in XI_KEYWORDS:
                pos = sent.find(kw)
                if pos >= 0 and not _has_negation(sent, pos):
                    xi_score += 1
            for kw in JI_KEYWORDS:
                pos = sent.find(kw)
                if pos >= 0:
                    ji_score += 1
        if xi_score > ji_score:
            results[gz] = 'XI'
        elif ji_score > xi_score:
            results[gz] = 'JI'
        elif xi_score > 0:
            results[gz] = 'MIXED'
    return results"""

c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('大运喜忌原文提取V2优化完成(大运引导词+上下文窗口)')
