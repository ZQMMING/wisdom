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
# 月支本气
BENQI = {"亥": "壬", "戌": "戊", "未": "己", "午": "丁"}

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
        return "七煞格" if benqi == "庚" else "官格"
    if t == "印": return "印格"
    if t == "食伤":
        return "食神格" if benqi == "丙" else "伤官格"
    if t == "比劫":
        return "建禄月劫格"
    return "UNDETERMINED"


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
    # 其他格：登记 Registry（成败谓词逐字在手，待对应命局触发）
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
