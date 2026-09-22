# -*- coding: utf-8 -*-
"""B轴明细分析：4条争合 + 11条B2=False"""
import sys
import io
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 天干五合
HE = {'甲':'己','己':'甲','乙':'庚','庚':'乙','丙':'辛','辛':'丙','丁':'壬','壬':'丁','戊':'癸','癸':'戊'}
HUA_SHEN = {'甲己': '土', '乙庚': '金', '丙辛': '水', '丁壬': '木', '戊癸': '火'}
KE = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
WUXING = {}
for g in '甲乙寅卯': WUXING[g] = '木'
for g in '丙丁巳午': WUXING[g] = '火'
for g in '戊己辰戌丑未': WUXING[g] = '土'
for g in '庚辛申酉': WUXING[g] = '金'
for g in '壬癸亥子': WUXING[g] = '水'
MONTH_WANG = {'寅': '木', '卯': '木', '巳': '火', '午': '火', '申': '金', '酉': '金',
              '亥': '水', '子': '水', '辰': '土', '戌': '土', '丑': '土', '未': '土'}

# 三合局
SAN_HE = {
    '木': ['亥', '卯', '未'],
    '火': ['寅', '午', '戌'],
    '金': ['巳', '酉', '丑'],
    '水': ['申', '子', '辰'],
}

def pair_key(a, b):
    return ''.join(sorted([a, b]))

def parse(key):
    s = key.strip()
    return [s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]]

def check_ju(zhi_list, hua_row):
    """检查支局是否成三合局"""
    if not hua_row:
        return False
    sanhe = SAN_HE.get(hua_row, [])
    return all(z in zhi_list for z in sanhe)

def probe(p):
    year_g, year_z, month_g, month_z, day_g, day_z, hour_g, hour_z = p
    zhi_list = [year_z, month_z, day_z, hour_z]
    gan_list = [year_g, month_g, hour_g]
    
    he_gan = HE.get(day_g)
    near_he = he_gan in (month_g, hour_g)
    same_day_g = sum(1 for g in gan_list if g == day_g)
    same_he_gan = sum(1 for g in gan_list if g == he_gan)
    zheng_he = (same_day_g >= 2) or (same_he_gan >= 2)
    
    pk = pair_key(day_g, he_gan)
    hua_row = HUA_SHEN.get(pk, '')
    month_row = MONTH_WANG.get(month_z, '')
    B2 = (month_row == hua_row)
    
    # A轴：支局是否成三合局
    A_ju = check_ju(zhi_list, hua_row)
    
    return {
        'B1b': near_he and zheng_he,
        'B2当令': B2,
        'A局全': A_ju,
        '化神行': hua_row,
        '争合': zheng_he,
    }

# 24条案例
cases = [
    ("li-066", "庚申乙酉庚戌庚辰", "化金气格"),
    ("li-071", "戊申壬戌庚申乙酉", "化金气格"),
    ("li-247", "壬申丙午癸亥戊午", "化火气格"),
    ("li-284", "戊子戊午癸酉戊午", "化火气格"),
    ("li-338", "乙丑甲申甲辰己巳", "化土气格"),
    ("li-341", "己卯丁卯壬午癸卯", "化木气格"),
    ("li-342", "丙戌戊戌癸巳壬戌", "化火气格"),
    ("li-356", "己未辛未丙戌戊戌", "化水气格"),
    ("li-458", "丙戌己亥甲戌庚午", "化土气格"),
    ("li-022", "庚寅壬午丁卯癸卯", "化木气格"),
    ("li-124", "辛丑癸巳戊申丙辰", "化火气格"),
    ("li-218", "戊午壬戌丁卯癸卯", "化木气格"),
    ("li-255", "乙卯乙酉庚寅壬午", "化金气格"),
    ("li-283", "丁丑壬子辛巳丙申", "化水气格"),
    ("li-314", "丙戌辛丑己卯甲子", "化土气格"),
    ("li-326", "丁卯辛亥丙寅丙申", "化水气格"),
    ("li-339", "戊辰壬戌甲辰己巳", "化土气格"),
    ("li-348", "己卯甲戌甲子己巳", "化土气格"),
    ("li-350", "甲寅丁丑甲戌己巳", "化土气格"),
    ("li-352", "甲辰丁卯壬辰辛亥", "化木气格"),
    ("li-412", "甲申癸酉庚子乙酉", "化金气格"),
    ("li-431", "庚午乙酉庚午壬午", "化金气格"),
    ("li-453", "己丑丙子辛酉壬辰", "化水气格"),
    ("li-485", "己丑庚午戊申癸亥", "化火气格"),
]

# 统计
zhenghe_cases = []
b2_false_cases = []

for li, key, old_pat in cases:
    p = parse(key)
    v = probe(p)
    
    if v['B1b']:
        zhenghe_cases.append((li, key, old_pat, v))
    
    if not v['B2当令']:
        b2_false_cases.append((li, key, old_pat, v))

print("=== 4条争合（B1b=True）逐行明细 ===\n")
print(f"{'li':<8} {'四柱':<14} {'旧格局':<10} {'化神行':<5} {'A局全':<6}")
print("-" * 55)
for li, key, old_pat, v in zhenghe_cases:
    print(f"{li:<8} {key:<14} {old_pat:<10} {v['化神行']:<5} {str(v['A局全']):<6}")

print()
print("=== 11条B2=False逐行明细 ===\n")
print(f"{'li':<8} {'四柱':<14} {'旧格局':<10} {'化神行':<5} {'A局全':<6}")
print("-" * 55)
for li, key, old_pat, v in b2_false_cases:
    print(f"{li:<8} {key:<14} {old_pat:<10} {v['化神行']:<5} {str(v['A局全']):<6}")

print()
print("=== B2=False的A轴分布 ===")
a_true = sum(1 for _, _, _, v in b2_false_cases if v['A局全'])
a_false = sum(1 for _, _, _, v in b2_false_cases if not v['A局全'])
print(f"B2=False + A局全=True: {a_true}条（走福德侧专旺型）")
print(f"B2=False + A局全=False: {a_false}条（既不走秀气侧也不走福德侧）")
