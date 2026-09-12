# -*- coding: utf-8 -*-
# 批量抓取中华典藏《河洛真数》易卦释义 5 章 → D:/shuntian/data/heluo/guajie_raw/
import urllib.request, ssl, re, os, time
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
OUT = r'D:\shuntian\data\heluo\guajie_raw'
os.makedirs(OUT, exist_ok=True)

CHAPTERS = {
    '上经卷之上': '382318',
    '上经卷之下': '382319',
    '下经卷之上': '382320',
    '下经卷之中': '382321',
    '下经卷之下': '382322',
}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30, context=ctx).read().decode('utf-8', errors='replace')

def to_text(html):
    t = re.sub(r'<script.*?</script>', '', html, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<br\s*/?>', '\n', t)
    t = re.sub(r'</p>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    lines = []
    for l in t.split('\n'):
        l = l.strip()
        if l:
            lines.append(l)
    return '\n'.join(lines)

total_lines = 0
for name, pid in CHAPTERS.items():
    url = f'https://www.diancang.xyz/xuanxuewushu/21177/{pid}.html'
    html = fetch(url)
    txt = to_text(html)
    path = os.path.join(OUT, f'易卦释义_{name}.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(txt)
    n = txt.count('\n') + 1
    total_lines += n
    print(f'{name}: {n} 行, {len(txt)} 字符 → {path}')
    time.sleep(1)

# 验证 64 卦覆盖
print('\n=== 64卦覆盖检查 ===')
import glob
GUA64 = ['乾','坤','屯','蒙','需','讼','师','比','小畜','履','泰','否','同人','大有','谦','豫','随','蛊','临','观','噬嗑','贲','剥','复','无妄','大畜','颐','大过','坎','离','咸','恒','遁','大壮','晋','明夷','家人','睽','蹇','解','损','益','夬','姤','萃','升','困','井','革','鼎','震','艮','渐','归妹','丰','旅','巽','兑','涣','节','中孚','小过','既济','未济']
all_txt = ''
for p in glob.glob(os.path.join(OUT, '*.txt')):
    all_txt += open(p, encoding='utf-8').read()
missing = []
for g in GUA64:
    # 卦名出现标志（章首标题如 "乾" 或 "乾为天"）
    if not re.search(g + r'[：:　]', all_txt) and not re.search(g + r'(为|卦)', all_txt):
        missing.append(g)
print('缺失:', missing if missing else '无，64卦全覆盖')
