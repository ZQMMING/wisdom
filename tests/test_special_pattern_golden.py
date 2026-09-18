# -*- coding: utf-8 -*-
"""特殊格局识别器 golden: 从格/专旺/日干化气/母灭 结构定性标签回归。
只校验结构类别与 CONFIRMED/CANDIDATE 状态; 不判用神成败吉凶, 不出 STRONG/WEAK。"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0b
from engines.common.wuxing_power import build_wuxing_power
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.special_pattern import build_special_patterns

K = ('year', 'month', 'day', 'hour')


def gp(s):
    return {K[i // 2]: [s[i], s[i + 1]] for i in range(0, 8, 2)}


# (四柱, 期望类别包含词; '无'=不应判任何特殊格, 期望状态或None)
CASES = [
    # --- 从格 ---
    ('丙寅庚寅壬午乙巳', '从财', 'CANDIDATE'),
    ('癸亥乙卯己未丁卯', '从杀', 'CANDIDATE'),
    ('庚戌甲申甲戌乙丑', '从杀', 'CANDIDATE'),
    ('辛卯辛卯辛卯辛卯', '从财', 'CANDIDATE'),
    ('甲午丁丑甲午丙寅', '从儿', 'CANDIDATE'),   # 从儿不论身强弱(甲有寅禄)
    ('丁巳癸卯癸卯丙辰', '从儿', None),
    ('戊申己未丙戌己丑', '从儿', 'CONFIRMED'),
    ('庚子庚辰戊申辛酉', '从儿', 'CONFIRMED'),
    ('壬子辛亥辛卯辛卯', '从儿', 'CANDIDATE'),
    ('丁丑壬寅丙申壬辰', '从杀', 'CANDIDATE'),   # 寅印被申冲拔+财生杀
    ('癸巳乙卯己亥癸酉', '从杀', 'CANDIDATE'),   # 巳禄被亥冲
    ('壬戌甲辰丁酉己酉', '从财', 'CANDIDATE'),
    ('戊申甲寅壬寅丁未', '从财', 'CANDIDATE'),   # 食伤当令制杀存财(去杀存财)
    ('乙卯己卯戊辰癸亥', '从官', 'CANDIDATE'),   # 孤根被当令官杀克拔, 卯乙正官主导
    ('壬寅辛亥辛亥壬辰', '从儿', 'CANDIDATE'),   # 日主真无根、孤印辰被当令旺水反侮
    ('丙戌壬辰癸巳甲寅', '从官', None),          # 辰戌戊正官当令主导
    ('戊戌丁巳甲寅己巳', '从势', 'CANDIDATE'),   # 火土两神并旺、衰极从势
    ('丁卯丙寅辛亥庚寅', '从杀', None),          # 财(寅木)生透干丙丁杀、气归于杀
    ('丙戌乙未乙巳丁亥', '从儿', None),          # 财当令而食伤叠透有根、财不透, 顺局从儿
    # --- 通根身库+食神制杀=正格, 不得判从 ---
    ('戊辰戊午壬辰甲辰', '无', None),
    ('壬子壬子丙戌戊戌', '无', None),
    ('丙辰乙未壬辰甲辰', '无', None),
    # --- 虚湿寒土当令反假从财=气候层(task#49), 当前结构层不判 ---
    ('庚辰己丑己亥壬申', '无', None),
    # --- 专旺 ---
    ('己巳辛未丙午丁酉', '炎上', 'CONFIRMED'),
    ('癸巳戊午丙午壬辰', '炎上', 'CANDIDATE'),
    ('甲寅乙亥乙卯癸未', '曲直', None),
    ('丁卯乙巳丁卯乙巳', '炎上', None),
    ('庚午壬午丙寅庚寅', '炎上', 'CANDIDATE'),
    # --- 日干化气 ---
    ('己卯丁卯壬午癸卯', '化木', 'CONFIRMED'),
    ('戊辰壬戌甲辰己巳', '化土', 'CONFIRMED'),
    ('己卯甲戌甲子己巳', '化土', 'CANDIDATE'),  # 假化
]

fails = 0
for c, exp, exp_state in CASES:
    p = gp(c)
    f = l0b(p)
    th = build_tian_he(p, f)
    wp = build_wuxing_power(p, f, th)
    sp = build_special_patterns(p, f, wp, th)
    got = sp['cong_type'] or sp['zhuanwang'] or sp['hua_qi'] or '无'
    state = sp['cong_state'] or (sp['patterns'][0]['state'] if sp['patterns'] else '')
    if exp == '无':
        ok = (got == '无')
    else:
        ok = (exp in got) and (exp_state is None or exp_state == state)
    if not ok:
        fails += 1
    print('PASS' if ok else 'FAIL', c, '期望[' + exp +
          (('/' + exp_state) if exp_state else '') + '] 得[' + str(got) + '/' + state + ']')

print()
print('TOTAL', len(CASES), 'FAILS', fails)
sys.exit(1 if fails else 0)
