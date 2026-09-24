# -*- coding: utf-8 -*-
"""
L2边界函数: 浮点→档唯一换算处
纪律: 全库只此一处, 其他位置禁止散装比较
"""

# 档位枚举(按强度排序)
ROOT_GRADES = ['禄刃', '长生', '库', '无根', '受制']

# 分界数值(唯一存储处)
# 党众值→档位:
#   ≥3.0 → 禄刃
#   ≥2.0 → 长生
#   ≥1.0 → 库
#   >0   → 无根
#   ≤0   → 受制
GRADES_THRESHOLDS = {
    '禄刃': 3.0,
    '长生': 2.0,
    '库': 1.0,
    '无根': 0.0,
}


def to_root_grade(dm_val: float) -> str:
    """
    党众值→根基档位(唯一边界函数)
    输入: 党众值(浮点)
    输出: 档位枚举{禄刃/长生/库/无根/受制}
    """
    if dm_val >= GRADES_THRESHOLDS['禄刃']:
        return '禄刃'
    elif dm_val >= GRADES_THRESHOLDS['长生']:
        return '长生'
    elif dm_val >= GRADES_THRESHOLDS['库']:
        return '库'
    elif dm_val > GRADES_THRESHOLDS['无根']:
        return '无根'
    else:
        return '受制'


if __name__ == '__main__':
    print('=== 边界函数测试 ===')
    print()
    for val in [5.0, 3.5, 2.5, 1.5, 0.5, 0.0]:
        print(f'  {val:.1f} → {to_root_grade(val)}')
