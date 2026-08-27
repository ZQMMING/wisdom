"""Generate GOLDEN-007..020 YAML assertion bodies from _explore ground truth.

The expected_* fields are transcribed mechanically from the engine's
deterministic Stub output (no hand-typing, no fabrication). The header
comment is curated per case from the manual semantic verification
(十神/藏干/主星/格局 logic against the standard tables).

Run from backend/:  PYTHONIOENCODING=utf-8 PYTHONPATH=src python gen_golden_yaml.py
"""

from __future__ import annotations
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXPLORE = REPO / "backend" / "_explore"
OUT = REPO / "docs" / "golden_cases"

STEM_ZH = {"JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
           "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸"}
BR_ZH = {"ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰",
         "SI": "巳", "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉",
         "XU": "戌", "HAI": "亥"}
STAR_ZH = {"TAIYANG": "太阳", "TIANFU": "天府", "ZIWEI": "紫微", "JUMEN": "巨门",
           "TIANTONG": "天同", "POJUN": "破军", "LIANZHEN": "廉贞", "TANLANG": "贪狼",
           "TAIYIN": "太阴"}


def split_ganzhi(p: str):
    for s, zh in STEM_ZH.items():
        if p.startswith(s):
            return s, p[len(s):]
    raise ValueError(p)


def pillars_section(pil: dict) -> list[str]:
    lines = ["bazi:"]
    lines.append("  four_pillars:")
    for k, key in (("year", "year_pillar"), ("month", "month_pillar"),
                   ("day", "day_pillar"), ("hour", "hour_pillar")):
        g = pil[k]
        st, br = split_ganzhi(g)
        lines.append(f"    {key}: {{ heavenly_stem: \"{st}\", earthly_branch: \"{br}\" }}  # {STEM_ZH[st]}{BR_ZH[br]}")
    lines.append(f'  day_master: "{pil["day_master"]}"')
    lines.append(f'  day_master_element: "{pil["day_master_element"]}"')
    return lines


def yaml_list(items) -> str:
    return "[" + ", ".join(f'"{i}"' for i in items) + "]"


def signals_section(signals: dict, layers=("BASELINE", "CYCLE_CONTEXT", "DAILY_ACTIVATION")) -> list[str]:
    lines = ["expected_signals:"]
    for layer in layers:
        sigs = signals.get(layer, [])
        if not sigs:
            lines.append(f"  {layer}: []")
            continue
        lines.append(f"  {layer}:")
        for s in sigs:
            lines.append(f'    - signal_id: "{s["signal_id"]}"')
            lines.append(f'      ontology_type: {s["ontology_type"]}')
            lines.append(f'      direction: {s["direction"]}')
            lines.append(f'      polarity: {s["polarity"]}')
            lines.append(f"      rule_refs: {yaml_list(s['rule_refs'])}")
            lines.append(f"      evidence_refs: {yaml_list(s['evidence_refs'])}")
    return lines


def claims_section(claims) -> list[str]:
    lines = ["expected_atomic_claims:"]
    for c in claims:
        lines.append(f'  - claim_id: "{c["claim_id"]}"')
        lines.append(f'    signal_type: {c["signal_type"]}')
        lines.append(f'    direction: {c["direction"]}')
        lines.append(f'    strength: {c["strength"]}')
        lines.append(f'    source_layers: {yaml_list(c["source_layers"])}')
        lines.append(f'    rule_refs: {yaml_list(c["rule_refs"])}')
        lines.append(f'    evidence_refs: {yaml_list(c["evidence_refs"])}')
    return lines


def cross_section(cross) -> list[str]:
    lines = ["expected_cross_analysis:"]
    lines.append(f'  status: {cross["status"]}')
    lines.append(f'  bazi_signal_refs: {yaml_list(cross["bazi_signal_refs"])}')
    lines.append(f'  ziwei_signal_refs: {yaml_list(cross["ziwei_signal_refs"])}')
    lines.append(f'  ontology_relationship: {json.dumps(cross.get("ontology_relationship"))}')
    lines.append(f'  evidence_sufficient: {str(cross["evidence_sufficient"]).lower()}')
    lines.append(f'  reason_code: "{cross.get("reason_code")}"')
    return lines


# (case_id, tag, focus comment lines)
CASES = [
    ("GOLDEN-007", "g007-zhengguan", [
        "正官格:酉月主气辛金(克我·异性)→正官,当令(非杂气)→ZPZ-105+ZPZ-106;",
        "时干庚金七杀透干(非当令)→ZPZ-130;三规则同向 CONSTRAINT→T205 合并。",
        "太阳主星→SUPPORT(§5.4);八字种子 SUPPORT(ZPZ-001)⊗太阳 SUPPORT 同型同向→ALIGNED。",
    ]),
    ("GOLDEN-008", "g008-zhengcai", [
        "正财格:丑月(杂气)主气己土(我克·异性)→正财,己透于月干→杂气透干取格;",
        "ZPZ-104(正财/偏财当令)+ZPZ-109(正财)+ZPZ-117(正财透干)同向 RESOURCE→合并。",
        "天府主星→SUPPORT;种子 SUPPORT⊗天府 SUPPORT→ALIGNED。",
    ]),
    ("GOLDEN-009", "g009-shishen", [
        "食神格:午月主气丁火(我生·同性)→食神,当令→ZPZ-103;",
        "年/月干戊土正财透干→ZPZ-127 RESOURCE;时干壬水正印透干→ZPZ-121 SUPPORT。",
        "紫微主星→SUPPORT;种子 SUPPORT⊗紫微 SUPPORT→ALIGNED。",
    ]),
    ("GOLDEN-010", "g010-shangguan", [
        "伤官格:巳月主气丙火(我生·异性)→伤官,当令→ZPZ-103+ZPZ-110 合并 OUTPUT;",
        "比肩透干(YI)→ZPZ-123;辛金七杀透干→ZPZ-130 CONSTRAINT。",
        "巨门主星→CONSTRAINT;八字七杀透 CONSTRAINT⊗巨门 CONSTRAINT 同型同向→ALIGNED。",
    ]),
    ("GOLDEN-011", "g011-qisha", [
        "七杀格:申月主气庚金(克我·同性)→七杀,当令+透干→ZPZ-105+ZPZ-107+ZPZ-120 合并 CONSTRAINT;",
        "食神透干(BING)→ZPZ-125 OUTPUT。",
        "天同主星→REFLECTION;八字 CONSTRAINT⊗REFLECTION 为注册跨型对(§7)→PARTIAL/SHARED_SUPERTYPE。",
    ]),
    ("GOLDEN-012", "g012-shishen2", [
        "食神格:巳月主气丙火(我生·同性)→食神,当令→ZPZ-103;",
        "伤官透干(DING)→ZPZ-126 OUTPUT 与 ZPZ-103 同向 OUTPUT→合并;劫财透(YI)→ZPZ-124。",
        "天同主星→REFLECTION;七杀透(ZPZ-130 CONSTRAINT)⊗REFLECTION 注册对→PARTIAL。",
    ]),
    ("GOLDEN-013", "g013-pojun-zagi", [
        "辰月(杂气)主气戊土七杀**不透干**→七杀格不取(ZPZ-105/107 不触发);",
        "仅种子 ZPZ-005 + 梯二(正财 ZPZ-127/偏财 ZPZ-128→RESOURCE、食神 ZPZ-125→OUTPUT);",
        "破军主星→CHANGE;八字 OUTPUT⊗CHANGE 为注册跨型对→PARTIAL。",
    ]),
    ("GOLDEN-014", "g014-piancai", [
        "偏财格:巳月主气丙火(我克·同性)→偏财,当令→ZPZ-104;",
        "偏财透干(BING)→ZPZ-118;伤官透(YI)→ZPZ-126 OUTPUT;正印透(XIN)→ZPZ-121 SUPPORT。",
        "廉贞主星→CONSTRAINT;RESOURCE⊗CONSTRAINT 未注册且无同型→INSUFFICIENT_RULES。",
    ]),
    ("GOLDEN-015", "g015-zhengyin-tanlang", [
        "正印格:申月主气庚金(生我·异性)→正印,当令→ZPZ-101+ZPZ-108 合并 SUPPORT;",
        "食神/伤官透干→ZPZ-125/126 OUTPUT;正官透→ZPZ-129 CONSTRAINT。",
        "贪狼主星→ACTION;SUPPORT⊗ACTION 未注册且无同型→INSUFFICIENT_RULES。",
    ]),
    ("GOLDEN-016", "g016-pianyin", [
        "偏印格:卯月主气乙木(生我·同性)→偏印,当令→ZPZ-101;",
        "丁火日主 FIRE 种子→ZPZ-002 ACTION;劫财/偏财透干(ZPZ-124/128)。",
        "紫微主星→SUPPORT;偏印格 SUPPORT(ZPZ-101)⊗紫微 SUPPORT 同型同向→ALIGNED。",
    ]),
    ("GOLDEN-017", "g017-ji-qisha", [
        "己土日主:卯月主气乙木(克我·同性)→七杀,当令+透干→ZPZ-105+107+120 合并 CONSTRAINT;",
        "比肩透(JI)→ZPZ-123;伤官透(GENG)→ZPZ-126。",
        "天同主星→REFLECTION;土日主种子 ZPZ-003 REFLECTION⊗天同 REFLECTION 同型同向→ALIGNED。",
    ]),
    ("GOLDEN-018", "g018-konggong", [
        "正印格:子月主气癸水(生我·异性)→正印,当令→ZPZ-101+108 合并 SUPPORT;",
        "偏印/伤官/七杀透干→ZPZ-122/126/130。",
        "命宫**空宫**(iztro 无主星)→无紫微基线信号(DECISION-009)→EVIDENCE_MISSING 边界。",
    ]),
    ("GOLDEN-019", "g019-taiyin", [
        "正印格:亥月主气壬水(生我·异性)→正印,当令+透干→ZPZ-101+108+111 合并 SUPPORT;",
        "伤官透(BING)→ZPZ-126;偏财透(JI)→ZPZ-128。",
        "太阴主星→REFLECTION;SUPPORT⊗REFLECTION 未注册且无同型→INSUFFICIENT_RULES。",
    ]),
    ("GOLDEN-020", "g020-ji-day", [
        "比肩当令:寅月主气甲木(同我·同性)→比肩→ZPZ-102+113 合并 RELATION;",
        "劫财/偏财/七杀透干(ZPZ-124/128/130)。",
        "分析日 2026-08-23 为己巳日→DAILY_ACTIVATION 层 QTB-014 触发 SIG-DA-JI000 ACTION;",
        "太阳主星→SUPPORT;种子 SUPPORT⊗太阳 SUPPORT→ALIGNED(DAILY 层参与 cross 输入但不同型不改变结论)。",
    ]),
]

SIG_DECISIONS = "  - DECISION-001\n  - DECISION-002\n  - DECISION-003\n  - DECISION-006\n  - DECISION-009\n  - DECISION-012\n"


def main() -> None:
    for case_id, tag, focus in CASES:
        d = json.load(open(EXPLORE / f"{tag}.json", encoding="utf-8"))
        inp = d["input"]
        pil = d["pillars"]
        ziwei_key = d["ziwei"]["main_star"]
        star_zh = STAR_ZH.get(ziwei_key, "空宫")
        cross = d["cross_analysis"]
        features = d["rendered_features"] if "rendered_features" in d else None

        header = [
            f"# {case_id}: {inp['birth_date']} {inp['hour']:02d}:00 "
            f"{'男' if inp['gender']=='M' else '女'}命 - {inp['theme']} theme",
            "#",
            "# T601 扩集(2026-08-18):合成命例(非真实人物),四柱经 sxtwl 校验,",
            "# 期望值取自定义引擎(Stub)确定性输出 + 十神/藏干/主星标准表人工核验。",
            "#",
        ]
        for line in focus:
            header.append(f"# {line}")
        header.append(f'# 命宫主星: {star_zh} ({ziwei_key or "无/未映射"})')
        header += [
            "",
            f"case_id: {case_id}",
            "spec_decisions_ref:",
            SIG_DECISIONS,
            'spec_version: "1.0"',
            "status: active",
            "",
            "input:",
            f'  birth_date: "{inp["birth_date"]}"',
            f'  hour: {inp["hour"]}',
            f'  gender: "{inp["gender"]}"',
            f'  date_of_analysis: "{inp["date_of_analysis"]}"',
            f'  theme: "{inp["theme"]}"',
            "",
        ]
        body = pillars_section(pil)
        body.append("")
        body += [
            "ziwei:",
            f'  soul_palace_main_star: "{ziwei_key}"     # {star_zh} (real iztro)'
            if ziwei_key else "  soul_palace_main_star: \"\"      # 命宫空宫(iztro 无主星)",
            "  soul_palace_sihua: []",
            "",
        ]
        body += signals_section(d["signals"])
        body += [""]
        body += claims_section(d["atomic_claims"])
        body += [""]
        body += cross_section(cross)
        body += [
            "",
            "expected_rendered_output_features:",
            f'  must_include_themes: ["{inp["theme"]}"]',
            '  must_not_contain:',
            '    - "一定"',
            '    - "肯定赚钱"',
            '    - "建议买入"',
            '    - "明天会"',
            '    - "吉凶"',
            '  approximate_length: "140-160 chars"',
            '  tone: "warm"',
            "",
        ]
        out_path = OUT / f"{case_id}.yaml"
        out_path.write_text("\n".join(header + body), encoding="utf-8")
        print(f"wrote {out_path.name} ({len(header+body)} lines)")


if __name__ == "__main__":
    main()
