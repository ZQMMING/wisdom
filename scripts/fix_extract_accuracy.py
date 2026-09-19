# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 优化1: 缩小上下文窗口, 从前后各2-3句缩小到前后各1句
old1 = """        # 对每个匹配的句子, 取前后各2句作为上下文
        # 完整干支匹配的句子上下文窗口更大(前后各3句)
        context_sents = set()
        for idx in matched_indices:
            for j in range(max(0, idx-2), min(len(sentences), idx+3)):
                context_sents.add(j)
        for idx in full_match_indices:
            for j in range(max(0, idx-3), min(len(sentences), idx+4)):
                context_sents.add(j)"""

new1 = """        # 对每个匹配的句子, 取前后各1句作为上下文(缩小窗口避免命例总体评价干扰)
        # 完整干支匹配的句子上下文窗口稍大(前后各2句)
        context_sents = set()
        for idx in matched_indices:
            for j in range(max(0, idx-1), min(len(sentences), idx+2)):
                context_sents.add(j)
        for idx in full_match_indices:
            for j in range(max(0, idx-2), min(len(sentences), idx+3)):
                context_sents.add(j)"""
c = c.replace(old1, new1)

# 优化2: 增加命例总体评价的排除逻辑
old2 = """        # 在上下文中判断喜忌
        xi_score = 0
        ji_score = 0
        # 关键短语匹配: 喜神即是X / 所嫌者X
        phrase_xi = False
        phrase_ji = False
        for idx in context_sents:
            sent = sentences[idx]
            for kw in XI_KEYWORDS:
                pos = sent.find(kw)
                if pos >= 0 and not _has_negation(sent, pos):
                    xi_score += 1
            for kw in JI_KEYWORDS:
                pos = sent.find(kw)
                if pos >= 0:
                    ji_score += 1"""

new2 = """        # 在上下文中判断喜忌
        xi_score = 0
        ji_score = 0
        # 关键短语匹配: 喜神即是X / 所嫌者X
        phrase_xi = False
        phrase_ji = False
        # 命例总体评价的排除前缀(这些句子不应该作为具体大运的喜忌判断)
        overview_prefixes = ['此造', '此满局', '此命', '此局', '以四柱', '观其', '夫', '盖', '总之', '大凡', '凡此', '由此观之', '由是观之']
        for idx in context_sents:
            sent = sentences[idx].strip()
            # 排除命例总体评价的句子
            is_overview = any(sent.startswith(prefix) for prefix in overview_prefixes)
            if is_overview and len(sent) > 20:
                continue
            for kw in XI_KEYWORDS:
                pos = sent.find(kw)
                if pos >= 0 and not _has_negation(sent, pos):
                    xi_score += 1
            for kw in JI_KEYWORDS:
                pos = sent.find(kw)
                if pos >= 0:
                    ji_score += 1"""
c = c.replace(old2, new2)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_dayun_xiji_accuracy.py优化完成(缩小上下文窗口+排除命例总体评价)')
