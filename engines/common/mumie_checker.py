# -*- coding: utf-8 -*-
"""
L2母灭五态判定
纪律: 阈值判例反推, 挂验
"""
import sys
sys.path.insert(0, '.')

from engines.common.dangzhong_counter import calc_dangzhong, WUXING_OF_STEM

# 母灭五态: 母行 → 子行
MUMIE_TAISHI = {
    '木': '火',   # 木多火熄
    '水': '木',   # 水多木漂
    '土': '金',   # 土重金埋
    '金': '火',   # 金多火销
    '水': '火',   # 水多火绝
}

# 阈值: 党众比 ≥ 3.0 (判例反推, 挂验)
# 标定盘:
#   土重金埋: 土6.3/金2.3=2.7 (已判出, 阈值≤2.7)
#   水多木漂: 水5.5/木1.5=3.7 (未判出, 阈值>?)
#   木多火熄: 木7.5/火1.5=5.0 (未判出)
# → 阈值取3.0, 落在2.7和3.7之间
THRESHOLD = 3.0  # ⏸挂验: 判例反推


def check_mumie(branches: list, stems: list, day_master: str) -> dict:
    """
    母灭五态判定
    输入: 四支+四干+日干
    输出: {status: '母灭'/'', taishi: '木多火熄'/'', ratio: 5.0}
    """
    dz = calc_dangzhong(branches, stems)

    # 日主五行
    dm_wx = WUXING_OF_STEM.get(day_master, '')

    for mu_wx, zi_wx in MUMIE_TAISHI.items():
        mu_val = dz.get(mu_wx, 0)
        zi_val = dz.get(zi_wx, 0)
        if zi_val > 0:
            ratio = mu_val / zi_val
        else:
            ratio = 999.0  # 子行全无党, 必熄

        # 判定: 母党众比 ≥ 阈值
        if ratio >= THRESHOLD:
            # 子行无气? (火<某值)
            if zi_val <= 2.0:  # 子行弱
                return {
                    'status': '母灭',
                    'taishi': f'{mu_wx}多{zi_wx}熄/漂/埋/销/绝',
                    'mu_wx': mu_wx,
                    'zi_wx': zi_wx,
                    'mu_val': mu_val,
                    'zi_val': zi_val,
                    'ratio': ratio,
                }

    return {
        'status': '',
        'taishi': '',
        'ratio': 0.0,
    }


if __name__ == '__main__':
    # 测试: 木多火熄盘
    print('=== 母灭判定测试 ===')
    print()

    # 盘1: 木多火熄
    r1 = check_mumie(['卯', '寅', '卯', '辰'], ['癸', '甲', '丁', '甲'], '丁')
    print(f'木多火熄盘: {r1}')

    # 盘2: 水多木漂
    r2 = check_mumie(['子', '亥', '丑', '午'], ['丙', '己', '乙', '壬'], '乙')
    print(f'水多木漂盘: {r2}')

    # 盘3: 土重金埋
    r3 = check_mumie(['申', '丑', '辰', '未'], ['庚', '己', '戊', '己'], '庚')
    print(f'土重金埋盘: {r3}')
