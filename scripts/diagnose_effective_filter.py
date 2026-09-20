# -*- coding: utf-8 -*-
"""P1有效性过滤层诊断脚本: 统计5个布尔条件在513例中的分布, 确认只命中目标6例, 不误伤其他案例.
不修改引擎, 只统计."""
import re, sys, json, collections
sys.path.insert(0, '.')

path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
GZ = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')

# 提取命例
pillars_lines = []
for i, ln in enumerate(lines):
    s = ln.strip()
    if s.startswith('八字'):
        b = s.split('：',1)[-1].split(':',1)[-1].strip()
        pp = GZ.findall(b)
        if len(pp)==4: pillars_lines.append((i, pp))
    else:
        pp = GZ.findall(s)
        if len(pp)==4 and len(s)<60:
            c = GZ.sub('',s).replace(' ','').replace('\u3000','')
            if c=='': pillars_lines.append((i, pp))

from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_from_power
from engines.common.special_pattern import build_special_patterns

# 五行/天干映射
WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
BRANCH_WX = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
YIN_WX = {'木':'水','火':'木','土':'火','金':'土','水':'金'}  # 生我者
CAI_WX = {'木':'土','火':'金','土':'水','金':'木','水':'火'}  # 我克者
SHISHANG_WX = {'木':'火','火':'土','土':'金','金':'水','水':'木'}  # 我生者

# 六冲
LIUCHONG = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅','卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}

# 天干五合
TIANHE = {'甲':'己','己':'甲','乙':'庚','庚':'乙','丙':'辛','辛':'丙','丁':'壬','壬':'丁','戊':'癸','癸':'戊'}

target_lines = {326, 438, 1227, 1350, 1366, 1507}

results = []
cond_stats = collections.Counter()
any_cond_cases = []
two_plus_cond_cases = []

for idx, (li, fp) in enumerate(pillars_lines):
    p = {'year':list(fp[0]),'month':list(fp[1]),'day':list(fp[2]),'hour':list(fp[3])}
    try:
        f = build(p)
        _wp = build_wuxing_power(p, f)
        _spec = build_spectrum_from_power(_wp)
        _qr = _spec.get('qiang_ruo', {})
        _ws = _spec.get('wang_shuai', {})
        _special = build_special_patterns(p, f, _wp)
        _is_cong = any(pt.get('pattern_id') in ('ZP-SPECIAL-CONG','ZP-SPECIAL-ZHUANWANG') for pt in _special.get('patterns',[]))

        dm = p['day'][0]
        dm_wx = WUXING[dm]
        yin_wx = YIN_WX[dm_wx]
        cai_wx = CAI_WX[dm_wx]
        ss_wx = SHISHANG_WX[dm_wx]

        # 天干列表
        stems = [p[k][0] for k in ('year','month','day','hour')]
        branches = [p[k][1] for k in ('year','month','day','hour')]

        # 条件A: 印被克 = 印星透干 AND 财星透干 AND 财星有根(本气/中气) AND 财克印
        yin_stems = [s for s in stems if WUXING[s] == yin_wx and s != dm]
        cai_stems = [s for s in stems if WUXING[s] == cai_wx]
        cai_has_root = any(BRANCH_WX.get(b) == cai_wx for b in branches)
        cai_ke_yin = KE[cai_wx] == yin_wx
        cond_A = bool(yin_stems) and bool(cai_stems) and cai_has_root and cai_ke_yin

        # 条件B: 根被冲 = 日支被冲 OR 月支被冲 (且被冲之支有日主根)
        day_branch = branches[2]
        month_branch = branches[1]
        # 检查日支/月支是否被其他支冲
        day_chong = any(LIUCHONG.get(day_branch) == b for b in branches if b != day_branch)
        month_chong = any(LIUCHONG.get(month_branch) == b for b in branches if b != month_branch)
        # 被冲之支是否有日主根 (本气/中气/余气为日主同类)
        def has_root_in_branch(br, dm_wx):
            hidden = f.get('hidden_stems', {}).get({'year':'year','month':'month','day':'day','hour':'hour'}[list(p.keys())[list(p.values()).index([stems[list(branches).index(br)] if br in branches else 'day', br])]] , br)
            # 简化: 检查支本气是否为日主五行
            return BRANCH_WX.get(br) == dm_wx
        day_has_root = BRANCH_WX.get(day_branch) == dm_wx
        month_has_root = BRANCH_WX.get(month_branch) == dm_wx
        cond_B = (day_chong and day_has_root) or (month_chong and month_has_root)

        # 条件C: 寒湿过重 = 月支 ∈ {亥,子,丑} AND 原局无火透干 AND 无火本气根
        month_is_winter = month_branch in ('亥','子','丑')
        fire_stems = [s for s in stems if WUXING[s] == '火']
        fire_ben_branches = [b for b in branches if BRANCH_WX.get(b) == '火']
        cond_C = month_is_winter and not fire_stems and not fire_ben_branches

        # 条件D: 泄气太重 = 食伤透干>=1 AND 食伤有本气根 AND 日主无重根
        ss_stems = [s for s in stems if WUXING[s] == ss_wx and s != dm]
        ss_has_ben_root = any(BRANCH_WX.get(b) == ss_wx for b in branches)
        has_heavy = _qr.get('has_heavy_root', False)
        cond_D = bool(ss_stems) and ss_has_ben_root and not has_heavy

        # 条件E: 合化改变五行 = 天干合化成功 (化神得时乘令: 化神五行=月令本气 或 化神有地支本气根>=2)
        # 先找天干五合对
        he_pairs_found = []
        for i, s1 in enumerate(stems):
            for j, s2 in enumerate(stems):
                if i < j and TIANHE.get(s1) == s2:
                    # 化神五行: 甲己合土, 乙庚合金, 丙辛合水, 丁壬合木, 戊癸合火
                    huashen_map = {'甲':'土','己':'土','乙':'金','庚':'金','丙':'水','辛':'水','丁':'木','壬':'木','戊':'火','癸':'火'}
                    huashen_wx = huashen_map.get(s1, '')
                    # 化神得时乘令: 月令本气=化神五行 或 化神有2个以上地支本气根
                    month_ben_wx = BRANCH_WX.get(month_branch, '')
                    huashen_ben_count = sum(1 for b in branches if BRANCH_WX.get(b) == huashen_wx)
                    huasheng_chenggong = (month_ben_wx == huashen_wx) or (huashen_ben_count >= 2)
                    if huasheng_chenggong:
                        he_pairs_found.append((s1, s2, huashen_wx))
        cond_E = bool(he_pairs_found)

        conds = {'A印被克':cond_A, 'B根被冲':cond_B, 'C寒湿过重':cond_C, 'D泄气太重':cond_D, 'E合化':cond_E}
        triggered = [k for k,v in conds.items() if v]
        n_triggered = len(triggered)

        for k in triggered:
            cond_stats[k] += 1
        if n_triggered >= 1:
            any_cond_cases.append({'line':li+1, 'pillars':fp, 'triggered':triggered, 'is_cong':_is_cong})
        if n_triggered >= 2:
            two_plus_cond_cases.append({'line':li+1, 'pillars':fp, 'triggered':triggered, 'is_cong':_is_cong})

        is_target = (li+1) in target_lines
        results.append({'line':li+1, 'pillars':fp, 'conds':conds, 'triggered':triggered,
                       'n_triggered':n_triggered, 'is_target':is_target, 'is_cong':_is_cong,
                       'raw_qiang_ruo':_qr.get('root_class',''), 'has_root':_qr.get('has_root',False)})
    except Exception as e:
        pass

# 统计
print(f'=== P1有效性过滤层诊断 ===')
print(f'总案例数: {len(results)}')
print(f'\n各条件命中数:')
for k, v in cond_stats.most_common():
    print(f'  {k}: {v}例')
print(f'\n任一条件触发: {len(any_cond_cases)}例')
print(f'两个以上条件触发: {len(two_plus_cond_cases)}例')

# 目标6例触发情况
print(f'\n=== 目标6例触发情况 ===')
for r in results:
    if r['is_target']:
        pillars = ''.join([f'{g}{z}' for g,z in r['pillars']])
        print(f'  L{r["line"]} {pillars} | 触发={r["triggered"]} | 从格={r["is_cong"]} | root={r["raw_qiang_ruo"]}')

# 非目标案例但触发条件的 (潜在误伤)
print(f'\n=== 非目标案例但触发任一条件 (潜在误伤, 排除从格) ===')
non_target_any = [r for r in results if r['n_triggered']>=1 and not r['is_target'] and not r['is_cong']]
print(f'共 {len(non_target_any)}例 (排除从格后)')
for r in non_target_any[:30]:
    pillars = ''.join([f'{g}{z}' for g,z in r['pillars']])
    print(f'  L{r["line"]} {pillars} | 触发={r["triggered"]} | root={r["raw_qiang_ruo"]}')

# 非目标案例但触发两个以上条件
print(f'\n=== 非目标案例但触发两个以上条件 (潜在误伤, 排除从格) ===')
non_target_two = [r for r in results if r['n_triggered']>=2 and not r['is_target'] and not r['is_cong']]
print(f'共 {len(non_target_two)}例 (排除从格后)')
for r in non_target_two[:20]:
    pillars = ''.join([f'{g}{z}' for g,z in r['pillars']])
    print(f'  L{r["line"]} {pillars} | 触发={r["triggered"]} | root={r["raw_qiang_ruo"]}')
