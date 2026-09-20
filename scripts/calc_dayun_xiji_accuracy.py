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
        ]
        # 段落级匹配: 找包含大运干支的段落
        matched_paragraphs = []
        for para in paragraphs:
            if any(p in para for p in dayun_patterns):
                matched_paragraphs.append(para)
        # 句子级匹配: 找包含大运干支的句子
        # 完整干支匹配的句子权重更高
        matched_indices = []
        full_match_indices = []
        full_patterns = [f'交{gz}', f'至{gz}', f'行{gz}', f'逢{gz}', f'入{gz}', f'{gz}运', gz]
        for i, sent in enumerate(sentences):
            if any(p in sent for p in dayun_patterns):
                matched_indices.append(i)
            if any(p in sent for p in full_patterns):
                full_match_indices.append(i)
        # V8.2: 完整干支匹配用前后各1句上下文, 引导词+天干/地支匹配只取句子本身
        context_sents = set()
        for idx in full_match_indices:
            for j in range(max(0, idx-1), min(len(sentences), idx+2)):
                context_sents.add(j)
        for idx in matched_indices:
            if idx not in full_match_indices:
                context_sents.add(idx)
        # 大运干支的五行和十神(用于关键短语匹配)
        gan_wx = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}.get(gan, '')
        zhi_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(zhi, '')
        dayun_wx_list = [gan_wx, zhi_wx] if gan_wx and zhi_wx else ([gan_wx] if gan_wx else ([zhi_wx] if zhi_wx else []))
        
        # 在上下文中判断喜忌
        xi_score = 0
        ji_score = 0
        # 关键短语匹配: 喜神即是X / 所嫌者X
        phrase_xi = False
        phrase_ji = False
        # V4: 更严格的语义角色标注, 区分"原局喜忌"与"大运喜忌"
        # 命例总体评价的排除前缀(这些句子不应该作为具体大运的喜忌判断)
        overview_prefixes = ['此造', '此满局', '此命', '此局', '以四柱', '观其', '夫', '盖', '总之', '大凡', '凡此', '由此观之', '由是观之',
                              '所喜者', '所惜者', '此亦', '此则', '更妙', '更喜', '所妙', '可喜', '可嫌', '嫌其', '惜其',
                              '前造', '后造', '彼造', '两造', '合而', '大抵', '大约', '大概', '此则', '此亦', '所重在', '所轻者',
                              '此命', '此局', '此造', '此满局', '此四柱', '此八字', '此命造', '此造命', '观此', '看此', '审此',
                              '总之', '大凡', '凡此', '由此观之', '由是观之', '概而言之', '统而论之', '要而论之', '推而言之',
                              '所喜', '所忌', '所嫌', '所畏', '所怕', '所恶', '所病', '所重', '所轻', '所妙', '所惜',
                              '更妙', '更喜', '可喜', '可嫌', '嫌其', '惜其', '妙在', '喜在', '忌在', '病在', '药在']
        # V6: 更严格的大运引导词匹配 - 区分明确引导词和模糊词
        # 明确大运引导词: 交/至/行/逢/入/到/走/上 + 干支
        # 模糊大运引导词: 运/岁/流年/大运等 (只有和完整干支一起出现时才匹配)
        explicit_guide_words = ['交', '至', '行', '逢', '入', '到', '走', '上', '运转', '运至', '运行', '运逢', '运入', '运交']
        vague_guide_words = ['运', '岁', '流年', '大运', '十年', '一运', '步运', '岁运', '小运', '限运', '气运',
                              '甲运', '乙运', '丙运', '丁运', '戊运', '己运', '庚运', '辛运', '壬运', '癸运',
                              '子运', '丑运', '寅运', '卯运', '辰运', '巳运', '午运', '未运', '申运', '酉运', '戌运', '亥运']
        dayun_guide_words = explicit_guide_words + vague_guide_words
        for idx in context_sents:
            sent = sentences[idx].strip()
            # V7: 排除纯大运列表的句子(只包含大运干支, 没有喜忌判断内容)
            _gz_chars = set('甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥 ')
            _non_gz = [ch for ch in sent if ch not in _gz_chars and not ch.isspace()]
            if len(_non_gz) <= 2 and len(sent) >= 4:
                continue
            # 排除命例总体评价的句子
            is_overview = any(sent.startswith(prefix) for prefix in overview_prefixes)
            if is_overview:
                continue
            # V7: 更严格排除原局总体评价(包含'以四柱观之'/'贫夭之命'等总体评价短语)
            overview_phrases = ['以四柱观之', '贫夭之命', '贫贱之命', '富贵之命', '寿夭之命', '此造', '此命', '此局', '此满局']
            if any(phrase in sent for phrase in overview_phrases) and len(sent) > 10:
                continue
            # V6: 检查句子中是否有大运引导词或完整大运干支
            # 明确引导词可以单独匹配, 模糊词必须和完整干支一起出现
            has_explicit_guide = any(gw in sent for gw in explicit_guide_words)
            has_vague_guide = any(gw in sent for gw in vague_guide_words)
            has_full_gz = gz in sent
            # 明确引导词 + 天干/地支 或 完整干支 或 模糊词+完整干支
            has_guide = has_explicit_guide or (has_vague_guide and has_full_gz)
            # V5: 更严格的语义角色标注 - 区分"原局喜忌"与"大运喜忌"
            # 原局喜忌的典型表达: "此造喜X"、"所喜者X"、"喜用X"、"为喜X"等 (没有大运引导词)
            # 大运喜忌的典型表达: "运行X地"、"交X运"、"至X运"、"行X运"等 (有大运引导词)
            # 只有明确包含大运引导词或完整大运干支的句子才计入大运喜忌判断
            # 原局喜忌的句子标记为ORIGINAL_BUREAU, 不与大运喜忌对齐
            is_original_bureau = False
            if not has_guide and not has_full_gz:
                # 检查是否是原局喜忌的典型表达
                original_bureau_patterns = ['此造', '此命', '此局', '所喜', '所忌', '喜用', '为喜', '为忌', '喜神', '忌神', '用神', '相神']
                if any(pattern in sent for pattern in original_bureau_patterns) and len(sent) > 10:
                    is_original_bureau = True
            # 如果是原局喜忌或没有大运引导词且没有完整大运干支, 则排除
            if is_original_bureau or (not has_guide and not has_full_gz and len(sent) > 10):
                continue
            for kw in XI_KEYWORDS:
                pos = sent.find(kw)
                if pos >= 0 and not _has_negation(sent, pos):
                    xi_score += 1
            for kw in JI_KEYWORDS:
                pos = sent.find(kw)
                if pos >= 0:
                    ji_score += 1
            # 关键短语: 喜神即是X / 喜用X / 为喜X / 即是喜X
            for phrase in ['喜神即是', '喜用', '为喜', '即是喜', '为用', '辅用', '相神', '喜神为']:
                ppos = sent.find(phrase)
                if ppos >= 0:
                    after = sent[ppos+len(phrase):ppos+len(phrase)+10]
                    # 检查五行匹配
                    for wx in dayun_wx_list:
                        if wx in after:
                            phrase_xi = True
                            break
                    # 检查天干地支匹配
                    if gan in after or zhi in after or gz in after:
                        phrase_xi = True
            # 关键短语: 所嫌者X / 所忌者X / 所畏者X / 所怕X / 嫌X
            for phrase in ['所嫌者', '所忌者', '所畏者', '所怕', '所恶', '所病', '嫌者', '忌者', '畏者']:
                ppos = sent.find(phrase)
                if ppos >= 0:
                    after = sent[ppos+len(phrase):ppos+len(phrase)+10]
                    for wx in dayun_wx_list:
                        if wx in after:
                            phrase_ji = True
                            break
                    if gan in after or zhi in after or gz in after:
                        phrase_ji = True
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
    engine_xiji_labels = {}
    for item in row.get('dayun_xiji', '').split('|'):
        if ':' in item:
            parts = item.split(':')
            if len(parts) >= 2:
                engine_xiji[parts[0]] = parts[1]
                if len(parts) >= 4:
                    engine_xiji_labels[parts[0]] = parts[3].split(',')
                else:
                    engine_xiji_labels[parts[0]] = [parts[1]]
    
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
        engine_labels = engine_xiji_labels.get(gz, [engine_label])
        case_total += 1
        total += 1
        
        # 映射: SUPPORT_USE_GOD/SUPPORT_XI_SHEN -> XI; SUPPRESS_USE_GOD -> JI
        # 使用多标签匹配: 任何一个标签匹配则匹配
        engine_xi = any(l in ('SUPPORT_USE_GOD', 'SUPPORT_XI_SHEN') for l in engine_labels)
        engine_ji = any(l == 'SUPPRESS_USE_GOD' for l in engine_labels)
        
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

# 保存所有不匹配案例到JSON文件
import json as _json
with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', 'w', encoding='utf-8') as _f:
    _json.dump(details, _f, ensure_ascii=False, indent=2)
print()
print('所有不匹配案例已保存到: scripts\dayun_mismatch_all.json (共%d个)' % len(details))
