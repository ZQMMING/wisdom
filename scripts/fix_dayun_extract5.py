# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改parse_dayun_xiji_from_text函数, 增加完整大运干支匹配优先级
old = """        # 大运引导词: 交/至/行/逢/入/到/走/上 + 天干/地支 + 运
        dayun_patterns = [
            f'交{gan}', f'交{zhi}', f'交{gz}',
            f'至{gan}', f'至{zhi}', f'至{gz}',
            f'行{gan}', f'行{zhi}', f'行{gz}',
            f'逢{gan}', f'逢{zhi}', f'逢{gz}',
            f'入{gan}', f'入{zhi}', f'入{gz}',
            f'{gan}运', f'{zhi}运', f'{gz}运',
            gan, zhi,  # 兜底: 直接匹配天干/地支
        ]"""
new = """        # 大运引导词: 交/至/行/逢/入/到/走/上 + 天干/地支 + 运
        # 优先级: 完整干支 > 引导词+干支 > 引导词+天干/地支 > 干支+运 > 天干/地支
        dayun_patterns = [
            # 最高优先级: 完整大运干支
            f'交{gz}', f'至{gz}', f'行{gz}', f'逢{gz}', f'入{gz}',
            f'{gz}运',
            # 次优先级: 引导词+天干/地支
            f'交{gan}', f'交{zhi}',
            f'至{gan}', f'至{zhi}',
            f'行{gan}', f'行{zhi}',
            f'逢{gan}', f'逢{zhi}',
            f'入{gan}', f'入{zhi}',
            f'{gan}运', f'{zhi}运',
            # 最低优先级: 直接匹配天干/地支(兜底)
            gan, zhi,
        ]"""
c = c.replace(old, new)

# 修改匹配逻辑, 增加完整干支匹配的权重
old2 = """        # 句子级匹配: 找包含大运干支的句子
        matched_indices = []
        for i, sent in enumerate(sentences):
            if any(p in sent for p in dayun_patterns):
                matched_indices.append(i)"""
new2 = """        # 句子级匹配: 找包含大运干支的句子
        # 完整干支匹配的句子权重更高
        matched_indices = []
        full_match_indices = []
        full_patterns = [f'交{gz}', f'至{gz}', f'行{gz}', f'逢{gz}', f'入{gz}', f'{gz}运', gz]
        for i, sent in enumerate(sentences):
            if any(p in sent for p in dayun_patterns):
                matched_indices.append(i)
            if any(p in sent for p in full_patterns):
                full_match_indices.append(i)"""
c = c.replace(old2, new2)

# 修改上下文窗口, 完整干支匹配的句子上下文窗口更大
old3 = """        # 对每个匹配的句子, 取前后各2句作为上下文
        context_sents = set()
        for idx in matched_indices:
            for j in range(max(0, idx-2), min(len(sentences), idx+3)):
                context_sents.add(j)"""
new3 = """        # 对每个匹配的句子, 取前后各2句作为上下文
        # 完整干支匹配的句子上下文窗口更大(前后各3句)
        context_sents = set()
        for idx in matched_indices:
            for j in range(max(0, idx-2), min(len(sentences), idx+3)):
                context_sents.add(j)
        for idx in full_match_indices:
            for j in range(max(0, idx-3), min(len(sentences), idx+4)):
                context_sents.add(j)"""
c = c.replace(old3, new3)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('大运喜忌原文提取V4优化完成(完整干支匹配优先级)')
