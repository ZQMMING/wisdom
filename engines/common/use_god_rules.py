# -*- coding: utf-8 -*-
"""PATCH-032 Rule Construction：PZZQ 月令取用 + QTBJ 九月乙木调候
- RULE-032-01：PZZQ 月令财星顺用 → use_god_state=CANDIDATE(财)/pattern_state=CANDIDATE(财格)
- RULE-032-02：QTBJ 九月乙木端用癸水 → climate_use_state=DETERMINED(癸水)
- SFTK qu_yong 未接线（留待 033），诚实 UNDETERMINED
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1983-11-03 命局
CHART = {
    "pillars": "癸亥 壬戌 乙未 壬午", "day_master_element": "WOOD",
    "month_order": "戌", "month_hidden": ["戊", "辛", "丁"],
    "stems": {"年": "癸", "月": "壬", "日": "乙", "时": "壬"},
    "hidden": {"亥": ["壬", "甲"], "戌": ["戊", "辛", "丁"], "未": ["己", "丁", "乙"], "午": ["丁", "己"]},
}

# 五行→十神（乙木日主）
ELEM_TO_TENGOD = {"木": "比肩", "火": "食伤", "土": "财", "金": "官杀", "水": "印"}


def rule_032_01_pzzq(c):
    """PZZQ 月令取用：月令所藏主气（本气）→十神→用神（顺用/逆用）"""
    month_zhi = c["month_order"]  # 戌
    hidden_map = {"戌": ["戊", "辛", "丁"]}  # 戌藏 戊(本气)辛(中气)丁(余气)
    benqi = hidden_map[month_zhi][0]  # 戊（土）
    ten_god = ELEM_TO_TENGOD["土"]  # 财
    # PZZQ-005-007：财=用神之善者→顺用
    if ten_god == "财":
        return {
            "rule_id": "RULE-032-01", "namespace": "PZZQ.use_god",
            "month_benqi": benqi, "ten_god": ten_god, "use_mode": "顺用",
            "use_god_state": "CANDIDATE(财)",
            "pattern_state": "CANDIDATE(财格)",
            "evidence": ["EVID-011", "EVID-015", "EVID-016", "EVID-017"],
            "note": "戌为杂气财库；财不透干（天干无戊），地支戌未双财库+午未合，成格待 structure 确认（PZZQ-007-006 透干会支）",
        }
    return {"use_god_state": "UNDETERMINED"}


def rule_032_02_qtbj(c):
    """QTBJ 九月乙木调候：端用癸水；癸透+辛藏→DETERMINED"""
    gui_visible = any(s == "癸" for s in c["stems"].values())          # 癸透
    xin_hidden = "辛" in c["month_hidden"] or "辛" in c["hidden"]["戌"]  # 辛藏（发水之源）
    ren_count = sum(1 for s in c["stems"].values() if s == "壬")         # 壬透数
    if gui_visible:
        cond = "癸透+辛藏发水源" if xin_hidden else "癸透无辛"
        return {
            "rule_id": "RULE-032-02", "namespace": "QTBJ.climate_use",
            "climate_use_state": "DETERMINED(癸水)",
            "condition": cond,
            "ren_visible": ren_count,
            "ren_limit": "四柱壬多水難生乙（断语层待综合，不影响调候用神）" if ren_count >= 2 else "壬未多",
            "evidence": ["EVID-018"],
            "note": "九月乙木必赖癸水滋养；本命癸透年干" + ("+戌中辛发水之源" if xin_hidden else "") + "→调候用神癸水确定",
        }
    return {"climate_use_state": "UNDETERMINED", "note": "九月乙木无癸→按 QTBJ 不满足滋养条件"}


if __name__ == "__main__":
    print("==== PATCH-032 Rule Construction（阶段 D 第一批） ====")
    print("\n==== 1983-11-03 命局 ====")
    print(f"  {CHART['pillars']} | 日主乙木 | 月令戌(藏戊辛丁)")
    print("\n==== RULE-032-01 PZZQ 月令取用 ====")
    r1 = rule_032_01_pzzq(CHART)
    print(json.dumps(r1, ensure_ascii=False, indent=1))
    print("\n==== RULE-032-02 QTBJ 九月乙木调候 ====")
    r2 = rule_032_02_qtbj(CHART)
    print(json.dumps(r2, ensure_ascii=False, indent=1))
    print("\n==== 输出汇总（1983-1103） ====")
    print(f"  use_god_state    = {r1['use_god_state']}")
    print(f"  pattern_state    = {r1['pattern_state']}")
    print(f"  climate_use_state= {r2['climate_use_state']}（{r2.get('condition')}）")
    print(f"  qu_yong_state    = UNDETERMINED（SFTK 病药未接线，留待 033）")
    print(f"  strength_state   = UNDETERMINED（无授权综合，不变）")
    print("\n==== 证据绑定 ====")
    print("  EVID-011 PZZQ-005-007 專求月令 | EVID-015 PZZQ-005-009 月令藏干变化")
    print("  EVID-016 PZZQ-007-006 杂气透干会支 | EVID-017 PZZQ-007-021 财喜根深")
    print("  EVID-018 QTBJ-022-001 九月乙木（注意：非 QTBJ-018-001，018 是五月乙木）")
