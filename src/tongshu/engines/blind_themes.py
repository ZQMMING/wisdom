# -*- coding: utf-8 -*-
"""盲派 L2.5 主题聚合层：12 维度最终输出契约（THEME-OUTPUT-001~012）。

层位：L2 事件之后、L3 现代语言之前。输出术语枚举（后端全量事实），
吉凶词汇拦截仍在 L3 映射层。全布尔/枚举，禁评分。

12 维度（用户定稿）：
01 性情禀赋 / 02 交游人际 / 03 婚姻配偶 / 04 子女 / 05 财帛 /
06 身体疾厄 / 07 迁移出行 / 08 事业功名 / 09 田宅家业 /
10 福德精神 / 11 父母长辈 / 12 才艺学业

取证源（原著优先）：
- 04 子女：段建业《盲派八字命理口诀·子女》（男命有财以七杀为儿正官为女；
  无财以食神为儿伤官为女；女命以食神为女伤官为儿；时柱=子女宫，枭印在时克子）
- 07 迁移：盲派金口诀·论驿马（申子辰马在寅、寅午戌马在申、巳酉丑马在亥、
  亥卯未马在巳；驿马主动；马逢冲必远行）
- 10 福德：盲派十神口诀（食神=寿星"此格为人多福寿"；六亲损断"印旺身强多福寿"）
- 12 才艺学业：段建业《盲派中级命理学》第11章学历专辑（官杀/印星/食神=学历神；
  印星须做功方表学历；食伤泄秀=才艺；金水主理、木火主文）
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..reasoning.bazi_ten_gods import BRANCH_HIDDEN_STEMS, ten_god

METHOD_SCOPE = "DUAN_JIANYE"


class ThemeState:
    """主题状态（全枚举，fail-closed）。"""
    ESTABLISHED = "ESTABLISHED"      # 结构事实确立
    CANDIDATE = "CANDIDATE"          # 候选取证成立
    UNDETERMINED = "UNDETERMINED"    # 事实缺失/证据未核证
    NOT_APPLICABLE = "NOT_APPLICABLE"  # 无对应结构


# 驿马查法（年支或日支查四柱）：申子辰马在寅 / 寅午戌马在申 /
# 巳酉丑马在亥 / 亥卯未马在巳（盲派金口诀·论驿马）
YIMA_MAP = {
    "SHEN": "YIN", "ZI": "YIN", "CHEN": "YIN",
    "YIN": "SHEN", "WU": "SHEN", "XU": "SHEN",
    "SI": "HAI", "YOU": "HAI", "CHOU": "HAI",
    "HAI": "SI", "MAO": "SI", "WEI": "SI",
}

# 十神分组（男命子女星：有财→官杀；无财→食伤）
GROUP_CAI = {"正财", "偏财"}
GROUP_GUAN = {"正官", "七杀"}
GROUP_SHISHANG = {"食神", "伤官"}
GROUP_YIN = {"正印", "偏印"}

# 12 主题元数据
THEME_DEFS = [
    ("THEME-001", "性情禀赋", "01"),
    ("THEME-002", "交游人际", "02"),
    ("THEME-003", "婚姻配偶", "03"),
    ("THEME-004", "子女", "04"),
    ("THEME-005", "财帛", "05"),
    ("THEME-006", "身体疾厄", "06"),
    ("THEME-007", "迁移出行", "07"),
    ("THEME-008", "事业功名", "08"),
    ("THEME-009", "田宅家业", "09"),
    ("THEME-010", "福德精神", "10"),
    ("THEME-011", "父母长辈", "11"),
    ("THEME-012", "才艺学业", "12"),
]


@dataclass
class ThemeEntry:
    """单条主题事实（来源链）。"""
    source: str      # 数据源字段路径，如 "marriage_event_structure.marriage_state"
    value: str       # 枚举值
    rule_id: str = ""

    def to_dict(self) -> dict:
        return {"source": self.source, "value": self.value, "rule_id": self.rule_id}


@dataclass
class BlindThemeResult:
    """L2.5 主题聚合结果：12 维度最终输出契约。"""
    themes: List[Dict] = field(default_factory=list)
    method_scope: str = METHOD_SCOPE
    status: str = ThemeState.UNDETERMINED

    def to_dict(self) -> dict:
        return {
            "themes": self.themes,
            "method_scope": self.method_scope,
            "status": self.status,
        }


class BlindThemeEngine:
    """12 主题聚合引擎：消费 L1/L1e/L1f/L2 输出，按主题归类。"""

    def aggregate(self, chart, blind_result, yingqi_result=None,
                  judgment_result=None) -> BlindThemeResult:
        d = blind_result.to_dict()
        b = getattr(chart, "to_dict", lambda: chart.to_dict())() if hasattr(chart, "to_dict") else {}
        branches = [chart.year_pillar.earthly_branch, chart.month_pillar.earthly_branch,
                    chart.day_pillar.earthly_branch, chart.hour_pillar.earthly_branch]
        stems = [chart.year_pillar.heavenly_stem, chart.month_pillar.heavenly_stem,
                 chart.day_pillar.heavenly_stem, chart.hour_pillar.heavenly_stem]
        day_master = chart.day_master

        themes = []
        themes.append(self._theme_01(blind_result, b))
        themes.append(self._theme_02(blind_result))
        themes.append(self._theme_03(blind_result))
        themes.append(self._theme_04(chart, stems, branches, day_master))
        themes.append(self._theme_05(blind_result))
        themes.append(self._theme_06(blind_result, d))
        themes.append(self._theme_07(chart, stems, branches, yingqi_result))
        themes.append(self._theme_08(blind_result))
        themes.append(self._theme_09(blind_result))
        themes.append(self._theme_10(blind_result, d))
        themes.append(self._theme_11(chart, stems, branches, day_master, d))
        themes.append(self._theme_12(chart, stems, day_master, d))

        return BlindThemeResult(
            themes=themes,
            status=ThemeState.ESTABLISHED if any(t["state"] != ThemeState.UNDETERMINED for t in themes)
            else ThemeState.UNDETERMINED,
        )

    # ── 01 性情禀赋：旺衰 + 五行失衡 + 透干十神（事实聚合，断语留 L3）──
    def _theme_01(self, br, chart_dict) -> Dict:
        entries = []
        wangshuai = getattr(br, "blind_wangshuai", "UNDETERMINED")
        entries.append(ThemeEntry("blind_wangshuai", str(wangshuai), "THEME-001"))
        imbal = chart_dict.get("five_element_imbalance") if chart_dict else None
        if imbal is not None:
            entries.append(ThemeEntry("five_element_imbalance", "TRUE" if imbal else "FALSE", "THEME-001"))
        tg = getattr(br, "transparent_ten_gods", None)
        if tg:
            entries.append(ThemeEntry("transparent_ten_gods", json.dumps(tg, ensure_ascii=False), "THEME-001"))
        state = ThemeState.ESTABLISHED if entries else ThemeState.UNDETERMINED
        return self._mk("THEME-001", "性情禀赋", state, entries, ["THEME-001"])

    # ── 02 交游人际：兄弟/姐妹计数 + 比劫做功状态 ──
    def _theme_02(self, br) -> Dict:
        entries = []
        kc = getattr(br, "kinship_count", None)
        if kc and isinstance(kc, dict):
            entries.append(ThemeEntry("kinship_count.brother_count", str(kc.get("brother_count", "?")), "THEME-002"))
            entries.append(ThemeEntry("kinship_count.sister_count", str(kc.get("sister_count", "?")), "THEME-002"))
        methods = getattr(br, "zuo_gong_methods", []) or []
        attrs = getattr(br, "zuo_gong_attributions", []) or []
        bijie_eff = any("比劫" in m and a == "EFFECTIVE" for m, a in zip(methods, attrs))
        entries.append(ThemeEntry("zuo_gong.比劫做功", "EFFECTIVE" if bijie_eff else "NOT_EFFECTIVE", "THEME-002"))
        state = ThemeState.ESTABLISHED if entries else ThemeState.UNDETERMINED
        return self._mk("THEME-002", "交游人际", state, entries, ["THEME-002"])

    # ── 03 婚姻配偶：L1e 婚姻结构全字段 ──
    def _theme_03(self, br) -> Dict:
        m = getattr(br, "marriage_event_structure", None) or {}
        entries = [ThemeEntry("marriage_event_structure.marriage_state", str(m.get("marriage_state", "UNDETERMINED")), "THEME-003")]
        if m.get("palace_state"):
            entries.append(ThemeEntry("marriage_event_structure.palace_state", str(m["palace_state"]), "THEME-003"))
        if m.get("spouse_star_present") is not None:
            entries.append(ThemeEntry("marriage_event_structure.spouse_star_present", str(m["spouse_star_present"]), "THEME-003"))
        state = ThemeState.ESTABLISHED if m.get("marriage_state") not in (None, "UNDETERMINED") else ThemeState.UNDETERMINED
        return self._mk("THEME-003", "婚姻配偶", state, entries, ["THEME-003", "JDG-MARRIAGE-001"])

    # ── 04 子女：子女星（男命有财→官杀/无财→食伤；女命→食伤）+ 子女宫时柱状态 ──
    def _theme_04(self, chart, stems, branches, day_master) -> Dict:
        entries = []
        gender = getattr(chart, "gender", "male")
        # 子女星确定（段建业盲派口诀·子女）
        star_tgs = []
        if gender == "male":
            has_cai = any(ten_god(day_master, s) in GROUP_CAI for s in stems) or any(
                ten_god(day_master, h) in GROUP_CAI for b in branches
                for h, _p in BRANCH_HIDDEN_STEMS.get(b, []))
            if has_cai:
                star_tgs = ["七杀", "正官"]  # 有财星→官杀为子女星
                star_rule = "男命有财→官杀为子女星(七杀为儿/正官为女)"
            else:
                star_tgs = ["食神", "伤官"]  # 无财星→食伤为子女星
                star_rule = "男命无财→食伤为子女星(食神为儿/伤官为女)"
        else:
            star_tgs = ["食神", "伤官"]  # 女命→食伤为子女星
            star_rule = "女命→食伤为子女星(食神为女/伤官为儿)"
        star_present = any(ten_god(day_master, s) in star_tgs for s in stems) or any(
            ten_god(day_master, h) in star_tgs for b in branches
            for h, _p in BRANCH_HIDDEN_STEMS.get(b, []))
        entries.append(ThemeEntry("children.star", star_rule, "THEME-004"))
        entries.append(ThemeEntry("children.star_present", "TRUE" if star_present else "FALSE", "THEME-004"))
        # 子女宫=时柱：时支被冲/穿/刑=伤；枭印在时柱=克子（口诀）
        hour_branch = branches[3]
        others = branches[:3]
        palace_hit = []
        if any(hour_branch in BRANCH_HIDDEN_STEMS and False for _ in [0]):
            pass
        # 时支与其他支冲穿刑（简：冲+穿）
        from ..engines.blind_bazi_engine import BRANCH_CHONG, BRANCH_CHUAN
        if BRANCH_CHONG.get(hour_branch) in others:
            palace_hit.append("时支逢冲")
        if BRANCH_CHUAN.get(hour_branch) in others:
            palace_hit.append("时支逢穿")
        # 枭印在时柱
        hour_stem = stems[3]
        if ten_god(day_master, hour_stem) == "偏印" or any(
                ten_god(day_master, h) == "偏印" for h, _p in BRANCH_HIDDEN_STEMS.get(hour_branch, [])):
            palace_hit.append("枭印在时柱(克子)")
        entries.append(ThemeEntry("children.palace_hit", "_AND_".join(palace_hit) if palace_hit else "STABLE", "THEME-004"))
        if palace_hit:
            state = ThemeState.CANDIDATE   # 子女宫受损组合=候选取证成立
        else:
            state = ThemeState.ESTABLISHED  # 星不显/宫安稳均为确定事实断言
        return self._mk("THEME-004", "子女", state, entries, ["THEME-004", "BLIND-CHILD-001"])

    # ── 05 财帛：L1e 财富结构全字段 ──
    def _theme_05(self, br) -> Dict:
        w = getattr(br, "wealth_event_structure", None) or {}
        entries = [ThemeEntry("wealth_event_structure.wealth_state", str(w.get("wealth_state", "UNDETERMINED")), "THEME-005")]
        if w.get("wealth_present") is not None:
            entries.append(ThemeEntry("wealth_event_structure.wealth_present", str(w["wealth_present"]), "THEME-005"))
        state = ThemeState.ESTABLISHED if w.get("wealth_state") not in (None, "UNDETERMINED") else ThemeState.UNDETERMINED
        return self._mk("THEME-005", "财帛", state, entries, ["THEME-005", "JDG-WEALTH-001"])

    # ── 06 身体疾厄：L1e 身体候选 + 燥土脆金 ──
    def _theme_06(self, br, d) -> Dict:
        b = getattr(br, "body_event_candidate", None) or {}
        entries = [ThemeEntry("body_event_candidate.candidate", str(b.get("candidate", "UNDETERMINED")), "THEME-006")]
        if b.get("lu_attacked") is not None:
            entries.append(ThemeEntry("body_event_candidate.lu_attacked", str(b["lu_attacked"]), "THEME-006"))
        if d.get("dry_earth_brittle"):
            entries.append(ThemeEntry("dry_earth_brittle", str(d["dry_earth_brittle"]), "THEME-006"))
        state = ThemeState.ESTABLISHED if (
            b.get("candidate") not in (None, "UNDETERMINED")
            or d.get("dry_earth_brittle") not in (None, "UNDETERMINED")
        ) else ThemeState.UNDETERMINED
        return self._mk("THEME-006", "身体疾厄", state, entries, ["THEME-006", "JDG-BODY-001"])

    # ── 07 迁移出行：驿马（年/日支查四柱）+ 驿马逢冲/逢合 + 大运流年引动 ──
    def _theme_07(self, chart, stems, branches, yingqi_result) -> Dict:
        entries = []
        yima_found = []
        for base_branch in (branches[0], branches[2]):  # 年支或日支查
            yima_b = YIMA_MAP.get(base_branch)
            if yima_b and yima_b in branches:
                yima_found.append(f"{base_branch}马在{yima_b}")
        entries.append(ThemeEntry("yima.present", "_AND_".join(yima_found) if yima_found else "NONE", "THEME-007"))
        # 驿马逢冲/逢合（大运流年层）
        yima_hit = []
        if yingqi_result is not None:
            for trg in yingqi_result.triggers:
                b = trg.get("branch")
                for yima_b in (YIMA_MAP.get(branches[0]), YIMA_MAP.get(branches[2])):
                    if yima_b and trg.get("kind") == "chong" and b == yima_b:
                        yima_hit.append(f"驿马{yima_b}逢冲({trg.get('source')})")
                    if yima_b and trg.get("kind") == "liuhe" and b == yima_b:
                        yima_hit.append(f"驿马{yima_b}逢合({trg.get('source')})")
        entries.append(ThemeEntry("yima.trigger", "_AND_".join(yima_hit) if yima_hit else "NO_TRIGGER", "THEME-007"))
        if yima_hit:
            state = ThemeState.CANDIDATE  # 马逢冲/合=动（迁移引动）
        else:
            state = ThemeState.ESTABLISHED  # 带马未动 / 不带马均为确定事实断言
        return self._mk("THEME-007", "迁移出行", state, entries, ["THEME-007", "BLIND-YIMA-001"])

    # ── 08 事业功名：职业方向 + 官贵状态 + 做功效率 ──
    def _theme_08(self, br) -> Dict:
        oc = getattr(br, "occupation_candidate", None) or {}
        o = getattr(br, "official_event_structure", None) or {}
        entries = [
            ThemeEntry("occupation_candidate.work_types", json.dumps(oc.get("work_types", []), ensure_ascii=False), "THEME-008"),
            ThemeEntry("official_event_structure.official_state", str(o.get("official_state", "UNDETERMINED")), "THEME-008"),
        ]
        we = getattr(br, "work_efficiency", None)
        if we:
            entries.append(ThemeEntry("work_efficiency", str(we), "THEME-008"))
        state = ThemeState.ESTABLISHED if o.get("official_state") not in (None, "UNDETERMINED") else ThemeState.UNDETERMINED
        return self._mk("THEME-008", "事业功名", state, entries, ["THEME-008", "JDG-OFFICIAL-001", "JDG-OCCUPATION-001"])

    # ── 09 田宅家业：墓库收物（财库/能量）+ 换象 ──
    def _theme_09(self, br) -> Dict:
        entries = []
        methods = getattr(br, "zuo_gong_methods", []) or []
        attrs = getattr(br, "zuo_gong_attributions", []) or []
        store_eff = any("墓库" in m and a == "EFFECTIVE" for m, a in zip(methods, attrs))
        entries.append(ThemeEntry("zuo_gong.墓库收物", "EFFECTIVE" if store_eff else "NOT_EFFECTIVE", "THEME-009"))
        ku_chong = [m for m in methods if "冲开墓库" in m]
        if ku_chong:
            entries.append(ThemeEntry("zuo_gong.冲开墓库", "_AND_".join(ku_chong), "THEME-009"))
        state = ThemeState.ESTABLISHED  # EFFECTIVE=收物成立 / NOT_EFFECTIVE=未成立，均为确定事实断言
        return self._mk("THEME-009", "田宅家业", state, entries, ["THEME-009"])

    # ── 10 福德精神：食神（寿星）+ 印旺身强（福）──
    def _theme_10(self, br, d) -> Dict:
        entries = []
        methods = getattr(br, "zuo_gong_methods", []) or []
        attrs = getattr(br, "zuo_gong_attributions", []) or []
        shishen_eff = any(("食神" in m or "食伤" in m) and a == "EFFECTIVE" for m, a in zip(methods, attrs))
        entries.append(ThemeEntry("zuo_gong.食伤做功", "EFFECTIVE" if shishen_eff else "NOT_EFFECTIVE", "THEME-010"))
        wangshuai = getattr(br, "blind_wangshuai", "UNDETERMINED")
        entries.append(ThemeEntry("blind_wangshuai", str(wangshuai), "THEME-010"))
        yin_eff = any(("印" in m) and a == "EFFECTIVE" for m, a in zip(methods, attrs))
        entries.append(ThemeEntry("zuo_gong.印做功", "EFFECTIVE" if yin_eff else "NOT_EFFECTIVE", "THEME-010"))
        state = ThemeState.ESTABLISHED if (shishen_eff or yin_eff) else ThemeState.CANDIDATE
        return self._mk("THEME-010", "福德精神", state, entries, ["THEME-010", "BLIND-FUDE-001"])

    # ── 11 父母长辈：父=偏财、母=印星（透干/藏干状态）──
    def _theme_11(self, chart, stems, branches, day_master, d) -> Dict:
        entries = []
        father_present = any(ten_god(day_master, s) == "偏财" for s in stems) or any(
            ten_god(day_master, h) == "偏财" for b in branches
            for h, _p in BRANCH_HIDDEN_STEMS.get(b, []))
        mother_present = any(ten_god(day_master, s) in GROUP_YIN for s in stems) or any(
            ten_god(day_master, h) in GROUP_YIN for b in branches
            for h, _p in BRANCH_HIDDEN_STEMS.get(b, []))
        entries.append(ThemeEntry("parents.father(偏财)", "PRESENT" if father_present else "ABSENT", "THEME-011"))
        entries.append(ThemeEntry("parents.mother(印星)", "PRESENT" if mother_present else "ABSENT", "THEME-011"))
        state = ThemeState.ESTABLISHED  # PRESENT=在局 / ABSENT=不显（缘淡），均为确定事实断言
        return self._mk("THEME-011", "父母长辈", state, entries, ["THEME-011"])

    # ── 12 才艺学业：印星（学业，须做功）+ 食伤（才艺，泄秀）──
    def _theme_12(self, chart, stems, day_master, d) -> Dict:
        entries = []
        methods = getattr(d, "zuo_gong_methods", []) if isinstance(d, dict) else []
        attrs = getattr(d, "zuo_gong_attributions", []) if isinstance(d, dict) else []
        # 直接用 d dict
        methods = d.get("zuo_gong_methods", []) or []
        attrs = d.get("zuo_gong_attributions", []) or []
        yin_eff = any("印" in m and a == "EFFECTIVE" for m, a in zip(methods, attrs))
        shixie_eff = any("食伤泄秀" in m and a == "EFFECTIVE" for m, a in zip(methods, attrs))
        entries.append(ThemeEntry("zuo_gong.印做功(学业)", "EFFECTIVE" if yin_eff else "NOT_EFFECTIVE", "THEME-012"))
        entries.append(ThemeEntry("zuo_gong.食伤泄秀(才艺)", "EFFECTIVE" if shixie_eff else "NOT_EFFECTIVE", "THEME-012"))
        # 文理方向（金水主理、木火主文——盲派中级第11章）
        dm_el = getattr(chart, "day_master_element", "FIRE")
        direction = "LI(金水)" if dm_el in {"METAL", "WATER"} else ("WEN(木火)" if dm_el in {"WOOD", "FIRE"} else "UNDETERMINED")
        entries.append(ThemeEntry("talent.direction", direction, "THEME-012"))
        state = ThemeState.ESTABLISHED if (yin_eff or shixie_eff) else ThemeState.CANDIDATE
        return self._mk("THEME-012", "才艺学业", state, entries, ["THEME-012", "BLIND-XUELI-001"])

    # ── 工具 ──
    def _mk(self, theme_id, name, state, entries, rule_ids) -> Dict:
        return {
            "theme_id": theme_id,
            "theme_name": name,
            "state": state,
            "entries": [e.to_dict() for e in entries],
            "rule_ids": rule_ids,
        }


def aggregate_blind_themes(chart, blind_result, yingqi_result=None,
                           judgment_result=None) -> BlindThemeResult:
    """便捷入口。"""
    return BlindThemeEngine().aggregate(chart, blind_result, yingqi_result, judgment_result)
