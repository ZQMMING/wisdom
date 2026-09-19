# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji_v2.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 调整六冲六合权重: 从2/1改为1/0.5
old1 = """            if primary in chong_hidden:
                chong_xiji -= 2  # 冲用神根, 忌
                relations.append('CHONG_PRIMARY_ROOT')
            if avoid and avoid[0] in chong_hidden:
                chong_xiji += 1  # 冲忌神根, 喜
                relations.append('CHONG_AVOID_ROOT')"""
new1 = """            if primary in chong_hidden:
                chong_xiji -= 1  # 冲用神根, 忌(权重减半)
                relations.append('CHONG_PRIMARY_ROOT')
            if avoid and avoid[0] in chong_hidden:
                chong_xiji += 0.5  # 冲忌神根, 喜(权重减半)
                relations.append('CHONG_AVOID_ROOT')"""
c = c.replace(old1, new1)

old2 = """            if he_huashen == primary:
                he_xiji += 2  # 合化用神, 喜
                relations.append('HE_PRIMARY')
            if avoid and he_huashen == avoid[0]:
                he_xiji -= 1  # 合化忌神, 忌
                relations.append('HE_AVOID')"""
new2 = """            if he_huashen == primary:
                he_xiji += 1  # 合化用神, 喜(权重减半)
                relations.append('HE_PRIMARY')
            if avoid and he_huashen == avoid[0]:
                he_xiji -= 0.5  # 合化忌神, 忌(权重减半)
                relations.append('HE_AVOID')"""
c = c.replace(old2, new2)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('大运喜忌V2权重调整完成(六冲六合权重减半)')
