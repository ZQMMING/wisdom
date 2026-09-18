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

# 日主五行
def day_wx(chart):
    s = chart[4] if len(chart) >= 5 else chart.split()[2][0]
    return {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}[s]

checks = [
    ('身旺', ['HEAVY-ROOT', 'YIN-PARTY', 'BIJIE-PARTY'], ['俗以','俗见','俗论','俗','似乎','看似','身旺者','身旺逢','必要身旺','身旺用','身旺喜']),
    ('身强', ['HEAVY-ROOT', 'YIN-PARTY', 'BIJIE-PARTY'], ['俗以','俗见','俗论','俗','似乎','看似','身强者']),
    ('日主旺', ['HEAVY-ROOT', 'YIN-PARTY', 'BIJIE-PARTY', 'DESHI-BUWANG'], ['俗以','俗见','俗论','俗','似乎','看似']),
    ('旺相', ['DESHI-BUWANG','HEAVY-ROOT'], ['俗以','俗见','俗论','俗','似乎','看似','运','大運','又要','必要','须要','喜','要日元','日元旺相者']),
    ('身弱', ['LIGHT-ROOT', 'JIRUO-WUGEN', 'WUGEN-YOUFU'], ['俗以','俗见','俗论','俗','财多','煞重','泄重','似乎','看似','弱中','弱变','弱不','非身弱','不论身','身弱者','身弱喜','身弱用']),
    ('日主弱', ['LIGHT-ROOT', 'WUGEN-YOUFU'], ['俗以','俗见','俗论','俗','财多','煞重','泄重','似乎','看似','弱中','弱变','弱不','非身弱','不论身']),
    ('衰弱', ['LIGHT-ROOT', 'JIRUO-WUGEN', 'WUGEN-YOUFU'], ['俗以','俗见','俗论','俗','似乎','看似','运','大運']),
    ('有根', ['HEAVY-ROOT', 'LIGHT-ROOT'], ['俗以','俗见','俗论','俗','似乎','看似','运','大運','无根']),
    ('无根', ['JIRUO-WUGEN'], ['俗以','俗见','俗论','俗','似乎','看似','运','大運','有根','非无根','不作无根','不为无根','不谓无根','岂无根','非无','不致无根','财官无根','财无根','官无根','杀无根','煞无根','食无根','伤无根','印无根','官星无根','财星无根','杀星无根','虚露无根','休囚无根','无根之木','无根之水','无根之火','无根之金','无根之土','火土无根','水木无根','金火无根','土金无根','木火无根','水火无根','火无根','土无根','金无根','水无根','至子','至丑','至寅','至卯','至辰','至巳','至午','至未','至申','至酉','至戌','至亥','行运','交运','入运','逢运','遇运','岁运','流年','无根气','全无根','无元神','根气','无根之','比肩无根','比劫无根','劫财无根','食神无根','伤官无根','偏财无根','正财无根','正官无根','七杀无根','偏印无根','正印无根','两透比肩','皆属无根','财官','食伤','印绶','官杀','比劫','枭神']),
    ('通根', ['HEAVY-ROOT', 'LIGHT-ROOT'], ['俗以','俗见','俗论','俗','似乎','看似','运','大運','财官通根','财通根','官通根','杀通根','煞通根','食通根','伤通根','印通根','官星通根','财星通根','杀星通根','食伤通根','印绶通根','官杀通根','比劫通根','比肩通根','劫财通根','枭神通根','财官皆通根','皆通根','不通根','一交','交运','行运','至子','至丑','至寅','至卯','至辰','至巳','至午','至未','至申','至酉','至戌','至亥']),
    ('得地', ['HEAVY-ROOT'], ['俗以','俗见','俗论','俗','似乎','看似','运','大運','星','官','财','食','伤','印','杀','煞','官星','财星']),
    ('得时', ['DESHI-BUWANG'], ['俗以','俗见','俗论','俗','似乎','看似','运','大運','支','星','官','财','食','伤','印','杀','煞','寅时','卯时','辰时','巳时','午时','未时','申时','酉时','戌时','亥时','子时','丑时','得时透','得时之','得时干']),
    ('得令', ['DESHI-BUWANG'], ['俗以','俗见','俗论','俗','似乎','看似','运','大運','星','官','财','食','伤','印','杀','煞']),
    ('失令', ['SHISHI-BURUO'], ['俗以','俗见','俗论','俗','似乎','看似','运','大運','星','官','财','食','伤','印','杀','煞','日主','合神','化神','财星','官星']),
    ('得势', ['YIN-PARTY', 'BIJIE-PARTY'], ['俗以','俗见','俗论','俗','似乎','看似','运','大運','星','官','财','食','伤','印','杀','煞']),
]

match = 0
total = 0
mismatches = []
by_kw = {}

for r in rows:
    line_no = int(r['line'])
    qs = r.get('queries','')
    text = get_case_text(line_no)
    dwx = day_wx(r['chart'])
    
    for kw, engine_qs, exclude in checks:
        if kw in text:
            idx = text.find(kw)
            context = text[max(0,idx-20):idx+len(kw)+20]
            if any(ex in context for ex in exclude):
                continue
            # 无根特殊处理：五行/天干/十神+无根，且不是日主
            if kw == '无根':
                cidx = context.find('无根')
                pre = context[:cidx] if cidx >= 0 else context[:20]
                stem_wx = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
                target = None
                for ch in reversed(pre[-8:]):
                    if ch in stem_wx:
                        target = stem_wx[ch]
                        break
                    if ch in '金木水火土':
                        target = ch
                        break
                if target and target != dwx:
                    continue
                # 十神字在前，排除（官星/财星/印星等无根）
                if any(s in pre[-10:] for s in ['官星','财星','印星','食伤','食神','伤官','七杀','官杀','财官','枭神','比劫','比肩','劫财','杀星','官杀']):
                    continue
            # 通根特殊处理：五行/天干/十神+通根，且不是日主
            if kw == '通根':
                cidx = context.find('通根')
                pre = context[:cidx] if cidx >= 0 else context[:20]
                stem_wx = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
                target = None
                for ch in reversed(pre[-8:]):
                    if ch in stem_wx:
                        target = stem_wx[ch]
                        break
                    if ch in '金木水火土':
                        target = ch
                        break
                if target and target != dwx:
                    continue
                if any(s in pre[-10:] for s in ['官星','财星','印星','食伤','食神','伤官','七杀','官杀','财官','枭神','比劫','比肩','劫财','杀星']):
                    continue
            total += 1
            by_kw[kw] = by_kw.get(kw, [0,0])
            by_kw[kw][1] += 1
            if any(eq in qs for eq in engine_qs):
                match += 1
                by_kw[kw][0] += 1
            else:
                mismatches.append((r['chart'], kw, engine_qs, qs[:80]))

print(f'总匹配: {match}/{total} = {match/total*100:.1f}%' if total>0 else '无对比样本')
print()
print('各关键词:')
for kw,(m,t) in sorted(by_kw.items(), key=lambda x:-x[1][1]):
    print(f'  {kw:6s}: {m}/{t} = {m/t*100:.0f}%')
print()
print(f'不匹配前20个:')
for m in mismatches[:20]:
    print(f'  {m[0]}: 原文"{m[1]}" 应有{m[2]} 实际{m[3][:50]}')
