# -*- coding: utf-8 -*-
"""
PATCH-058 流年+状态变化链路
原局 → 大运 → 流年 → 状态变化
流年: 该年干支(立春换年柱); 状态变化: 大运/流年干支与原局生克冲合
铁律: 无评分/权重; 状态变化只输出作用关系, 不直接改写strength
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'

ELEM = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土',
        '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}  # 我克
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}  # 我生
CHONG = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
         '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}


def liunian(year):
    """流年干支(立春换年, 简化用年柱)"""
    return GAN[(year - 4) % 10] + ZHI[(year - 4) % 12]


def state_change(piliunian, dayun_ganzhi_list, qiyun_age, current_age, day_master):
    """
    状态变化: 当前大运+流年与原局的作用关系
    piliunian: 流年柱
    dayun_ganzhi_list: 大运8柱
    qiyun_age: 起运岁数
    current_age: 当前虚岁
    day_master: 日主
    return: 作用关系(不改strength)
    """
    idx = int((current_age - qiyun_age) // 10)
    idx = max(0, min(idx, len(dayun_ganzhi_list) - 1))
    dy = dayun_ganzhi_list[idx]
    dyg, dyz = dy[0], dy[1]
    lg, lz = piliunian[0], piliunian[1]

    dm_elem = ELEM[day_master]
    effects = []
    # 天干生克
    for g, label in [(dyg, "大运干"), (lg, "流年干")]:
        ge = ELEM[g]
        if ge == dm_elem:
            effects.append(f"{label}{g}同氣(比劫)")
        elif KE[dm_elem] == ge:
            effects.append(f"{label}{g}日主克(財)")
        elif KE[ge] == dm_elem:
            effects.append(f"{label}{g}克日主(官殺)")
        elif SHENG[dm_elem] == ge:
            effects.append(f"{label}{g}日主生(食傷)")
        elif SHENG[ge] == dm_elem:
            effects.append(f"{label}{g}生日主(印)")
    # 地支冲
    for z, label in [(dyz, "大运支"), (lz, "流年支")]:
        pass
    return {"current_dayun": dy, "liunian": piliunian,
            "age_idx": idx, "effects": effects,
            "note": "作用关系登记, 不改写strength_state; 待Rule Layer裁决喜忌"}


if __name__ == '__main__':
    print("=== PATCH-058 流年+状态变化 ===")
    # GC-001 硬编码: 癸亥 壬戌 乙未 壬午, 大运逆排, 起运8.7岁
    dm = '乙'
    dayun = ['辛酉','庚申','己未','戊午','丁巳','丙辰','乙卯','甲寅']
    qiyun_age = 8.7
    ln = liunian(2024)
    print(f'原局: 癸亥 壬戌 乙未 壬午 日主{dm}')
    print(f'大运: {" ".join(dayun)}')
    print(f'起运: 8.7岁逆排')
    print(f'流年2024: {ln}')
    r = state_change(ln, dayun, qiyun_age, 41, dm)
    print(f'41虚岁 大运: {r["current_dayun"]}')
    print(f'作用关系: {r["effects"]}')
