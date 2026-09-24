# -*- coding: utf-8 -*-
"""
L2党众计数器
纪律: 参数外置, 逻辑与数值分离
     散局不加成(#033连锁)
     输入走汇总层输出
"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import BRANCH_CANGGAN, get_hehui_summary

# ========== WEIGHTS参数表(每个带背书状态) ==========
WEIGHTS = {
    # 有原文背书
    '透干': 1.0,      # ✅原文: 透干为重
    '本气': 1.0,      # ✅原文: 本气为重
    # 预案挂验
    '中气': 0.5,      # ⏸预案: 递减, 无原文定量
    '余气': 0.3,      # ⏸预案: 递减, 无原文定量
    # 合会加成(挂验)
    '三会': 2.0,      # ⏸预案: 方之力重
    '三合全': 1.5,    # ⏸预案
    '半局': 0.8,      # ⏸预案
    '六合': 0.5,      # ⏸预案
}

# 五行表
WUXING_OF_STEM = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火',
    '戊': '土', '己': '土', '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

# 地支五行(用于合会加成)
WUXING_OF_BRANCH = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}


def calc_dangzhong(branches: list, stems: list) -> dict:
    """
    党众计数器
    输入: 四支+四干
    输出: {五行: 党众值}
    纪律: 散局不加成(#033连锁)
    """
    # 1. 初始化
    result = {wx: 0.0 for wx in ['木', '火', '土', '金', '水']}

    # 2. 透干计数
    for s in stems:
        wx = WUXING_OF_STEM.get(s, '')
        if wx:
            result[wx] += WEIGHTS['透干']

    # 3. 地支藏干计数
    for b in branches:
        cg = BRANCH_CANGGAN.get(b, ['', '', ''])
        # 本气
        if cg[0]:
            wx = WUXING_OF_STEM.get(cg[0], '')
            if wx:
                result[wx] += WEIGHTS['本气']
        # 中气
        if cg[1]:
            wx = WUXING_OF_STEM.get(cg[1], '')
            if wx:
                result[wx] += WEIGHTS['中气']
        # 余气
        if cg[2]:
            wx = WUXING_OF_STEM.get(cg[2], '')
            if wx:
                result[wx] += WEIGHTS['余气']

    # 4. 合会加成(走汇总层输出, 散局不加成)
    summary = get_hehui_summary(branches, stems)

    # 三会方加成
    if summary['fang_wx']:
        result[summary['fang_wx']] += WEIGHTS['三会']

    # 三合/半局加成(散局不加)
    for h in summary['hehui']:
        if h['status'] == '全':
            result[h['hua']] += WEIGHTS['三合全']
        elif h['status'] == '半局':
            result[h['hua']] += WEIGHTS['半局']
        elif h['status'] == '局散':
            # #033连锁: 散局不加成
            pass
        # 合而不化/半局合而不化: 不加成(待挂验)

    return result


if __name__ == '__main__':
    # 测试: 木多火熄盘(癸卯甲寅丁卯甲辰)
    branches = ['卯', '寅', '卯', '辰']
    stems = ['癸', '甲', '丁', '甲']
    print('木多火熄盘:', branches, stems)
    dz = calc_dangzhong(branches, stems)
    for wx, val in sorted(dz.items(), key=lambda x: -x[1]):
        print(f'  {wx}: {val:.1f}')
