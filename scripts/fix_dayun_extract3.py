# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在parse_dayun_xiji_from_text函数中, 增加明确的喜忌运引导词匹配
old = """        # 在上下文中判断喜忌
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

new = """        # V3: 明确的喜忌运引导词匹配 (优先级最高)
        explicit_xi = False
        explicit_ji = False
        explicit_xi_patterns = [
            f'交{gan}运.*发', f'交{zhi}运.*发', f'交{gz}运.*发',
            f'交{gan}运.*贵', f'交{zhi}运.*贵', f'交{gz}运.*贵',
            f'交{gan}运.*亨', f'交{zhi}运.*亨', f'交{gz}运.*亨',
            f'至{gan}运.*发', f'至{zhi}运.*发',
            f'行{gan}运.*发', f'行{zhi}运.*发',
            f'{gan}运.*大发', f'{zhi}运.*大发',
            f'{gan}运.*顺遂', f'{zhi}运.*顺遂',
            f'{gan}运.*兴隆', f'{zhi}运.*兴隆',
            f'{gan}运.*得意', f'{zhi}运.*得意',
        ]
        explicit_ji_patterns = [
            f'交{gan}运.*不寿', f'交{zhi}运.*不寿', f'交{gz}运.*不寿',
            f'交{gan}运.*而亡', f'交{zhi}运.*而亡',
            f'交{gan}运.*而卒', f'交{zhi}运.*而卒',
            f'交{gan}运.*而死', f'交{zhi}运.*而死',
            f'交{gan}运.*破败', f'交{zhi}运.*破败',
            f'交{gan}运.*灾', f'交{zhi}运.*灾',
            f'至{gan}运.*不寿', f'至{zhi}运.*不寿',
            f'至{gan}运.*而亡', f'至{zhi}运.*而亡',
            f'行{gan}运.*不寿', f'行{zhi}运.*不寿',
            f'{gan}运.*不禄', f'{zhi}运.*不禄',
            f'{gan}运.*夭', f'{zhi}运.*夭',
            f'{gan}运.*贫', f'{zhi}运.*贫',
            f'{gan}运.*贱', f'{zhi}运.*贱',
        ]
        for idx in context_sents:
            sent = sentences[idx]
            for pat in explicit_xi_patterns:
                if re.search(pat, sent):
                    explicit_xi = True
                    break
            for pat in explicit_ji_patterns:
                if re.search(pat, sent):
                    explicit_ji = True
                    break
            if explicit_xi or explicit_ji:
                break
        
        if explicit_xi and not explicit_ji:
            results[gz] = 'XI'
            continue
        if explicit_ji and not explicit_xi:
            results[gz] = 'JI'
            continue
        
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
print('大运喜忌原文提取V3优化完成(增加明确喜忌运引导词)')
