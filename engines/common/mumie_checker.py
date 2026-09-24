# -*- coding: utf-8 -*-
"""
L2母灭五态判定(修正版)
本质: 印星(生我者)成势 + 日主无根不受生
"""
import sys
sys.path.insert(0, '.')

from engines.common.dangzhong_counter import calc_dangzhong, WUXING_OF_STEM

# 印星=生我者
SHENG_ME = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}

# 阈值: 判例反推, 挂验
# 真母灭盘:
#   木多火熄: 木(印)7.5 vs 火(日主)1.5 → 印比=5.0
#   水多木漂: 水(印)5.5 vs 木(日主)1.5 → 印比=3.7
# 健康盘上限:
#   水多火绝盘(健康): 水5.0 vs 火1.0 → 印比=5.0 (但日主是火, 水是印, 这是水多火绝?)
# → 阈值取4.0, 落在3.7和5.0之间
YIN_THRESHOLD = 3.5  # ⏸挂验: 判例反推(真母灭3.7, 健康盘上限3.1)
DAYMASTER_MAX = 2.0  # 日主党众≤2.0算无根


def check_mumie(branches: list, stems: list, day_master: str) -> dict:
    """
    母灭五态判定(修正版)
    本质: 印星成势 + 日主无根
    """
    dz = calc_dangzhong(branches, stems)

    dm_wx = WUXING_OF_STEM.get(day_master, '')
    yin_wx = SHENG_ME.get(dm_wx, '')  # 印星=生我者

    dm_val = dz.get(dm_wx, 0)
    yin_val = dz.get(yin_wx, 0)

    # 判定: 印党众比 ≥ 阈值 且 日主党众 ≤ 上限 且 印星有党
    if yin_val > 0 and dm_val > 0:
        ratio = yin_val / dm_val
    else:
        ratio = 999.0

    if yin_val > 0 and ratio >= YIN_THRESHOLD and dm_val <= DAYMASTER_MAX:
        # 状态分档: 比值≥5.0→CONFIRMED, 3.5-5.0→CANDIDATE
        state = 'CONFIRMED' if ratio >= 5.0 else 'CANDIDATE'
        return {
            'status': '母灭',
            'taishi': f'{yin_wx}多{dm_wx}熄',
            'mu_wx': yin_wx,
            'zi_wx': dm_wx,
            'mu_val': yin_val,
            'zi_val': dm_val,
            'ratio': ratio,
            'state': state,
        }

    return {
        'status': '',
        'taishi': '',
        'ratio': 0.0,
    }


if __name__ == '__main__':
    print('=== 母灭判定(修正版) ===')
    print()

    # 真母灭盘
    r1 = check_mumie(['卯', '寅', '卯', '辰'], ['癸', '甲', '丁', '甲'], '丁')
    print(f'木多火熄: {r1}')

    r2 = check_mumie(['子', '亥', '丑', '午'], ['丙', '己', '乙', '壬'], '乙')
    print(f'水多木漂: {r2}')

    # 健康盘(不应判出)
    r3 = check_mumie(['戌', '子', '子', '辰'], ['壬', '壬', '甲', '戊'], '甲')
    print(f'健康盘1(甲日主, 水=印): {r3}')

    r4 = check_mumie(['亥', '亥', '卯', '卯'], ['癸', '癸', '丁', '癸'], '丁')
    print(f'健康盘2(丁日主, 木=印): {r4}')
