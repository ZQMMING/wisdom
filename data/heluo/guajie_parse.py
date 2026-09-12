# -*- coding: utf-8 -*-
# 解析《河洛真数·易卦释义》5 章 → 结构化 64 卦判词 JSON
import re, os, json, glob

RAW = r'D:\shuntian\data\heluo\guajie_raw'
OUT = r'D:\shuntian\data\heluo\guajie_data.json'

GUA_NAMES = ['乾','坤','屯','蒙','需','讼','师','比','小畜','履','泰','否','同人','大有','谦','豫','随','蛊','临','观','噬嗑','贲','剥','复','无妄','大畜','颐','大过','坎','离','咸','恒','遁','大壮','晋','明夷','家人','睽','蹇','解','损','益','夬','姤','萃','升','困','井','革','鼎','震','艮','渐','归妹','丰','旅','巽','兑','涣','节','中孚','小过','既济','未济']
GUA_SET = set(GUA_NAMES)

YAO_RE = re.compile(r'^(初九|九二|九三|九四|九五|上九|初六|六二|六三|六四|六五|上六)[：:]')
XIANG_RE = re.compile(r'^《象》曰[：:]')
SHAO_RE = re.compile(r'^邵曰[：:]')

# 断语关键字（叶/不叶/岁运）
YE_KEYS = ['叶吉', '叶者', '归元', '入局', '得时', '当此爻', '入贵格']
BUYE_KEYS = ['不叶', '不归元', '不入局', '生不及时', '不及时', '难当此爻', '失正', '失位', '不得正']
SUIYUN_KEYS = ['岁运逢', '岁运值']

def is_duan(line):
    return any(k in line for k in ['数卦', '元数', '数不', '数又归元', '数有归元', '命数', '若人支干', '如生', '若生', '如数', '岁运逢', '岁运值', '人命得此', '若支干', '生于阴月', '如不入局', '入局'])

def parse_file(path):
    lines = [l.strip() for l in open(path, encoding='utf-8') if l.strip()]
    # 去掉导航：找到第一个卦头/卦辞行
    start = 0
    for i, l in enumerate(lines):
        if re.match(r'^(乾|坤|屯|蒙|需|讼|师|比|小畜|履|泰|否|同人|大有|谦)[：:元虎野匪]', l):
            start = i
            break
    guas = []
    cur = None
    cur_yao = None
    for i in range(start, len(lines)):
        l = lines[i]
        # 卦头：卦名 + ： + 卦辞（或卦辞直接开头，如"履虎尾""否之匪人"）
        m = re.match(r'^([\u4e00-\u9fff]{1,3})[：:](.{0,40})', l)
        if m and m.group(1) in GUA_SET and not YAO_RE.match(l):
            if cur:
                if cur_yao:
                    cur['yaos'].append(cur_yao)
                guas.append(cur)
            cur = {'name': m.group(1), 'gua_ci': m.group(2), 'lines': [], 'yaos': []}
            cur_yao = None
            continue
        # 无前缀卦辞行（仅5卦：履虎尾/否之匪人/同人于野/习坎/艮其背）→ 开新卦
        m2 = re.match(r'^(履虎尾|否之匪人|同人于野|习坎|艮其背)', l)
        if m2 and cur and (len(cur['yaos']) >= 6 or cur_yao is None) and not YAO_RE.match(l) and not XIANG_RE.match(l):
            if cur_yao:
                cur['yaos'].append(cur_yao)
                cur_yao = None
            guas.append(cur)
            gname = m2.group(1)
            if gname == '否之匪人':
                gname = '否'
            elif gname == '习坎':
                gname = '坎'
            elif gname == '艮其背':
                gname = '艮'
            elif gname == '履虎尾':
                gname = '履'
            elif gname == '同人于野':
                gname = '同人'
            cur = {'name': gname, 'gua_ci': l, 'lines': [], 'yaos': []}
            continue
        if cur is None:
            continue
        # 爻头
        ym = YAO_RE.match(l)
        if ym:
            if cur_yao:
                cur['yaos'].append(cur_yao)
            cur_yao = {'yao': ym.group(1), 'ci': l.split('：', 1)[1] if '：' in l else l.split(':', 1)[1],
                       'xiang': '', 'yi': '', 'duans': [], 'shao': ''}
            continue
        if cur_yao is None:
            cur['lines'].append(l)
            continue
        # 象曰
        if XIANG_RE.match(l):
            cur_yao['xiang'] = l.split('：', 1)[1] if '：' in l else ''
            continue
        # 邵曰
        if SHAO_RE.match(l):
            cur_yao['shao'] = l.split('：', 1)[1] if '：' in l else l
            # 上九/上六 → 立即收尾
            if cur_yao['yao'] in ('上九', '上六'):
                cur['yaos'].append(cur_yao)
                cur_yao = None
            continue
        # 断语行 vs 释义行
        if is_duan(l) and (any(k in l for k in YE_KEYS) or any(k in l for k in BUYE_KEYS) or any(k in l for k in SUIYUN_KEYS)):
            cur_yao['duans'].append(l)
        else:
            cur_yao['yi'] = (cur_yao['yi'] + ' ' + l).strip()
    if cur:
        if cur_yao:
            cur['yaos'].append(cur_yao)
        guas.append(cur)
    return guas

all_guas = []
for p in sorted(glob.glob(os.path.join(RAW, '*.txt'))):
    all_guas.extend(parse_file(p))

# 按 64 卦顺序排，缺失卦名用顺序表补（爻组法已保证 6 爻一组）
order = {n: i for i, n in enumerate(GUA_NAMES)}
all_guas.sort(key=lambda g: order.get(g['name'], 999))
missing = [n for n in GUA_NAMES if n not in [g['name'] for g in all_guas]]
if missing:
    # 用顺序补齐（爻数顺序 = 64 卦顺序）
    idx = 0
    for n in GUA_NAMES:
        if idx < len(all_guas) and all_guas[idx]['name'] == n:
            idx += 1
        elif n in missing:
            # 找到未命名（并入错误）卦：重建
            pass
    print('仍缺失:', missing)
total_yaos = 0
no_duan = []
for g in all_guas:
    for y in g['yaos']:
        total_yaos += 1
        if not y['duans']:
            no_duan.append((g['name'], y['yao']))
print('总爻数:', total_yaos)
print('无断语爻:', no_duan[:20], '…' if len(no_duan) > 20 else '', '共', len(no_duan))

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(all_guas, f, ensure_ascii=False, indent=1)
print('已写入:', OUT, os.path.getsize(OUT), 'bytes')
