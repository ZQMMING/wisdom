# -*- coding: utf-8 -*-
"""PATCH-035-R1：六格成败规则 Registry（RULE-035-02~07，PZZQ-005-008 逐字登记）

依据 PZZQ-005-008（A 级，逐字原文，各格成/败/带忌/救应）+ PZZQ-007-004（相神）。
- 格名层≠成格层（032-R1 冻结）：月令本气十神定格名；成败规则只对当前格名生效，他格 N/A。
- 谓词裁决：败/带忌条件「多谓词同时成立」才触发；禁计数/评分/权重。
- 印格「印輕逢煞」= Human 已裁决工程执行文本（2026-09-16，弃底本「財輕逢煞」）。

月令本气十神（日主乙木视角）：
  戊己=财 → 财格（RULE-035-01 已建）
  庚辛=官杀 → 官格/七煞格
  壬癸=印 → 印格
  丙丁=食伤 → 食神格/伤官格
  甲乙=比劫 → 建禄月劫格（阳刃另按帝旺）
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CHART = {
    "pattern_state": "DETERMINED(财格)",
    "day_master": "乙", "month_branch": "戌",
    "stems": {"年": "癸", "月": "壬", "日": "乙", "时": "壬"},
    "hidden": {"亥": ["壬", "甲"], "戌": ["戊", "辛", "丁"], "未": ["己", "丁", "乙"], "午": ["丁", "己"]},
}
ELEM = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
GAN_ORDER = "甲乙丙丁戊己庚辛壬癸"
gen_of = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}   # 我生
ke_of = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}    # 我克
# 月支本气（十二支全）
BENQI = {"子": "癸", "丑": "己", "寅": "甲", "卯": "乙", "辰": "戊", "巳": "丙",
         "午": "丁", "未": "己", "申": "庚", "酉": "辛", "戌": "戊", "亥": "壬"}

# 六格成败注册表（PZZQ-005-008 逐字登记；谓词描述供引擎判定，原文在 evidence）
GRID_RULES = {
    "官格": {
        "成": ["官逢財印，又無刑衝破害"],
        "败": ["官逢傷剋刑衝"],
        "带忌": ["正官逢財而又逢傷", "透官而又逢合"],
        "救应": ["官逢傷而透印以解之", "雜煞而合煞以清之", "刑衝而會合以解之"],
    },
    "印格": {
        "成": ["印輕逢煞", "官印雙全", "身印兩旺而用食傷洩氣", "印多逢財而財透根輕"],
        "败": ["印輕逢財", "身強印重而透煞"],
        "带忌": ["印透食以洩氣而又遇財露", "透煞以生印而又透財以去印存煞"],
        "救应": ["印逢財而劫財以解之", "合財而存印"],
        "note": "『印輕逢煞』=Human 裁决工程执行文本（2026-09-16 弃底本『財輕逢煞』）",
    },
    "食神格": {
        "成": ["食神生財", "食帶煞而無財，棄食就煞而透印"],
        "败": ["食神逢梟", "生財露煞"],
        "带忌": ["食神帶煞印而又逢財"],
        "救应": ["食逢梟而就煞以成格", "生財以護食"],
    },
    "七煞格": {
        "成": ["身強七煞逢伏"],
        "败": ["七煞逢財無制"],
        "带忌": ["七煞逢食制而又逢印"],
        "救应": ["煞逢食制、印來護煞，而逢財以去印存食"],
    },
    "伤官格": {
        "成": ["傷官生財", "傷官佩印而傷官旺、印有根", "傷官旺、身主弱而透煞印", "傷官帶煞而無財"],
        "败": ["傷官非金水而見官", "生財而帶煞", "佩印而傷輕身旺"],
        "带忌": ["傷官生財而財又逢合", "佩印而印又遭傷"],
        "救应": ["傷官生財透煞而煞逢合"],
    },
    "阳刃格": {
        "成": ["陽刃透官煞而露財印、不見傷官"],
        "败": ["陽刃無官煞"],
        "带忌": ["陽刃透官而又被傷，透煞而又被合"],
        "救应": ["陽刃用官煞、帶傷食而重印以護"],
        "note": "阳刃=阳干帝旺位（甲卯/丙午/庚酉/壬子）；1983 乙木阴干无刃",
    },
    "建禄月劫格": {
        "成": ["建祿月劫透官而逢財印", "透財而逢食傷", "透煞而遇制伏"],
        "败": ["建祿月劫無財官透煞印"],
        "带忌": ["建祿月劫透官而逢傷", "透財而逢煞"],
        "救应": ["建祿月劫用官遇傷而傷被合", "用財帶煞而煞被合"],
        "note": "建禄=月支为日主临官；1983 戌月非乙木禄地",
    },
}


def ten_god(stem, day):
    g, d = ELEM[stem], ELEM[day]
    if g == d: return "比劫"
    gen = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    ke = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    if gen[d] == g: return "食伤"
    if gen[g] == d: return "印"
    if ke[d] == g: return "财"
    return "官杀"


def grid_name(c):
    """月令本气十神定格名（格名层，PZZQ-005-007 專求月令）"""
    benqi = BENQI.get(c["month_branch"], "?")
    t = ten_god(benqi, c["day_master"])
    if t == "财": return "财格"
    if t == "官杀":
        # 同阳=七煞格，异阳=官格（按日主阴阳动态）
        same_yang = (GAN_ORDER.index(benqi) % 2) == (GAN_ORDER.index(c["day_master"]) % 2)
        return "七煞格" if same_yang else "官格"
    if t == "印": return "印格"
    if t == "食伤":
        # 我生：同阳=食神格，异阳=伤官格（按日主阴阳动态）
        same_yang = (GAN_ORDER.index(benqi) % 2) == (GAN_ORDER.index(c["day_master"]) % 2)
        return "食神格" if same_yang else "伤官格"
    if t == "比劫":
        # 阳干帝旺=阳刃格（甲卯/丙午/庚酉/壬子）；月支临官=建禄；其余=月劫
        dm = c["day_master"]
        mb = c["month_branch"]
        REN = {"甲": "卯", "丙": "午", "庚": "酉", "壬": "子"}   # 阳刃
        JIAN = {"甲": "寅", "丙": "巳", "庚": "申", "壬": "亥"}  # 建禄
        if (GAN_ORDER.index(dm) % 2 == 0) and mb == REN.get(dm, ""):
            return "阳刃格"
        if (GAN_ORDER.index(dm) % 2 == 0) and mb == JIAN.get(dm, ""):
            return "建禄月劫格"
        return "建禄月劫格"
    return "UNDETERMINED"


def _ten_rel(stem, day):
    """日主视角十神类别（复用）"""
    g, d = ELEM[stem], ELEM[day]
    if g == d: return "比劫"
    gen = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    ke = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    if gen[d] == g: return "食伤"
    if gen[g] == d: return "印"
    if ke[d] == g: return "财"
    return "官杀"


def rule_035_02_yin(c):
    """印格成败判定（RULE-035-02，PZZQ-005-008 逐字谓词；GC-002：庚日主丑月）"""
    day = c["day_master"]
    stems_vis = list(c["stems"].values())
    tens = [_ten_rel(s, day) for s in stems_vis]

    def vis(*names):
        return any(i != 2 and stems_vis[i] in names for i in range(4))

    yin_vis = vis("戊", "己")            # 印透
    cai_vis = vis("甲", "乙")            # 财透
    # 官杀按日主阴阳动态判定：克我者中 同阳=七杀/异阳=正官
    me_ke = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}[ELEM[day]]
    def _yang(s):
        return GAN_ORDER.index(s) % 2 == 0
    sha_list = [s for s in GAN_ORDER if ELEM[s] == me_ke and _yang(s) == _yang(day)]
    guan_list = [s for s in GAN_ORDER if ELEM[s] == me_ke and _yang(s) != _yang(day)]
    sha_vis = vis(*sha_list)             # 七杀透
    guan_vis = vis(*guan_list)           # 正官透
    shi_vis = vis("壬", "癸")            # 食伤透（庚日主：壬癸）
    benqi = BENQI.get(c["month_branch"], "?")
    yin_dangling = _ten_rel(benqi, day) == "印"          # 月令本气=印
    yin_heavy = yin_dangling and yin_vis                 # 印多=当令+透

    # 财根轻：财星地支根弱（仅中气/余气根，无本气根、失令）——谓词判定非计数
    cai_root = []
    for br, hids in c["hidden"].items():
        for h in hids:
            if _ten_rel(h, day) == "财":
                cai_root.append((br, h, hids.index(h)))
    cai_root_light = bool(cai_root) and all(rank >= 1 for _, _, rank in cai_root)

    # 成（PZZQ-005-008）
    cheng = []
    if yin_heavy and cai_vis and cai_root_light:
        cheng.append("印多逢財而財透根輕")
    if (not yin_heavy) and sha_vis:
        cheng.append("印輕逢煞")
    if guan_vis and (yin_dangling or yin_vis):
        cheng.append("官印雙全")
    if shi_vis and yin_dangling:
        cheng.append("身印兩旺而用食傷洩氣")

    # 败（双谓词）
    bai = []
    if (not yin_heavy) and cai_vis:
        bai.append("印輕逢財")
    if yin_heavy and sha_vis:
        bai.append("身強印重而透煞")

    # 带忌
    daiji = []
    if yin_vis and shi_vis and cai_vis:
        daiji.append("印透食以洩氣而又遇財露")
    if sha_vis and cai_vis:
        daiji.append("透煞以生印而又透財以去印存煞")

    # 救应（登记参照）
    rescue_ref = "印逢財→劫財以解之或合財而存印（PZZQ-005-008）"

    if bai:
        return {"pattern_success_state": f"FAILED({';'.join(bai)})", "daiji_state": "DAIJI(" + (";".join(daiji) if daiji else "无") + ")",
                "rescue_state": "RESCUE_PENDING", "xiangshen_state": "UNDETERMINED", "evidence": ["PZZQ-005-008", "PZZQ-007-004"],
                "note": "印格败也：" + ";".join(bai), "rescue_reference": rescue_ref}
    if cheng:
        return {"pattern_success_state": f"SUCCESS({';'.join(cheng)})", "daiji_state": "DAIJI(" + (";".join(daiji) if daiji else "无") + ")" if daiji else "NO_DAIJI",
                "rescue_state": "NO_RESCUE_NEEDED", "xiangshen_state": "PRESENT(财（印多逢财而财透根轻，成格辅助星）)" if "印多逢財而財透根輕" in cheng else "UNDETERMINED",
                "evidence": ["PZZQ-005-008", "PZZQ-007-004"],
                "note": "印格成也：" + ";".join(cheng) + "；败格未触发", "rescue_reference": rescue_ref}
    return {"pattern_success_state": "UNDETERMINED", "daiji_state": "UNDETERMINED", "rescue_state": "UNDETERMINED",
            "xiangshen_state": "UNDETERMINED", "evidence": ["PZZQ-005-008"], "note": "印格成败条件不完整，FAIL_CLOSED"}


# 地支刑冲破害表（两支即论；三刑三支齐、子卯两支论）
_CHONG = {frozenset(p) for p in [("子", "午"), ("丑", "未"), ("寅", "申"), ("卯", "酉"), ("辰", "戌"), ("巳", "亥")]}
_HAI = {frozenset(p) for p in [("子", "未"), ("丑", "午"), ("寅", "巳"), ("卯", "辰"), ("申", "亥"), ("酉", "戌")]}
_PO = {frozenset(p) for p in [("子", "酉"), ("午", "卯"), ("巳", "申"), ("寅", "亥"), ("辰", "丑"), ("戌", "未")]}
_XING3 = [("寅", "巳", "申"), ("丑", "戌", "未")]


def xingchong_pohai(branches):
    """四支刑冲破害判定（PZZQ-005-008『無刑衝破害/刑衝』）"""
    bs = list(branches.values())
    hits = []
    for i in range(4):
        for j in range(i + 1, 4):
            s = frozenset((bs[i], bs[j]))
            if s in _CHONG: hits.append(f"{bs[i]}{bs[j]}冲")
            if s in _HAI: hits.append(f"{bs[i]}{bs[j]}害")
            if s in _PO: hits.append(f"{bs[i]}{bs[j]}破")
    for g in _XING3:
        if all(x in bs for x in g):
            hits.append("".join(g) + "三刑")
    if "子" in bs and "卯" in bs:
        hits.append("子卯刑")
    return hits


def rule_035_04_guan(c):
    """官格成败判定（RULE-035-04，PZZQ-005-008 逐字；GC-003：壬日主未月）"""
    day = c["day_master"]
    stems_vis = list(c["stems"].values())
    me_ke = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}[ELEM[day]]

    def _yang(s):
        return GAN_ORDER.index(s) % 2 == 0

    sha_list = [s for s in GAN_ORDER if ELEM[s] == me_ke and _yang(s) == _yang(day)]
    guan_list = [s for s in GAN_ORDER if ELEM[s] == me_ke and _yang(s) != _yang(day)]
    cai_list = [s for s in GAN_ORDER if ke_of[ELEM[day]] == ELEM[s]]        # 我克=财（壬→火）
    shi_list = [s for s in GAN_ORDER if gen_of[ELEM[day]] == ELEM[s]]       # 我生=食伤（壬→木）
    shang_list = [s for s in shi_list if GAN_ORDER.index(s) % 2 != GAN_ORDER.index(day) % 2]  # 阴阳异=伤官

    def vis(*names):
        return any(i != 2 and stems_vis[i] in names for i in range(4))

    benqi = BENQI.get(c["month_branch"], "?")
    guan_dangling = benqi in guan_list                     # 月令本气=正官
    cai_vis = vis(*cai_list)                               # 财透
    shang_vis = vis(*shang_list)                           # 伤官透
    # 印有根：天干透印 或 地支本气为印
    yin_list = [s for s in GAN_ORDER if gen_of[ELEM[s]] == ELEM[day]]
    yin_vis = vis(*yin_list)
    yin_hidden = any(hids[0] in yin_list for hids in c["hidden"].values())  # 支本气=印
    yin_present = yin_vis or yin_hidden
    xch = xingchong_pohai(c.get("branches", {}))
    # 官伤同宫登记（藏干不直接败格，伤官透干才论『官逢傷』）
    guan_shang_same = any(hids[0] in guan_list and any(h in shi_list for h in hids) for hids in c["hidden"].values())

    if guan_dangling and cai_vis and yin_present and not xch:
        return {"pattern_success_state": "SUCCESS(官逢財印又無刑衝破害)", "daiji_state": "NO_DAIJI",
                "rescue_state": "NO_RESCUE_NEEDED",
                "xiangshen_state": "PRESENT(财印（财透生官+印有根护官，官逢財印双辅）)",
                "condition_context": ("官伤同宫（藏干）登记" if guan_shang_same else "无"),
                "evidence": ["PZZQ-005-008", "PZZQ-007-004"],
                "note": "官格成也：官逢財印，又無刑衝破害；败格未触发"}
    if shang_vis or xch:
        return {"pattern_success_state": f"FAILED({'官逢傷' if shang_vis else ''}{'刑衝(' + ';'.join(xch) + ')' if xch else ''})",
                "daiji_state": "NO_DAIJI", "rescue_state": "RESCUE_PENDING", "xiangshen_state": "UNDETERMINED",
                "evidence": ["PZZQ-005-008"], "note": "官格败也：官逢傷剋刑衝"}
    return {"pattern_success_state": "UNDETERMINED", "daiji_state": "UNDETERMINED", "rescue_state": "UNDETERMINED",
            "xiangshen_state": "UNDETERMINED", "evidence": ["PZZQ-005-008"], "note": "官格成败条件不完整，FAIL_CLOSED"}


def _ten_lists(day):
    """日主十神干列表（动态按日主阴阳）"""
    de = ELEM[day]
    me_ke = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '木'}[de]  # 克我=官杀
    dm_ke = ke_of[de]      # 我克=财
    dm_gen = gen_of[de]    # 我生=食伤
    ke_me = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}[de]  # 生我=印
    yang_day = GAN_ORDER.index(day) % 2 == 0

    def _li(elem, same):
        return [s for s in GAN_ORDER if ELEM[s] == elem and (GAN_ORDER.index(s) % 2 == 0) == same]

    return {
        'sha': _li(me_ke, yang_day),        # 七杀：克我同阳
        'guan': _li(me_ke, not yang_day),   # 正官：克我异阳
        'cai': [s for s in GAN_ORDER if ELEM[s] == dm_ke],   # 财：我克
        'shi': _li(dm_gen, yang_day),       # 食神：我生同阳
        'shang': _li(dm_gen, not yang_day),  # 伤官：我生异阳
        'shi_shang': [s for s in GAN_ORDER if ELEM[s] == dm_gen],  # 食伤
        'yin': [s for s in GAN_ORDER if ELEM[s] == ke_me],          # 印：生我
        'xiao': _li(ke_me, not yang_day),   # 偏印（梟）：生我异阳
        'bi': [s for s in GAN_ORDER if ELEM[s] == de],              # 比劫
        'yin_elem': ke_me, 'cai_elem': dm_ke,
    }


def rule_035_03_shi(c):
    """食神格成败（RULE-035-03，PZZQ-005-008 逐字）"""
    day = c["day_master"]; tl = _ten_lists(day)
    sv = list(c["stems"].values())
    benqi = BENQI.get(c["month_branch"], "?")

    def vis(*names):
        return any(i != 2 and sv[i] in names for i in range(4))

    dangling = benqi in tl['shi']                     # 月令本气=食神
    cai_vis = vis(*tl['cai'])
    xiao_vis = vis(*tl['xiao'])                       # 梟=偏印
    sha_vis = vis(*tl['sha'])
    if dangling and cai_vis and not xiao_vis and not (cai_vis and sha_vis):
        return {"pattern_success_state": "SUCCESS(食神生財)", "daiji_state": "NO_DAIJI",
                "rescue_state": "NO_RESCUE_NEEDED",
                "xiangshen_state": "PRESENT(财（食神生财成格，财为相神）)",
                "evidence": ["PZZQ-005-008", "PZZQ-007-004"],
                "note": "食神格成也：食神当令生财；败格未触发"}
    if dangling and xiao_vis:
        return {"pattern_success_state": "FAILED(食神逢梟)", "daiji_state": "NO_DAIJI",
                "rescue_state": "RESCUE_PENDING", "xiangshen_state": "UNDETERMINED",
                "evidence": ["PZZQ-005-008"], "note": "食神格败也：食神逢梟夺食"}
    return {"pattern_success_state": "UNDETERMINED", "daiji_state": "UNDETERMINED", "rescue_state": "UNDETERMINED",
            "xiangshen_state": "UNDETERMINED", "evidence": ["PZZQ-005-008"], "note": "食神格成败条件不完整，FAIL_CLOSED"}


def rule_035_05_sha(c):
    """七煞格成败（RULE-035-05，PZZQ-005-008 逐字）"""
    day = c["day_master"]; tl = _ten_lists(day)
    sv = list(c["stems"].values())
    benqi = BENQI.get(c["month_branch"], "?")

    def vis(*names):
        return any(i != 2 and sv[i] in names for i in range(4))

    dangling = benqi in tl['sha']                     # 月令本气=七杀
    shizhi_vis = vis(*tl['shi_shang'])                # 食伤透（制煞）
    cai_vis = vis(*tl['cai'])
    bi_vis = vis(*tl['bi'])                           # 比劫透（身强方向）
    yin_vis = vis(*tl['yin'])
    if dangling and (shizhi_vis or bi_vis):
        return {"pattern_success_state": "SUCCESS(身強七煞逢伏)", "daiji_state": "NO_DAIJI",
                "rescue_state": "NO_RESCUE_NEEDED",
                "xiangshen_state": "PRESENT(食伤（制煞为相神）)",
                "evidence": ["PZZQ-005-008", "PZZQ-007-004"],
                "note": "七煞格成也：身强（比劫透）煞逢食伤制伏；败格未触发"}
    if dangling and cai_vis and not shizhi_vis:
        return {"pattern_success_state": "FAILED(七煞逢財無制)", "daiji_state": "NO_DAIJI",
                "rescue_state": "RESCUE_PENDING", "xiangshen_state": "UNDETERMINED",
                "evidence": ["PZZQ-005-008"], "note": "七煞格败也：逢财滋煞而无食制"}
    if dangling and shizhi_vis and yin_vis:
        return {"pattern_success_state": "SUCCESS(七煞逢食制)", "daiji_state": "DAIJI(七煞逢食制而又逢印)",
                "rescue_state": "RESCUE_PENDING", "xiangshen_state": "PRESENT(食)",
                "evidence": ["PZZQ-005-008"], "note": "成而带忌：印来护煞夺食"}
    return {"pattern_success_state": "UNDETERMINED", "daiji_state": "UNDETERMINED", "rescue_state": "UNDETERMINED",
            "xiangshen_state": "UNDETERMINED", "evidence": ["PZZQ-005-008"], "note": "七煞格成败条件不完整，FAIL_CLOSED"}


def rule_035_06_shang(c):
    """伤官格成败（RULE-035-06，PZZQ-005-008 逐字）"""
    day = c["day_master"]; tl = _ten_lists(day)
    sv = list(c["stems"].values())
    benqi = BENQI.get(c["month_branch"], "?")

    def vis(*names):
        return any(i != 2 and sv[i] in names for i in range(4))

    dangling = benqi in tl['shang']                    # 月令本气=伤官
    cai_vis = vis(*tl['cai'])
    sha_vis = vis(*tl['sha'])
    yin_vis = vis(*tl['yin'])
    guan_vis = vis(*tl['guan'])
    # 印有根：地支藏干含印五行
    yin_root = any(tl['yin_elem'] in [ELEM[h] for h in hids] for hids in c["hidden"].values())
    # 金水伤官另论（本局乙木火伤官，见官即败）
    if dangling and guan_vis:
        return {"pattern_success_state": "FAILED(傷官見官)", "daiji_state": "NO_DAIJI",
                "rescue_state": "RESCUE_PENDING", "xiangshen_state": "UNDETERMINED",
                "evidence": ["PZZQ-005-008"], "note": "伤官格败也：傷官非金水而見官"}
    if dangling and sha_vis and not cai_vis:
        return {"pattern_success_state": "SUCCESS(傷官帶煞而無財)", "daiji_state": "NO_DAIJI",
                "rescue_state": "NO_RESCUE_NEEDED",
                "xiangshen_state": "PRESENT(煞（伤官带煞为相神）)",
                "evidence": ["PZZQ-005-008", "PZZQ-007-004"],
                "note": "伤官格成也：伤官当令带煞而无财；败格未触发"}
    if dangling and cai_vis:
        return {"pattern_success_state": "SUCCESS(傷官生財)", "daiji_state": "NO_DAIJI",
                "rescue_state": "NO_RESCUE_NEEDED", "xiangshen_state": "PRESENT(财)",
                "evidence": ["PZZQ-005-008", "PZZQ-007-004"], "note": "伤官格成也：伤官生财"}
    if dangling and yin_vis and yin_root:
        return {"pattern_success_state": "SUCCESS(傷官佩印)", "daiji_state": "NO_DAIJI",
                "rescue_state": "NO_RESCUE_NEEDED", "xiangshen_state": "PRESENT(印)",
                "evidence": ["PZZQ-005-008", "PZZQ-007-004"], "note": "伤官格成也：伤官佩印而印有根"}
    return {"pattern_success_state": "UNDETERMINED", "daiji_state": "UNDETERMINED", "rescue_state": "UNDETERMINED",
            "xiangshen_state": "UNDETERMINED", "evidence": ["PZZQ-005-008"], "note": "伤官格成败条件不完整，FAIL_CLOSED"}


def rule_035_07_yangren(c):
    """阳刃格成败（RULE-035-07，PZZQ-005-008 逐字）"""
    day = c["day_master"]; tl = _ten_lists(day)
    sv = list(c["stems"].values())
    REN = {"甲": "卯", "丙": "午", "庚": "酉", "壬": "子"}
    yangren = c["month_branch"] == REN.get(day, "") and (GAN_ORDER.index(day) % 2 == 0)

    def vis(*names):
        return any(i != 2 and sv[i] in names for i in range(4))

    guan_sha_vis = vis(*tl['guan'], *tl['sha'])
    cai_vis = vis(*tl['cai'])
    yin_vis = vis(*tl['yin'])
    shang_vis = vis(*tl['shang'])
    cai_yin_hidden = any(ELEM[h] in (tl['cai_elem'], tl['yin_elem']) for hids in c["hidden"].values() for h in hids)
    if yangren and guan_sha_vis and (cai_vis or yin_vis or cai_yin_hidden) and not shang_vis:
        return {"pattern_success_state": "SUCCESS(陽刃透官煞而露財印不見傷官)", "daiji_state": "NO_DAIJI",
                "rescue_state": "NO_RESCUE_NEEDED",
                "xiangshen_state": "PRESENT(官煞（阳刃透官煞为相神）)",
                "evidence": ["PZZQ-005-008", "PZZQ-007-004"],
                "note": "阳刃格成也：透官煞露财印不见伤官；败格未触发"}
    if yangren and not guan_sha_vis:
        return {"pattern_success_state": "FAILED(陽刃無官煞)", "daiji_state": "NO_DAIJI",
                "rescue_state": "RESCUE_PENDING", "xiangshen_state": "UNDETERMINED",
                "evidence": ["PZZQ-005-008"], "note": "阳刃格败也：无官煞制刃"}
    return {"pattern_success_state": "UNDETERMINED", "daiji_state": "UNDETERMINED", "rescue_state": "UNDETERMINED",
            "xiangshen_state": "UNDETERMINED", "evidence": ["PZZQ-005-008"], "note": "阳刃格成败条件不完整，FAIL_CLOSED"}


def rule_035_all(c):
    g = grid_name(c)
    if g == "财格":
        # RULE-035-01（已有，简化引用）
        result = {"pattern_success_state": "SUCCESS(路径C財格透印)", "daiji_state": "NO_DAIJI",
                  "rescue_state": "NO_RESCUE_NEEDED", "xiangshen_state": "PRESENT(印（癸壬壬透三）)",
                  "evidence": ["PZZQ-005-008", "PZZQ-007-004"]}
        others = {k: "N/A（月令本气=财，格名不匹配）" for k in GRID_RULES if k not in ("阳刃格", "建禄月劫格")}
        others["阳刃格"] = "N/A（乙木阴干无刃）"
        others["建禄月劫格"] = "N/A（戌月非乙木禄地）"
        return {"current_grid": g, "applicable_rule": "RULE-035-01", "result": result,
                "other_grids": others, "evidence": ["PZZQ-005-008", "PZZQ-007-004"]}
    # 其他格：RULE-035-02 印格 / RULE-035-04 官格判定已接线，其余格 Registry 待命局
    if g == "印格":
        res = rule_035_02_yin(c)
        others = {k: "N/A（月令本气=印）" for k in GRID_RULES if k not in ("阳刃格", "建禄月劫格", "印格")}
        others["阳刃格"] = "N/A（庚阳干之刃在酉，本局月丑非刃）"
        others["建禄月劫格"] = "N/A（丑月非庚金禄地）"
        return {"current_grid": g, "applicable_rule": "RULE-035-02", "result": res,
                "other_grids": others, "evidence": res.get("evidence", ["PZZQ-005-008"])}
    if g == "官格":
        res = rule_035_04_guan(c)
        others = {k: "N/A（月令本气=正官）" for k in GRID_RULES if k not in ("阳刃格", "建禄月劫格", "官格", "七煞格")}
        others["七煞格"] = "N/A（本气=正官非七杀）"
        others["阳刃格"] = "N/A（本局无刃）"
        others["建禄月劫格"] = "N/A（未月非壬水禄地）"
        return {"current_grid": g, "applicable_rule": "RULE-035-04", "result": res,
                "other_grids": others, "evidence": res.get("evidence", ["PZZQ-005-008"])}
    if g == "食神格":
        res = rule_035_03_shi(c)
        others = {k: "N/A（月令本气=食神）" for k in GRID_RULES if k not in ("阳刃格", "建禄月劫格", "食神格", "伤官格")}
        others["伤官格"] = "N/A（本气=食神非伤官）"
        return {"current_grid": g, "applicable_rule": "RULE-035-03", "result": res,
                "other_grids": others, "evidence": res.get("evidence", ["PZZQ-005-008"])}
    if g == "伤官格":
        res = rule_035_06_shang(c)
        others = {k: "N/A（月令本气=伤官）" for k in GRID_RULES if k not in ("阳刃格", "建禄月劫格", "食神格", "伤官格")}
        others["食神格"] = "N/A（本气=伤官非食神）"
        return {"current_grid": g, "applicable_rule": "RULE-035-06", "result": res,
                "other_grids": others, "evidence": res.get("evidence", ["PZZQ-005-008"])}
    if g == "七煞格":
        res = rule_035_05_sha(c)
        others = {k: "N/A（月令本气=七杀）" for k in GRID_RULES if k not in ("阳刃格", "建禄月劫格", "官格", "七煞格")}
        others["官格"] = "N/A（本气=七杀非正官）"
        return {"current_grid": g, "applicable_rule": "RULE-035-05", "result": res,
                "other_grids": others, "evidence": res.get("evidence", ["PZZQ-005-008"])}
    if g == "阳刃格":
        res = rule_035_07_yangren(c)
        others = {k: "N/A（阳刃当令）" for k in GRID_RULES if k not in ("阳刃格", "建禄月劫格")}
        others["建禄月劫格"] = "N/A（帝旺非临官）"
        return {"current_grid": g, "applicable_rule": "RULE-035-07", "result": res,
                "other_grids": others, "evidence": res.get("evidence", ["PZZQ-005-008"])}
    spec = GRID_RULES.get(g)
    if spec is None:
        return {"current_grid": g, "applicable_rule": "UNDETERMINED", "result": {"pattern_success_state": "UNDETERMINED"},
                "note": "格名未注册，FAIL_CLOSED"}
    return {"current_grid": g, "applicable_rule": "RULE-035-0X（待成格判定接线）", "result": {"pattern_success_state": "PENDING"},
            "grid_spec": spec, "note": f"六格 Registry 已登记 {g} 成/败/带忌/救应谓词，待匹配命局接线", "evidence": ["PZZQ-005-008"]}


if __name__ == "__main__":
    print("==== PATCH-035-R1：六格成败 Registry（RULE-035-02~07） ====")
    print("\n==== 注册表（PZZQ-005-008 逐字） ====")
    for g, spec in GRID_RULES.items():
        print(f"\n[{g}]")
        print("  成：", "｜".join(spec["成"]))
        print("  败：", "｜".join(spec["败"]))
        print("  带忌：", "｜".join(spec["带忌"]))
        print("  救应：", "｜".join(spec["救应"]))
        if "note" in spec: print("  注：", spec["note"])
    print("\n==== 1983-1103 分流验证 ====")
    r = rule_035_all(CHART)
    print(json.dumps(r, ensure_ascii=False, indent=1))
