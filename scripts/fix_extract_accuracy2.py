# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 优化: 只有当大运引导词出现在上下文中时, 才判断为具体大运的喜忌
old = """        # 在上下文中判断喜忌
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

new = """        # 在上下文中判断喜忌
        xi_score = 0
        ji_score = 0
        # 关键短语匹配: 喜神即是X / 所嫌者X
        phrase_xi = False
        phrase_ji = False
        # 命例总体评价的排除前缀(这些句子不应该作为具体大运的喜忌判断)
        overview_prefixes = ['此造', '此满局', '此命', '此局', '以四柱', '观其', '夫', '盖', '总之', '大凡', '凡此', '由此观之', '由是观之', '所喜者', '所惜者', '此亦', '此则', '此则']
        # 大运引导词(只有当这些词出现在上下文中时, 才判断为具体大运的喜忌)
        dayun_guide_words = ['交', '至', '行', '逢', '入', '到', '走', '上', '运']
        # 检查上下文中是否有大运引导词
        has_dayun_guide = False
        for idx in context_sents:
            sent = sentences[idx].strip()
            if any(gw in sent for gw in dayun_guide_words):
                has_dayun_guide = True
                break
        # 如果没有大运引导词, 只有完整干支匹配时才判断(降低权重)
        guide_weight = 1.0 if has_dayun_guide else 0.3
        
        for idx in context_sents:
            sent = sentences[idx].strip()
            # 排除命例总体评价的句子
            is_overview = any(sent.startswith(prefix) for prefix in overview_prefixes)
            if is_overview and len(sent) > 20:
                continue
            for kw in XI_KEYWORDS:
                pos = sent.find(kw)
                if pos >= 0 and not _has_negation(sent, pos):
                    xi_score += guide_weight
            for kw in JI_KEYWORDS:
                pos = sent.find(kw)
                if pos >= 0:
                    ji_score += guide_weight"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_dayun_xiji_accuracy.py优化完成(增加大运引导词权重+更多命例总体评价排除)')
