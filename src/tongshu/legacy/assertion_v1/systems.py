# -*- coding: utf-8 -*-
"""多体系独立断言Producer (P3 Systems Layer).

每个Producer只输出对应体系的独立断言, 供上层主题断言整合.
- ZiweiAssertionProducer: 紫微斗数断事断言
- BlindAssertionProducer: 盲派应期断言
- HeluoAssertionProducer: 河洛理数卦象断言

契约: 实现 AssertionProducer 协议 (subject + produce).
单体系信号置信最高 LIKELY (契约 §9, 不越级 SUPPORTED).
"""
from __future__ import annotations

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


# ═══════════════════════════════════════════════════════════════════
# 紫微斗数断言Producer
# ═══════════════════════════════════════════════════════════════════

class ZiweiAssertionProducer:
    """紫微斗数独立断言Producer.

    subject=ziwei. 输出紫微命宫主星+大限四化的结构/激活断言.
    单体系, 置信最高 LIKELY.
    """

    subject = "ziwei"

    def __init__(self) -> None:
        from tongshu.engines.ziwei_engine import ZiweiEngine
        self._engine = ZiweiEngine()

    def produce(self, inp: AssertionInput, chart, context: dict | None = None) -> Assertion:
        context = context or {}
        if chart is None:
            return insufficient_evidence(self.subject, "chart is None")

        try:
            from lunar_python import Solar
            birth = context.get("birth")  # (year, month, day, hour, gender)
            if birth is None:
                return insufficient_evidence(self.subject, "no birth info in context")

            y, mo, d, h = birth[:4]
            gender = birth[4] if len(birth) > 4 else "male"
            solar = Solar.fromYmdHms(y, mo, d, h, 0, 0)
            lunar = solar.getLunar()
            lunar_date = (lunar.getYear(), abs(lunar.getMonth()), lunar.getDay())

            zw_chart = self._engine.compute(lunar_date, h, gender=gender)
            full = self._engine.full_chart(lunar_date, h, gender=gender)
            palaces = full.get("palaces", {})

            # V3: 倪海厦"看一个宫一定看三方四正与对面"
            # 命宫三方四正: 命宫 + 财帛 + 官禄 + 迁移(对面)
            SANFANG_SIZHENG = {
                "命宫": "命宫",
                "财帛": "财帛宫(三方)",
                "官禄": "官禄宫(三方)",
                "迁移": "迁移宫(对面)",
            }

            def _gong_stars(gong_key: str) -> str:
                g = palaces.get(gong_key, {})
                major = g.get("major", [])
                minor = g.get("minor", [])
                stars = major + minor
                return "、".join(stars) if stars else "无主星"

            # 命宫主星
            ming_stars = _gong_stars("命宫")
            # 三方四正各宫主星
            sanfang_info = {}
            for gong_key, gong_label in SANFANG_SIZHENG.items():
                sanfang_info[gong_label] = _gong_stars(gong_key)

            # 三方四正吉凶统计: 吉星(禄/权/科/魁/钺/左辅/右弼/文昌/文曲) vs 凶星(忌/羊/陀/火/铃/空/劫)
            JI_STARS = {"禄", "权", "科", "魁", "钺", "左辅", "右弼", "文昌", "文曲", "天魁", "天钺"}
            XIONG_STARS = {"忌", "羊", "陀", "火", "铃", "空", "劫", "擎羊", "陀罗", "火星", "铃星", "地空", "地劫"}

            sanfang_ji = 0
            sanfang_xiong = 0
            for gong_key in SANFANG_SIZHENG:
                g = palaces.get(gong_key, {})
                all_stars = g.get("major", []) + g.get("minor", [])
                for s in all_stars:
                    if any(js in s for js in JI_STARS):
                        sanfang_ji += 1
                    if any(xs in s for xs in XIONG_STARS):
                        sanfang_xiong += 1

            # 紫微本命方向
            direction_str = self._engine.native_direction(zw_chart)
            direction = self._map_direction(direction_str)
            # 三方四正凶多则方向偏负
            if sanfang_xiong > sanfang_ji and direction == Direction.NEUTRAL:
                direction = Direction.NEGATIVE
            elif sanfang_ji > sanfang_xiong and direction == Direction.NEUTRAL:
                direction = Direction.POSITIVE

            # 焦点年份大限四化
            focus_years = context.get("focus_years", [])
            time_desc = ""
            if focus_years:
                year_dir = self._engine.native_direction_for_year(
                    zw_chart, lunar_date, h, gender, focus_years[0])
                time_desc = f"焦点年{focus_years[0]}大限四化方向: {year_dir}"

            # V3: mechanism包含三方四正分析
            sanfang_str = "; ".join(f"{k}={v}" for k, v in sanfang_info.items())
            # V11: 分宫细象(紫微本位: 分领域细分 — 各宫对应各主题领域)
            FEN_GONG = {
                "夫妻": "夫妻宫", "财帛": "财帛宫", "官禄": "官禄宫",
                "疾厄": "疾厄宫", "迁移": "迁移宫",
            }
            fengong_parts = [f"{gl}={_gong_stars(gk)}" for gk, gl in FEN_GONG.items()]
            fengong_str = "; ".join(fengong_parts)
            mechanism = (
                f"紫微命宫{ming_stars}; 本命方向{direction_str}; "
                f"三方四正[{sanfang_str}]; 分宫细象[{fengong_str}]; "
                f"三方吉凶: 吉{sanfang_ji}/凶{sanfang_xiong}"
            )
            if time_desc:
                mechanism += f"; {time_desc}"

            # V3: evidence包含命宫+三方四正
            evidence_list = [
                EvidenceRef(system="ziwei", signal_ref=f"命宫{ming_stars}", agrees=True),
                EvidenceRef(system="ziwei", signal_ref=f"三方四正吉{sanfang_ji}/凶{sanfang_xiong}",
                           agrees=(sanfang_ji >= sanfang_xiong)),
            ]

            # V8: 结构化advice — 基于三方四正吉凶和命宫主星
            from tongshu.assertion.advice_optimizer import (
                AdviceSource, AdviceCategory, make_advice, optimize_advice,
            )
            advice_items = []
            if sanfang_xiong > sanfang_ji:
                advice_items.append(make_advice(
                    content="三方四正凶星偏多, 宜守不宜攻, 避免重大投资/变动",
                    source=AdviceSource.ZIWEI, category=AdviceCategory.CAUTION,
                    priority=4, direction=direction.value, confidence=0.65,
                ))
            elif sanfang_ji > sanfang_xiong:
                advice_items.append(make_advice(
                    content="三方四正吉星汇聚, 可积极进取, 把握机遇",
                    source=AdviceSource.ZIWEI, category=AdviceCategory.ACTION,
                    priority=4, direction=direction.value, confidence=0.65,
                ))
            else:
                advice_items.append(make_advice(
                    content="三方四正吉凶参半, 稳扎稳打, 不宜冒进",
                    source=AdviceSource.ZIWEI, category=AdviceCategory.ACTION,
                    priority=3, direction=direction.value, confidence=0.5,
                ))
            # 化忌提醒
            for gong_key in SANFANG_SIZHENG:
                g = palaces.get(gong_key, {})
                all_stars = g.get("major", []) + g.get("minor", [])
                if any("忌" in s for s in all_stars):
                    advice_items.append(make_advice(
                        content=f"{gong_key}见化忌, 该领域需特别谨慎",
                        source=AdviceSource.ZIWEI, category=AdviceCategory.CAUTION,
                        priority=5, direction=direction.value, confidence=0.7,
                    ))
                    break
            # 焦点年大限四化方向补充
            if time_desc and "negative" in time_desc:
                advice_items.append(make_advice(
                    content="焦点年大限四化偏凶, 该年宜守成避险, 谨慎决策",
                    source=AdviceSource.ZIWEI, category=AdviceCategory.CAUTION,
                    priority=5, direction="negative", confidence=0.7,
                ))
            elif time_desc and "positive" in time_desc:
                advice_items.append(make_advice(
                    content="焦点年大限四化偏吉, 该年可积极进取, 把握机遇",
                    source=AdviceSource.ZIWEI, category=AdviceCategory.ACTION,
                    priority=5, direction="positive", confidence=0.7,
                ))
            optimized = optimize_advice(advice_items, topic=context.get("topic", "general"), max_items=4)
            advice = optimized["text"]
            # 优化统计入mechanism
            stats = optimized["stats"]
            if stats["original_count"] > 0:
                mechanism += (f" | advice优化: {stats['original_count']}→{stats['final_count']}条"
                              f"(去重{stats['deduped_count']}/冲突{stats['conflict_count']}"
                              f"/交叉{stats['cross_validation_score']})")

            # V10: 古籍引用交叉验证 — 紫微依据
            from tongshu.assertion.classical_citations import get_ziwei_citation
            classical_refs = [
                get_ziwei_citation("sanfang_sizheng"),  # 倪海厦: 三方四正
                get_ziwei_citation("ming_gong"),        # 命宫一身之主
            ]
            if focus_years:
                classical_refs.append(get_ziwei_citation("dayun"))  # 命好不如限好
            classical_refs = [c for c in classical_refs if c][:3]

            return Assertion(
                subject=self.subject,
                assertion_type=AssertionType.STRUCTURAL,
                state=StateKind.STABLE if direction == Direction.NEUTRAL else (
                    StateKind.EXPANSION if direction == Direction.POSITIVE else StateKind.CONTRACTION),
                direction=direction,
                mechanism=mechanism,
                time=time_desc,
                evidence=tuple(evidence_list),
                confidence=Confidence.LIKELY,
                abstain=False,
                advice=advice,
                classical_refs=tuple(classical_refs),
            )
        except Exception as exc:
            return insufficient_evidence(self.subject, f"ziwei error: {exc}")

    @staticmethod
    def _map_direction(s: str) -> Direction:
        if s in ("opportunity", "POSITIVE", "positive"):
            return Direction.POSITIVE
        if s in ("caution", "NEGATIVE", "negative"):
            return Direction.NEGATIVE
        return Direction.NEUTRAL


# ═══════════════════════════════════════════════════════════════════
# 盲派应期断言Producer
# ═══════════════════════════════════════════════════════════════════

class BlindAssertionProducer:
    """盲派独立断言Producer.

    subject=blind. 输出盲派本命结构倾向+焦点年份应期引动断言.
    单体系, 置信最高 LIKELY.
    """

    subject = "blind"

    def __init__(self) -> None:
        from tongshu.engines.blind_bazi_engine import BlindBaziEngine
        from tongshu.engines.blind_yingqi import BlindYingqiEngine
        self._blind = BlindBaziEngine()
        self._yingqi = BlindYingqiEngine()

    def produce(self, inp: AssertionInput, chart, context: dict | None = None) -> Assertion:
        context = context or {}
        if chart is None:
            return insufficient_evidence(self.subject, "chart is None")

        try:
            birth = context.get("birth")
            if birth is None:
                return insufficient_evidence(self.subject, "no birth info in context")

            gender = birth[4] if len(birth) > 4 else "male"
            pillars = birth[:4]  # (year, month, day, hour) — 需要转成干支

            # 盲派本命结构倾向
            res = self._blind.compute(pillars, gender=gender)
            opp = sum(1 for s in res.signals
                      if getattr(getattr(s, 'direction', None), 'value', getattr(s, 'direction', None)) == "POSITIVE")
            caut = sum(1 for s in res.signals
                       if getattr(getattr(s, 'direction', None), 'value', getattr(s, 'direction', None)) == "NEGATIVE")
            native_dir = "opportunity" if opp > caut else ("caution" if caut > opp else "neutral")

            # 焦点年份应期引动
            focus_years = context.get("focus_years", [])
            yingqi_desc = ""
            yingqi_neg = yingqi_pos = 0
            if focus_years:
                for y in focus_years:
                    try:
                        yr = self._yingqi.analyze(pillars, gender, target_year=y)
                        for e in yr.yingqi_events:
                            if e.get("direction") == "NEGATIVE":
                                yingqi_neg += 1
                            elif e.get("direction") == "POSITIVE":
                                yingqi_pos += 1
                    except Exception:
                        pass
                if yingqi_neg or yingqi_pos:
                    yingqi_desc = f"焦点年应期: 引动事件{yingqi_neg+yingqi_pos}个(凶{yingqi_neg}/吉{yingqi_pos})"

            direction = Direction.POSITIVE if native_dir == "opportunity" else (
                Direction.NEGATIVE if native_dir == "caution" else Direction.NEUTRAL)
            # 应期凶多则方向偏负
            if yingqi_neg > yingqi_pos:
                direction = Direction.NEGATIVE
            elif yingqi_pos > yingqi_neg and direction == Direction.NEUTRAL:
                direction = Direction.POSITIVE

            mechanism = (
                f"盲派本命做功[{res.zuo_gong_type or '无'}]"
                f"; 宾主体用[体:{'/'.join(res.ti_stems or []) or '无'}/"
                f"用:{'/'.join(res.yong_stems or []) or '无'}]"
                f"; 方向{native_dir}(吉{opp}/凶{caut})"
            )
            if yingqi_desc:
                mechanism += f"; {yingqi_desc}"

            # V8: 结构化advice — 基于盲派应期引动
            from tongshu.assertion.advice_optimizer import (
                AdviceSource, AdviceCategory, make_advice, optimize_advice,
            )
            advice_items = []
            if yingqi_neg > yingqi_pos:
                advice_items.append(make_advice(
                    content="焦点年应期凶多吉少, 宜守成避险, 避免重大决策",
                    source=AdviceSource.BLIND, category=AdviceCategory.CAUTION,
                    priority=4, direction=direction.value, confidence=0.65,
                ))
            elif yingqi_pos > yingqi_neg:
                advice_items.append(make_advice(
                    content="焦点年应期吉象显现, 可积极把握机遇",
                    source=AdviceSource.BLIND, category=AdviceCategory.ACTION,
                    priority=4, direction=direction.value, confidence=0.65,
                ))
            else:
                advice_items.append(make_advice(
                    content="焦点年应期吉凶参半, 稳扎稳打为宜",
                    source=AdviceSource.BLIND, category=AdviceCategory.ACTION,
                    priority=3, direction=direction.value, confidence=0.5,
                ))
            if native_dir == "caution":
                advice_items.append(make_advice(
                    content="本命结构偏凶, 终身宜谨慎行事, 不宜冒进",
                    source=AdviceSource.BLIND, category=AdviceCategory.CAUTION,
                    priority=5, direction="negative", confidence=0.7,
                ))
            elif native_dir == "opportunity":
                advice_items.append(make_advice(
                    content="本命结构偏吉, 可发挥优势, 积极进取",
                    source=AdviceSource.BLIND, category=AdviceCategory.ACTION,
                    priority=5, direction="positive", confidence=0.7,
                ))
            optimized = optimize_advice(advice_items, topic=context.get("topic", "general"), max_items=4)
            advice = optimized["text"]
            # 优化统计入mechanism
            stats = optimized["stats"]
            if stats["original_count"] > 0:
                mechanism += (f" | advice优化: {stats['original_count']}→{stats['final_count']}条"
                              f"(去重{stats['deduped_count']}/冲突{stats['conflict_count']}"
                              f"/交叉{stats['cross_validation_score']})")

            # V10: 古籍引用交叉验证 — 盲派依据
            from tongshu.assertion.classical_citations import get_blind_citation
            classical_refs = [get_blind_citation("binzhu"), get_blind_citation("tiyong")]
            if focus_years:
                classical_refs.append(get_blind_citation("yingqi"))  # 应期口诀
            classical_refs = [c for c in classical_refs if c][:3]

            return Assertion(
                subject=self.subject,
                assertion_type=AssertionType.ACTIVATION,
                state=StateKind.ACTIVATION if focus_years else StateKind.STABLE,
                direction=direction,
                mechanism=mechanism,
                time=yingqi_desc,
                evidence=(EvidenceRef(
                    system="blind",
                    signal_ref=f"本命{native_dir}; 应期凶{yingqi_neg}/吉{yingqi_pos}",
                    agrees=True,
                ),),
                confidence=Confidence.LIKELY,
                abstain=False,
                advice=advice,
                classical_refs=tuple(classical_refs),
            )
        except Exception as exc:
            return insufficient_evidence(self.subject, f"blind error: {exc}")


# ═══════════════════════════════════════════════════════════════════
# 河洛理数断言Producer
# ═══════════════════════════════════════════════════════════════════

class HeluoAssertionProducer:
    """河洛理数独立断言Producer (V4: 64卦四维数据增强).

    subject=heluo. 输出河洛先天卦/元堂/流年卦象断言.
    V4增强: 使用64卦四维验证数据(卦辞/大象传/白话/人间道/占卜道)
    丰富断言内容, 避免只输出卦名而无实质解读.
    单体系, 置信最高 LIKELY.
    """

    subject = "heluo"

    def __init__(self) -> None:
        from tongshu.engines.heluo.canonical import HeluoCanonical
        from tongshu.engines.yi.gua_four_dim_loader import is_available as gua_4dim_available
        self._canonical = HeluoCanonical()
        self._gua_4dim_available = gua_4dim_available()

    def produce(self, inp: AssertionInput, chart, context: dict | None = None) -> Assertion:
        context = context or {}
        if chart is None:
            return insufficient_evidence(self.subject, "chart is None")

        try:
            bazi = context.get("bazi")  # [(干,支),...]
            gender = context.get("gender", "male")
            birth_hour = context.get("birth_hour", "子")
            birth_year = context.get("birth_year")

            if bazi is None or birth_year is None:
                return insufficient_evidence(self.subject, "no bazi/birth_year in context")

            result = self._canonical.calculate(
                bazi=bazi, gender=gender, birth_hour=birth_hour,
                era="zhong", birth_year=birth_year)

            prenatal = result.prenatal.hexagram_name
            yuantang = result.yuantang.yuantang
            postnatal = result.postnatal.hexagram_name

            # V4: 64卦四维数据增强 — 先天卦卦辞+大象传
            from tongshu.engines.yi.gua_four_dim_loader import (
                get_gua_ci, get_daxiang, get_baihua, get_renjian, build_gua_summary,
            )
            prenatal_ci = get_gua_ci(prenatal)
            prenatal_daxiang = get_daxiang(prenatal)
            postnatal_baihua = get_baihua(postnatal, max_len=120)

            # 焦点年份流年卦
            focus_years = context.get("focus_years", [])
            liunian_desc = ""
            liunian_dirs = []
            liunian_advice_parts = []
            if focus_years:
                for y in focus_years:
                    entry = next((e for e in result.timeline.yearly_hexagrams
                                  if e["year"] == y), None)
                    if entry:
                        hex_name = entry["hexagram"]
                        liunian_desc += f"{y}年{hex_name}; "
                        # 简单方向: 凶卦名偏负
                        from tongshu.engines.gua_jixiong import gua_name_direction
                        d = gua_name_direction(hex_name)
                        liunian_dirs.append(d)
                        # V4: 流年卦人间道指引(画险趋吉)
                        renjian = get_renjian(hex_name, max_len=80)
                        if renjian:
                            liunian_advice_parts.append(f"{y}年({hex_name}): {renjian}")

            # 综合方向
            avg_dir = sum(liunian_dirs) / len(liunian_dirs) if liunian_dirs else 0
            direction = Direction.POSITIVE if avg_dir > 0.2 else (
                Direction.NEGATIVE if avg_dir < -0.2 else Direction.NEUTRAL)

            # V4: 丰富mechanism — 先天卦辞+大象传 + 后天白话解读
            mechanism_parts = [f"河洛先天{prenatal}元堂{yuantang}→后天{postnatal}"]
            if prenatal_ci:
                mechanism_parts.append(f"先天卦辞: {prenatal_ci}")
            if prenatal_daxiang:
                mechanism_parts.append(f"大象: {prenatal_daxiang}")
            if postnatal_baihua:
                mechanism_parts.append(f"后天解读: {postnatal_baihua}")
            if liunian_desc:
                mechanism_parts.append(f"流年: {liunian_desc.rstrip('; ')}")
            mechanism = " | ".join(mechanism_parts)

            # V7: 结构化advice优化 — 去重/冲突检测/交叉验证/权重排序
            from tongshu.assertion.advice_optimizer import (
                AdviceItem, AdviceSource, AdviceCategory, optimize_advice, make_advice,
            )
            advice_items: list[AdviceItem] = []

            # 1. 流年卦人间道指引(画险趋吉) — 优先级最高
            for part in liunian_advice_parts:
                advice_items.append(make_advice(
                    content=part,
                    source=AdviceSource.HUMAN_WAY,
                    category=AdviceCategory.ACTION,
                    priority=5,
                    direction=direction.value,
                    confidence=0.7,
                ))

            # 2. 傅佩荣64卦多维度断言(时运/财运/家宅/事业/婚恋/疾病/诉讼)
            try:
                from tongshu.engines.yi.fupeirong_loader import build_advice_from_gua, is_available as fp_available
                if fp_available():
                    # 后天卦多维度建议(终身趋势)
                    postnatal_advice = build_advice_from_gua(postnatal, topics=["wealth", "career", "health"])
                    if postnatal_advice:
                        advice_items.append(make_advice(
                            content=f"后天卦({postnatal})多维度: {postnatal_advice}",
                            source=AdviceSource.FUPEIRONG,
                            category=AdviceCategory.WEALTH,
                            priority=4,
                            direction=direction.value,
                            confidence=0.6,
                        ))
                    # 流年卦多维度建议(焦点年)
                    if focus_years:
                        for y in focus_years:
                            entry = next((e for e in result.timeline.yearly_hexagrams
                                          if e["year"] == y), None)
                            if entry:
                                hex_name = entry["hexagram"]
                                year_advice = build_advice_from_gua(hex_name, topics=["fortune", "wealth"])
                                if year_advice:
                                    advice_items.append(make_advice(
                                        content=f"{y}年({hex_name}): {year_advice}",
                                        source=AdviceSource.FUPEIRONG,
                                        category=AdviceCategory.FORTUNE,
                                        priority=4,
                                        direction=direction.value,
                                        confidence=0.6,
                                    ))
            except Exception:
                pass  # 傅佩荣数据不可用时降级

            # 3. 大师智慧建议(南怀瑾/曾仕强易经哲学)
            try:
                from tongshu.engines.yi.master_wisdom_loader import build_wisdom_advice, is_available as mw_available
                if mw_available():
                    # 根据卦象方向选择主题
                    if direction == Direction.POSITIVE:
                        wisdom_topics = ["自强", "厚德"]
                    elif direction == Direction.NEGATIVE:
                        wisdom_topics = ["知几", "守正"]
                    else:
                        wisdom_topics = ["时位", "变易"]
                    wisdom_text = build_wisdom_advice(wisdom_topics)
                    if wisdom_text:
                        advice_items.append(make_advice(
                            content=wisdom_text,
                            source=AdviceSource.MASTER,
                            category=AdviceCategory.WISDOM,
                            priority=2,
                            direction="neutral",
                            confidence=0.5,
                        ))
            except Exception:
                pass  # 大师智慧数据不可用时降级

            # 4. 兜底: 后天卦白话解读
            if not advice_items and postnatal_baihua:
                advice_items.append(make_advice(
                    content=f"后天卦({postnatal})指引: {postnatal_baihua}",
                    source=AdviceSource.YIJING,
                    category=AdviceCategory.WISDOM,
                    priority=3,
                    direction=direction.value,
                    confidence=0.55,
                ))

            # 5. 优化advice: 去重→冲突检测→交叉验证→权重排序
            topic = context.get("topic", "general")
            optimized = optimize_advice(advice_items, topic=topic, max_items=5)
            advice = optimized["text"]
            # 将优化统计存入mechanism(便于调试)
            stats = optimized["stats"]
            if stats["original_count"] > 0:
                mechanism_parts.append(
                    f"advice优化: 原始{stats['original_count']}条→最终{stats['final_count']}条"
                    f"(去重{stats['deduped_count']}/冲突{stats['conflict_count']}"
                    f"/交叉验证{stats['cross_validation_score']})"
                )
            mechanism = " | ".join(mechanism_parts)

            # V10: 古籍引用交叉验证 — 河洛/易经依据
            from tongshu.assertion.classical_citations import get_heluo_citation, get_yijing_citation
            classical_refs = [
                get_heluo_citation("xiantian"),  # 先天卦为本命
                get_heluo_citation("houtian"),   # 后天卦为运势
                get_yijing_citation("guaci"),    # 《周易》卦辞
            ]
            if focus_years:
                classical_refs.append(get_heluo_citation("liunian"))  # 流年卦
            classical_refs = [c for c in classical_refs if c][:3]

            return Assertion(
                subject=self.subject,
                assertion_type=AssertionType.STRUCTURAL,
                state=StateKind.STABLE,
                direction=direction,
                mechanism=mechanism,
                time=liunian_desc.rstrip('; '),
                evidence=(EvidenceRef(
                    system="heluo",
                    signal_ref=f"先天{prenatal}元堂{yuantang}后天{postnatal}",
                    agrees=True,
                ),),
                confidence=Confidence.LIKELY,
                abstain=False,
                advice=advice,
                classical_refs=tuple(classical_refs),
            )
        except Exception as exc:
            return insufficient_evidence(self.subject, f"heluo error: {exc}")


# ═══════════════════════════════════════════════════════════════════
# 子平八字断言Producer (V8: 补齐第四大体系)
# ═══════════════════════════════════════════════════════════════════

class ZipingAssertionProducer:
    """子平八字独立断言Producer (V8).

    subject=ziping. 基于BaziEngine排盘结果, 从子平视角输出方向断言.
    核心信号(子平经典):
    - 五行平衡: 失衡→健康/整体偏凶; 均衡→偏吉
    - 配偶星: 受克/官杀混杂→婚姻偏凶
    - 日主强弱与用神: 从spouse_star_strength等间接信号
    - 大运/流年应期: focus_years与luck_pillars对照
    单体系, 置信最高 LIKELY.
    """

    subject = "ziping"

    def __init__(self) -> None:
        from tongshu.engines.bazi_engine import BaziEngine
        self._bazi = BaziEngine()

    def produce(self, inp: AssertionInput, chart, context: dict | None = None) -> Assertion:
        context = context or {}
        if chart is None:
            return insufficient_evidence(self.subject, "chart is None")

        try:
            birth = context.get("birth")
            if birth is None:
                return insufficient_evidence(self.subject, "no birth info in context")

            y, mo, d, h = birth[:4]
            gender = birth[4] if len(birth) > 4 else "male"

            # 1. 排盘
            bchart = self._bazi.compute((y, mo, d, h), gender=gender)

            # === V11 子平本位: 旺衰/格局/用神 (回归本位强项, 不压缩为单一信号) ===
            from tongshu.engines.strength_engine import (
                evaluate_strength, _SUPPORT_ELEMENTS, _DRAIN_ELEMENTS,
            )
            from tongshu.engines.bazi_engine import (
                _BRANCH_HIDDEN_MAIN, _ten_god, STEM_ELEMENT,
            )
            sr = evaluate_strength(bchart)
            wangshuai = sr.verdict or "未定"          # 身强/身弱/从强/从弱
            climate = sr.climate                      # cold/hot/dry/wet
            tiaohou_xi = list(sr.tiaohou_primary or [])   # 《穷通宝鉴》调候主用神
            tiaohou_fu = list(sr.tiaohou_secondary or []) # 调候次用神
            dm_el = STEM_ELEMENT[bchart.day_master] if bchart.day_master in STEM_ELEMENT else ""
            # 扶抑喜忌: 身强/从强→喜克泄耗(DRAIN), 身弱/从弱→喜生扶(SUPPORT)
            if "身强" in wangshuai or "从强" in wangshuai:
                fuyi_xi = sorted(_DRAIN_ELEMENTS.get(dm_el, set()))
                fuyi_ji = sorted(_SUPPORT_ELEMENTS.get(dm_el, set()))
            elif "身弱" in wangshuai or "从弱" in wangshuai:
                fuyi_xi = sorted(_SUPPORT_ELEMENTS.get(dm_el, set()))
                fuyi_ji = sorted(_DRAIN_ELEMENTS.get(dm_el, set()))
            else:
                fuyi_xi = fuyi_ji = []
            _EL_CN = {"WOOD": "木", "FIRE": "火", "EARTH": "土", "METAL": "金", "WATER": "水"}
            fuyi_xi_cn = "/".join(_EL_CN.get(e, e) for e in fuyi_xi) or "未定"
            fuyi_ji_cn = "/".join(_EL_CN.get(e, e) for e in fuyi_ji) or "未定"
            # 格局: 月令本气藏干对日主的十神 → 立格
            month_branch = bchart.month_pillar.earthly_branch
            month_main_hidden = _BRANCH_HIDDEN_MAIN.get(month_branch, "")
            geju_ten_god = _ten_god(bchart.day_master, month_main_hidden) if month_main_hidden else ""
            geju = f"{geju_ten_god}格" if geju_ten_god else "格局未定"

            # 2. 五行平衡 → 整体/健康方向
            fe = bchart.five_element_balance or {}
            imbalance = bchart.five_element_imbalance

            # 3. 配偶星受克 → 婚姻方向
            spouse_attack = bchart.spouse_star_attack  # rob_wealth/guan_sha_mixed/none
            officer_mixed = bchart.officer_mixed
            spouse_strength = bchart.spouse_star_strength  # strong/weak/rootless
            day_branch_clash = bchart.day_branch_clash
            day_branch_harm = bchart.day_branch_harm

            # 4. 宫位信号计数
            neg_signals = 0
            pos_signals = 0

            # 五行失衡(健康/整体)
            if imbalance:
                neg_signals += 1
            else:
                pos_signals += 1

            # 配偶星受克/官杀混杂(婚姻/事业)
            if spouse_attack == "rob_wealth" or officer_mixed:
                neg_signals += 1
            elif spouse_strength == "strong":
                pos_signals += 1

            # 日支被冲/害(婚姻/健康)
            if day_branch_clash or day_branch_harm:
                neg_signals += 1

            # 5. 大运/流年应期
            focus_years = context.get("focus_years", [])
            luck_desc = ""
            luck_neg = luck_pos = 0
            if focus_years:
                start_age = bchart.start_age
                for i, lp in enumerate(bchart.luck_pillars or []):
                    # 大运起始岁数
                    dayun_age = start_age + i * 10
                    for y in focus_years:
                        # 简化: 出生年+大运年龄≈该大运覆盖年份
                        if 0 < dayun_age <= 60:
                            pass
                # 用排盘结果判断: 日主五行 vs 大运五行生克(简化为信号)
                luck_desc = f"子平排盘: 起运{bchart.start_age:.1f}岁, 大运{len(bchart.luck_pillars or [])}步"

            # 6. 综合方向
            if neg_signals > pos_signals:
                direction = Direction.NEGATIVE
            elif pos_signals > neg_signals:
                direction = Direction.POSITIVE
            else:
                direction = Direction.NEUTRAL

            # mechanism (V11: 本位维度结构化输出 旺衰/格局/用神)
            mechanism = (
                f"子平本位[旺衰:{wangshuai}; 气候:{climate}; "
                f"格局:{geju}; 调候用神:{'/'.join(tiaohou_xi) or '未定'}; "
                f"扶抑喜用:{fuyi_xi_cn}]"
            )
            mechanism += f"五行{('失衡' if imbalance else '均衡')}(吉{pos_signals}/凶{neg_signals})"
            if spouse_attack != "none":
                mechanism += f"; 配偶星受克({spouse_attack})"
            if officer_mixed:
                mechanism += "; 官杀混杂"
            if day_branch_clash or day_branch_harm:
                mechanism += "; 日支冲害"
            if luck_desc:
                mechanism += f"; {luck_desc}"
            if focus_years:
                mechanism += "; 焦点年需查流年引动"

            # advice
            advice_parts = []
            if imbalance:
                advice_parts.append("八字五行失衡, 健康方面需注意对应五行所主的脏腑, 宜补益调和")
            if spouse_attack != "none" or officer_mixed:
                advice_parts.append("配偶星受克/官杀混杂, 婚姻感情宜多沟通包容, 避免冲动决策")
            if day_branch_clash or day_branch_harm:
                advice_parts.append("日支冲害, 婚姻与健康需留意波动, 稳字当头")
            if not advice_parts:
                if direction == Direction.POSITIVE:
                    advice_parts.append("八字结构均衡, 整体走势平稳, 可稳中求进")
                else:
                    advice_parts.append("八字整体平稳, 保持良好作息与心态")
            advice = " ; ".join(advice_parts)

            # V10: 古籍引用交叉验证 — 子平依据
            from tongshu.assertion.classical_citations import (
                get_strength_citation, get_ten_god_citation, get_tiaohou_citation,
            )
            classical_refs = []
            # 旺衰/五行
            classical_refs.append(get_strength_citation("verdict"))  # 《滴天髓·衰旺》
            # 配偶星/十神(视信号)
            if spouse_attack == "rob_wealth":
                classical_refs.append(get_ten_god_citation("piancai"))  # 偏财受克
            if officer_mixed:
                classical_refs.append(get_ten_god_citation("qisha"))  # 官杀混杂
            if imbalance:
                classical_refs.append(get_strength_citation("de_ling"))  # 月令/五行
            classical_refs = [c for c in classical_refs if c][:3]
            # V11: 旺衰/调候/格局 古籍依据
            from tongshu.assertion.classical_citations import (
                get_strength_citation, get_tiaohou_citation,
            )
            benwei_refs = [
                get_strength_citation("verdict"),        # 《滴天髓·衰旺》: 能知衰旺
                get_strength_citation("month_command"),  # 《子平真诠·论用神》: 月令乃提纲
                get_tiaohou_citation("primary"),         # 《穷通宝鉴》调候主用神
            ]
            benwei_refs = [r for r in benwei_refs if r]
            for r in benwei_refs:
                if r not in classical_refs:
                    classical_refs.append(r)
            classical_refs = classical_refs[:5]

            return Assertion(
                subject=self.subject,
                assertion_type=AssertionType.STRUCTURAL,
                state=StateKind.STABLE,
                direction=direction,
                mechanism=mechanism,
                time=focus_years and f"焦点年{','.join(map(str, focus_years))}" or "",
                evidence=(EvidenceRef(
                    system="ziping",
                    signal_ref=f"五行{'失衡' if imbalance else '均衡'}; 配偶星{spouse_attack or '正常'}",
                    agrees=True,
                ),),
                confidence=Confidence.LIKELY,
                abstain=False,
                advice=advice,
                classical_refs=tuple(classical_refs),
            )
        except Exception as exc:
            return insufficient_evidence(self.subject, f"ziping error: {exc}")


__all__ = [
    "ZiweiAssertionProducer",
    "BlindAssertionProducer",
    "HeluoAssertionProducer",
    "ZipingAssertionProducer",
]
