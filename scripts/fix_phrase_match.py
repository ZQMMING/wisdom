# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在parse_dayun_xiji_from_text函数中增加关键短语匹配
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

new = """        # 大运干支的五行和十神(用于关键短语匹配)
        gan_wx = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}.get(gan, '')
        zhi_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(zhi, '')
        dayun_wx_list = [gan_wx, zhi_wx] if gan_wx and zhi_wx else ([gan_wx] if gan_wx else ([zhi_wx] if zhi_wx else []))
        
        # 在上下文中判断喜忌
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
                    ji_score += 1
            # 关键短语: 喜神即是X / 喜用X / 为喜X
            for phrase in ['喜神即是', '喜用', '为喜', '即是喜', '为用', '辅用', '相神']:
                ppos = sent.find(phrase)
                if ppos >= 0:
                    # 检查短语后面的五行是否与大运五行匹配
                    after = sent[ppos+len(phrase):ppos+len(phrase)+5]
                    for wx in dayun_wx_list:
                        if wx in after:
                            phrase_xi = True
                            break
            # 关键短语: 所嫌者X / 所忌者X / 所畏者X / 所怕X
            for phrase in ['所嫌者', '所忌者', '所畏者', '所怕', '所恶', '所病', '嫌', '畏', '怕']:
                ppos = sent.find(phrase)
                if ppos >= 0:
                    after = sent[ppos+len(phrase):ppos+len(phrase)+5]
                    for wx in dayun_wx_list:
                        if wx in after:
                            phrase_ji = True
                            break
        # 关键短语优先
        if phrase_xi and not phrase_ji:
            results[gz] = 'XI'
        elif phrase_ji and not phrase_xi:
            results[gz] = 'JI'
        elif phrase_xi and phrase_ji:
            results[gz] = 'MIXED'
        elif xi_score > ji_score:
            results[gz] = 'XI'
        elif ji_score > xi_score:
            results[gz] = 'JI'
        elif xi_score > 0:
            results[gz] = 'MIXED'
    return results"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_dayun_xiji_accuracy.py关键短语匹配优化完成')
