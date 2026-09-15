# -*- coding: utf-8 -*-
"""PATCH-001 修正-3：enum_registry 74 条加 domain 字段 + dts_effect/support 补值 + v1.8.0"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\governance\enum_registry.json'
reg = json.load(open(P, encoding='utf-8'))

# domain 标注（PATCH §5 七类 + TECHNICAL）——逐条人工定稿
DOMAIN = {
    # 技术/分类（非状态机）
    'engine_status': 'TECHNICAL',
    'rule_match_state': 'TECHNICAL',
    'text_layer': 'TECHNICAL',
    'evidence_grade': 'TECHNICAL',
    'dts_qi_type': 'TECHNICAL',
    'operator': 'TECHNICAL',
    'rule_operator': 'TECHNICAL',
    'smth_combination_type': 'TECHNICAL',
    'sftk_disease_type': 'TECHNICAL',
    'sftk_medicine_type': 'TECHNICAL',
    # 存在性 EXISTENCE_STATE
    'dts_tian_status': 'EXISTENCE_STATE',
    'dts_di_status': 'EXISTENCE_STATE',
    'dts_stem_position': 'EXISTENCE_STATE',
    'dts_xing_state': 'EXISTENCE_STATE',
    'dts_guan': 'EXISTENCE_STATE',
    'dts_rigan_state': 'EXISTENCE_STATE',
    'dts_caixing': 'EXISTENCE_STATE',
    'dts_yongshen_state': 'EXISTENCE_STATE',
    'dts_jishen_location': 'EXISTENCE_STATE',
    'dts_keshen_location': 'EXISTENCE_STATE',
    # 条件/关系 CONDITION_STATE
    'dts_support_state': 'CONDITION_STATE',
    'dts_cong_support_state': 'CONDITION_STATE',
    'dts_climate': 'CONDITION_STATE',
    'dts_climate_type': 'CONDITION_STATE',
    'dts_hua_state': 'CONDITION_STATE',
    'dts_zhan_state': 'CONDITION_STATE',
    'dts_stimulus': 'CONDITION_STATE',
    'dts_gold_meets': 'CONDITION_STATE',
    'dts_wood_flow': 'CONDITION_STATE',
    'dts_cold_level': 'CONDITION_STATE',
    'dts_hot_level': 'CONDITION_STATE',
    'dts_dry_level': 'CONDITION_STATE',
    'dts_qing_state': 'CONDITION_STATE',
    'dts_qingqi_state': 'CONDITION_STATE',
    'dts_wuxing_state': 'CONDITION_STATE',
    'dts_rensha_state': 'CONDITION_STATE',
    'dts_caiguan': 'CONDITION_STATE',
    'dts_yangren_state': 'CONDITION_STATE',
    'dts_xueqi_state': 'CONDITION_STATE',
    'dts_pillar_relation': 'CONDITION_STATE',
    'dts_wood_state': 'CONDITION_STATE',
    'dts_earth_state': 'CONDITION_STATE',
    'dts_jinshui_state': 'CONDITION_STATE',
    'dts_shuitu_state': 'CONDITION_STATE',
    'dts_xing_ding_state': 'CONDITION_STATE',
    'smth_completeness': 'CONDITION_STATE',
    'smth_activation_status': 'CONDITION_STATE',
    'sftk_dongjing_state': 'CONDITION_STATE',
    'sftk_gaitou_state': 'CONDITION_STATE',
    # 强弱 STRENGTH_STATE
    'dts_strength_state': 'STRENGTH_STATE',
    'dts_day_strength_classic': 'STRENGTH_STATE',
    'dts_cai_guan_state': 'STRENGTH_STATE',
    'dts_fire_state': 'STRENGTH_STATE',
    'dts_wo_shi': 'STRENGTH_STATE',
    'dts_di': 'STRENGTH_STATE',
    'dts_day_master_strength': 'STRENGTH_STATE',
    'dts_branch_strength': 'STRENGTH_STATE',
    # 效力 EFFECT_STATE
    'dts_effect_state': 'EFFECT_STATE',
    # 角色/喜忌 ROLE_STATE
    'qtbj_requirement_type': 'ROLE_STATE',
    'dts_zhen_shen_state': 'ROLE_STATE',
    'dts_jia_shen_state': 'ROLE_STATE',
    'dts_jishen_state': 'ROLE_STATE',
    'dts_xiongwu_state': 'ROLE_STATE',
    'dts_decai_relation': 'ROLE_STATE',
    # 格局 PATTERN_STATE
    'pzzq_formation_state': 'PATTERN_STATE',
    'pzzq_destruction_state': 'PATTERN_STATE',
    'pzzq_rescue_state': 'PATTERN_STATE',
    'pzzq_structure_state': 'PATTERN_STATE',
    'dts_pattern': 'PATTERN_STATE',
    'dts_xiang_state': 'PATTERN_STATE',
    'dts_geju': 'PATTERN_STATE',
    'dts_zhige_state': 'PATTERN_STATE',
    # 成败结果 RESULT_STATE
    'pzzq_chengbai_state': 'RESULT_STATE',
    'dts_special_state': 'RESULT_STATE',
}

# 校验覆盖
missing = [e['enum_id'] for e in reg['enums'] if e['enum_id'] not in DOMAIN]
assert not missing, '未标注 domain: %s' % missing

for e in reg['enums']:
    eid = e['enum_id']
    e['domain'] = DOMAIN[eid]
    # 修正-1/2：补值
    if eid == 'dts_effect_state':
        e['values'] = ['effective', 'partially_effective', 'ineffective', 'blocked',
                       'conditional', 'undetermined']
        e['description'] = ('附录 L-3 + PATCH-001 §8：效力状态。'
                            'CONDITIONAL=效力成立但有条件依赖（如伤官配印需身弱方有效）；'
                            'UNDETERMINED=证据/规则不足以确定效力。')
    if eid == 'dts_support_state':
        e['values'] = ['NONE', 'WEAK', 'NORMAL', 'STRONG', 'EXCESSIVE', 'UNDETERMINED']
        e['description'] = ('附录 L-3 + PATCH-001 §7：生扶/支持强度。'
                            'EXCESSIVE=生扶过旺（生多为克，母慈灭子类）；'
                            'UNDETERMINED=无法确定。'
                            '从格专用 dts_cong_support_state（有无生扶）不并入本强度枚举（F-3 裁决）。')

reg['version'] = 'v1.8.0'
reg.setdefault('changelog', []).append({
    'version': 'v1.8.0',
    'date': '2026-09-16',
    'reason': 'V2.22-PATCH-001 §5/§7/§8/§16：74 条枚举补 domain 状态域标注；'
              'dts_effect_state +CONDITIONAL/UNDETERMINED；'
              'dts_support_state +EXCESSIVE/UNDETERMINED',
})

json.dump(reg, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅ v1.8.0 写入完成')
print('枚举数:', len(reg['enums']))

# 验证
reg2 = json.load(open(P, encoding='utf-8'))
from collections import Counter
dom = Counter(e['domain'] for e in reg2['enums'])
print('domain 分布:', dict(dom))
for eid in ('dts_effect_state', 'dts_support_state'):
    e = next(e for e in reg2['enums'] if e['enum_id'] == eid)
    print(eid, e['values'])
