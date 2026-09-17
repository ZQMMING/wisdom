# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, '.')
from engines.common.daymaster_activity import (
    build_activity_tou_cang, build_activity_clash_class, classify_clash_branch,
    ACTIVE_CANDIDATE, DORMANT, ABSENT_STATE,
    SHENGFANG_CLASH, KU_CLASH, BAI_CLASH)

fails = 0


def check(name, cond, extra=''):
    global fails
    if not cond:
        fails += 1
    print(('PASS' if cond else 'FAIL'), name, extra)


# ===== 模块① 透藏动静 =====
def tc_group(state, tou, cang):
    return {'state': state, 'tou': tou, 'cang': cang,
            'stem_pillars': [], 'hidden_pillars': []}


tc = {'groups': {
    'BIJIE': tc_group('TOU_CANG_BOTH', True, True),
    'YIN': tc_group('TOU_ONLY', True, False),
    'SHISHANG': tc_group('CANG_ONLY', False, True),
    'CAI': tc_group('ABSENT', False, False),
    'GUANSHA': tc_group('CANG_ONLY', False, True),
}}
a1 = build_activity_tou_cang(tc)
g = a1['groups']
check('透藏俱备->ACTIVE_CANDIDATE', g['BIJIE']['activity_state'] == ACTIVE_CANDIDATE)
check('只透->ACTIVE_CANDIDATE', g['YIN']['activity_state'] == ACTIVE_CANDIDATE)
check('只藏->DORMANT', g['SHISHANG']['activity_state'] == DORMANT)
check('不现->ABSENT', g['CAI']['activity_state'] == ABSENT_STATE)
check('官杀藏->DORMANT', g['GUANSHA']['activity_state'] == DORMANT)

# 边界: 判定字段无有力/无用/吉/凶/STRONG/WEAK
blob1 = json.dumps(g, ensure_ascii=False)
for bad in ['有力', '无力', '无用', '吉', '凶', 'STRONG', 'WEAK', 'score']:
    ok = bad not in blob1
    if not ok:
        fails += 1
    check('动静判定字段禁用词:' + bad, ok)

# ===== 模块② 冲支三类 =====
# 六冲: 寅申/巳亥(生方) 辰戌/丑未(库) 子午/卯酉(败)
check('寅=生方冲', classify_clash_branch('寅') == SHENGFANG_CLASH)
check('申=生方冲', classify_clash_branch('申') == SHENGFANG_CLASH)
check('巳=生方冲', classify_clash_branch('巳') == SHENGFANG_CLASH)
check('亥=生方冲', classify_clash_branch('亥') == SHENGFANG_CLASH)
check('辰=库冲', classify_clash_branch('辰') == KU_CLASH)
check('戌=库冲', classify_clash_branch('戌') == KU_CLASH)
check('丑=库冲', classify_clash_branch('丑') == KU_CLASH)
check('未=库冲', classify_clash_branch('未') == KU_CLASH)
check('子=败冲UNKNOWN', classify_clash_branch('子') == BAI_CLASH)
check('午=败冲UNKNOWN', classify_clash_branch('午') == BAI_CLASH)
check('卯=败冲UNKNOWN', classify_clash_branch('卯') == BAI_CLASH)
check('酉=败冲UNKNOWN', classify_clash_branch('酉') == BAI_CLASH)

# mock D8 输出: 月根寅逢申冲(生方), 日根辰逢戌冲(库), 时根子逢午冲(败)
rr = {'root_branch_relations': {
    'month': {'branch': '寅', 'is_root': True, 'relations': [
        {'relation': 'CLASH', 'with_branches': ['申']}]},
    'day': {'branch': '辰', 'is_root': True, 'relations': [
        {'relation': 'CLASH', 'with_branches': ['戌']}]},
    'hour': {'branch': '子', 'is_root': True, 'relations': [
        {'relation': 'CLASH', 'with_branches': ['午']}]},
    'year': {'branch': '午', 'is_root': False, 'relations': [
        {'relation': 'CLASH', 'with_branches': ['子']}]},
}}
a2 = build_activity_clash_class(rr)
p = a2['root_clash_pillars']
check('月寅生方冲', p['month']['clash_class'] == SHENGFANG_CLASH and p['month']['with_branches'] == ['申'])
check('日辰库冲', p['day']['clash_class'] == KU_CLASH)
check('时子败冲UNKNOWN', p['hour']['clash_class'] == BAI_CLASH)
check('非根支不标注', 'year' not in p)

# 合/刑关系不产生 clash 标注
rr2 = {'root_branch_relations': {
    'month': {'branch': '寅', 'is_root': True, 'relations': [
        {'relation': 'TRIPLE_COMBINE', 'with_branches': ['午', '戌']}]}}}
check('合局不产生冲类', build_activity_clash_class(rr2)['root_clash_pillars'] == {})

# 边界: 判定字段无根拔/伤/发/吉/凶/STRONG/WEAK
blob2 = json.dumps(p, ensure_ascii=False)
for bad in ['根拔', '伤根', '旺者发', '衰者拔', '吉', '凶', 'STRONG', 'WEAK']:
    ok = bad not in blob2
    if not ok:
        fails += 1
    check('冲类判定字段禁用词:' + bad, ok)



# ===== 模块③ 合去归属(真实 L0 build) =====
from engines.common.l0_fact_builder import build as _build
from engines.common.daymaster_activity import build_activity_combine_away, DAYMASTER_BOUND_COMBINE, COMBINE_AWAY, CONTROL_NEGOTIATED

def _comb(p):
    return build_activity_combine_away(_build(p))['adjacent_combines']

# 年己月甲 甲日主: 年月相邻, 己财被甲比肩合走, 日主非合方
c1 = _comb({'year':'己丑','month':'甲子','day':'甲寅','hour':'丙寅'})
k1 = [x for x in c1 if x['pillars']==['year','month']][0]
check('年己月甲=合去候选', k1['kind']==COMBINE_AWAY and '正财' in k1['combined_ten_gods'])
check('财被合非克神', k1['control_negotiated'] is False)

# 年丁月壬 丙日主: 壬七杀被丁合, 贪合忘克前提
c2 = _comb({'year':'丁酉','month':'壬辰','day':'丙寅','hour':'甲午'})
k2 = c2[0]
check('七杀被合=贪合忘克候选', k2['control_negotiated'] is True and k2['control_kind']==CONTROL_NEGOTIATED)

# 月己日甲 甲日主: 月日相邻日主被合(同时年月也有比肩合财)
c3 = _comb({'year':'甲子','month':'己巳','day':'甲寅','hour':'丙寅'})
kinds3 = [(tuple(x['pillars']), x['kind']) for x in c3]
check('月日=日主被合候选', (('month','day'), DAYMASTER_BOUND_COMBINE) in kinds3)
check('年月=比肩合财去', any(p==('year','month') and k==COMBINE_AWAY for p,k in kinds3))

# 隔位(年己日甲, 月丙时甲): 无相邻合
c4 = _comb({'year':'己丑','month':'丙寅','day':'甲寅','hour':'甲子'})
check('隔位不论合', c4==[])

# 边界: 判定字段无成败/化真/争合/吉凶/STRONG/WEAK
blob3 = json.dumps(c3, ensure_ascii=False)
for bad in ['无用','化真','争合','妒合','吉','凶','STRONG','WEAK','喜神']:
    ok = bad not in blob3
    if not ok: fails+=1
    check('合去判定字段禁用词:'+bad, ok)

print()
print('FAILS', fails)
sys.exit(1 if fails else 0)
