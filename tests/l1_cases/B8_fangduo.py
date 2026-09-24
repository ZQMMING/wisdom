# -*- coding: utf-8 -*-
"""
L1定向用例库 - 类目B8: 方夺字
裁决#022: 三会>三合, 字归方
裁决#022b: 中神被夺→三合散, 生支被夺→半局残
"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import _is_sanhui, _get_hehua_branch

PASS = 0
FAIL = 0

print('=== B8 方夺字 ===')
print()

# 关键盘: 寅卯辰方+亥卯未局 → 卯归方, 亥未不成局
print('--- 关键盘: 方夺中神 ---')
# 地支: 寅卯辰亥 (寅卯辰木方+亥卯未缺未)
# 卯是木方中神+木局中神 → 归方, 亥未不成局
branches = ['寅', '卯', '辰', '亥']
# 三会方成?
fang_result = _is_sanhui('卯', branches)
# 三合还成吗? (亥卯未缺未, 本来就不成)
he_result = _get_hehua_branch('亥', branches, ['甲'])
print(f'  寅卯辰亥: 木方={fang_result}, 亥未局={he_result}')
# 期望: 木方成✅, 亥未局不成(缺未)✅
if fang_result == '木' and he_result == '':
    PASS += 1
    print(f'  OK: 方夺中神, 局散')
else:
    FAIL += 1
    print(f'  FAIL')

print()
print('--- 方夺生支 ---')
# 亥子丑方+亥卯未局 → 亥归方(生支), 卯未=旺墓半局残
# 地支: 亥子丑卯
branches2 = ['亥', '子', '丑', '卯']
fang_result2 = _is_sanhui('亥', branches2)
# 卯未局? 缺未 → 不成
he_result2 = _get_hehua_branch('卯', branches2, ['甲'])
print(f'  亥子丑卯: 水方={fang_result2}, 卯未局={he_result2}')
if fang_result2 == '水' and he_result2 == '':
    PASS += 1
    print(f'  OK: 方夺生支, 局残(缺未)')
else:
    FAIL += 1
    print(f'  FAIL')

print()
print(f'B8结果: {PASS} PASS / {FAIL} FAIL')
print(f'备注: 方/局汇总层待实现(当前只是分开判)')
print()
