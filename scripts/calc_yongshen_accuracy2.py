# -*- coding: utf-8 -*-
"""改进版: 用带空格格式搜索命例, 提取用神断言, 计算准确率."""
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
    # 模式1: 用神必在X / 用神在X / 用神为X / 用神是X
    for m in re.finditer(r'用神[必是乃为在有取宜用]+[了]?([^，。；！？\s]{1,6})', all_text):
        results.update(extract_wuxing(m.group(1)))
    # 模式2: X为用神 / X即是用神 / X就是用神 / X乃用神
    for m in re.finditer(r'([^，。；！？\s]{1,6})[即乃为是]+用神', all_text):
        results.update(extract_wuxing(m.group(1)))
    # 模式3: 用X / 取X为用 / 以X为用
    for m in re.finditer(r'[用取以]([^，。；！？\s]{1,4})[为用]', all_text):
        results.update(extract_wuxing(m.group(1)))
    # 模式4: X用神 (如"壬水用神伤尽")
    for m in re.finditer(r'([甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥木火土金水]{1,6})用神', all_text):
        results.update(extract_wuxing(m.group(1)))
    # 模式5: 用神X伤 / 用神X尽
    for m in re.finditer(r'用神([^，。；！？\s]{1,4})[伤尽去损]', all_text):
        results.update(extract_wuxing(m.group(1)))
    return results

# 读取DTS原文
with open(dts_path, encoding='utf-8-sig') as f:
    content = f.read()

# 读取引擎输出
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    engine_rows = list(reader)

print('引擎输出命例数:', len(engine_rows))

# 对齐
match_count = 0
mismatch_count = 0
unknown_count = 0
not_found = 0
mismatches = []

for row in engine_rows:
    chart = row['chart']
    # 带空格格式
    chart_spaced = chart[:2] + ' ' + chart[2:4] + ' ' + chart[4:6] + ' ' + chart[6:8]

    found_pos = content.find(chart_spaced)
    if found_pos < 0:
        not_found += 1
        continue

    # 提取后1200字上下文 (命例断语通常在后面)
    ctx_end = min(len(content), found_pos + 1500)
    context = content[found_pos:ctx_end]

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
