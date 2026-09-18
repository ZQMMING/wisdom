# -*- coding: utf-8 -*-
import re, sys, csv
sys.path.insert(0, '.')
DTS = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(DTS, encoding='utf-8').read().splitlines()
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))
GZ = r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]'
BZ_RE = re.compile(rf'^{GZ}\s+{GZ}\s+{GZ}\s+{GZ}\s*$')


def case_text(ln):
    e = ln + 1
    while e < len(lines):
        l = lines[e].strip()
        if l.startswith('八字：') or l.startswith('====') or l.startswith('【') or BZ_RE.match(l): break
        e += 1
    return re.sub(r'\s+', '', ''.join(lines[ln + 1:e]))


KW = re.compile(r'(身旺|身弱|身强|身衰|日主旺|日主弱|日元|旺|弱|衰|埋|漂|浊|枯|塞|通明|夭|贵|科甲|富贵|贫|贱|吉|凶|从|格|用|喜|忌|生扶|受生|不受|克|泄|太过|不及)')
mm = [r for r in rows if (r.get('mu_mie') or '').strip()]
print('母灭候选', len(mm), '例\n')
for r in mm:
    ch = r['chart']
    ln = lines and None
    for i, l in enumerate(lines):
        if BZ_RE.match(l.strip()) and ''.join(l.split()) == ch:
            ln = i; break
    t = case_text(ln) if ln is not None else ''
    # 去掉大运序列(开头连续干支)
    t2 = re.sub(r'^([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]){2,}', '', t)
    print('══', ch, '七档', r['spectrum'], 'ratio', r['ratio'], '气候', r.get('climate', ''))
    print(t2[:240])
    print()
