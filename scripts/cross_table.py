# -*- coding: utf-8 -*-
"""B2 × A局全 交叉表"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HE = {'甲':'己','己':'甲','乙':'庚','庚':'乙','丙':'辛','辛':'丙','丁':'壬','壬':'丁','戊':'癸','癸':'戊'}
HUA_SHEN = {'甲己': '土', '乙庚': '金', '丙辛': '水', '丁壬': '木', '戊癸': '火'}
WUXING = {}
for g in '甲乙寅卯': WUXING[g] = '木'
for g in '丙丁巳午': WUXING[g] = '火'
for g in '戊己辰戌丑未': WUXING[g] = '土'
for g in '庚辛申酉': WUXING[g] = '金'
for g in '壬癸亥子': WUXING[g] = '水'
MONTH_WANG = {'寅': '木', '卯': '木', '巳': '火', '午': '火', '申': '金', '酉': '金',
              '亥': '水', '子': '水', '辰': '土', '戌': '土', '丑': '土', '未': '土'}
SAN_HE = {'木': ['亥', '卯', '未'], '火': ['寅', '午', '戌'], '金': ['巳', '酉', '丑'], '水': ['申', '子', '辰']}

def pair_key(a, b):
    return ''.join(sorted([a, b]))

def parse(key):
    s = key.strip()
    return [s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]]

def check_ju(zhi_list, hua_row):
    if not hua_row:
        return False
    sanhe = SAN_HE.get(hua_row, [])
    return all(z in zhi_list for z in sanhe)

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

# 交叉表
cross = {
    (True, True): [],    # B2=True + A局全=True
    (True, False): [],   # B2=True + A局全=False
    (False, True): [],   # B2=False + A局全=True
    (False, False): [],  # B2=False + A局全=False
}

for li, key, old_pat in cases:
    p = parse(key)
    year_g, year_z, month_g, month_z, day_g, day_z, hour_g, hour_z = p
    zhi_list = [year_z, month_z, day_z, hour_z]
    
    he_gan = HE.get(day_g)
    pk = pair_key(day_g, he_gan)
    hua_row = HUA_SHEN.get(pk, '')
    month_row = MONTH_WANG.get(month_z, '')
    B2 = (month_row == hua_row)
    A_ju = check_ju(zhi_list, hua_row)
    
    cross[(B2, A_ju)].append(li)

print("=== B2 × A局全 交叉表 ===\n")
print(f"{'':<20} {'A局全=True':<15} {'A局全=False':<15}")
print("-" * 55)
print(f"{'B2=True（化神当令）':<20} {len(cross[(True, True)]):<15} {len(cross[(True, False)]):<15}")
print(f"{'B2=False（不当令）':<20} {len(cross[(False, True)]):<15} {len(cross[(False, False)]):<15}")
print()

print("=== 明细 ===\n")
print(f"B2=True + A局全=True（两侧俱足）: {len(cross[(True, True)])}条")
print(f"  li: {', '.join(cross[(True, True)])}")
print()
print(f"B2=True + A局全=False（仅秀气侧）: {len(cross[(True, False)])}条")
print(f"  li: {', '.join(cross[(True, False)])}")
print()
print(f"B2=False + A局全=True（仅福德侧）: {len(cross[(False, True)])}条")
print(f"  li: {', '.join(cross[(False, True)])}")
print()
print(f"B2=False + A局全=False（两轴皆空）: {len(cross[(False, False)])}条")
print(f"  li: {', '.join(cross[(False, False)])}")
