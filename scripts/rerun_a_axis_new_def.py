# -*- coding: utf-8 -*-
"""重跑A轴交叉表（新定义：或方或局全）"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 天干五合
HE = {'甲':'己','己':'甲','乙':'庚','庚':'乙','丙':'辛','辛':'丙','丁':'壬','壬':'丁','戊':'癸','癸':'戊'}

# 化神五行（由合对定）
HUA_SHEN = {'甲己': '土', '乙庚': '金', '丙辛': '水', '丁壬': '木', '戊癸': '火'}

# 五行映射
WUXING = {}
for g in '甲乙寅卯': WUXING[g] = '木'
for g in '丙丁巳午': WUXING[g] = '火'
for g in '戊己辰戌丑未': WUXING[g] = '土'
for g in '庚辛申酉': WUXING[g] = '金'
for g in '壬癸亥子': WUXING[g] = '水'

# 月支当令五行
MONTH_WANG = {'寅': '木', '卯': '木', '巳': '火', '午': '火', '申': '金', '酉': '金',
              '亥': '水', '子': '水', '辰': '土', '戌': '土', '丑': '土', '未': '土'}

# A轴：或方或局全（新定义）
A_JU = {
    '木': [('寅', '卯', '辰'), ('亥', '卯', '未')],  # 曲直
    '火': [('巳', '午', '未'), ('寅', '午', '戌')],  # 炎上
    '土': [('辰', '戌', '丑', '未')],                # 稼穑（唯一无替代）
    '金': [('申', '酉', '戌'), ('巳', '酉', '丑')],  # 从革
    '水': [('亥', '子', '丑'), ('申', '子', '辰')],  # 润下
}

def pair_key(a, b):
    return ''.join(sorted([a, b]))

# 24条案例
cases = [
    ("li-066", "庚申乙酉庚戌庚辰", "从革·化气型", "Z:归位专旺"),
    ("li-071", "戊申壬戌庚申乙酉", "从旺格", "O:其他格局"),
    ("li-247", "壬申丙午癸亥戊午", "从杀格", "O:其他格局"),
    ("li-284", "戊子戊午癸酉戊午", "从杀格", "O:其他格局"),
    ("li-338", "乙丑甲申甲辰己巳", "从杀格", "O:其他格局"),
    ("li-341", "己卯丁卯壬午癸卯", "从财格", "O:其他格局"),
    ("li-342", "丙戌戊戌癸巳壬戌", "从杀/从官", "O:其他格局"),
    ("li-356", "己未辛未丙戌戊戌", "从儿格", "O:其他格局"),
    ("li-458", "丙戌己亥甲戌庚午", "从杀格", "O:其他格局"),
    # S1: 局不全(15条)
    ("li-022", "庚寅壬午丁卯癸卯", "化木气格", "S1:局不全"),
    ("li-124", "辛丑癸巳戊申丙辰", "化火气格", "S1:局不全"),
    ("li-218", "戊午壬戌丁卯癸卯", "化木气格", "S1:局不全"),
    ("li-255", "乙卯乙酉庚寅壬午", "化金气格", "S1:局不全"),
    ("li-283", "丁丑壬子辛巳丙申", "化水气格", "S1:局不全"),
    ("li-314", "丙戌辛丑己卯甲子", "化土气格", "S1:局不全"),
    ("li-326", "丁卯辛亥丙寅丙申", "化水气格", "S1:局不全"),
    ("li-339", "戊辰壬戌甲辰己巳", "化土气格", "S1:局不全"),
    ("li-348", "己卯甲戌甲子己巳", "化土气格", "S1:局不全"),
    ("li-350", "甲寅丁丑甲戌己巳", "化土气格", "S1:局不全"),
    ("li-352", "甲辰丁卯壬辰辛亥", "化木气格", "S1:局不全"),
    ("li-412", "甲申癸酉庚子乙酉", "化金气格", "S1:局不全"),
    ("li-431", "庚午乙酉庚午壬午", "化金气格", "S1:局不全"),
    ("li-453", "己丑丙子辛酉壬辰", "化水气格", "S1:局不全"),
    ("li-485", "己丑庚午戊申癸亥", "化火气格", "S1:局不全"),
]

def parse(key):
    s = key.strip()
    return [s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]]

def probe(p):
    year_g, year_z, month_g, month_z, day_g, day_z, hour_g, hour_z = p
    zhi_list = [year_z, month_z, day_z, hour_z]
    gan_list = [year_g, month_g, hour_g]
    
    # B1: 独合/争合
    he_gan = HE.get(day_g)
    near_he = he_gan in (month_g, hour_g)
    same_day_g = sum(1 for g in gan_list if g == day_g)
    same_he_gan = sum(1 for g in gan_list if g == he_gan)
    zheng_he = (same_day_g >= 2) or (same_he_gan >= 2)
    B1a = near_he and not zheng_he
    B1b = near_he and zheng_he
    
    # B2: 化神当令
    pk = pair_key(day_g, he_gan)
    hua_row = HUA_SHEN.get(pk, '')
    month_row = MONTH_WANG.get(month_z, '')
    B2 = (month_row == hua_row)
    
    # B3: 逢龙引化
    B3 = '辰' in zhi_list
    
    # A轴：或方或局全（新定义）
    a_ju = False
    a_ju_detail = ''
    if hua_row:
        for ju in A_JU.get(hua_row, []):
            if all(z in zhi_list for z in ju):
                a_ju = True
                a_ju_detail = ''.join(ju)
                break
    
    return {
        'B1a': B1a,
        'B1b': B1b,
        'B2当令': B2,
        'B3辰': B3,
        'A局全(新定义)': a_ju,
        'A局全详情': a_ju_detail,
        '日干': day_g,
        '化神行': hua_row,
        '争合': zheng_he,
    }

print(f"=== A轴交叉表重跑（新定义：或方或局全，{len(cases)}条） ===\n")
print(f"{'li':<8} {'四柱':<14} {'分类':<10} {'日干':<4} {'化神行':<5} {'B2当令':<6} {'A局全(新)':<8} {'A局详情':<10} {'争合':<5}")
print("-" * 90)

# 交叉表统计
cross = {
    'B2=T & A=T': 0,
    'B2=T & A=F': 0,
    'B2=F & A=T': 0,
    'B2=F & A=F': 0,
}

# 翻转的li清单
flipped = []

for li, key, expect, category in cases:
    p = parse(key)
    v = probe(p)
    
    # 交叉表统计
    if v['B2当令'] and v['A局全(新定义)']:
        cross['B2=T & A=T'] += 1
    elif v['B2当令'] and not v['A局全(新定义)']:
        cross['B2=T & A=F'] += 1
    elif not v['B2当令'] and v['A局全(新定义)']:
        cross['B2=F & A=T'] += 1
    else:
        cross['B2=F & A=F'] += 1
    
    # 检测翻转（旧定义A=F，新定义A=T）
    # 旧定义只有三合局，新定义加了三会
    # 我们直接看新定义的结果
    if v['A局全(新定义)']:
        flipped.append((li, key, v['化神行'], v['A局全详情']))
    
    print(f"{li:<8} {key:<14} {category:<10} {v['日干']:<4} {v['化神行']:<5} {str(v['B2当令']):<6} {str(v['A局全(新定义)']):<8} {v['A局全详情']:<10} {str(v['争合']):<5}")

print()
print("=== 交叉表统计（B2 × A局全） ===")
for k, v in cross.items():
    print(f"  {k}: {v}条")

print()
print("=== A局全=True的案例（新定义） ===")
if flipped:
    for li, key, row, detail in flipped:
        print(f"  {li}: {key}（{row}行，{detail}全）")
else:
    print("  无（仍为0条）")

print()
print("=== li=66 checksum ===")
p66 = parse("庚申乙酉庚戌庚辰")
v66 = probe(p66)
print(f"li=66: {v66['化神行']}行, B2={v66['B2当令']}, A局全(新)={v66['A局全(新定义)']}, A局详情={v66['A局全详情']}")
print(f"预期: 申酉戌全 → A局全=True（新定义）")
print(f"结果: {'✅ 翻过来了' if v66['A局全(新定义)'] else '❌ 还是False'}")
