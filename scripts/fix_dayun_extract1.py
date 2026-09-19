# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 优化1: 增加否定词列表, 在关键词匹配时排除否定词
old1 = """XI_KEYWORDS = ['喜', '利', '吉', '宜', '前程', '富贵', '发', '亨', '通', '兴隆', '得意', '顺遂']
JI_KEYWORDS = ['忌', '不利', '凶', '不宜', '不禄', '夭', '贫', '贱', '败', '破', '灾', '病', '死', '阻', '艰', '苦']"""

new1 = """XI_KEYWORDS = ['喜', '利', '吉', '宜', '前程', '富贵', '发', '亨', '通', '兴隆', '得意', '顺遂', '有功', '得名', '进用', '升迁', '登科', '及第', '荣华']
JI_KEYWORDS = ['忌', '不利', '凶', '不宜', '不禄', '夭', '贫', '贱', '败', '破', '灾', '病', '死', '阻', '艰', '苦', '不寿', '刑伤', '克妻', '克子', '破财', '丢官', '罢职', '流落', '寒酸']
NEGATION_PREFIX = ['不', '无', '未', '莫', '勿', '弗', '非']"""

c = c.replace(old1, new1)

# 优化2: 修改parse_dayun_xiji_from_text函数, 排除否定词, 增加上下文匹配
old2 = """def parse_dayun_xiji_from_text(text, dayun_list):
    \"\"\"从断语文本中提取大运喜忌判断.\"\"\"
    results = {}
    for gz in dayun_list:
        gan = gz[0]
        zhi = gz[1]
        # 找大运干支附近的喜忌判断
        # 简单方法: 找包含该大运天干或地支的句子
        sentences = re.split(r'[，。；！？\\n]', text)
        for sent in sentences:
            if gan in sent or zhi in sent:
                # 判断喜忌
                xi_score = sum(1 for kw in XI_KEYWORDS if kw in sent)
                ji_score = sum(1 for kw in JI_KEYWORDS if kw in sent)
                if xi_score > ji_score:
                    results[gz] = 'XI'
                elif ji_score > xi_score:
                    results[gz] = 'JI'
                elif xi_score > 0:
                    results[gz] = 'MIXED'
    return results"""

new2 = """def _has_negation(sent, keyword_pos):
    \"\"\"检查关键词前是否有否定词.\"\"\"
    for i in range(max(0, keyword_pos-2), keyword_pos):
        if sent[i] in NEGATION_PREFIX:
            return True
    return False

def parse_dayun_xiji_from_text(text, dayun_list):
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

c = c.replace(old2, new2)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('大运喜忌原文提取优化完成(否定词排除+关键词扩展)')
