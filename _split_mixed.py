# -*- coding: utf-8 -*-
"""D-4 Mixed Source 拆条：9 条混排 → 68 个语义单元
每个单元独立 source_id（原ID-NN）/ text_layer / evidence_grade /
annotation_type / attribution；QUOTED_SOURCE 带 origin 追溯字段。"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\registries\source\sources.sftk.jsonl'
lines = open(P, encoding='utf-8').read().splitlines()
src = {}
for l in lines:
    if l.strip():
        s = json.loads(l)
        src[s['source_id']] = s

def split_record(sid, anchors):
    """anchors: [(start_marker, layer, grade, ann_type, attribution, origin), ...]"""
    s = src[sid]
    text = s['source_text']
    units = []
    for i, (mark, layer, grade, ann_type, attribution, origin) in enumerate(anchors):
        pos = text.find(mark)
        if pos < 0:
            print(f'!! 锚点未找到 {sid}: {mark[:15]}')
            continue
        end = text.find(anchors[i + 1][0]) if i + 1 < len(anchors) else len(text)
        seg = text[pos:end].strip()
        units.append({
            'source_id': f'{sid}-{i + 1:02d}',
            'engine': s['engine'],
            'book': s['book'],
            'chapter': s['chapter'],
            'text_id': f"SFTK-T-{sid.split('-')[1]}-{sid.split('-')[2]}-{i + 1:02d}",
            'text_layer': layer,
            'source_text': seg,
            'resource_id': s['resource_id'],
            'logical_uri': f"source://sftk/{sid.split('-')[1]}/{sid.split('-')[2]}-{i + 1:02d}",
            'relative_path': s['relative_path'],
            'version': '1.1.0',
            'status': 'CANDIDATE' if layer != 'UNVERIFIED' else 'NEEDS_REVIEW',
            'evidence_grade': grade,
        })
        if layer == 'ANNOTATION':
            units[-1]['annotation_type'] = ann_type
            units[-1]['attribution'] = attribution
        if layer == 'QUOTED_SOURCE':
            units[-1]['quoted_origin'] = origin
            units[-1]['origin_source_id'] = None
            units[-1]['origin_verification'] = 'PENDING'
        if layer == 'UNVERIFIED':
            units[-1]['notes'] = '转录页码标记或断句残片，非古籍正文'
    return units

# 定义 9 条拆法
PLAN = {
'SFTK-018-012': [
    ('古歌云絕處逢生', 'QUOTED_SOURCE', 'D', None, None, '古歌（待核）'),
    ('又歌云或云胎養', 'QUOTED_SOURCE', 'D', None, None, '古歌（待核）'),
    ('古歌云偏官如虎', 'QUOTED_SOURCE', 'D', None, None, '古歌（待核）'),
    ('補曰月上偏官', 'ANNOTATION', 'B', 'SUPPLEMENT', 'ZHANG_NAN', None),
    ('又歌曰偏官不可例言凶', 'QUOTED_SOURCE', 'D', None, None, '歌曰（待核）'),
    ('解曰偏官即尅我之神', 'ANNOTATION', 'B', 'EXPLANATION', 'UNKNOWN', None),
    ('又歌曰偏官有制化爲權', 'QUOTED_SOURCE', 'D', None, None, '歌曰（待核）'),
    ('解曰偏官之格', 'ANNOTATION', 'B', 'EXPLANATION', 'UNKNOWN', None),
],
'SFTK-043-003': [
    ('宜殺旺之地輕重不同斟酌在人也', 'ORIGINAL', 'A', None, None, None),
    ('補曰先以歲德扶殺言之', 'ANNOTATION', 'B', 'SUPPLEMENT', 'ZHANG_NAN', None),
    ('淵海註曰且如甲日見庚年', 'QUOTED_SOURCE', 'D', None, None, '《淵海子平》註（待核）'),
    ('纂要歌曰年上偏官為歲殺', 'QUOTED_SOURCE', 'D', None, None, '《纂要》（待核）'),
    ('古歌曰歲德主來見戊年', 'QUOTED_SOURCE', 'D', None, None, '古歌（待核）'),
    ('問扶殺格格解所收詩歌', 'ORIGINAL', 'A', None, None, None),
    ('又補歲德扶財格', 'ANNOTATION', 'B', 'SUPPLEMENT', 'ZHANG_NAN', None),
    ('淵海註曰且如甲人見戊己年', 'QUOTED_SOURCE', 'D', None, None, '《淵海子平》註（待核）'),
    ('專財格', 'ORIGINAL', 'A', None, None, None),
    ('纂要云如甲日見己巳時', 'QUOTED_SOURCE', 'D', None, None, '《纂要》（待核）'),
    ('歌曰日時秀氣最難尋', 'QUOTED_SOURCE', 'D', None, None, '《纂要》所引歌（待核）'),
    ('此即時馬格異而理同', 'ORIGINAL', 'A', None, None, None),
],
'SFTK-062-038': [
    ('申宮詩曰申金剛健', 'QUOTED_SOURCE', 'D', None, None, '《十天干體象全編》（待核）'),
    ('酉宮詩曰八月從魁', 'QUOTED_SOURCE', 'D', None, None, '《十天干體象全編》（待核）'),
    ('戌宮詩曰九月從魁', 'QUOTED_SOURCE', 'D', None, None, '《十天干體象全編》（待核）'),
    ('亥宮詩曰登明之位', 'QUOTED_SOURCE', 'D', None, None, '《十天干體象全編》（待核）'),
    ('總咏五行用法總無真', 'QUOTED_SOURCE', 'D', None, None, '《十天干體象全編》總咏（待核）'),
    ('干支所屬', 'UNVERIFIED', 'D', None, None, None),
],
'SFTK-124-025': [
    ('又韻逢煞切宜看印', 'ORIGINAL', 'A', None, None, None),
    ('歌釋癸日提逢癸丑', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('歌釋財神二三疊見', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('歌釋癸日生居巳位', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('歌釋壬生臨午位', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('歌釋甲生庚金秋旺', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
],
'SFTK-124-064': [
    ('身强殺淺化煞為權', 'ORIGINAL', 'A', None, None, None),
    ('歌釋化煞為權何以取', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
],
'SFTK-124-095': [
    ('甲逢己而生旺定懷中正之心', 'ORIGINAL', 'A', None, None, None),
    ('歇釋甲逢己土合甲旺', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
],
'SFTK-124-107': [
    ('木向春生處世安然必壽', 'ORIGINAL', 'A', None, None, None),
    ('歌釋甲乙生於春月', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('金弱遇火炎之地血疾無宜', 'ORIGINAL', 'A', None, None, None),
    ('歌釋庚日生居火地', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('土虛逢木旺之鄉脾傷論定', 'ORIGINAL', 'A', None, None, None),
    ('歌釋甲子年提丁卯', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('甲子 丁卯 己丑 乙亥 簡子之命', 'ORIGINAL', 'A', None, None, None),
    ('金遇艮而遇土號曰返魂', 'ORIGINAL', 'A', None, None, None),
    ('歌釋庚金生寅遇火', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('水入巽而見金名為不絕', 'ORIGINAL', 'A', None, None, None),
    ('歌釋壬癸生居巳地', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('壬水受氣於巳水得母而長生而能生', 'ORIGINAL', 'A', None, None, None),
    ('神峰通考 卷五 一五', 'UNVERIFIED', 'D', None, None, None),
],
'SFTK-125-029': [
    ('詩釋偏正財多禍必多', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('財逢有傷還忌陰謀之賊', 'ORIGINAL', 'A', None, None, None),
    ('詩釋財無刼奪則無傷', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('殺無陰制當尋伏敵之兵', 'ORIGINAL', 'A', None, None, None),
    ('詩釋併多七殺正刑明制', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('貴人頭上戴財官門充驅馬', 'ORIGINAL', 'A', None, None, None),
    ('詩釋貴人互換得相成', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('生旺宮中藏刼殺勇奪三軍', 'ORIGINAL', 'A', None, None, None),
    ('詩釋長生刼煞本非奇', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('為跨馬以亡身', 'ORIGINAL', 'A', None, None, None),
    ('詩釋歲運逢財日主貪', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('因得祿而避位', 'ORIGINAL', 'A', None, None, None),
    ('詩釋官星失馬不為官', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('印解兩賢之厄', 'ORIGINAL', 'A', None, None, None),
    ('詩釋兩殺重來威制重', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
    ('神峰通考 卷五 二九', 'UNVERIFIED', 'D', None, None, None),
],
'SFTK-125-057': [
    ('入庫傷官陰生陽死', 'ORIGINAL', 'A', None, None, None),
    ('詩釋五陽歸庫無生氣', 'ANNOTATION', 'B', 'SONG_EXPLANATION', 'SFTK_TRADITION', None),
],
}

# 执行拆条
new_records = []
for sid, anchors in PLAN.items():
    units = split_record(sid, anchors)
    new_records.extend(units)
    print(f'{sid}: 拆成 {len(units)} 单元')

# 重写 jsonl：移除 9 条原记录，插入新单元（保持章节顺序：在原位置插入）
new_lines = []
for l in lines:
    if not l.strip():
        continue
    s = json.loads(l)
    if s['source_id'] in PLAN:
        # 原位置插入该条的拆条单元
        for u in [x for x in new_records if x['source_id'].startswith(s['source_id'] + '-')]:
            new_lines.append(json.dumps(u, ensure_ascii=False))
        continue
    new_lines.append(l)

open(P, 'w', encoding='utf-8').write('\n'.join(new_lines) + '\n')
print(f'重写完成。总行数: {len(new_lines)}（原 {len(lines)}，其中删 9 条混排）')

# 校验
ids = [json.loads(x)['source_id'] for x in new_lines if x.strip()]
dup = {i for i in ids if ids.count(i) > 1}
print(f'source_id 唯一性: {"OK" if not dup else "DUPLICATE: " + str(dup)}')
layers = {}
for x in new_lines:
    if x.strip():
        s = json.loads(x)
        layers[s.get('text_layer')] = layers.get(s.get('text_layer'), 0) + 1
print('text_layer 分布:', layers)
