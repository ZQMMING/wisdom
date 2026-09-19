# -*- coding: utf-8 -*-
"""改进版v3: 命例断语 = 当前命例到下一个命例之间的文字, 避免串扰."""
import re
import csv

dts_path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
csv_path = r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv'

STEM_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
BRANCH_WX = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}

def extract_wuxing(text):
    results = set()
    for stem in '甲乙丙丁戊己庚辛壬癸':
        if stem in text:
            results.add(STEM_WX[stem])
    for branch in '子丑寅卯辰巳午未申酉戌亥':
        if branch in text:
            results.add(BRANCH_WX[branch])
    for wx in '木火土金水':
        if wx in text:
            results.add(wx)
    return results

def extract_yongshen_wuxing(sentences):
    all_text = '。'.join(sentences)
    results = set()
    for m in re.finditer(r'用神[必是乃为在有取宜用]+[了]?([^，。；！？\s]{1,6})', all_text):
        results.update(extract_wuxing(m.group(1)))
    for m in re.finditer(r'([^，。；！？\s]{1,6})[即乃为是]+用神', all_text):
        results.update(extract_wuxing(m.group(1)))
    for m in re.finditer(r'[用取以]([^，。；！？\s]{1,4})[为用](?!仇|忌)', all_text):
        results.update(extract_wuxing(m.group(1)))
    for m in re.finditer(r'([甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥木火土金水]{1,6})用神', all_text):
        results.update(extract_wuxing(m.group(1)))
    for m in re.finditer(r'([^，。；！？\s]{1,6})而为用喜神', all_text):
        results.update(extract_wuxing(m.group(1)))
    for m in re.finditer(r'([甲乙丙丁戊己庚辛壬癸][木火土金水]?)[^。]{0,30}?而为用喜神', all_text):
        results.update(extract_wuxing(m.group(1)))
    for m in re.finditer(r'用神([^，。；！？\s]{1,4})[伤尽去损]', all_text):
        results.update(extract_wuxing(m.group(1)))
    for m in re.finditer(r'必以([^，。；！？\s]{1,6})为用', all_text):
        results.update(extract_wuxing(m.group(1)))
    return results

# 读取DTS原文
with open(dts_path, encoding='utf-8-sig') as f:
    content = f.read()

# 读取引擎输出
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    engine_rows = list(reader)

# 找到所有命例的位置 (带空格格式)
chart_pattern = re.compile(r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]\s+[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]\s+[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]\s+[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]')

all_chart_positions = []
for m in chart_pattern.finditer(content):
    chart = re.sub(r'\s+', '', m.group())
    all_chart_positions.append((m.start(), m.end(), chart))

print('原文中找到命例位置:', len(all_chart_positions))

# 建立chart到位置的映射
chart_to_pos = {}
for pos, end, chart in all_chart_positions:
    if chart not in chart_to_pos:
        chart_to_pos[chart] = []
    chart_to_pos[chart].append((pos, end))

# 对每个引擎输出命例, 找到其在原文中的位置, 断语 = 当前位置到下一个命例位置
match_count = 0
mismatch_count = 0
unknown_count = 0
not_found = 0
mismatches = []

# 按位置排序所有命例
sorted_positions = sorted(all_chart_positions, key=lambda x: x[0])

for row in engine_rows:
    chart = row['chart']
    if chart not in chart_to_pos:
        not_found += 1
        continue

    # 取第一个出现位置
    pos, end = chart_to_pos[chart][0]

    # 找到下一个命例的位置
    next_pos = len(content)
    for p, e, c in sorted_positions:
        if p > end + 10:  # 下一个命例(跳过自己)
            next_pos = p
            break

    # 断语 = 当前命例结束到下一个命例开始
    context = content[end:next_pos]
    # 遇到章节标题时截断(避免包含下一章内容)
    chapter_match = re.search(r'={3,}\s*[^=]+\s*={3,}', context)
    if chapter_match:
        context = context[:chapter_match.start()]

    sentences = re.split(r'[。；！？\n]', context)
    ys_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) > 5 and any(k in s for k in ['用神', '喜神', '忌神', '喜用', '所喜', '所忌', '宜用', '取用']):
            ys_sentences.append(s)

    if not ys_sentences:
        unknown_count += 1
        continue

    original_yongshen = extract_yongshen_wuxing(ys_sentences)
    if not original_yongshen:
        unknown_count += 1
        continue

    engine_primary = row.get('ys_primary', '').strip()
    engine_wuxings = set()
    if engine_primary:
        for part in engine_primary.split('|'):
            if part in '木火土金水':
                engine_wuxings.add(part)

    if not engine_wuxings:
        unknown_count += 1
        continue

    if engine_wuxings & original_yongshen:
        match_count += 1
    else:
        mismatch_count += 1
        mismatches.append({
            'chart': chart,
            'original': original_yongshen,
            'engine': engine_wuxings,
            'sentence': ys_sentences[0][:120],
        })

total = match_count + mismatch_count
print('原文中未找到:', not_found)
print('无法提取(无具体五行):', unknown_count)
print('总可对齐命例:', total)
print('匹配:', match_count, '(%.1f%%)' % (match_count/total*100 if total else 0))
print('不匹配:', mismatch_count, '(%.1f%%)' % (mismatch_count/total*100 if total else 0))
print()
print('=== 不匹配样例(前30) ===')
for i, m in enumerate(mismatches[:30]):
    print('[%d] %s' % (i+1, m['chart']))
    print('  原文用神: %s' % m['original'])
    print('  引擎用神: %s' % m['engine'])
    print('  原文: %s' % m['sentence'])
    print()
