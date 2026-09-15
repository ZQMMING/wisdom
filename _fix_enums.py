# -*- coding: utf-8 -*-
"""枚举三态/多态化修正：enum_registry.json"""
import json, io, sys, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = r'D:\shuntian-ziping-p0\governance\enum_registry.json'
reg = json.load(open(path, encoding='utf-8'))
enums = reg['enums']
by_id = {e['enum_id']: e for e in enums}

# A. 单值枚举 → 补反态 + UNDETERMINED
single_fix = {
    'dts_tian_status':   (['全一氣'], ['全一氣', '非全一氣', 'UNDETERMINED'], 'DTS-010-004 天全一氣；反例=非全一氣'),
    'dts_di_status':     (['全三物'], ['全三物', '非全三物', 'UNDETERMINED'], 'DTS-010-006/007 地全三物；反例=非全三物'),
    'dts_xing_state':    (['形全'], ['形全', '形缺', 'UNDETERMINED'], 'DTS-011-003/008 形全者宜損其有餘，形缺者宜補其不足'),
    'dts_xiang_state':   (['子衆母衰'], ['君亢', '臣過', '母旺子孤', '子衆母衰', 'UNDETERMINED'], 'DTS-048/049/050/051 君臣母子四象'),
    'dts_fire_state':    (['烈'], ['烈', '不烈', 'UNDETERMINED'], 'DTS-027-001 火烈'),
    'dts_stimulus':      (['金水之激'], ['金水之激', '非激', 'UNDETERMINED'], 'DTS-031 金水之激'),
    'dts_gold_meets':    (['水'], ['水', '非水', 'UNDETERMINED'], 'DTS-035 金遇水'),
    'dts_wood_flow':     (['奔南'], ['奔南', '不奔南', 'UNDETERMINED'], 'DTS-032 木奔南'),
    'dts_dry_level':     (['DRY_WITH_MOIST'], ['DRY_WITH_MOIST', 'DRY_NO_MOIST', 'UNDETERMINED'], '寒溫濕燥論；地道有濕燥'),
}

# B. 二态枚举 → 补 UNKNOWN/UNDETERMINED（保留古典二值）
two_fix = {
    'smth_completeness':        ['complete', 'incomplete', 'UNKNOWN'],
    'dts_cai_guan_state':       ['NOT_STRONG', 'STRONG', 'UNKNOWN'],
    'dts_hua_state':            ['真', '假', '未化', 'UNDETERMINED'],
    'dts_stem_position':        ['陽乘陽位', '陰乘陰位', 'UNDETERMINED'],
    'dts_zhan_state':           ['天戰', '地戰', '無戰', 'UNDETERMINED'],
    'dts_cold_level':           ['COLD_WITH_WARM', 'COLD_NO_WARM', 'UNDETERMINED'],
    'dts_hot_level':            ['HOT_WITH_COOL', 'HOT_NO_COOL', 'UNDETERMINED'],
    'dts_qingqi_state':         ['有清氣', '無清氣', 'UNDETERMINED'],
    'dts_guan':                 ['露', '不露', 'UNDETERMINED'],
    'dts_zhen_shen_state':      ['得用', '不得用', 'UNDETERMINED'],
    'dts_jia_shen_state':       ['用假', '不用假', 'UNDETERMINED'],
    'dts_jishen_state':         ['太露', '深藏', 'UNDETERMINED'],
    'dts_xiongwu_state':        ['深藏', '顯現', 'UNDETERMINED'],
    'dts_wo_shi':               ['強衆', '強寡', 'UNDETERMINED'],
    'dts_di':                   ['敵寡', '敵衆', 'UNDETERMINED'],
    'dts_decai_relation':       ['德勝才', '才勝德', 'UNDETERMINED'],
    'dts_wuxing_state':         ['不戾正清和', '濁亂偏枯', 'UNDETERMINED'],
    'dts_rigan_state':          ['得氣', '無氣', 'UNDETERMINED'],
    'dts_caixing':              ['遇', '不遇', 'UNDETERMINED'],
    'dts_rensha_state':         ['神清氣勢恢', '不恢', 'UNDETERMINED'],
    'dts_caiguan':              ['和', '不和', 'UNDETERMINED'],
    'dts_geju':                 ['清純', '混濁', 'UNDETERMINED'],
    'dts_yangren_state':        ['戰', '弱', 'UNDETERMINED'],
    'dts_yongshen_state':       ['多', '不多', 'UNDETERMINED'],
    'dts_zhige_state':          ['濁', '清', 'UNDETERMINED'],
    'dts_xueqi_state':          ['亂', '和', 'UNDETERMINED'],
    'dts_jishen_location':      ['入五臟', '不入', 'UNDETERMINED'],
    'dts_keshen_location':      ['遊六經', '不遊', 'UNDETERMINED'],
    'dts_pillar_relation':      ['地生天', '天合地', 'UNDETERMINED'],
    'dts_branch_strength':      ['旺', '不旺', 'UNDETERMINED'],
    'dts_wood_state':           ['不受水', '受水', 'UNDETERMINED'],
    'dts_earth_state':          ['不受火', '受火', 'UNDETERMINED'],
    'dts_jinshui_state':        ['枯傷', '不枯', 'UNDETERMINED'],
    'dts_shuitu_state':         ['相勝', '不相勝', 'UNDETERMINED'],
}

# C. 弃用 dts_day_master_strength（与附录L-3 strength_state 冲突）
# D. 删除 dts_shangguan_ge_state（复用 qing_state）
# E. xing_state 语义拆分：寿段「定」→ 新建 xing_ding_state；xing_state 保留形全形缺

removed = []
renamed = []

new_enums = []
for e in enums:
    eid = e['enum_id']
    if eid == 'dts_shangguan_ge_state':
        removed.append(eid)
        continue  # 删除，复用 qing_state
    if eid == 'dts_day_master_strength':
        e['status'] = 'DEPRECATED'
        e['values'] = ['衰', '旺', 'UNDETERMINED']
        e['description'] = (e.get('description','') + '；2026-09-16 DEPRECATED：与附录L-3 strength_state 六级冲突，改用 strength_state；古典层用 day_strength_classic（WANG/SHUAI/JUN_HENG）')
        new_enums.append(e)
        continue
    if eid in single_fix:
        old, new, note = single_fix[eid]
        e['values'] = new
        e['description'] = (e.get('description','') + '；2026-09-16 三态化：' + note)
        e['status'] = e.get('status', 'PENDING')
        new_enums.append(e)
        continue
    if eid in two_fix:
        e['values'] = two_fix[eid]
        e['description'] = (e.get('description','') + '；2026-09-16 三态化：补 UNKNOWN/UNDETERMINED 兜底值（V2.22 附录L 值域治理铁律）')
        e['status'] = e.get('status', 'PENDING')
        new_enums.append(e)
        continue
    # xing_state 拆分：新增 xing_ding_state
    if eid == 'dts_xing_state':
        new_enums.append(e)  # xing_state 保留（形全/形缺/UNDETERMINED，已在 single_fix 处理）
        continue
    new_enums.append(e)

# 新增 xing_ding_state（寿段「定」）
xing_ding = {
    "enum_id": "dts_xing_ding_state",
    "engine_scope": ["DI_TIAN_SUI"],
    "values": ["定", "不定", "UNDETERMINED"],
    "description": "2026-09-16 新建（三态化拆分）：《滴天髓》何知章寿段「柱中無沖無合，無缺無貪，則定性矣」——xing_state 原被「定」（寿段）与「形全/形缺」（形全形缺篇）两语义共用，拆分后 xing_ding_state 承载「性定」语义",
    "source_rule_required": True,
    "status": "PENDING"
}
new_enums.append(xing_ding)

reg['enums'] = new_enums
reg['version'] = 'v1.7.0'
reg.setdefault('changelog', []).append('2026-09-16 v1.7.0 枚举三态/多态化修正：45 条问题枚举（36 二态+9 单值）补 UNKNOWN/UNDETERMINED 兜底；删除 shangguan_ge_state（复用 qing_state）；dts_day_master_strength DEPRECATED（对齐附录L-3 strength_state）；新增 xing_ding_state（拆分 xing_state 语义污染）')

json.dump(reg, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 验证
reg2 = json.load(open(path, encoding='utf-8'))
e2 = reg2['enums']
single = [e for e in e2 if e.get('values') and len(e['values'])==1]
two_no_unknown = [e for e in e2 if e.get('values') and len(e['values'])==2]
print('修正后总枚举:', len(e2))
print('剩余单值:', len(single), [e['enum_id'] for e in single])
print('剩余二态无兜底:', len(two_no_unknown), [e['enum_id'] for e in two_no_unknown])
print('删除:', removed)
print('新增:', 'dts_xing_ding_state')
print('version:', reg2['version'])
