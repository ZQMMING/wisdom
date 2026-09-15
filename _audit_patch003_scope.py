# -*- coding: utf-8 -*-
"""SIX_CLASSICS_SCOPE_MATRIX 生成：28 领域 × 六部 扫描
每格输出：命中数 / 章节TOP / 代表原文（ORIGINAL/A优先）/ evidence_status=AUDIT_DRAFT"""
import json, io, sys
from collections import OrderedDict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'
ENGINES = ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']
ENG_NAME = {'yhzp': 'L2A渊海子平', 'pzzq': 'L2B子平真诠', 'dts': 'L2C滴天髓',
            'qtbj': 'L2D穷通宝鉴', 'smth': 'L2E三命通会', 'sftk': 'L3神峰通考'}

DOMAINS = [
    ('01基础五行', ['五行', '生剋', '生克', '制化', '洩氣', '泄气']),
    ('02十神', ['正官', '七殺', '七杀', '偏官', '正財', '正财', '偏財', '偏财', '正印', '偏印', '梟神', '枭神', '食神', '傷官', '伤官', '比肩', '劫財', '劫财', '倒食']),
    ('03月令', ['月令', '提綱', '提纲', '司令', '當權', '当权']),
    ('04生旺休囚', ['生旺', '休囚', '死絕', '死绝', '長生', '长生', '沐浴', '冠帶', '冠带', '臨官', '临官', '帝旺', '墓庫', '墓库', '入墓']),
    ('05旺', ['身旺', '太旺', '旺相', '旺極', '旺极', '日主旺', '主旺', '旺之極']),
    ('06强', ['身強', '身强', '日主強', '日主强', '太強', '太强', '主強', '主强']),
    ('07根气', ['無根', '无根', '有根', '通根', '得根', '根氣', '根气', '歸祿', '归禄']),
    ('08得令', ['得令', '失令']),
    ('09得地', ['得地', '得垣', '歸垣', '归垣']),
    ('10得势', ['得勢', '得势', '失勢', '失势', '持勢', '持势']),
    ('11党众', ['成黨', '成党', '黨多', '党多', '黨眾', '党众', '一黨', '一党']),
    ('12生扶克泄耗', ['生扶', '扶身', '幫身', '帮身', '助身', '尅泄', '克泄', '洩耗', '泄耗', '耗氣', '耗气']),
    ('13气势', ['氣勢', '气势', '旺勢', '旺势', '勢旺', '势旺', '大勢', '大势']),
    ('14格局', ['格局', '成格', '破格', '入格', '格成', '格敗', '格败', '敗格', '败格']),
    ('15格局成败', ['成格', '敗格', '败格', '敗局', '败局', '救應', '救应', '成局', '破局', '格之成', '格之敗']),
    ('16用神', ['用神', '喜神', '忌神']),
    ('17相神', ['相神']),
    ('18顺逆', ['順用', '逆用', '順生', '顺生', '逆生', '順之', '逆之']),
    ('19清浊', ['清濁', '清浊', '濁氣', '浊气', '清氣', '清气', '清者', '濁者']),
    ('20真假', ['真假', '真神', '假神', '真化', '假化', '真從', '真从', '假從', '假从', '真者', '假者']),
    ('21调候', ['調候', '调候', '寒暖', '燥濕', '燥湿', '寒溫', '寒温', '暖燥']),
    ('22病药', ['病藥', '病药', '去病', '藥神', '药神', '有病', '病者', '藥者', '药者']),
    ('23通关', ['通關', '通关', '引通', '關通']),
    ('24从化专旺', ['從象', '从象', '化象', '專旺', '专旺', '炎上', '稼穡', '稼穑', '從革', '从革', '潤下', '润下', '曲直', '從兒', '从儿', '從財', '从财', '棄命', '弃命', '從殺', '从杀']),
    ('25干支组合', ['合局', '會局', '会局', '三合', '六合', '暗合', '刑沖', '刑冲', '沖破', '冲破', '相沖', '相冲', '地支', '天干']),
    ('26六亲', ['六親', '六亲', '父母', '夫妻', '妻妾', '子息', '兄弟', '尅父', '克父', '剋母', '克母', '尅妻', '克妻', '妨夫', '刑夫', '尅子', '克子', '喪父', '丧父']),
    ('27神煞', ['神煞', '貴人', '贵人', '羊刃', '桃花', '驛馬', '驿马', '華蓋', '华盖', '魁罡', '天德', '月德', '亡神', '空亡']),
    ('28命例验证', ['此命', '一命', '命例', '驗之', '验之', '余驗', '余验', '予驗', '予验', '屢驗', '屡验']),
]

# 预载
books = {}
for eng in ENGINES:
    lines = open(f'{ROOT}/sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    books[eng] = [json.loads(l) for l in lines if l.strip()]

# 命中分布矩阵
mat = {d[0]: {e: 0 for e in ENGINES} for d in DOMAINS}
for dname, keys in DOMAINS:
    for eng in ENGINES:
        for s in books[eng]:
            txt = s.get('source_text', '')
            if any(k in txt for k in keys):
                mat[dname][eng] += 1

# 输出矩阵
out = []
out.append('# SIX_CLASSICS_SCOPE_MATRIX（六部经典职责总表 · 初稿）\n')
out.append('> 日期：2026-09-16 ｜ evidence_status 全格 = **AUDIT_DRAFT**（待 Human 逐格审批，未达 VERIFIED）')
out.append('> 用途：Scope Map / 防漏清单，**不作任何业务规则**；28 领域不合并（旺/强/得令/得地/得势各自独立）\n')
out.append('| 领域 | L2A渊海 | L2B真诠 | L2C滴天 | L2D穷通 | L2E三命 | L3神峰 |')
out.append('|---|---|---|---|---|---|---|')
for dname, _ in DOMAINS:
    row = [str(mat[dname][e]) for e in ENGINES]
    out.append(f'| {dname} | ' + ' | '.join(row) + ' |')

out.append('\n---\n')
out.append('# 逐格证据（代表原文，ORIGINAL/A 优先；证据待逐格钉查）\n')
for dname, keys in DOMAINS:
    out.append(f'\n## 领域 {dname}\n')
    out.append('关键词：' + ' / '.join(keys) + '\n')
    for eng in ENGINES:
        hits = [s for s in books[eng] if any(k in s.get('source_text', '') for k in keys)]
        if not hits:
            continue
        chs = Counter(s.get('chapter', '?') for s in hits)
        top_ch = '、'.join(f'{c}×{n}' for c, n in chs.most_common(4))
        originals = [s for s in hits if s.get('text_layer') == 'ORIGINAL']
        out.append(f'- **{ENG_NAME[eng]}**：{len(hits)}条（章节TOP：{top_ch}）')
        for s in (originals or hits)[:2]:
            out.append(f'  - `{s["source_id"]}` [{s.get("text_layer")}/{s.get("evidence_grade")}] {s.get("chapter")}：{s.get("source_text", "")[:90]}')
        out.append('')

open(r'D:\shuntian-ziping-p0\docs\SIX_CLASSICS_SCOPE_MATRIX_2026-09-16.md', 'w', encoding='utf-8').write('\n'.join(out))
print('矩阵已生成 docs/SIX_CLASSICS_SCOPE_MATRIX_2026-09-16.md')
print('\n命中矩阵：')
print('领域\t' + '\t'.join(ENGINES))
for dname, _ in DOMAINS:
    print(dname + '\t' + '\t'.join(str(mat[dname][e]) for e in ENGINES))
