# -*- coding: utf-8 -*-
import csv, re, sys
sys.path.insert(0,'.')

lines=open(r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt',encoding='utf-8').readlines()
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
print(f'总案例: {len(rows)}')

GZ = r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]'
BZ_RE = re.compile(rf'^{GZ}\s+{GZ}\s+{GZ}\s+{GZ}\s*$')

def get_case_text(line_no):
    start = line_no + 1
    end = start
    while end < len(lines):
        l = lines[end].strip()
        if l.startswith('八字：') or l.startswith('====') or l.startswith('【') or BZ_RE.match(l):
            break
        end += 1
    return ''.join(lines[start:end])

checks = [
    ('身旺', ['HEAVY-ROOT', 'DESHI-BUWANG'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似']),
    ('身强', ['HEAVY-ROOT'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似']),
    ('身弱', ['LIGHT-ROOT', 'JIRUO-WUGEN'], ['俗以', '俗见', '俗论', '俗', '财多', '煞重', '泄重', '似乎', '看似', '弱中', '弱变', '弱不']),
    ('日主旺', ['HEAVY-ROOT'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似']),
    ('日主弱', ['LIGHT-ROOT'], ['俗以', '俗见', '俗论', '俗', '财多', '煞重', '泄重', '似乎', '看似', '弱中', '弱变', '弱不']),
    ('得地', ['HEAVY-ROOT'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '运', '大運', '星', '官', '财', '食', '伤', '印', '杀', '煞', '伤', '官星', '财星']),
    ('得时', ['DESHI-BUWANG'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '运', '大運', '支', '星', '官', '财', '食', '伤', '印', '杀', '煞']),
    ('得令', ['DESHI-BUWANG'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '运', '大運', '星', '官', '财', '食', '伤', '印', '杀', '煞']),
    ('失令', ['SHISHI-BURUO'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '运', '大運', '星', '官', '财', '食', '伤', '印', '杀', '煞', '日主']),
    ('得势', ['YIN-PARTY', 'BIJIE-PARTY'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '运', '大運', '星', '官', '财', '食', '伤', '印', '杀', '煞']),
]

match = 0
total = 0
mismatches = []

for r in rows:
    line_no = int(r['line'])
    qs = r.get('queries','')
    text = get_case_text(line_no)
    
    for kw, engine_qs, exclude in checks:
        if kw in text:
            idx = text.find(kw)
            context = text[max(0,idx-20):idx+len(kw)+20]
            if any(ex in context for ex in exclude):
                continue
            total += 1
            if any(eq in qs for eq in engine_qs):
                match += 1
            else:
                mismatches.append((r['chart'], kw, engine_qs, qs[:80]))

print(f'正面判断匹配: {match}/{total} = {match/total*100:.1f}%' if total>0 else '无对比样本')
print()
print(f'不匹配前15个:')
for m in mismatches[:15]:
    print(f'  {m[0]}: 原文"{m[1]}" 引擎应有{m[2]} 实际有{m[3][:60]}')
