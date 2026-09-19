# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 优化: 更严格地排除命例总体评价
old = """        # 命例总体评价的排除前缀(这些句子不应该作为具体大运的喜忌判断)
        overview_prefixes = ['此造', '此满局', '此命', '此局', '以四柱', '观其', '夫', '盖', '总之', '大凡', '凡此', '由此观之', '由是观之']
        for idx in context_sents:
            sent = sentences[idx].strip()
            # 排除命例总体评价的句子
            is_overview = any(sent.startswith(prefix) for prefix in overview_prefixes)
            if is_overview and len(sent) > 20:
                continue"""

new = """        # 命例总体评价的排除前缀(这些句子不应该作为具体大运的喜忌判断)
        overview_prefixes = ['此造', '此满局', '此命', '此局', '以四柱', '观其', '夫', '盖', '总之', '大凡', '凡此', '由此观之', '由是观之',
                              '所喜者', '所惜者', '此亦', '此则', '此则', '更妙', '更喜', '所妙', '可喜', '可嫌', '嫌其', '惜其',
                              '前造', '后造', '此造', '彼造', '两造', '合而', '总之', '大抵', '大约', '大概']
        # 大运引导词(只有当这些词出现在句子中时, 才认为是具体大运的喜忌判断)
        dayun_guide_in_sent = ['交', '至', '行', '逢', '入', '到', '走', '上', '运', '岁', '流年', '大运']
        for idx in context_sents:
            sent = sentences[idx].strip()
            # 排除命例总体评价的句子
            is_overview = any(sent.startswith(prefix) for prefix in overview_prefixes)
            # 检查句子中是否有大运引导词
            has_guide = any(gw in sent for gw in dayun_guide_in_sent)
            # 如果是命例总体评价且没有大运引导词, 则排除
            if is_overview and len(sent) > 20 and not has_guide:
                continue
            # 如果句子以"此"开头且没有大运引导词, 也排除(更严格)
            if sent.startswith('此') and len(sent) > 15 and not has_guide:
                continue
            # 如果句子以"所"开头且没有大运引导词, 也排除(更严格)
            if sent.startswith('所') and len(sent) > 15 and not has_guide:
                continue"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_dayun_xiji_accuracy.py优化完成(更严格地排除命例总体评价: 此/所开头且无大运引导词的句子排除)')
