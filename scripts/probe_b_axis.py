# -*- coding: utf-8 -*-
"""伪B轴规格探测脚本（纯规格，不动引擎）"""
import sys
import io
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 天干五合
HE = {'甲':'己','己':'甲','乙':'庚','庚':'乙','丙':'辛','辛':'丙','丁':'壬','壬':'丁','戊':'癸','癸':'戊'}

# 五行映射
WUXING = {}
for g in '甲乙寅卯': WUXING[g] = '木'
for g in '丙丁巳午': WUXING[g] = '火'
for g in '戊己辰戌丑未': WUXING[g] = '土'
for g in '庚辛申酉': WUXING[g] = '金'
for g in '壬癸亥子': WUXING[g] = '水'

# 月支当令五行
MONTH_WANG = {'寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金',
              '亥':'水','子':'水','辰':'土','戌':'土','丑':'土','未':'土'}

# 24条案例（去重后）
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
    
    # B1: 独合
    he_gan = HE.get(day_g)  # 日干的合神
    near_he = he_gan in (month_g, hour_g)  # 紧邻合（月/时干）
    
    # 争合：能与日干相合的天干数（不含日干自身）
    he_count = sum(1 for g in gan_list if HE.get(g) == day_g)
    
    B1a = near_he and (he_count == 1)  # 紧邻独合
    B1b = near_he and (he_count >= 2)  # 紧邻争合
    
    # B2: 化神当令
    hua_god = he_gan  # 化神
    hua_row = WUXING.get(hua_god, '')  # 化神五行
    month_row = MONTH_WANG.get(month_z, '')  # 月令五行
    B2 = (month_row == hua_row)  # 化神当令（只认当旺，宽松版暂略）
    
    # B3: 逢龙引化
    B3 = '辰' in zhi_list
    
    # B4: 无破（proxy：克化神之天干数+地支数）
    ke_map = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
    ke_god = ke_map.get(hua_row, '')
    ke_gan_count = sum(1 for g in gan_list if WUXING.get(g) == ke_god)
    ke_zhi_count = sum(1 for z in zhi_list if WUXING.get(z) == ke_god)
    B4 = (ke_gan_count == 0) and (ke_zhi_count <= 1)
    
    return {
        'B1a': B1a,
        'B1b': B1b,
        'B2当令': B2,
        'B3辰': B3,
        'B4无破': B4,
        '化神': hua_god,
        '化神行': hua_row,
        '争合': he_count >= 2,
        '破数': ke_gan_count + ke_zhi_count
    }

print(f"=== 伪B轴规格探测（{len(cases)}条） ===\n")
print(f"{'li':<8} {'四柱':<14} {'分类':<10} {'B1a':<5} {'B1b':<5} {'B2':<5} {'B3':<5} {'B4':<5} {'化神':<4} {'争合':<5} {'破数':<4}")
print("-" * 90)

# 统计
b1a_count = 0
b1b_count = 0
b2_count = 0
b3_count = 0
b4_count = 0

for li, key, expect, category in cases:
    p = parse(key)
    v = probe(p)
    
    if v['B1a']: b1a_count += 1
    if v['B1b']: b1b_count += 1
    if v['B2当令']: b2_count += 1
    if v['B3辰']: b3_count += 1
    if v['B4无破']: b4_count += 1
    
    print(f"{li:<8} {key:<14} {category:<10} {str(v['B1a']):<5} {str(v['B1b']):<5} {str(v['B2当令']):<5} {str(v['B3辰']):<5} {str(v['B4无破']):<5} {v['化神']:<4} {str(v['争合']):<5} {v['破数']:<4}")

print()
print("=== 统计汇总 ===")
print(f"B1a（紧邻独合）: {b1a_count}/{len(cases)} = {b1a_count/len(cases)*100:.1f}%")
print(f"B1b（紧邻争合）: {b1b_count}/{len(cases)} = {b1b_count/len(cases)*100:.1f}%")
print(f"B2（化神当令）: {b2_count}/{len(cases)} = {b2_count/len(cases)*100:.1f}%")
print(f"B3（逢龙引化）: {b3_count}/{len(cases)} = {b3_count/len(cases)*100:.1f}%")
print(f"B4（无破）: {b4_count}/{len(cases)} = {b4_count/len(cases)*100:.1f}%")

print()
print("=== 关键发现 ===")
print(f"1. B1a={b1a_count}条：紧邻独合（无争合）的案例数")
print(f"2. B3辰覆盖率={b3_count}/{len(cases)}={b3_count/len(cases)*100:.1f}%：若<30%，增益档区分度不足")
print(f"3. B4无破={b4_count}条：与现有闸门的重合度待验证")
