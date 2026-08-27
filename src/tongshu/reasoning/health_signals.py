"""健康确定性信号层 (DISPATCH_HERMES_HEALTH_ACCURACY.md §二).

依据《断事要点提炼与规则制定依据.md》三·健康:
1. 五行→脏腑映射: 木肝、火心、土脾、金肺、水肾(《黄帝内经》藏象+《渊海子平》)
2. 调候失衡: 夏燥缺水、冬寒缺火 → 偏颇(《穷通宝鉴》调候第一等药)
3. 体用失衡(BLIND-002): 体弱不胜用 → 疲惫/筋骨/睡眠
4. 印星为靠山: 印有根则不惧克

方向修正原则(§二.5): 结合 D1 旺衰结论 — 忌神受克=减险, 喜用被冲=加险。
禁止只看"有冲就减分"。

输出全部中间项可审计, 禁止合并为单浮点分掩盖过程。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tongshu.engines.bazi_engine import STEM_ELEMENT
from tongshu.engines.strength_engine import D1StrengthResult, evaluate_strength

# 五行→脏腑映射 (《黄帝内经·素问·阴阳应象大论》; 与 K2G 词库 HLT 规则一致)
ELEMENT_ORGAN = {
    "WOOD": "肝胆",
    "FIRE": "心小肠",
    "EARTH": "脾胃",
    "METAL": "肺大肠",
    "WATER": "肾膀胱",
}

# 调候需求 (《穷通宝鉴》调候框架):
# 寒局(climate=cold)需火暖, 热局(hot)需水润, 燥局(dry)需水润, 湿局(wet)需火/土燥
_CLIMATE_REMEDY = {
    "cold": "FIRE",   # 冬寒喜火
    "hot": "WATER",   # 夏热喜水
    "dry": "WATER",   # 秋燥喜水
    "wet": "EARTH",   # 春湿喜土燥(次取火)
    "neutral": None,
}


@dataclass
class HealthSignalResult:
    """健康信号结果 — 全部中间项可审计。"""
    # 输入快照
    day_master_element: str
    climate: str
    verdict: str                      # D1 旺衰结论: 身强/身弱/从强/从弱

    # 五行脏腑层
    element_balance: dict = field(default_factory=dict)     # {EL: share}
    excess_elements: list[str] = field(default_factory=list)  # 过旺五行 (>0.40)
    deficient_elements: list[str] = field(default_factory=list)  # 过弱五行 (<0.05)
    organ_risks_static: list[str] = field(default_factory=list)
    # 例: ["金过旺→肺大肠偏颇(过旺亦病,《内经》亢害)"]

    # 调候失衡层 (调候字是第一等药——《穷通宝鉴》)
    remedy_element: str | None = None       # 调候所需五行
    remedy_present: bool = False            # 调候字是否在局
    climate_imbalance: bool = False         # 调候缺失 = True
    organ_risk_climate: str | None = None   # 例 "寒局无火→肾膀胱/心小肠寒凝风险"

    # 体用失衡层 (BLIND-002)
    support_count: float = 0.0
    drain_count: float = 0.0
    body_use_imbalance: bool = False        # 身弱且泄耗>生扶*1.3
    body_use_note: str = ""

    def to_dict(self) -> dict:
        return {
            "day_master_element": self.day_master_element,
            "climate": self.climate,
            "verdict": self.verdict,
            "element_balance": self.element_balance,
            "excess_elements": self.excess_elements,
            "deficient_elements": self.deficient_elements,
            "organ_risks_static": list(self.organ_risks_static),
            "remedy_element": self.remedy_element,
            "remedy_present": self.remedy_present,
            "climate_imbalance": self.climate_imbalance,
            "organ_risk_climate": self.organ_risk_climate,
            "support_count": self.support_count,
            "drain_count": self.drain_count,
            "body_use_imbalance": self.body_use_imbalance,
            "body_use_note": self.body_use_note,
        }


_EVIDENCE = {
    "organ_map": "《黄帝内经·素问·阴阳应象大论》: 木生酸,酸生肝…; 与《渊海子平》论疾病章一致",
    "climate": "《穷通宝鉴》调候框架: 调候字是第一等药(盲派五步法·找药引)",
    "body_use": "盲派 BLIND-002: 体弱不胜用 → 疲惫/筋骨/睡眠; 《滴天髓》: 强者宜泄、弱者宜补",
}


def evaluate_health_signals(chart) -> HealthSignalResult:
    """对任意命例输出健康信号全部中间项(调度令 §二 验收)。"""
    from tongshu.engines.bazi_engine import calc_five_element_balance

    d1: D1StrengthResult = evaluate_strength(chart)
    balance, _imbalance_flag = calc_five_element_balance(chart)

    # ---- 五行脏腑层 ----
    excess = [el for el, v in balance.items() if v > 0.40]
    deficient = [el for el, v in balance.items() if v < 0.05]
    organ_static = []
    for el in excess:
        organ_static.append(f"{el}过旺→{ELEMENT_ORGAN[el]}偏颇(《内经》亢则害)")
    for el in deficient:
        organ_static.append(f"{el}过弱→{ELEMENT_ORGAN[el]}失养")

    # ---- 调候失衡层 ----
    remedy = _CLIMATE_REMEDY.get(d1.climate)
    remedy_present = False
    if remedy is not None:
        stems = chart.four_stems()
        branches = chart.four_branches()
        for s in stems:
            if STEM_ELEMENT[s] == remedy:
                remedy_present = True
                break
        if not remedy_present:
            from tongshu.engines.strength_engine import _hidden_stems
            for b in branches:
                for h in _hidden_stems(b):
                    if STEM_ELEMENT[h] == remedy:
                        remedy_present = True
                        break
                if remedy_present:
                    break
    climate_imbalance = remedy is not None and not remedy_present
    organ_climate = None
    if climate_imbalance:
        if d1.climate == "cold":
            organ_climate = "寒局无火→心小肠/肾膀胱寒凝风险(《穷通宝鉴》冬金水寒)"
        elif d1.climate == "hot":
            organ_climate = "热局无水→肾膀胱阴虚燥热风险(夏火土重)"
        elif d1.climate == "dry":
            organ_climate = "燥局无水→肺大肠燥伤风险"
        elif d1.climate == "wet":
            organ_climate = "湿局无土→脾胃湿困风险"

    # ---- 体用失衡层 (BLIND-002) ----
    body_use_imbalance = (
        d1.verdict == "身弱" and d1.support_count * 1.3 < d1.drain_count
    )
    body_use_note = (
        f"体={d1.support_count:.1f}(印比), 用耗={d1.drain_count:.1f}(财官食伤); "
        f"{'不胜用→疲惫/筋骨/睡眠信号' if body_use_imbalance else '体能担用'}"
    ) if d1.verdict == "身弱" else f"旺衰={d1.verdict}, 不入体用失衡判定"

    return HealthSignalResult(
        day_master_element=d1.day_master_element,
        climate=d1.climate,
        verdict=d1.verdict,
        element_balance=dict(balance),
        excess_elements=excess,
        deficient_elements=deficient,
        organ_risks_static=organ_static,
        remedy_element=remedy,
        remedy_present=remedy_present,
        climate_imbalance=climate_imbalance,
        organ_risk_climate=organ_climate,
        support_count=d1.support_count,
        drain_count=d1.drain_count,
        body_use_imbalance=body_use_imbalance,
        body_use_note=body_use_note,
    )


def health_signal_score(result: HealthSignalResult) -> float:
    """将健康信号折算为年度风险权重(仅用于应期排序, 非黑箱总分)。

    权重来源:
      - 调候缺失(第一等药缺): 2.0 —— 但若流年补上调候字则归零(方向正确性)
      - 体用失衡: 1.5
      - 每个脏腑静态风险: 0.8
    方向修正(调度令 §二.5): 由调用方在流年上下文中应用。
    """
    score = 0.0
    if result.climate_imbalance:
        score += 2.0
    if result.body_use_imbalance:
        score += 1.5
    score += 0.8 * len(result.organ_risks_static)
    return score
