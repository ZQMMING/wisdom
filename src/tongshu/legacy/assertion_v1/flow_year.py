# -*- coding: utf-8 -*-
"""P3 Flow-Year Assertion Producer（断事断言层，固化 v3 能力）。

把 EVENT_TOPIC 多流年信号 → 结构化 Assertion：
  - 输入边界（Rule 01）：仅依赖 birth_datetime + 系统计算的排盘/时间变量
  - 单体系（EVENT_TOPIC）信号，置信最高 LIKELY（契约 §9，不越级 SUPPORTED）
  - 聚焦信号叠加最强的关键年份，给出规则机制 + 方向（polarity）+ 古籍证据
  - 不做前端表达；只产出可审计的 Assertion（mechanism/time/evidence/direction）

== 经典依据 ==
  每条规则自带 evidence_refs（E-K2G 证据链），此处透传不重写。
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from tongshu.assertion.contract import (
    Assertion,
    AssertionInput,
    AssertionType,
    Confidence,
    Direction,
    EvidenceRef,
    StateKind,
    insufficient_evidence,
)
from tongshu.engines.bazi_engine import BaziEngine, BaziChart
from tongshu.reasoning.event_topic import EventTopicEngine
from tongshu.reasoning.rule_loader import RuleLoader
from tongshu.engines.annual_event_evaluator import HeluoScorer, YiScorer
from tongshu.engines.blind_bazi_engine import BlindBaziEngine
from tongshu.engines.blind_yingqi import BlindYingqiEngine
from tongshu.engines.ziwei_engine import ZiweiEngine

# 静态健康基线前缀（每年都触发的背景信号，不计入年度焦点，避免虚高）
STATIC_PREFIX = ("ETP-HLT", "ETP-SX", "ETP-TH")
# 评估窗口：命主 35–55 岁（中年阶段，断事窗口）
WINDOW_AGE_MIN, WINDOW_AGE_MAX = 35, 55
FOCUS_YEARS_MAX = 5


def _default_rules() -> list[dict]:
    """默认加载 data/rules 全部规则（RuleLoader 是唯一规则源）。"""
    here = Path(__file__).resolve().parents[3]  # src/tongshu/assertion -> backend
    loader = RuleLoader(data_dir=here / "data", schema_dir=here / "data" / "schemas")
    return loader.rules


def _birth_year(inp: AssertionInput, chart: BaziChart) -> int:
    """从输入/排盘解析出生年。优先 inp.birth_datetime（ISO8601）。"""
    if inp.birth_datetime:
        try:
            return datetime.fromisoformat(inp.birth_datetime.replace("Z", "+00:00")).year
        except ValueError:
            pass
    # fallback: 尝试从 chart 元数据取
    y = getattr(chart, "birth_year", None)
    if y:
        return int(y)
    raise ValueError("cannot resolve birth year from input/chart")


def _resolve_rules(context: dict) -> list[dict]:
    rules = context.get("rules")
    if rules is None:
        rules = _default_rules()
    return rules


class FlowYearAssertionProducer:
    """断事断言 Producer：subject=flow_year，输出流年时间窗口断言。"""

    subject = "flow_year"

    def __init__(self, rules: list[dict] | None = None) -> None:
        self._rules = rules if rules is not None else _default_rules()
        self._engine = EventTopicEngine(self._rules)
        self._rule_map = {r.get("rule_id"): r for r in self._rules}
        self._heluo = HeluoScorer()
        self._yi = YiScorer()
        self._blind = BlindBaziEngine()
        self._blind_yingqi = BlindYingqiEngine()
        self._ziwei = ZiweiEngine()

    # ---- 盲派方向（本命结构倾向） ----
    def _blind_dir(self, birth) -> str:
        if birth is None:
            return "neutral"
        res = self._blind.compute(birth[:4], gender=birth[4] if len(birth) > 4 else "male")
        opp, caut = 0, 0
        for s in res.signals:
            d = getattr(s, "direction", None)
            val = getattr(d, "value", d)
            if val == "POSITIVE":
                opp += 1
            elif val == "NEGATIVE":
                caut += 1
        return "caution" if caut > opp else "opportunity" if opp > caut else "neutral"

    # ---- 盲派应期方向（动态：焦点年份冲穿合三刑墓库开闭引动） ----
    def _blind_yingqi_dir(self, birth, years: list[int]) -> str:
        """盲派应期引擎对每个焦点年份分析引动事件, 统计NEGATIVE/POSITIVE得出年度方向.

        盲派应期三法: 大限应期/禄原身应期/遁藏透干应期 + 运年引动(冲穿合三刑墓库开闭).
        穿倒主位/三刑主位=caution; 合入主位/冲开墓库/三合局=opportunity.
        """
        if birth is None or not years:
            return "neutral"
        gender = birth[4] if len(birth) > 4 else "male"
        c, o = 0, 0
        for y in years:
            try:
                r = self._blind_yingqi.analyze(birth[:4], gender, target_year=y)
                neg = sum(1 for e in r.yingqi_events if e.get("direction") == "NEGATIVE")
                pos = sum(1 for e in r.yingqi_events if e.get("direction") == "POSITIVE")
                # 主位NEGATIVE(穿倒/三刑主位)权重加倍
                main_neg = sum(1 for e in r.yingqi_events
                               if e.get("direction") == "NEGATIVE" and e.get("strength", 0) >= 0.7)
                if (neg + main_neg) > pos:
                    c += 1
                elif pos > (neg + main_neg):
                    o += 1
            except Exception:
                pass
        return "caution" if c > o else "opportunity" if o > c else "neutral"

    # ---- 紫微方向（命宫主星 + 大限四化） ----
    def _ziwei_dir(self, birth, focus_years=None) -> str:
        """紫微本命方向倾向. V2.6修复: 传hour(0-23)而非ti(时辰index),
        避免compute内部time_index_from_hour双重转换导致时辰错位.
        V2.6升级: 支持按焦点年份取对应大限四化(native_direction_for_year).
        """
        if birth is None:
            return "neutral"
        try:
            from lunar_python import Solar
            y, mo, d, h = birth[:4]
            solar = Solar.fromYmdHms(y, mo, d, h, 0, 0)
            lunar = solar.getLunar()
            g = birth[4] if len(birth) > 4 else "male"
            # V2.6 fix: 传h(小时)而非ti, compute内部会做time_index_from_hour
            lunar_date = (lunar.getYear(), lunar.getMonth(), lunar.getDay())
            chart = self._ziwei.compute(lunar_date, h, gender=g)
            # V2.6: 按焦点年份取对应大限四化(取第一个焦点年份代表)
            if focus_years:
                return self._ziwei.native_direction_for_year(
                    chart, lunar_date, h, g, focus_years[0])
            return self._ziwei.native_direction(chart)
        except Exception:
            return "neutral"

    # ---- 多体系方向 ----
    @staticmethod
    def _year_system_direction(disaster: float, wealth: float, threshold: float = 0.6) -> str:
        """单体系单年方向：灾>财→caution；财>灾→opportunity；接近→neutral。"""
        if disaster > wealth + threshold:
            return "caution"
        if wealth > disaster + threshold:
            return "opportunity"
        return "neutral"

    def _heluo_dir(self, chart, years: list[int], birth=None) -> str:
        """河洛方向. V3: 优先使用实际河洛流年卦吉凶方向, 无birth时fallback到数理.

        birth=(year, month, day, hour, gender)
        """
        c, o = 0, 0
        for y in years:
            if birth is not None:
                # V3: 使用实际河洛流年卦吉凶方向
                direction = self._heluo.score_year_direction(
                    birth[0], birth[1], birth[2], birth[3], birth[4], y)
                if direction > 0.2:
                    o += 1
                elif direction < -0.2:
                    c += 1
            else:
                # fallback: 数理模运算
                d = self._year_system_direction(
                    self._heluo.score_disaster(chart, (y - 4) % 60, y),
                    self._heluo.score_wealth(chart, (y - 4) % 60, y),
                )
                if d == "caution":
                    c += 1
                elif d == "opportunity":
                    o += 1
        return "caution" if c > o else "opportunity" if o > c else "neutral"

    def _yi_dir(self, chart, years: list[int], birth=None) -> str:
        """易经方向. V3: 优先使用实际易经卦象吉凶方向, 无birth时fallback到年干五行.

        birth=(year, month, day, hour, gender)
        """
        if getattr(self._yi, "yi_available", False) is False:
            return "neutral"
        c, o = 0, 0
        for y in years:
            if birth is not None:
                # V3: 使用实际易经卦象吉凶方向
                direction = self._yi.score_year_direction(
                    birth[0], birth[1], birth[2], birth[3], birth[4], y)
                if direction > 0.2:
                    o += 1
                elif direction < -0.2:
                    c += 1
            else:
                # fallback: 年干五行
                d = self._year_system_direction(
                    self._yi.score_disaster(chart, y),
                    self._yi.score_wealth(chart, y),
                    threshold=0.3,
                )
                if d == "caution":
                    c += 1
                elif d == "opportunity":
                    o += 1
        return "caution" if c > o else "opportunity" if o > c else "neutral"

    def produce(self, inp: AssertionInput, chart, context: dict | None = None) -> Assertion:
        context = context or {}
        if chart is None:
            return insufficient_evidence(self.subject, "chart is None")
        rules = _resolve_rules(context)
        if rules is not self._rules:
            self._rules = rules
            self._engine = EventTopicEngine(rules)
            self._rule_map = {r.get("rule_id"): r for r in rules}

        try:
            birth_y = _birth_year(inp, chart)
        except ValueError as exc:
            return insufficient_evidence(self.subject, str(exc))

        start = birth_y + WINDOW_AGE_MIN
        end = birth_y + WINDOW_AGE_MAX

        # ---- 1. 多流年 EVENT_TOPIC 动态信号扫描 ----
        year_dyn: dict[int, list] = {}
        for y in range(start, end + 1):
            sigs = self._engine.match(chart, year=y)
            dyn = [s for s in sigs if not s.signal_id.startswith(STATIC_PREFIX)]
            if dyn:
                year_dyn[y] = dyn

        if not year_dyn:
            return insufficient_evidence(self.subject, "no dynamic EVENT_TOPIC signal in window")

        # ---- 2. 聚焦信号叠加最强的年份（去相邻重复） ----
        ranked = sorted(year_dyn.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        focus: list[tuple[int, list]] = []
        for y, dyn in ranked:
            if focus and abs(y - focus[-1][0]) <= 1 and len(focus[-1][1]) >= len(dyn):
                continue
            focus.append((y, dyn))
            if len(focus) >= FOCUS_YEARS_MAX:
                break

        # ---- 3. 汇总机制 / 方向 / 证据 ----
        mech_lines: list[str] = []
        evidence: list[EvidenceRef] = []
        n_opportunity, n_caution = 0, 0
        seen_refs: set[str] = set()
        for y, dyn in focus:
            items = []
            for s in dyn[:6]:
                rid = s.rule_refs[0] if s.rule_refs else s.signal_id
                r = self._rule_map.get(rid, {})
                title = r.get("title", "") or rid
                pol = s.polarity
                if pol == "opportunity":
                    n_opportunity += 1
                elif pol == "caution":
                    n_caution += 1
                items.append(f"{title}")
                if rid not in seen_refs:
                    seen_refs.add(rid)
                    evidence.append(EvidenceRef(system="event_topic", signal_ref=rid))
            mech_lines.append(f"{y}年：{'；'.join(items)}")
        mechanism = "流年触发机制：" + "；".join(mech_lines)

        # ---- 4. 跨体系收敛裁定 ----
        et_dir = ("opportunity" if n_opportunity > n_caution
                  else "caution" if n_caution > n_opportunity else "neutral")
        # 解析出生信息(供河洛/易经/盲派使用)
        birth_info = None
        if inp.birth_datetime:
            try:
                from datetime import datetime as _dt
                _d = _dt.fromisoformat(inp.birth_datetime.replace("Z", "+00:00"))
                g = "female" if getattr(inp, "_gender", None) == "female" else "male"
                birth_info = (_d.year, _d.month, _d.day, _d.hour, g)
            except ValueError:
                pass
        heluo_dir = self._heluo_dir(chart, [y for y, _ in focus], birth=birth_info)
        yi_dir = self._yi_dir(chart, [y for y, _ in focus], birth=birth_info)
        # 盲派：本命结构方向（静态倾向）
        blind_dir = self._blind_dir(birth_info)
        # 盲派应期方向(动态): 对焦点年份用应期引擎分析冲穿合三刑墓库开闭
        blind_yingqi_dir = self._blind_yingqi_dir(birth_info, [y for y, _ in focus])
        # 综合: 应期方向非neutral时以应期为准(动态年度针对性强于静态本命); 否则用本命方向
        blind_dir_combined = blind_dir if blind_yingqi_dir == "neutral" else blind_yingqi_dir
        ziwei_dir = self._ziwei_dir(birth_info, focus_years=[y for y, _ in focus])

        # V3: 倪海厦"命好不如限好" — 分离大运(限)和流年体系
        # 大运(限)体系: 紫微大限四化 + 盲派本命结构(静态/十年维度)
        # 流年体系: event_topic + 河洛流年卦 + 易经流年卦名 + 盲派应期(动态/年度维度)
        dayun_sys_dirs = {"ziwei_dayun": ziwei_dir, "blind_native": blind_dir}
        liunian_sys_dirs = {"event_topic": et_dir, "heluo": heluo_dir,
                             "yi": yi_dir, "blind_yingqi": blind_yingqi_dir}

        def _majority_dir(sys_dirs: dict) -> tuple[Direction, list[str], list[str]]:
            """多数体系方向收敛. 返回(方向, 同向体系, 反向体系)."""
            opp = [s for s, d in sys_dirs.items() if d == "opportunity"]
            caut = [s for s, d in sys_dirs.items() if d == "caution"]
            if len(opp) > len(caut):
                return Direction.POSITIVE, opp, caut
            if len(caut) > len(opp):
                return Direction.NEGATIVE, caut, opp
            return Direction.NEUTRAL, [], []

        # 大运方向(限)
        dayun_dir, dayun_agree, dayun_comp = _majority_dir(dayun_sys_dirs)
        # 流年方向
        liunian_dir, liunian_agree, liunian_comp = _majority_dir(liunian_sys_dirs)

        # V3: 综合方向 = 大运*0.6 + 流年*0.4 (命好不如限好, 大运为主)
        DAYUN_W = 0.6
        LIUNIAN_W = 0.4
        def _dir_score(d: Direction) -> float:
            return 1.0 if d == Direction.POSITIVE else (-1.0 if d == Direction.NEGATIVE else 0.0)
        combined_score = _dir_score(dayun_dir) * DAYUN_W + _dir_score(liunian_dir) * LIUNIAN_W
        if combined_score > 0.1:
            direction, state = Direction.POSITIVE, StateKind.ACTIVATION
        elif combined_score < -0.1:
            direction, state = Direction.NEGATIVE, StateKind.SUPPRESSION
        else:
            direction, state = Direction.NEUTRAL, StateKind.STABLE

        # 置信度: 大运+流年同向且各有>=2体系 → SUPPORTED; 否则 LIKELY
        all_agree = dayun_agree + liunian_agree
        if len(all_agree) >= 2 and dayun_dir == liunian_dir and dayun_dir != Direction.NEUTRAL:
            confidence = Confidence.SUPPORTED
        else:
            confidence = Confidence.LIKELY
        agreeing = all_agree if direction != Direction.NEUTRAL else []
        comp_sys = dayun_comp + liunian_comp

        # V3: 建设性建议(画险趋吉)
        if direction == Direction.NEGATIVE:
            advice = (
                "画险趋吉：此限/年以守成为主，忌冒险投资或重大变动；"
                "进德修业、积累实力，待限运转好再图进取。"
                f"（大运{dayun_dir.value}权重{DAYUN_W}，流年{liunian_dir.value}权重{LIUNIAN_W}）"
            )
        elif direction == Direction.POSITIVE:
            advice = (
                "利建侯：此限/年运势向好，宜主动出击、广结善缘、建立事业基础；"
                "但需戒盛，吉处藏凶，保持警戒心。"
                f"（大运{dayun_dir.value}权重{DAYUN_W}，流年{liunian_dir.value}权重{LIUNIAN_W}）"
            )
        else:
            advice = (
                "中平之年：宜稳扎稳打，不宜大进大退；"
                "观察大势，积累资源，等待明确方向出现。"
                f"（大运{dayun_dir.value}权重{DAYUN_W}，流年{liunian_dir.value}权重{LIUNIAN_W}）"
            )
        # 证据：SUPPORTED 时同向体系 agrees=True；否则保持 event_topic 引用
        if agreeing:
            evidence = [
                EvidenceRef(system=e.system, signal_ref=e.signal_ref,
                            agrees=(e.system in agreeing))
                for e in evidence
            ]
            for sys_name in ("heluo", "yi", "blind", "ziwei"):
                if sys_name in agreeing:
                    evidence.append(
                        EvidenceRef(system=sys_name, signal_ref=f"{sys_name}-yearly", agrees=True)
                    )
        else:
            evidence = [
                EvidenceRef(system=e.system, signal_ref=e.signal_ref) for e in evidence
            ]
        # 互补提示体系：方向相反但保留（agrees=False 标记为互补维度，非否定）
        for sys_name in comp_sys:
            evidence.append(
                EvidenceRef(system=sys_name, signal_ref=f"{sys_name}-yearly", agrees=False)
            )
        conv_note = (
            f"；跨体系收敛(V3大运权重): 大运(限)={dayun_dir.value}(紫微大限{ziwei_dir}/盲派本命{blind_dir}), "
            f"流年={liunian_dir.value}(event_topic={et_dir}/河洛{heluo_dir}/易经{yi_dir}/盲派应期{blind_yingqi_dir}), "
            f"综合={direction.value}(大运{DAYUN_W}+流年{LIUNIAN_W}), 主导={agreeing or '无'}, 互补={comp_sys or '无'}, 置信={confidence.value}"
        )
        mechanism = mechanism + conv_note

        time_desc = (
            f"评估窗口 {start}–{end}（命主 {WINDOW_AGE_MIN}–{WINDOW_AGE_MAX} 岁）；"
            f"焦点年份：{'/'.join(str(y) for y, _ in focus)}"
        )

        return Assertion(
            subject=self.subject,
            assertion_type=AssertionType.TIMING_WINDOW,
            state=state,
            direction=direction,
            mechanism=mechanism,
            time=time_desc,
            evidence=tuple(evidence),
            confidence=confidence,   # 大运+流年同向且>=2体系→SUPPORTED；否则 LIKELY
            abstain=False,
            dayun_direction=dayun_dir,
            liunian_direction=liunian_dir,
            dayun_weight=DAYUN_W,
            liunian_weight=LIUNIAN_W,
            advice=advice,
        )


__all__ = ["FlowYearAssertionProducer"]
