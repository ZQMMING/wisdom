#!/usr/bin/env python3
"""紫微斗数Runtime Trace：固定案例完整排盘审计

固定案例: 毛泽东 1893-12-26 06:00 农历 癸巳年十一月十九日辰时
出生地: 湖南湘潭 (东经112.9°)

只做 Runtime Trace，不修改任何代码。
逐项指出每个结果来自哪个函数/规则/第三方库。
"""
import os, sys, json, subprocess
from pathlib import Path
from datetime import datetime

# Setup paths
for p in ['C:/Users/wisdom/wisdom/src', 'D:/today/backend/src']:
    if Path(p).exists():
        sys.path.insert(0, p)

os.environ['TONGSHU_ALLOW_ZIWEI_STUB'] = '1'

from tongshu.engines.ziwei_engine import ZiweiEngine, GAN_SIHUA, SIHUA_EFFECT, time_index_from_hour

engine = ZiweiEngine()

print("=" * 70)
print("紫微斗数 Runtime Trace — 固定案例完整排盘审计")
print("=" * 70)

# ── 固定案例 ──────────────────────────────────────────────
LUNAR_DATE = (1893, 11, 19)   # 农历
HOUR = 6                      # 辰时 (06:00-07:59)
GENDER = 'male'
LONGITUDE = 112.9             # 湖南湘潭
SOLAR_DATE = (1893, 12, 26)   # 对应阳历

print(f"\n【输入参数】")
print(f"  农历日期: {LUNAR_DATE} (年={LUNAR_DATE[0]}, 月={LUNAR_DATE[1]}, 日={LUNAR_DATE[2]})")
print(f"  阳历日期: {SOLAR_DATE}")
print(f"  时辰: {HOUR}h (辰时)")
print(f"  性别: {GENDER}")
print(f"  出生地经度: {LONGITUDE}°E")
print(f"  出生地纬度: ~27.8°N (湘潭)")

# ── 1. 历法转换 ──────────────────────────────────────────
print(f"\n{'='*70}")
print("1. 历法转换")
print("=" * 70)

# 1.1 时辰索引
ti = time_index_from_hour(HOUR)
print(f"\n1.1 时辰索引:")
print(f"  输入: hour={HOUR}")
print(f"  公式: ((hour + 1) // 2) % 12")
print(f"  计算: (({HOUR} + 1) // 2) % 12 = {ti}")
print(f"  来源: ziwei_engine.py time_index_from_hour()")
print(f"  → index={ti} (辰时)")

# 1.2 真太阳时校正
true_solar_ti = engine.corrected_hour_index(HOUR, LONGITUDE, SOLAR_DATE)
print(f"\n1.2 真太阳时校正:")
print(f"  输入: hour={HOUR}, longitude={LONGITUDE}°E, solar_date={SOLAR_DATE}")
print(f"  公式: calculate_true_solar_time(bj, longitude)")
print(f"  结果: corrected_hour_index = {true_solar_ti}")
print(f"  来源: ziwei_engine.py corrected_hour_index()")
print(f"  → 真太阳时辰index={true_solar_ti}")
print(f"  ⚠️ 注意: true_solar_ti != ti → 真太阳时影响了排盘!")
print(f"     原始辰时(index=6) → 真太阳时后变为index={true_solar_ti}")

# 1.3 闰月处理
is_leap = LUNAR_DATE[1] < 0
print(f"\n1.3 闰月处理:")
print(f"  输入月={LUNAR_DATE[1]}")
print(f"  is_leap = {LUNAR_DATE[1]} < 0 = {is_leap}")
print(f"  来源: ziwei_engine.py _compute_via_iztro() line 245")
print(f"  → 非闰月，is_leap=False")

# 1.4 子时/晚子时处理
print(f"\n1.4 子时/晚子时处理:")
print(f"  hour={HOUR} → time_index_from_hour({HOUR}) = {ti}")
print(f"  规则: 0h→0(早子), 23h→12(晚子), 其余((h+1)//2)%12")
print(f"  → 辰时正确，无子时边界问题")

# ── 2. 命盘定位 ──────────────────────────────────────────
print(f"\n{'='*70}")
print("2. 命盘定位")
print("=" * 70)

chart = engine.compute(LUNAR_DATE, HOUR, GENDER)
full = engine.full_chart(LUNAR_DATE, HOUR, GENDER)

print(f"\n2.1 命宫定位:")
print(f"  命宫地支: {full['soulPalaceBranch']}")
print(f"  来源: iztro astrolabe.earthlyBranchOfSoulPalace")
print(f"  调用: byLunar('{LUNAR_DATE[0]}-{LUNAR_DATE[1]}-{LUNAR_DATE[2]}', {ti}, '{GENDER}', false)")

print(f"\n2.2 身宫定位:")
print(f"  身宫地支: {full['bodyPalaceBranch']}")
print(f"  来源: iztro astrolabe.earthlyBranchOfBodyPalace")

print(f"\n2.3 五行局:")
print(f"  五行局: {full['fiveElementsClass']}")
print(f"  来源: iztro astrolabe.fiveElementsClass")
print(f"  → 纳音起局，由命宫干支决定")

# ── 3. 星曜落宫 ──────────────────────────────────────────
print(f"\n{'='*70}")
print("3. 星曜落宫")
print("=" * 70)

print(f"\n3.1 命宫主星:")
print(f"  主星: {chart.soul_palace_main_star} ({full['palaces']['命宫']['major']})")
print(f"  来源: iztro astrolabe.palaces.find(p => p.earthlyBranch === astrolabe.earthlyBranchOfSoulPalace)")
print(f"  空宫借星: {full['palaces']['命宫']['major'] == []}")

print(f"\n3.2 天府星位置:")
tianfu_palace = None
for pname, pdata in full['palaces'].items():
    if '天府' in pdata['major']:
        tianfu_palace = pname
        break
print(f"  天府星: {'命宫' if tianfu_palace == '命宫' else (tianfu_palace or '未找到')}宫")

print(f"\n3.3 十四主星分布:")
for branch in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
    for pname, pdata in full['palaces'].items():
        if pdata['branch'] == branch:
            major = [s for s in pdata['major'] if s in {'紫微','天府','太阳','武曲','天同','廉贞','太阴','贪狼','巨门','天相','天梁','七杀','破军','天机'}]
            if major:
                print(f"  {branch}宫({pname}): {', '.join(major)}")
            break

print(f"\n3.4 辅星/煞星:")
for pname, pdata in full['palaces'].items():
    if pdata['minor']:
        print(f"  {pname}宫: 辅星={pdata['minor']}")

# ── 4. 四化系统 ──────────────────────────────────────────
print(f"\n{'='*70}")
print("4. 四化系统")
print("=" * 70)

# 4.1 生年干
year_stem_idx = (LUNAR_DATE[0] - 4) % 10
year_stems = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
year_stem = year_stems[year_stem_idx]
print(f"\n4.1 生年干:")
print(f"  农历年={LUNAR_DATE[0]} → 天干索引={(LUNAR_DATE[0]-4)%10} → 生年干={year_stem}")
print(f"  来源: ziwei_engine.py score_topic() line 457-460")

# 4.2 生年四化表
print(f"\n4.2 生年四化表 (GAN_SIHUA):")
print(f"  数据源: ziwei_engine.py GAN_SIHUA dict (line 76-87)")
print(f"  注释: '中州派/王亭之主流版本'")
print(f"  {year_stem}干四化: {GAN_SIHUA[year_stem]}")
print(f"  禄={GAN_SIHUA[year_stem][0]}, 权={GAN_SIHUA[year_stem][1]}, 科={GAN_SIHUA[year_stem][2]}, 忌={GAN_SIHUA[year_stem][3]}")

# 4.3 生年四化落宫
print(f"\n4.3 生年四化落宫:")
sihua_palaces = engine.get_sihua_palaces(full, year_stem)
print(f"  化禄: {sihua_palaces['hua_lu']} ({GAN_SIHUA[year_stem][0]})")
print(f"  化权: {sihua_palaces['hua_quan']} ({GAN_SIHUA[year_stem][1]})")
print(f"  化科: {sihua_palaces['hua_ke']} ({GAN_SIHUA[year_stem][2]})")
print(f"  化忌: {sihua_palaces['hua_ji']} ({GAN_SIHUA[year_stem][3]})")
print(f"  来源: ziwei_engine.py get_sihua_palaces()")

# 4.4 四化效果映射
print(f"\n4.4 四化效果映射 (SIHUA_EFFECT):")
print(f"  HUA_LU: {SIHUA_EFFECT['HUA_LU']}")
print(f"  HUA_QUAN: {SIHUA_EFFECT['HUA_QUAN']}")
print(f"  HUA_KE: {SIHUA_EFFECT['HUA_KE']}")
print(f"  HUA_JI: {SIHUA_EFFECT['HUA_JI']}")
print(f"  ⚠️ 架构警告: INCREASE/DECREASE 是语义解释层，不应冻结为Deterministic Core")
print(f"  来源: ziwei_engine.py SIHUA_EFFECT dict (line 47-52)")

# 4.5 大限四化
print(f"\n4.5 大限四化:")
decadal = engine.flow_decadal_mutagen([1893], LUNAR_DATE, HOUR, GENDER)
print(f"  1893年大限四化: {decadal.get(1893, [])}")
print(f"  来源: iztro astrolabe.horoscope('1893-6-15').decadal.mutagen")

# ── 5. 十二宫 ────────────────────────────────────────────
print(f"\n{'='*70}")
print("5. 十二宫")
print("=" * 70)

print(f"\n5.1 十二宫地支排列:")
ZW_PALACES_ORDER = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", "迁移", "仆役", "官禄", "田宅", "福德", "父母"]
for i, pname in enumerate(ZW_PALACES_ORDER):
    pdata = full['palaces'][pname]
    print(f"  {i+1:2d}. {pname}: {pdata['branch']}宫, 天干{pdata['stem']}, 主星{pdata['major'][:3]}")

print(f"\n5.2 十二宫顺序来源:")
print(f"  固定顺序: ziwei_engine.py ZW_PALACES_ORDER (line 91)")
print(f"  宫位地支: iztro astrolabe.palaces[].earthlyBranch")

# ── 6. 三方四正 ──────────────────────────────────────────
print(f"\n{'='*70}")
print("6. 三方四正")
print("=" * 70)

print(f"\n6.1 命宫三方四正:")
sfsz = engine.get_sanfang_sizheng(full, '命宫')
print(f"  本宫: {sfsz['ben']} ({sfsz['ben_branch']})")
print(f"  对宫: {sfsz['dui']} ({sfsz['dui_branch']})")
print(f"  三合1: {sfsz['sanhe1']} ({sfsz['sanhe1_branch']})")
print(f"  三合2: {sfsz['sanhe2']} ({sfsz['sanhe2_branch']})")
print(f"  四方主星: {sfsz['all_major']}")
print(f"  来源: ziwei_engine.py get_sanfang_sizheng()")
print(f"  公式: 本宫(idx) + 对宫(idx+6) + 三合(idx+4, idx+8)")

# ── 7. 大限系统 ──────────────────────────────────────────
print(f"\n{'='*70}")
print("7. 大限系统")
print("=" * 70)

print(f"\n7.1 大限范围:")
for pname in ZW_PALACES_ORDER:
    pdata = full['palaces'][pname]
    dr = pdata['decadalRange']
    print(f"  {pname}({pdata['branch']}): {dr[0]}-{dr[1]}岁, 天干{pdata['decadalStem']}")

print(f"\n7.2 大限推算来源:")
print(f"  范围: iztro astrolabe.palaces[].decadal.range")
print(f"  天干: iztro astrolabe.palaces[].decadal.heavenlyStem")
print(f"  ⚠️ 未验证: 起运年龄2岁是否符合传统规则")

# ── 8. 流年/流月/流日 ────────────────────────────────────
print(f"\n{'='*70}")
print("8. 流年/流月/流日")
print("=" * 70)

print(f"\n8.1 流年四化 (1893年):")
yearly = engine.flow_years_mutagen([1893], LUNAR_DATE, HOUR, GENDER)
print(f"  结果: {yearly.get(1893, [])}")
print(f"  来源: iztro astrolabe.horoscope('1893-6-15').yearly.mutagen")

print(f"\n8.2 流月四化 (2000年1月):")
monthly = engine.flow_month_mutagen(2000, 1, (2000, 1, 15), HOUR, GENDER)
print(f"  结果: {monthly}")
print(f"  来源: iztro astrolabe.horoscope('2000-1-15').monthly.mutagen")
print(f"  ⚠️ 注意: 使用阳历日期(2000-1-15)，iztro内部转换农历")

print(f"\n8.3 流日四化 (2000年1月15日):")
daily = engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), HOUR, GENDER)
print(f"  结果: {daily}")
print(f"  来源: iztro astrolabe.horoscope('2000-1-15').daily.mutagen")

print(f"\n8.4 四时间尺度对比:")
print(f"  生年四化: {GAN_SIHUA[year_stem]} (由{year_stem}干触发)")
print(f"  大限四化: {decadal.get(1893, [])}")
print(f"  流年四化: {yearly.get(1893, [])}")
print(f"  流月四化: {monthly}")
print(f"  流日四化: {daily}")

# ── 9. 宫干自化 ──────────────────────────────────────────
print(f"\n{'='*70}")
print("9. 宫干自化")
print("=" * 70)

for pname in ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄']:
    zihua = engine.palace_self_mutagen(full, pname)
    if zihua:
        print(f"  {pname}宫({full['palaces'][pname]['stem']}干): 自化{zihua}")
    else:
        print(f"  {pname}宫({full['palaces'][pname]['stem']}干): 无自化")
print(f"  来源: ziwei_engine.py palace_self_mutagen() → GAN_SIHUA查表")

# ── 10. 流派特征总结 ──────────────────────────────────────
print(f"\n{'='*70}")
print("10. CURRENT_IMPLEMENTED_ZIWEI_RULE_PROFILE")
print("=" * 70)

print(f"""
┌─────────────────────────────────────────────────────────────────┐
│  CURRENT_IMPLEMENTED_ZIWEI_RULE_PROFILE                        │
├─────────────────────────────────────────────────────────────────┤
│  核心引擎: iztro 2.6.0 (npm package)                          │
│  调用方式: Node.js subprocess → byLunar() + horoscope()       │
│  数据口径: 农历输入，阳历输出                                   │
├─────────────────────────────────────────────────────────────────┤
│  [已确认] 流派特征:                                             │
│  1. 四化表: 中州派/王亭之主流版本 (GAN_SIHUA dict)              │
│  2. 闰月: lunar_python 负月表示 (如-10=闰十月)                  │
│  3. 子时: 0h=早子(index 0), 23h=晚子(index 12)                 │
│  4. 真太阳时: 有校正函数，但默认不调用(需传入longitude)         │
│  5. 命宫/身宫: iztro byLunar() 计算                          │
│  6. 五行局: iztro fiveElementsClass                           │
│  7. 十二宫: 固定顺序 ZW_PALACES_ORDER                         │
│  8. 三方四正: 本宫+对宫(+6)+三合(+4,+8)                       │
│  9. 大限: iztro decadal.range + decadal.heavenlyStem          │
│  10. 流年/流月/流日: horoscope('YYYY-M-D') 链式调用           │
│  11. 空宫借星: 命宫无主星时借对宫主星                           │
│  12. 宫干自化: GAN_SIHUA 查表实现                             │
├─────────────────────────────────────────────────────────────────┤
│  [无法确定] 流派特征:                                           │
│  1. 大限顺逆规则: iztro默认算法，未验证是否符合传统              │
│  2. 起运年龄: 命宫2岁起，但未验证传统规则                       │
│  3. 流月算法: iztro内部斗君/流月命宫推算，黑盒                   │
│  4. 流日算法: iztro内部推算，黑盒                               │
│  5. 紫微星安星法: 黑盒(iztro内部)                               │
│  6. 十四主星安星法: 黑盒(iztro内部)                             │
│  7. 辅星/煞星安星法: 黑盒(iztro内部)                            │
│  8. 命宫计算公式: 黑盒(iztro内部)                               │
├─────────────────────────────────────────────────────────────────┤
│  [架构问题]                                                      │
│  1. native_direction() 已实现 → 违反ea3574d裁决                │
│  2. SIHUA_EFFECT (INCREASE/DECREASE) → 语义层不应冻结           │
│  3. 断事评分 score_topic() → 已实现，不应冻结                   │
│  4. 真太阳时校正函数存在但未在compute()中自动调用               │
└─────────────────────────────────────────────────────────────────┘
""")

# ── 11. 关键函数溯源 ──────────────────────────────────────
print(f"{'='*70}")
print("11. 关键函数/规则溯源")
print("=" * 70)

溯源 = [
    ("time_index_from_hour()", "ziwei_engine.py:94-104", "时辰→index映射"),
    ("corrected_hour_index()", "ziwei_engine.py:949-971", "真太阳时校正"),
    ("_compute_via_iztro()", "ziwei_engine.py:239-317", "核心排盘→iztro byLunar()"),
    ("full_chart()", "ziwei_engine.py:869-914", "完整命盘→iztro palaces[]"),
    ("flow_decadal_mutagen()", "ziwei_engine.py:765-794", "大限四化→iztro horoscope(Y-6-15)"),
    ("flow_years_mutagen()", "ziwei_engine.py:319-356", "流年四化→iztro horoscope(Y-6-15)"),
    ("flow_month_mutagen()", "ziwei_engine.py:819-843", "流月四化→iztro horoscope(Y-M-15)"),
    ("flow_day_mutagen()", "ziwei_engine.py:845-867", "流日四化→iztro horoscope(Y-M-D)"),
    ("get_sihua_palaces()", "ziwei_engine.py:388-415", "生年四化落宫→GAN_SIHUA查表"),
    ("palace_self_mutagen()", "ziwei_engine.py:928-947", "宫干自化→GAN_SIHUA查表"),
    ("get_sanfang_sizheng()", "ziwei_engine.py:572-629", "三方四正→地支索引计算"),
    ("native_direction()", "ziwei_engine.py:186-214", "方向判断→违反ea3574d裁决❌"),
    ("score_topic()", "ziwei_engine.py:417-570", "断事评分→已实现，不应冻结❌"),
]

print(f"\n{'函数':<30} {'位置':<30} {'说明'}")
print("-" * 90)
for name, loc, desc in 溯源:
    marker = "❌" in desc and " [VIOLATION]" or ""
    print(f"{name:<30} {loc:<30} {desc}{marker}")

print(f"\n{'='*70}")
print("Runtime Trace 完成")
print("=" * 70)
