# -*- coding: utf-8 -*-
"""P0 五大引擎统一适配器 (ARCHITECTURE_V13_FINAL §九-P0).

每个 Adapter 将引擎内部计算结果转换为 EngineEvidence 列表.
铁律:
- 只输出纯事实, 不含 polarity/direction/吉凶判断.
- 不改引擎内部计算逻辑, 只做输出适配.
- rule_id 稳定不变, 用于 Golden Case 反查追踪.
"""
from __future__ import annotations

from typing import Any

from tongshu.assertion.engine_evidence import (
    BaseEngineAdapter,
    EngineEvidence,
    EngineName,
    TemporalScope,
)


# ═══════════════════════════════════════════════════════════════════
# 子平八字 Adapter
# ═══════════════════════════════════════════════════════════════════

class ZiPingAdapter(BaseEngineAdapter):
    """子平八字适配器. 本位: 旺衰/格局/调候用神/扶抑喜用."""

    engine_name = EngineName.ZI_PING

    def produce_evidence(self, inp, chart, context=None) -> list[EngineEvidence]:
        context = context or {}
        evidences: list[EngineEvidence] = []
        try:
            birth = context.get("birth")
            if birth is None:
                return evidences
            y, mo, d, h = birth[:4]
            gender = birth[4] if len(birth) > 4 else "male"

            from tongshu.engines.bazi_engine import BaziEngine
            from tongshu.engines.strength_engine import evaluate_strength

            bchart = BaziEngine().compute((y, mo, d, h), gender=gender)
            sr = evaluate_strength(bchart)

            # 日主
            if bchart.day_master:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_DAY_MASTER",
                    value=bchart.day_master,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"pillar": "day"},
                ))

            # 旺衰判定
            if sr.verdict:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_WANGSHUAI_VERDICT",
                    value=sr.verdict,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"climate": sr.climate or ""},
                ))

            # 格局(月令立格)
            from tongshu.engines.bazi_engine import _BRANCH_HIDDEN_MAIN, _ten_god
            month_branch = bchart.month_pillar.earthly_branch
            month_main = _BRANCH_HIDDEN_MAIN.get(month_branch, "")
            if month_main and bchart.day_master:
                geju_tg = _ten_god(bchart.day_master, month_main)
                if geju_tg:
                    evidences.append(EngineEvidence(
                        engine=self.engine_name,
                        rule_id="ZP_GEJU",
                        value=f"{geju_tg}格",
                        temporal_scope=TemporalScope.BIRTH,
                        attributes={"month_branch": month_branch, "ten_god": geju_tg},
                    ))

            # 调候主用神(《穷通宝鉴》)
            if sr.tiaohou_primary:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_TIAHOU_PRIMARY",
                    value=list(sr.tiaohou_primary),
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"source": "穷通宝鉴"},
                ))

            # 调候次用神
            if sr.tiaohou_secondary:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_TIAHOU_SECONDARY",
                    value=list(sr.tiaohou_secondary),
                    temporal_scope=TemporalScope.BIRTH,
                ))

            # 扶抑喜用
            from tongshu.engines.strength_engine import _SUPPORT_ELEMENTS, _DRAIN_ELEMENTS
            from tongshu.engines.bazi_engine import STEM_ELEMENT
            dm_el = STEM_ELEMENT.get(bchart.day_master, "")
            wangshuai = sr.verdict or ""
            if "身强" in wangshuai or "从强" in wangshuai:
                fuyi_xi = sorted(_DRAIN_ELEMENTS.get(dm_el, set()))
                fuyi_ji = sorted(_SUPPORT_ELEMENTS.get(dm_el, set()))
            elif "身弱" in wangshuai or "从弱" in wangshuai:
                fuyi_xi = sorted(_SUPPORT_ELEMENTS.get(dm_el, set()))
                fuyi_ji = sorted(_DRAIN_ELEMENTS.get(dm_el, set()))
            else:
                fuyi_xi = fuyi_ji = []
            if fuyi_xi:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_FUYI_XI",
                    value=fuyi_xi,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"method": "扶抑"},
                ))
            if fuyi_ji:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_FUYI_JI",
                    value=fuyi_ji,
                    temporal_scope=TemporalScope.BIRTH,
                ))

            # 五行失衡
            if bchart.five_element_imbalance:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_FIVE_ELEMENT_IMBALANCE",
                    value=True,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"balance": bchart.five_element_balance or {}},
                ))

            # 配偶星受克
            if bchart.spouse_star_attack and bchart.spouse_star_attack != "none":
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_SPOUSE_STAR_ATTACK",
                    value=bchart.spouse_star_attack,
                    temporal_scope=TemporalScope.BIRTH,
                ))

            # 官杀混杂
            if bchart.officer_mixed:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_OFFICER_MIXED",
                    value=True,
                    temporal_scope=TemporalScope.BIRTH,
                ))

            # 日支冲/害
            if bchart.day_branch_clash:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_DAY_BRANCH_CLASH",
                    value=bchart.day_branch_clash,
                    temporal_scope=TemporalScope.BIRTH,
                ))
            if bchart.day_branch_harm:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="ZP_DAY_BRANCH_HARM",
                    value=bchart.day_branch_harm,
                    temporal_scope=TemporalScope.BIRTH,
                ))

        except Exception:
            pass
        return evidences


# ═══════════════════════════════════════════════════════════════════
# 盲派 Adapter
# ═══════════════════════════════════════════════════════════════════

class BlindSchoolAdapter(BaseEngineAdapter):
    """盲派适配器. 本位: 做功结构/宾主体用/刑冲合害墓库/应期."""

    engine_name = EngineName.BLIND_SCHOOL

    def produce_evidence(self, inp, chart, context=None) -> list[EngineEvidence]:
        context = context or {}
        evidences: list[EngineEvidence] = []
        try:
            birth = context.get("birth")
            if birth is None:
                return evidences
            gender = birth[4] if len(birth) > 4 else "male"
            pillars = birth[:4]

            from tongshu.engines.blind_bazi_engine import BlindBaziEngine
            res = BlindBaziEngine().compute(pillars, gender=gender)

            # 做功类型
            if res.zuo_gong_type:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="BS_ZUO_GONG_TYPE",
                    value=res.zuo_gong_type,
                    temporal_scope=TemporalScope.BIRTH,
                ))

            # 体(日主一方)
            if res.ti_stems:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="BS_TI_STEMS",
                    value=list(res.ti_stems),
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"role": "体"},
                ))

            # 用(财官一方)
            if res.yong_stems:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="BS_YONG_STEMS",
                    value=list(res.yong_stems),
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"role": "用"},
                ))

            # 盲派信号(逐条提取, 不含方向)
            for i, sig in enumerate(res.signals or []):
                sig_val = getattr(sig, "value", None) or str(sig)
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id=f"BS_SIGNAL_{i:03d}",
                    value=sig_val,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"signal_type": getattr(sig, "type", "")},
                ))

            # 焦点年份应期
            focus_years = context.get("focus_years", [])
            if focus_years:
                try:
                    from tongshu.engines.blind_yingqi import BlindYingqiEngine
                    yq = BlindYingqiEngine()
                    for yr in focus_years:
                        try:
                            analysis = yq.analyze(pillars, gender, target_year=yr)
                            for j, ev in enumerate(analysis.yingqi_events or []):
                                evidences.append(EngineEvidence(
                                    engine=self.engine_name,
                                    rule_id=f"BS_YINGQI_{yr}_{j:03d}",
                                    value=ev.get("event", str(ev)),
                                    temporal_scope=TemporalScope.YEAR,
                                    attributes={"year": yr, "raw": ev},
                                ))
                        except Exception:
                            pass
                except Exception:
                    pass

        except Exception:
            pass
        return evidences


# ═══════════════════════════════════════════════════════════════════
# 紫微斗数 Adapter
# ═══════════════════════════════════════════════════════════════════

class ZiWeiAdapter(BaseEngineAdapter):
    """紫微斗数适配器. 本位: 命宫主星/12宫细象/四化飞布/大限流年."""

    engine_name = EngineName.ZI_WEI

    # 核心宫位(用于提取纯事实, 不做吉凶判断)
    _CORE_PALACES = [
        ("命宫", "ZW_MING_GONG"),
        ("财帛", "ZW_CAIBO_GONG"),
        ("官禄", "ZW_GUANLU_GONG"),
        ("迁移", "ZW_QIANYI_GONG"),
        ("夫妻", "ZW_FUQI_GONG"),
        ("疾厄", "ZW_JIE_GONG"),
        ("福德", "ZW_FUDE_GONG"),
        ("田宅", "ZW_TIANZHAI_GONG"),
        ("子女", "ZW_ZINV_GONG"),
        ("交友", "SW_JIAOYOU_GONG"),
        ("父母", "ZW_FUMU_GONG"),
        ("兄弟", "ZW_XIONGDI_GONG"),
    ]

    def produce_evidence(self, inp, chart, context=None) -> list[EngineEvidence]:
        context = context or {}
        evidences: list[EngineEvidence] = []
        try:
            birth = context.get("birth")
            if birth is None:
                return evidences
            y, mo, d, h = birth[:4]
            gender = birth[4] if len(birth) > 4 else "male"

            from lunar_python import Solar
            solar = Solar.fromYmdHms(y, mo, d, h, 0, 0)
            lunar = solar.getLunar()
            lunar_date = (lunar.getYear(), abs(lunar.getMonth()), lunar.getDay())

            from tongshu.engines.ziwei_engine import ZiweiEngine
            eng = ZiweiEngine()
            full = eng.full_chart(lunar_date, h, gender=gender)
            palaces = full.get("palaces", {})

            # 各宫主星/辅星(纯事实, 不做吉凶计数)
            for gong_key, rule_id in self._CORE_PALACES:
                g = palaces.get(gong_key, {})
                major = g.get("major", [])
                minor = g.get("minor", [])
                if major:
                    evidences.append(EngineEvidence(
                        engine=self.engine_name,
                        rule_id=f"{rule_id}_MAJOR",
                        value=list(major),
                        temporal_scope=TemporalScope.BIRTH,
                        attributes={"palace": gong_key},
                    ))
                if minor:
                    evidences.append(EngineEvidence(
                        engine=self.engine_name,
                        rule_id=f"{rule_id}_MINOR",
                        value=list(minor),
                        temporal_scope=TemporalScope.BIRTH,
                        attributes={"palace": gong_key},
                    ))

            # 生年四化(从命盘提取)
            sihua = full.get("sihua", {})
            if sihua:
                for hua_name, hua_target in sihua.items():
                    evidences.append(EngineEvidence(
                        engine=self.engine_name,
                        rule_id=f"ZW_SIHUA_{hua_name}",
                        value=hua_target,
                        temporal_scope=TemporalScope.BIRTH,
                        attributes={"transformation": hua_name},
                    ))

            # 焦点年份大限四化
            focus_years = context.get("focus_years", [])
            if focus_years:
                try:
                    zw_chart = eng.compute(lunar_date, h, gender=gender)
                    for yr in focus_years:
                        try:
                            yr_dir = eng.native_direction_for_year(
                                zw_chart, lunar_date, h, gender, yr)
                            evidences.append(EngineEvidence(
                                engine=self.engine_name,
                                rule_id=f"ZW_DAYUN_{yr}",
                                value=yr_dir,
                                temporal_scope=TemporalScope.YEAR,
                                attributes={"year": yr},
                            ))
                        except Exception:
                            pass
                except Exception:
                    pass

        except Exception:
            pass
        return evidences


# ═══════════════════════════════════════════════════════════════════
# 河洛理数 Adapter
# ═══════════════════════════════════════════════════════════════════

class HeLuoAdapter(BaseEngineAdapter):
    """河洛理数适配器. 本位: 先天卦/元堂/后天卦/大运流年卦."""

    engine_name = EngineName.HE_LUO

    def produce_evidence(self, inp, chart, context=None) -> list[EngineEvidence]:
        context = context or {}
        evidences: list[EngineEvidence] = []
        try:
            bazi = context.get("bazi")
            gender = context.get("gender", "male")
            birth_hour = context.get("birth_hour", "子")
            birth_year = context.get("birth_year")

            if bazi is None or birth_year is None:
                return evidences

            from tongshu.engines.heluo.canonical import HeluoCanonical
            result = HeluoCanonical().calculate(
                bazi=bazi, gender=gender, birth_hour=birth_hour,
                era="zhong", birth_year=birth_year,
            )

            # 先天卦
            if result.prenatal and result.prenatal.hexagram_name:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="HL_PRENATAL_HEXAGRAM",
                    value=result.prenatal.hexagram_name,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"layer": "先天"},
                ))

            # 元堂
            if result.yuantang and result.yuantang.yuantang:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="HL_YUANTANG",
                    value=result.yuantang.yuantang,
                    temporal_scope=TemporalScope.BIRTH,
                ))

            # 后天卦
            if result.postnatal and result.postnatal.hexagram_name:
                evidences.append(EngineEvidence(
                    engine=self.engine_name,
                    rule_id="HL_POSTNATAL_HEXAGRAM",
                    value=result.postnatal.hexagram_name,
                    temporal_scope=TemporalScope.BIRTH,
                    attributes={"layer": "后天"},
                ))

            # 流年卦
            if result.timeline and result.timeline.yearly_hexagrams:
                for entry in result.timeline.yearly_hexagrams:
                    yr = entry.get("year")
                    hex_name = entry.get("hexagram")
                    if yr and hex_name:
                        evidences.append(EngineEvidence(
                            engine=self.engine_name,
                            rule_id=f"HL_YEAR_HEXAGRAM_{yr}",
                            value=hex_name,
                            temporal_scope=TemporalScope.YEAR,
                            attributes={"year": yr},
                        ))

        except Exception:
            pass
        return evidences


# ═══════════════════════════════════════════════════════════════════
# 易经 Adapter
# ═══════════════════════════════════════════════════════════════════

class YiJingAdapter(BaseEngineAdapter):
    """易经适配器. 本位: 卦辞/爻辞/大象传/人间道/决策建议.

    易经引擎是数据查询层, 基于河洛卦象结果查询易经文本数据.
    """

    engine_name = EngineName.YI_JING

    def produce_evidence(self, inp, chart, context=None) -> list[EngineEvidence]:
        context = context or {}
        evidences: list[EngineEvidence] = []
        try:
            # 从context或河洛结果获取卦名
            hex_names = context.get("yi_hexagrams", [])
            if not hex_names:
                # 尝试从河洛adapter结果获取
                heluo_evs = context.get("_heluo_evidences", [])
                for ev in heluo_evs:
                    if isinstance(ev, EngineEvidence) and ev.rule_id.startswith("HL_"):
                        if isinstance(ev.value, str) and ev.value not in hex_names:
                            hex_names.append(ev.value)

            from tongshu.engines.yi.classical_text import get_classical_text
            from tongshu.engines.yi.gua_four_dim_loader import (
                get_gua_ci, get_daxiang, get_baihua, get_renjian,
            )

            for hex_name in hex_names:
                if not hex_name:
                    continue
                # 卦辞
                try:
                    gua_ci = get_gua_ci(hex_name)
                    if gua_ci:
                        evidences.append(EngineEvidence(
                            engine=self.engine_name,
                            rule_id=f"YJ_GUACI_{hex_name}",
                            value=gua_ci,
                            temporal_scope=TemporalScope.BIRTH,
                            attributes={"hexagram": hex_name, "type": "卦辞"},
                        ))
                except Exception:
                    pass
                # 大象传
                try:
                    daxiang = get_daxiang(hex_name)
                    if daxiang:
                        evidences.append(EngineEvidence(
                            engine=self.engine_name,
                            rule_id=f"YJ_DAXIANG_{hex_name}",
                            value=daxiang,
                            temporal_scope=TemporalScope.BIRTH,
                            attributes={"hexagram": hex_name, "type": "大象传"},
                        ))
                except Exception:
                    pass
                # 人间道
                try:
                    renjian = get_renjian(hex_name, max_len=200)
                    if renjian:
                        evidences.append(EngineEvidence(
                            engine=self.engine_name,
                            rule_id=f"YJ_RENJIAN_{hex_name}",
                            value=renjian,
                            temporal_scope=TemporalScope.BIRTH,
                            attributes={"hexagram": hex_name, "type": "人间道"},
                        ))
                except Exception:
                    pass

        except Exception:
            pass
        return evidences


# ═══════════════════════════════════════════════════════════════════
# Adapter 注册表
# ═══════════════════════════════════════════════════════════════════

ADAPTER_REGISTRY: dict[EngineName, type[BaseEngineAdapter]] = {
    EngineName.ZI_PING: ZiPingAdapter,
    EngineName.BLIND_SCHOOL: BlindSchoolAdapter,
    EngineName.ZI_WEI: ZiWeiAdapter,
    EngineName.HE_LUO: HeLuoAdapter,
    EngineName.YI_JING: YiJingAdapter,
}


def get_adapter(engine: EngineName) -> BaseEngineAdapter:
    """获取引擎适配器实例."""
    cls = ADAPTER_REGISTRY.get(engine)
    if cls is None:
        raise ValueError(f"Unknown engine: {engine}")
    return cls()


def produce_all_evidence(inp, chart, context=None) -> dict[EngineName, list[EngineEvidence]]:
    """一次性产出所有引擎的统一证据.

    Returns:
        {engine_name: [EngineEvidence, ...]}
    """
    context = context or {}
    result: dict[EngineName, list[EngineEvidence]] = {}
    for name, adapter_cls in ADAPTER_REGISTRY.items():
        try:
            adapter = adapter_cls()
            evs = adapter.produce_evidence(inp, chart, context)
            if evs:
                result[name] = evs
        except Exception:
            result[name] = []
    return result


__all__ = [
    "ZiPingAdapter",
    "BlindSchoolAdapter",
    "ZiWeiAdapter",
    "HeLuoAdapter",
    "YiJingAdapter",
    "ADAPTER_REGISTRY",
    "get_adapter",
    "produce_all_evidence",
]
