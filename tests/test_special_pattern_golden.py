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
    ('癸亥乙卯戊午甲寅', '从杀', 'CANDIDATE'),   # 虚土不纳火: 无辰戌丑未本气根(午寄禄/寅长生寄生火宫)、官杀当令成势透干、印不透化杀不力, 假从寄宫根待运拔
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
    ('癸亥己未丙午己丑', '无', None),          # 午未不合化日主午火刃根; 伤官泄身用印正格(喜印非从儿)
    # --- 专旺 ---
    ('己巳辛未丙午丁酉', '炎上', 'CONFIRMED'),
    ('癸巳戊午丙午壬辰', '炎上', 'CANDIDATE'),
    ('甲寅乙亥乙卯癸未', '曲直', None),
    ('丁卯乙巳丁卯乙巳', '炎上', None),
    ('庚午壬午丙寅庚寅', '炎上', 'CANDIDATE'),
    # task#50 六合化神归化反哺(他神支化印/从旺, 日主根不被化走)
    ('庚戌壬午丙寅己亥', '炎上', 'CANDIDATE'),   # 寅亥合木, 亥水官杀化印(火局顺势)
    ('丁亥壬寅丙午丁酉', '炎上', 'CANDIDATE'),   # 寅亥合木(寅月化神当令), 亥杀化印
    ('己丑丙子壬辰戊申', '润下', 'CANDIDATE'),   # 申子辰水局当令, 子丑合丑土从旺水
    ('戊午丙辰戊辰辛酉', '稼穑', 'CONFIRMED'),  # 重重火土, 辰酉不合化日主辰根, 酉伤官顺泄
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

# 母多灭子两级锚点(24例逐读DTS原文裁定): CONFIRMED=食伤财官三端真有力通道全断真灭;
# CANDIDATE=水方局孤泄被克漂没为病(待病药作用层分有药无药, 不反转方向);
# 反例=官杀当令化杀/官印相生任官/食伤当令吐秀/财破印/水冲奔从印/印局被冲, 皆不得误判母灭
MUMIE = [
    # —— CONFIRMED 真灭/无依坏命 8 ——
    ('戊辰壬戌辛未己丑', True, 'CONFIRMED'),  # 满局印绶土重金埋、壬水用神伤尽、木被冲, 克妻无子
    ('辛丑乙未庚辰丁丑', True, 'CONFIRMED'),  # 土重丁火熄、辛金肆逞冲去木火微根、财官虽有若无, 削发为僧
    ('丙辰辛丑庚辰丙子', True, 'CONFIRMED'),  # 重重湿土、丙合辛化水时丙无根、寒湿无生发, 破尽为僧
    ('己丑戊辰辛亥戊戌', True, 'CONFIRMED'),  # 重重厚土埋藏脆嫩之金、亥水孤泄被围克绝、无木疏土, 乙丑运夭
    ('辛丑辛丑癸酉癸丑', True, 'CONFIRMED'),  # 重重湿土叠叠寒金、癸水浊而且冻气浊神枯(金多水浊), 戊戌运夭
    ('癸卯甲寅丁卯甲辰', True, 'CONFIRMED'),  # 寅卯辰会木、癸归甲、木多火熄(俗论身强被"不知"否定), 丁未丙午助身方发
    ('戊戌丙辰辛丑戊戌', True, 'CONFIRMED'),  # 原文直述四柱皆土、丙火元神泄尽、土重金坦、母多灭子
    ('丙戌戊戌辛丑戊戌', True, 'CONFIRMED'),  # 三戌一丑四库土重、土重金埋pair, 水木运犯母落职
    # —— CANDIDATE 水方局孤泄为病(病药层细分, 不反转) 2 ——
    ('丙子己亥乙丑壬午', True, 'CANDIDATE'),  # 水泛火绝为病, 然己土透通根午止水卫火、有病得药, 甲第青云
    ('己亥丙子乙丑壬午', True, 'CANDIDATE'),  # 亥子丑水局、午孤丙透被壬克、己土虚, 虚湿骑马亦忧, 丙克尽而亡
    # —— 反例(非母灭) 16 ——
    ('壬戌壬子甲子戊辰', False, None),  # 戊土砥柱透干通根戌制水、印旺用财调候, 财破印
    ('癸亥癸亥丁卯癸卯', False, None),  # 癸杀透干通根亥、卯印化=杀印相生, 非纯印灭子
    ('辛未乙未庚辰丁亥', False, None),  # 丁火司令元神发露为用、财官通根有气、亥水润, 中乡榜迁司马
    ('戊辰庚申甲子甲子', False, None),  # 申月杀令木凋金锐、支全水局化肃杀生化有情, 科甲封疆(杀印相生)
    ('己巳癸酉壬辰甲辰', False, None),  # 秋水通源印秉令、官杀制化合宜、甲木制杀吐秀纯粹, 诰封二品
    ('丁未庚戌庚辰丙子', False, None),  # 丁火源头生土土生金、两藏财库、身旺用官, 名利双辉
    ('壬辰甲辰庚午丙戌', False, None),  # 春金杀旺、用神在土(印化杀)、土金运发财, 印为用神非埋
    ('庚辰丁亥庚辰丁丑', False, None),  # 亥月水(食伤)当令、丁火并透辰亥藏甲乙、足以用火(官), 仕至郡守
    ('乙未戊子庚辰丁丑', False, None),  # 子月水(食伤)当令、未土破子、木火得余气、用木生火, 财官格
    ('壬子辛亥乙亥丙子', False, None),  # 昆仑之水冲奔、地支本气全亥子清纯, 顺其流纳其气(从印/润下), 非灭
    ('癸酉乙卯丁未辛亥', False, None),  # 亥卯未木局逢卯酉紧邻冲、破其印局、乙辛战财杀肆逞, 病在财杀攻身
    ('己亥丙寅丁亥庚戌', False, None),  # 丁生寅月木当权火逢相旺、亥官合寅被庚隔, 木火相旺身不弱
    ('丙子己亥乙亥丙子', False, None),  # 亥月两丙透寒木向阳、印水不透干不克食伤、清纯粹, 只财官不足
    ('壬辰己酉甲申甲子', False, None),  # 申月杀令合官留杀、辰财酉官化金党杀、子水局化杀(杀印相生), 病在财党杀
    ('甲子丙子甲申己巳', False, None),  # 虚极不受水生/化神假(交作用层), 巳申合水丙虚, 结构层不判母灭
    ('丁未壬子庚戌丙戌', False, None),  # 仲冬水旺、支重燥土(未戌)去湿、丁壬合护官, 仕至州牧(燥土非埋金)
]
for c, exp_mm, exp_st in MUMIE:
    pp = gp(c); ff = l0b(pp); tth = build_tian_he(pp, ff); wwp = build_wuxing_power(pp, ff, tth)
    ssp = build_special_patterns(pp, ff, wwp, tth)
    got_mm = bool(ssp.get('mu_mie')); got_st = ssp.get('mu_mie_state')
    ok = (got_mm == exp_mm) and (exp_st is None or got_st == exp_st)
    if not ok: fails += 1
    print('PASS' if ok else 'FAIL', c, '期望母灭=' + str(exp_mm) + '/' + str(exp_st)
          + ' 得=' + str(got_mm) + '/' + str(got_st))

print()
# 两气成象锚点(天干地支本气仅两行、各成势、相生成象; 顺食伤秀神; 不与从/专旺冲突)
LIANGQI = [
    ('甲午丁卯甲午丁卯', '火'),  # 木火通明, 取丁火伤官秀气为用
    ('丙午戊戌丙午戊戌', '土'),  # 火土成象, 顺土(食伤)泄秀
    ('戊戌辛酉戊戌辛酉', '金'),  # 土金成象, 取辛金伤官为用
    ('癸亥甲寅癸亥甲寅', '木'),  # 水木清华, 水生木顺木(食伤)秀神
]
for c, exp_xiu in LIANGQI:
    pp = gp(c); ff = l0b(pp); tth = build_tian_he(pp, ff); wwp = build_wuxing_power(pp, ff, tth)
    ssp = build_special_patterns(pp, ff, wwp, tth)
    lq = ssp.get('liangqi')
    ok = (bool(lq) and lq.get('xiu') == exp_xiu and not ssp.get('zhuanwang') and not ssp.get('cong_type'))
    if not ok: fails += 1
    print('PASS' if ok else 'FAIL', c, '期望两气成象秀神=' + exp_xiu
          + ' 得=' + str(None if not lq else (lq.get('name'), lq.get('xiu'))))

print()
print('TOTAL', len(CASES) + len(MUMIE) + len(LIANGQI), 'FAILS', fails)
sys.exit(1 if fails else 0)
