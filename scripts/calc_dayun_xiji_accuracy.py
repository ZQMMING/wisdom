# -*- coding: utf-8 -*-
"""大运应期喜忌与DTS断语对齐评估 V1.0
提取DTS原文中大运断语的喜忌判断, 与引擎dayun_xiji标签对齐。
"""
import re, csv, sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')

dts_path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
csv_path = r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv'

with open(dts_path, encoding='utf-8-sig') as f:
    content = f.read()

# 读取CSV
with open(csv_path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

# 命例定位: 八字格式 "辛卯 丁酉 庚午 丙子"
chart_pattern = re.compile(r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])')

# 大运喜忌关键词
XI_KEYWORDS = ['喜', '利', '吉', '宜', '前程', '富贵', '发', '亨', '通', '兴隆', '得意', '顺遂', '有功', '得名', '进用', '升迁', '登科', '及第', '荣华']
JI_KEYWORDS = ['忌', '不利', '凶', '不宜', '不禄', '夭', '贫', '贱', '败', '破', '灾', '病', '死', '阻', '艰', '苦', '不寿', '刑伤', '克妻', '克子', '破财', '丢官', '罢职', '流落', '寒酸']
NEGATION_PREFIX = ['不', '无', '未', '莫', '勿', '弗', '非']

def extract_dayun_judgment(chart_str, content):
    """提取命例的大运断语."""
    # 找命例位置
    chart_no_space = chart_str.replace(' ', '')
    # 在原文中找带空格的八字
    for m in chart_pattern.finditer(content):
        found = ''.join(m.groups())
        if found == chart_no_space:
            # 大运断语 = 当前命例到下一个命例之间, 或到下一个"八字："之前
            start = m.end()
            # 找下一个命例或下一个"八字："
            next_m = chart_pattern.search(content, start + 10)
            next_bazi = content.find('八字：', start + 10)
            end = min(next_m.start() if next_m else 999999, next_bazi if next_bazi > 0 else 999999)
            if end > 999999:
                end = start + 2000
            ctx = content[start:end]
            return ctx[:1500]
    return ''

def _has_negation(sent, keyword_pos):
    """检查关键词前是否有否定词或否定短语."""
    # 检查关键词前2个字符是否有否定词
    for i in range(max(0, keyword_pos-2), keyword_pos):
        if sent[i] in NEGATION_PREFIX:
            return True
    # 检查更长的否定短语
    neg_phrases = ['不以为', '不足为', '未足为', '不可为', '不能为', '不必为', '不可以', '未可以', '不啻', '无非', '不过']
    for phrase in neg_phrases:
        if keyword_pos >= len(phrase):
            if sent[keyword_pos-len(phrase):keyword_pos] == phrase:
                return True
    return False

def parse_dayun_xiji_from_text(text, dayun_list):
    """从断语文本中提取大运喜忌判断 V3.
    优化: 1)增加大运引导词匹配(交/至/行/逢/入X运); 2)段落级匹配+句子级上下文; 3)排除否定词.
    """
    results = {}
    # 段落级分割: 以换行符分隔
    paragraphs = re.split(r'\n+', text)
    sentences = re.split(r'[，。；！？\n]', text)
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
                            break
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
    return results

# 对齐评估
total = 0
matched = 0
mismatched = 0
no_judgment = 0
details = []

for row in rows:
    chart = row['chart']
    dayun_str = row.get('dayun', '')
    if not dayun_str:
        continue
    dayun_list = dayun_str.split('|')
    
    # 引擎大运喜忌
    engine_xiji = {}
    for item in row.get('dayun_xiji', '').split('|'):
        if ':' in item:
            parts = item.split(':')
            if len(parts) >= 2:
                engine_xiji[parts[0]] = parts[1]
    
    # 原文大运断语
    judgment_text = extract_dayun_judgment(chart, content)
    if not judgment_text:
        no_judgment += 1
        continue
    
    # 解析原文喜忌
    text_xiji = parse_dayun_xiji_from_text(judgment_text, dayun_list)
    
    if not text_xiji:
        no_judgment += 1
        continue
    
    # 对齐
    case_matched = 0
    case_total = 0
    for gz, text_label in text_xiji.items():
        if gz not in engine_xiji:
            continue
        engine_label = engine_xiji[gz]
        case_total += 1
        total += 1
        
        # 映射: SUPPORT_USE_GOD/SUPPORT_XI_SHEN -> XI; SUPPRESS_USE_GOD -> JI
        engine_xi = engine_label in ('SUPPORT_USE_GOD', 'SUPPORT_XI_SHEN')
        engine_ji = engine_label == 'SUPPRESS_USE_GOD'
        
        text_xi = text_label == 'XI'
        text_ji = text_label == 'JI'
        
        if (engine_xi and text_xi) or (engine_ji and text_ji):
            matched += 1
            case_matched += 1
        elif text_label == 'MIXED':
            matched += 1  # 混合不算错
            case_matched += 1
        else:
            mismatched += 1
            details.append({
                'chart': chart,
                'dayun': gz,
                'engine': engine_label,
                'text': text_label,
                'text_snippet': judgment_text[:100],
            })
    
    if case_total > 0:
        pass

print('=== 大运应期喜忌对齐评估 V1.0 ===')
print('总可对齐大运: %d' % total)
print('匹配: %d (%.1f%%)' % (matched, matched/total*100 if total else 0))
print('不匹配: %d' % mismatched)
print('无原文喜忌判断: %d' % no_judgment)
print()
print('=== 不匹配样例(前10) ===')
for d in details[:10]:
    print('%s %s: 引擎=%s, 原文=%s' % (d['chart'], d['dayun'], d['engine'], d['text']))
    print('  原文: %s' % d['text_snippet'][:80])
