# -*- coding: utf-8 -*-
# 抓取诗断秘诀卷上/下
import urllib.request, ssl, re, os, time
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0'}
OUT = r'D:\shuntian\data\heluo\guajie_raw'
CHAPTERS = {'诗断秘诀卷之上': '382323', '诗断秘诀卷之下': '382324'}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30, context=ctx).read().decode('utf-8', errors='replace')

def to_text(html):
    t = re.sub(r'<script.*?</script>', '', html, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<br\s*/?>', '\n', t)
    t = re.sub(r'</p>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('&nbsp;', ' ').replace('&amp;', '&')
    return '\n'.join(l.strip() for l in t.split('\n') if l.strip())

for name, pid in CHAPTERS.items():
    html = fetch(f'https://www.diancang.xyz/xuanxuewushu/21177/{pid}.html')
    txt = to_text(html)
    path = os.path.join(OUT, f'{name}.txt')
    open(path, 'w', encoding='utf-8').write(txt)
    print(name, len(txt), '字符 →', path)
    time.sleep(1)

# 验证大畜断诗
t = open(os.path.join(OUT, '诗断秘诀卷之上.txt'), encoding='utf-8').read()
print('大畜诗:', '✅' if '天衢一道' in t or '妇人携锦' in t or '龙牙虎爪' in t else '❌')
print('含"身亡":', t.count('身亡'), ' 含"数凶":', t.count('数凶'))
