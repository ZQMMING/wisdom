# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V6: 更严格的大运引导词匹配 - 区分明确引导词和模糊词
old = """        # 大运引导词(只有当这些词出现在句子中时, 才认为是具体大运的喜忌判断)
        dayun_guide_words = ['交', '至', '行', '逢', '入', '到', '走', '上', '运', '岁', '流年', '大运', '十年', '一运', '步运',
                              '运转', '运至', '运行', '运逢', '运入', '运交', '岁运', '大运', '小运', '限运', '气运', '步运',
                              '甲运', '乙运', '丙运', '丁运', '戊运', '己运', '庚运', '辛运', '壬运', '癸运',
                              '子运', '丑运', '寅运', '卯运', '辰运', '巳运', '午运', '未运', '申运', '酉运', '戌运', '亥运']"""

new = """        # V6: 更严格的大运引导词匹配 - 区分明确引导词和模糊词
        # 明确大运引导词: 交/至/行/逢/入/到/走/上 + 干支
        # 模糊大运引导词: 运/岁/流年/大运等 (只有和完整干支一起出现时才匹配)
        explicit_guide_words = ['交', '至', '行', '逢', '入', '到', '走', '上', '运转', '运至', '运行', '运逢', '运入', '运交']
        vague_guide_words = ['运', '岁', '流年', '大运', '十年', '一运', '步运', '岁运', '小运', '限运', '气运',
                              '甲运', '乙运', '丙运', '丁运', '戊运', '己运', '庚运', '辛运', '壬运', '癸运',
                              '子运', '丑运', '寅运', '卯运', '辰运', '巳运', '午运', '未运', '申运', '酉运', '戌运', '亥运']
        dayun_guide_words = explicit_guide_words + vague_guide_words"""
c = c.replace(old, new)

# 修改has_guide判断逻辑: 明确引导词可以单独匹配, 模糊词必须和完整干支一起
old2 = """            # 检查句子中是否有大运引导词或完整大运干支
            has_guide = any(gw in sent for gw in dayun_guide_words)
            has_full_gz = gz in sent"""

new2 = """            # V6: 检查句子中是否有大运引导词或完整大运干支
            # 明确引导词可以单独匹配, 模糊词必须和完整干支一起出现
            has_explicit_guide = any(gw in sent for gw in explicit_guide_words)
            has_vague_guide = any(gw in sent for gw in vague_guide_words)
            has_full_gz = gz in sent
            # 明确引导词 + 天干/地支 或 完整干支 或 模糊词+完整干支
            has_guide = has_explicit_guide or (has_vague_guide and has_full_gz)"""
c = c.replace(old2, new2)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_dayun_xiji_accuracy.py V6优化完成(更严格的大运引导词匹配: 明确引导词可单独匹配, 模糊词必须和完整干支一起)')
