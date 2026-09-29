# -*- coding: utf-8 -*-
"""
L2边界函数: 纯布尔枚举(0浮点)
纪律: 全库只此一处, 其他位置禁止散装比较
"""

# 档位枚举(按强度排序)
ROOT_GRADES = ['禄刃', '长生', '库', '无根', '受制']

# 党众计数→档位(纯整数, 0浮点)
# 党众计数规则:
#   透干+1, 本气+1, 中气+0(不算), 余气+0(不算)
#   禄刃: 党众>=2(透干+本气)
#   长生: 党众>=1(透干或本气)
#   库: 地支见库根(辰戌丑未)
#   无根: 无根
#   受制: 根被冲克

def to_root_grade(root_count: int, has_root: bool, root_controlled: bool) -> str:
    """
    党众计数→根基档位(纯布尔枚举)
    输入: root_count(整数党众计数), has_root(有无根), root_controlled(根是否受制)
    输出: 档位枚举{禄刃/长生/库/无根/受制}
    """
    if root_controlled:
        return '受制'
    if not has_root:
        return '无根'
    if root_count >= 2:
        return '禄刃'
    if root_count >= 1:
        return '长生'
    return '库'


if __name__ == '__main__':
    print('=== 边界函数测试(纯布尔) ===')
    print()
    print('  党众2+有根+未受制 → 禄刃')
    print('  党众1+有根+未受制 → 长生')
    print('  党众0+有根+未受制 → 库')
    print('  有根=假 → 无根')
    print('  根受制 → 受制')
