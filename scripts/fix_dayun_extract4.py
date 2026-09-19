# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改parse_dayun_xiji_from_text函数, 增加段落级匹配
old = """def parse_dayun_xiji_from_text(text, dayun_list):
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
                context_sents.add(j)"""

new = """def parse_dayun_xiji_from_text(text, dayun_list):
    \"\"\"从断语文本中提取大运喜忌判断 V3.
    优化: 1)增加大运引导词匹配(交/至/行/逢/入X运); 2)段落级匹配+句子级上下文; 3)排除否定词.
    \"\"\"
    results = {}
    # 段落级分割: 以换行符分隔
    paragraphs = re.split(r'\\n+', text)
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
        # 段落级匹配: 找包含大运干支的段落
        matched_paragraphs = []
        for para in paragraphs:
            if any(p in para for p in dayun_patterns):
                matched_paragraphs.append(para)
        # 句子级匹配: 找包含大运干支的句子
        matched_indices = []
        for i, sent in enumerate(sentences):
            if any(p in sent for p in dayun_patterns):
                matched_indices.append(i)
        # 对每个匹配的句子, 取前后各2句作为上下文
        context_sents = set()
        for idx in matched_indices:
            for j in range(max(0, idx-2), min(len(sentences), idx+3)):
                context_sents.add(j)
        # 将匹配的段落也加入上下文(分割成句子)
        for para in matched_paragraphs:
            para_sents = re.split(r'[，。；！？]', para)
            for ps in para_sents:
                if ps.strip():
                    # 在全局sentences中查找
                    for i, sent in enumerate(sentences):
                        if ps.strip() in sent:
                            context_sents.add(i)
                            break"""

c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('大运喜忌原文提取V3优化完成(段落级匹配)')
