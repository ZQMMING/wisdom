"""DTS 基础态势派生（Phase 6 §65 ·《滴天髓》基础字段）。

本轮输出（对应 DTS 规则 001-009，不依赖 strength 旺衰）：
- stem           : 日干（CAND-DTS-001/002 丙/癸 判定「陽之至/陰之至」）
- stem_yinyang   : 日干阴阳（003/004 從氣不從勢/從勢）
- branch_yinyang : 月支阴阳（005/006 動強速達/靜專否泰；口径：月支，月令为纲）
- relation       : "沖"（007/009 沖关系存在时；展开 L0 relations.liu_chong）
- pillar         : 日柱干支（018/019 甲申/戊寅/癸丑/庚寅 判定；= stem_branch_pair）
- tian_status    : 四天干同五行 → "全一氣"（012，DTS-010-004）
- di_status      : 四地支成三会/三合局 → "全三物"（013，DTS-010-006/007 注：寅卯辰、亥卯未）
- stem_position  : 日干阳+日支阳 → "陽乘陽位"；阴+阴 → "陰乘陰位"（014/015，DTS-010-008/010）
- xing_state     : 四柱干支五行覆盖（DTS-011-003/008：五行俱全→"形全"；有缺→"形缺"）
- pattern        : "兩氣合而成象"（DTS-011-001/002 注：天干属一行、地支属一行且两行相生，
  如天干屬木地支屬火；其象屬一，见金水则破——静态盘干支各一行即无第三行）
- zhan_state     : "天戰"/"地戰"（DTS-046-002 注：干頭遇甲乙庚辛→天戰；地支寅申卯酉→地戰；
  并存时天戰优先，口径记录）
- xiang_state    : 君亢/臣過/母旺子孤/子衆母衰（DTS-048-002/049-002/050-002/051-002 注：
  日主行满盘（四支全日主五行）时按财/官/食伤/印行出现数判定，取首命中）
- pattern        : "獨象"/"全象"（DTS-011-005/007 注：一者為獨，曲直炎上之類（日主行≥6/8 专旺）；
  三者為全，有傷官而又有財（8字恰含日主/食伤/财三行且日主行旺））
- cong_state     : "真"/"假"（DTS-040-002/042-002 注：日主孤弱無氣、絕無一毫生扶→真从；
  中有所助及暗生→假从；保守按 8 字生扶行（比劫+印）计数 0-1→真、2-3→假，财官行≥4）
- hua_state      : "真"/"假"（DTS-041-002/043-002 注：日干合干单透一位、不遇印比劫及同类干、
  有辰（龙）、化神得令（月支=合化五行）→真化；合成立但缺真化条件→假化）

注：CAND-DTS-007（生方忌沖動）为 suppress 规则，RuleEngine 只消费 emit，
suppress 语义 V2.22 未定义条款，已记录待审批裁决；本派生只注入其前置字段。
旺衰类字段（source_strength/target_strength/day_master_strength 等）依赖
strength_state 判定（《滴天髓》衰旺篇规则），后续篇章派生接入。
"""

from __future__ import annotations

from typing import Any, Dict

# 干五行
STEM_ELEMENT: Dict[str, str] = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
# 支五行
BRANCH_ELEMENT: Dict[str, str] = {
    "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水", "子": "水", "丑": "土",
}
# 三合局（任两支成局即视为局气，取完整组判定：组内三支齐全）
SANHE: Dict[str, set] = {
    "寅午戌": {"寅", "午", "戌"},
    "申子辰": {"申", "子", "辰"},
    "巳酉丑": {"巳", "酉", "丑"},
    "亥卯未": {"亥", "卯", "未"},
}
# 三会方（DTS-010-007 注「寅卯辰、亥卯未」）
SANHUI: Dict[str, set] = {
    "寅卯辰": {"寅", "卯", "辰"},
    "巳午未": {"巳", "午", "未"},
    "申酉戌": {"申", "酉", "戌"},
    "亥子丑": {"亥", "子", "丑"},
}
# 干阴阳（阳干：甲丙戊庚壬）
STEM_YINYANG: Dict[str, str] = {
    "甲": "陽", "丙": "陽", "戊": "陽", "庚": "陽", "壬": "陽",
    "乙": "陰", "丁": "陰", "己": "陰", "辛": "陰", "癸": "陰",
}
# 支阴阳（阳支：子寅辰午申戌）
BRANCH_YINYANG: Dict[str, str] = {
    "子": "陽", "寅": "陽", "辰": "陽", "午": "陽", "申": "陽", "戌": "陽",
    "丑": "陰", "卯": "陰", "巳": "陰", "未": "陰", "酉": "陰", "亥": "陰",
}


def _has_bureau(branches: list) -> bool:
    """四地支是否成三会/三合局（组内三支齐全）。"""
    bset = set(branches)
    for grp in list(SANHE.values()) + list(SANHUI.values()):
        if grp <= bset:
            return True
    return False


# 五行相生（木→火→土→金→水→木）
_SHENG: Dict[str, str] = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
# 五行相克（木克土、土克水、水克火、火克金、金克木）
_KE: Dict[str, str] = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
# 天干六合（日干→合干）
_HE: Dict[str, str] = {"甲": "己", "己": "甲", "乙": "庚", "庚": "乙", "丙": "辛",
                       "辛": "丙", "丁": "壬", "壬": "丁", "戊": "癸", "癸": "戊"}
# 合化五行（DTS-041-002 注原文推演：丙辛冬月（水）、戊癸夏月（火）、乙庚秋月（金）、
# 丁壬春月（木）、甲己生於四季（土）→ 甲己化土/乙庚化金/丙辛化水/丁壬化木/戊癸化火）
_HUA: Dict[str, str] = {"甲": "土", "己": "土", "乙": "金", "庚": "金", "丙": "水",
                        "辛": "水", "丁": "木", "壬": "木", "戊": "火", "癸": "火"}


def _generates(a: str, b: str) -> bool:
    """a 生 b。"""
    return _SHENG.get(a) == b


def _ke(a: str, b: str) -> bool:
    """a 克 b。"""
    return _KE.get(a) == b


def derive_state(day_stem: str | None = None,
                 month_branch: str | None = None,
                 hidden: Any = None,
                 transparent_stems: Any = None,
                 branches: Any = None,
                 base: Dict[str, Any] | None = None,
                 l0_chart: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """DTS 基础态势派生（§65）：注入 stem/阴阳/冲关系。"""
    out: Dict[str, Any] = {}
    if day_stem:
        out["stem"] = day_stem
        out["stem_yinyang"] = STEM_YINYANG.get(day_stem)
    if month_branch:
        out["branch_yinyang"] = BRANCH_YINYANG.get(month_branch)
    relations = (base or {}).get("relations") or {}
    if relations.get("liu_chong"):
        out["relation"] = "沖"
    if base and base.get("stem_branch_pair"):
        out["pillar"] = base["stem_branch_pair"]
    # 全一氣：四天干同五行（DTS-010-004）
    if base:
        stems = [base.get("year_stem"), base.get("month_stem"), day_stem, base.get("hour_stem")]
        if all(stems) and len({STEM_ELEMENT.get(s) for s in stems}) == 1:
            out["tian_status"] = "全一氣"
    # 全三物：四地支成三会/三合局（DTS-010-006/007）
    if branches and _has_bureau(list(branches)):
        out["di_status"] = "全三物"
    # 陽乘陽位 / 陰乘陰位（DTS-010-008/010；口径：日干坐日支）
    if day_stem and (base or {}).get("day_branch"):
        ds_yy = STEM_YINYANG.get(day_stem)
        db_yy = BRANCH_YINYANG.get((base or {}).get("day_branch"))
        if ds_yy == "陽" and db_yy == "陽":
            out["stem_position"] = "陽乘陽位"
        elif ds_yy == "陰" and db_yy == "陰":
            out["stem_position"] = "陰乘陰位"
    # 形全/形缺：四柱干支五行覆盖（DTS-011-003/008「形全者宜損其有餘，形缺者宜補其不足」）
    if base:
        els = {STEM_ELEMENT.get(s) for s in (base.get("year_stem"), base.get("month_stem"),
                                             day_stem, base.get("hour_stem"))}
        els |= {BRANCH_ELEMENT.get(b) for b in (base.get("year_branch"), base.get("month_branch"),
                                                base.get("day_branch"), base.get("hour_branch"))}
        els.discard(None)
        out["xing_state"] = "形全" if len(els) >= 5 else "形缺"
    # 兩氣合而成象（DTS-011-001/002）：四干全一行、四支全一行、两行相生
    if base and day_stem:
        stems4 = [base.get("year_stem"), base.get("month_stem"), day_stem, base.get("hour_stem")]
        brs4 = [base.get("year_branch"), base.get("month_branch"),
                base.get("day_branch"), base.get("hour_branch")]
        if all(stems4) and all(brs4):
            stem_els = {STEM_ELEMENT.get(s) for s in stems4}
            br_els = {BRANCH_ELEMENT.get(b) for b in brs4}
            if len(stem_els) == 1 and len(br_els) == 1:
                se, be = next(iter(stem_els)), next(iter(br_els))
                if se != be and _generates(se, be):
                    out["pattern"] = "兩氣合而成象"
    # 天戰/地戰（DTS-046-002 注：干頭遇甲乙庚辛→天戰；地支寅申卯酉→地戰）
    if base and day_stem:
        stems4 = [base.get("year_stem"), base.get("month_stem"), day_stem, base.get("hour_stem")]
        brs4 = [base.get("year_branch"), base.get("month_branch"),
                base.get("day_branch"), base.get("hour_branch")]
        if any(s in ("甲", "乙") for s in stems4) and any(s in ("庚", "辛") for s in stems4):
            out["zhan_state"] = "天戰"
        elif "寅" in brs4 and "申" in brs4 or ("卯" in brs4 and "酉" in brs4):
            out["zhan_state"] = "地戰"
    # 君亢/臣過/母旺子孤/子衆母衰（DTS-048-002/049-002/050-002/051-002 注：
    # 「滿盤是木」=日主行过半（8字中≥5）；「內有一二X氣」=该行 1≤count≤2，
    # 按篇序（君象→臣象→母象→子象）取首；印多（≥3）独立判定为子衆母衰）
    if base and day_stem:
        day_el = STEM_ELEMENT.get(day_stem)
        stems4 = [base.get("year_stem"), base.get("month_stem"), day_stem, base.get("hour_stem")]
        brs4 = [base.get("year_branch"), base.get("month_branch"),
                base.get("day_branch"), base.get("hour_branch")]
        if day_el and all(stems4) and all(brs4):
            els8 = [STEM_ELEMENT.get(s) for s in stems4] + [BRANCH_ELEMENT.get(b) for b in brs4]
            from collections import Counter
            cnt = Counter(e for e in els8 if e)
            if cnt.get(day_el, 0) >= 5:  # 日主行满盘（过半）
                sheng_wo = _SHENG.get(day_el)      # 日主所生：食伤
                ke = _KE.get(day_el)               # 日主所克：财
                ke_wo = next((k for k, v in _KE.items() if v == day_el), None)  # 克日主：官
                sheng = next((k for k, v in _SHENG.items() if v == day_el), None)  # 生日主：印
                picks = []
                if ke and 1 <= cnt.get(ke, 0) <= 2:
                    picks.append("君亢")        # 君盛臣衰（财一二）
                if ke_wo and 1 <= cnt.get(ke_wo, 0) <= 2:
                    picks.append("臣過")        # 臣盛君衰（官一二）
                if sheng_wo and 1 <= cnt.get(sheng_wo, 0) <= 2:
                    picks.append("母旺子孤")    # 母旺子孤（食伤一二）
                if picks:
                    out["xiang_state"] = picks[0]
                elif sheng and cnt.get(sheng, 0) >= 3:
                    out["xiang_state"] = "子衆母衰"  # 子衆母衰（印多）
    # 獨象/全象（DTS-011-005/007 注：一者為獨，曲直炎上之類是也；三者為全，有傷官而又有財是也）
    # PENDING_VERIFY 口径（无原文量化，待多源验证/Human 裁决）：
    #   獨象＝8字中日主行 ≥6（"一者為獨"未给量化；传统专旺另需当令/会局/无克，未纳入）
    #   全象＝8字恰含日主/食伤/财三行且日主行 ≥3（"主旺喜財旺"依赖旺衰，暂以计数近似）
    if base and day_stem:
        day_el = STEM_ELEMENT.get(day_stem)
        stems4 = [base.get("year_stem"), base.get("month_stem"), day_stem, base.get("hour_stem")]
        brs4 = [base.get("year_branch"), base.get("month_branch"),
                base.get("day_branch"), base.get("hour_branch")]
        if day_el and all(stems4) and all(brs4):
            els8 = [STEM_ELEMENT.get(s) for s in stems4] + [BRANCH_ELEMENT.get(b) for b in brs4]
            from collections import Counter
            cnt = Counter(e for e in els8 if e)
            if cnt.get(day_el, 0) >= 6:
                out["pattern"] = "獨象"        # 一行专旺（曲直炎上之類）[PENDING_VERIFY]
            else:
                sheng_wo = _SHENG.get(day_el)      # 食伤行
                ke = _KE.get(day_el)               # 财行
                others = {e for e in cnt if e not in (day_el, sheng_wo, ke)}
                if (sheng_wo and cnt.get(sheng_wo, 0) >= 1 and ke
                        and cnt.get(ke, 0) >= 1 and cnt.get(day_el, 0) >= 3 and not others):
                    out["pattern"] = "全象"        # 三者為全：主/食伤/财三行 [PENDING_VERIFY]
    # 真从/假从（DTS-040-002/042-002 注：日主孤弱無氣，天地人元絕無一毫生扶之力，才官強甚→真从；
    # 中有所助及暗生者，從之不真→假从）
    # Human 裁决 2026-09-15：不量化——「才官強甚/中有所助」为结构事实+性质枚举，
    # 架构 = 结构事实 → 状态判定 → 从格规则（CAND-DTS-047/049 消费两枚举）：
    #   cai_guan_state : NOT_STRONG / STRONG（「才官強甚」）
    #   support_state  : NONE / HAS_SUPPORT（「絕無一毫生扶」vs「中有所助及暗生」）
    # PENDING_VERIFY：STRONG 初版按结构事实近似（财官得令∧（透干∨通根））；
    #   组合/制化维度待 strength 前置引擎接入后接管；「暗生」并入 HAS_SUPPORT（藏干生扶）
    if base and day_stem:
        day_el = STEM_ELEMENT.get(day_stem)
        stems4 = [base.get("year_stem"), base.get("month_stem"), day_stem, base.get("hour_stem")]
        brs4 = [base.get("year_branch"), base.get("month_branch"),
                base.get("day_branch"), base.get("hour_branch")]
        if day_el and all(stems4) and all(brs4):
            ke = _KE.get(day_el)                                                 # 财行（日主所克）
            ke_wo = next((k for k, v in _KE.items() if v == day_el), None)       # 官杀行（克日主）
            cai_guan = {e for e in (ke, ke_wo) if e}
            # 结构事实（财官强甚）：
            de_ling = BRANCH_ELEMENT.get(base.get("month_branch")) in cai_guan   # 得令
            tou_gan = any(STEM_ELEMENT.get(s) in cai_guan for s in stems4)       # 透干
            tong_gen = False                                                     # 通根（藏干含财官）
            if isinstance(hidden, dict):
                for _v in hidden.values():
                    if isinstance(_v, (list, tuple)) and any(
                            STEM_ELEMENT.get(_s) in cai_guan for _s in _v):
                        tong_gen = True
            out["cai_guan_state"] = "STRONG" if (de_ling and (tou_gan or tong_gen)) else "NOT_STRONG"
            # 结构事实（生扶有无）：干支（除日干）比劫/印行 + 藏干生扶（含「暗生」）
            sheng = next((k for k, v in _SHENG.items() if v == day_el), None)    # 印行
            has = False
            for i, s in enumerate(stems4):
                if i == 2:      # 跳过日柱位置（日干自身非生扶）
                    continue
                if STEM_ELEMENT.get(s) in (day_el, sheng):
                    has = True
            if not has:
                for b in brs4:
                    if BRANCH_ELEMENT.get(b) in (day_el, sheng):
                        has = True
                        break
            if not has and isinstance(hidden, dict):
                for _v in hidden.values():
                    if isinstance(_v, (list, tuple)) and any(
                            STEM_ELEMENT.get(_s) in (day_el, sheng) for _s in _v):
                        has = True
                        break
            out["support_state"] = "HAS_SUPPORT" if has else "NONE"
    # 身旺/身衰/均衡（strength 最小可用版）
    # Human 裁决 2026-09-16：清浊（CAND-DTS-029/086/087）判定依赖 strength——「清」=用神有力、
    # 「浊」=忌神当权；用神取法以旺衰为锚（身旺喜克泄耗、身弱喜生扶），未定旺衰则清浊无锚点，
    # 整组待命为逻辑必然。最小版输出（PENDING_VERIFY，结构事实近似，不量化）：
    #   day_strength_state : WANG / SHUAI / JUN_HENG（日主旺/衰/均衡）
    #   yong_shen_el       : 喜用五行（WANG→财/官杀/食伤行；SHUAI→印/比劫行；JUN_HENG→空=中和无定喜）
    #   yong_shen_ten_god  : 喜用十神方向（同上对应）
    # 结构事实：得令＝月支∈{日主,印}行；得地＝四支藏干本气∈{日主,印}行；
    #   得势＝其余三干有帮扶（布尔，不计数）；WANG＝得令∧(得地∨得势)；SHUAI＝¬得令∧¬得地∧¬得势
    # PENDING_VERIFY：藏干权重（本气/中气/余气）、组合/制化维度未纳入——待 strength 精度迭代；
    #   JUN_HENG 喜用为空（中和无定喜，调候/通关维度后续）
    if base and day_stem:
        day_el = STEM_ELEMENT.get(day_stem)
        stems4 = [base.get("year_stem"), base.get("month_stem"), day_stem, base.get("hour_stem")]
        brs4 = [base.get("year_branch"), base.get("month_branch"),
                base.get("day_branch"), base.get("hour_branch")]
        if day_el and all(stems4) and all(brs4):
            sheng = next((k for k, v in _SHENG.items() if v == day_el), None)    # 印行（生我）
            bang = {day_el, sheng} if sheng else {day_el}                        # 生扶行（比劫+印）
            de_ling = BRANCH_ELEMENT.get(base.get("month_branch")) in bang       # 得令
            de_di = False                                                        # 得地（藏干本气）
            if isinstance(hidden, dict):
                for _v in hidden.values():
                    if isinstance(_v, (list, tuple)) and _v and STEM_ELEMENT.get(_v[0]) in bang:
                        de_di = True
                        break
            de_shi = any(STEM_ELEMENT.get(s) in bang for i, s in enumerate(stems4) if i != 2)  # 得势（布尔，跳过日柱位置）
            if de_ling and (de_di or de_shi):
                out["day_strength_state"] = "WANG"
            elif not de_ling and not de_di and not de_shi:
                out["day_strength_state"] = "SHUAI"
            else:
                out["day_strength_state"] = "JUN_HENG"
            if out["day_strength_state"] == "WANG":
                sheng_wo = _SHENG.get(day_el)                                    # 食伤（我生）
                ke = _KE.get(day_el)                                             # 财（我克）
                ke_wo = next((k for k, v in _KE.items() if v == day_el), None)   # 官杀（克我）
                els = {e for e in (ke, ke_wo, sheng_wo) if e}
                out["yong_shen_el"] = sorted(els)
                out["yong_shen_ten_god"] = ["财", "官杀", "食伤"]
            elif out["day_strength_state"] == "SHUAI":
                els = {e for e in (day_el, sheng) if e}
                out["yong_shen_el"] = sorted(els)
                out["yong_shen_ten_god"] = ["印", "比劫"]
            else:
                out["yong_shen_el"] = []
                out["yong_shen_ten_god"] = []
    # 真化/假化（DTS-041-002/043-002 注：日干合干單透一位在月時上合之，不遇壬癸甲乙戊己，
    # 而有辰字（龍），且化神得令（丙辛冬月/戊癸夏月/乙庚秋月/丁壬春月/甲己四季）→真化；
    # 暗扶日主、合神虛弱、無龍以運之→假化）
    # 合化行表 _HUA 依 DTS-041-002 注原文（甲己化土/乙庚化金/丙辛化水/丁壬化木/戊癸化火）；
    # 五合关系与「五合均可真化」为 DIRECT_TEXT（原文直接列举）
    # Human 裁决 2026-09-15：「不遇」存在版本异文（崇祯本「壬癸甲乙戊己」/《滴天髓阐微》
    # 「壬癸甲乙戊」/另一通行本「壬癸甲乙庚」），不固化为最终规则——
    # 仅作甲己案例原文条件保留（值按底本，PENDING_VERIFY），其余四合（乙庚/丙辛/丁壬/戊癸）
    # 原文未列「不遇」集合，不套用（DIRECT_TEXT 无此条件，不类推）
    if base and day_stem:
        stems4 = [base.get("year_stem"), base.get("month_stem"), day_stem, base.get("hour_stem")]
        brs4 = [base.get("year_branch"), base.get("month_branch"),
                base.get("day_branch"), base.get("hour_branch")]
        if all(stems4) and all(brs4):
            he = _HE.get(day_stem)
            if he and he in (stems4[1], stems4[3]):      # 月干或时干合
                hua_el = _HUA.get(day_stem)
                other_stems = [s for s in stems4 if s not in (day_stem, he)]  # 剔除日干与合干
                if hua_el:
                    # 单透：合干在四干中只一位
                    single = sum(1 for s in stems4 if s == he) == 1
                    # 「不遇」检查仅甲己合（原文字面条件，PENDING_VERIFY）；
                    # 其余四合不检查（原文未列集合，不类推）[DIRECT_TEXT]
                    not_yu = True
                    if day_stem == "甲" and he == "己":
                        day_el2 = STEM_ELEMENT.get(day_stem)
                        sheng2 = next((k for k, v in _SHENG.items() if v == day_el2), None) if day_el2 else None
                        bad = {s for s in other_stems if STEM_ELEMENT.get(s) in
                               (day_el2, sheng2, "土")}   # 壬癸（印）甲乙（比劫）戊己（同类土）
                        not_yu = not bad
                    has_chen = "辰" in brs4
                    de_ling = BRANCH_ELEMENT.get(base.get("month_branch")) == hua_el
                    if single and not_yu and has_chen and de_ling:
                        out["hua_state"] = "真"
                    elif single and not (has_chen and de_ling):
                        out["hua_state"] = "假"    # 合成立但缺龙/化神不得令 [PENDING_VERIFY]
    return out
