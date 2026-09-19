# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 优化: 更严格的语义角色标注, 区分"原局喜忌"与"大运喜忌"
old = """        # 命例总体评价的排除前缀(这些句子不应该作为具体大运的喜忌判断)
        overview_prefixes = ['此造', '此满局', '此命', '此局', '以四柱', '观其', '夫', '盖', '总之', '大凡', '凡此', '由此观之', '由是观之']
        for idx in context_sents:
            sent = sentences[idx].strip()
            # 排除命例总体评价的句子
            is_overview = any(sent.startswith(prefix) for prefix in overview_prefixes)
            if is_overview and len(sent) > 20:
                continue
            for kw in XI_KEYWORDS:"""

new = """        # V4: 更严格的语义角色标注, 区分"原局喜忌"与"大运喜忌"
        # 命例总体评价的排除前缀(这些句子不应该作为具体大运的喜忌判断)
        overview_prefixes = ['此造', '此满局', '此命', '此局', '以四柱', '观其', '夫', '盖', '总之', '大凡', '凡此', '由此观之', '由是观之',
                              '所喜者', '所惜者', '此亦', '此则', '更妙', '更喜', '所妙', '可喜', '可嫌', '嫌其', '惜其',
                              '前造', '后造', '彼造', '两造', '合而', '大抵', '大约', '大概', '此则', '此亦', '所重在', '所轻者']
        # 大运引导词(只有当这些词出现在句子中时, 才认为是具体大运的喜忌判断)
        dayun_guide_words = ['交', '至', '行', '逢', '入', '到', '走', '上', '运', '岁', '流年', '大运', '十年', '一运', '步运']
        for idx in context_sents:
            sent = sentences[idx].strip()
            # 排除命例总体评价的句子
            is_overview = any(sent.startswith(prefix) for prefix in overview_prefixes)
            if is_overview and len(sent) > 15:
                continue
            # 检查句子中是否有大运引导词或完整大运干支
            has_guide = any(gw in sent for gw in dayun_guide_words)
            has_full_gz = gz in sent
            # 如果没有大运引导词且没有完整大运干支, 则排除(可能是命例总体评价)
            if not has_guide and not has_full_gz and len(sent) > 10:
                continue
            for kw in XI_KEYWORDS:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_dayun_xiji_accuracy.py V4优化完成(更严格的语义角色标注: 无大运引导词且无完整干支的句子排除)')
