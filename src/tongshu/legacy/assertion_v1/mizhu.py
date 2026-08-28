# -*- coding: utf-8 -*-
"""迷津断言Producer (P3 Mizhu Layer).

倪海厦《天纪》方法论: 算命分两部分 —— 迷津(一辈子注意什么) + 流年(逐年运势).
迷津层输出终身注意事项, 基于命宫格局/三方四正/化忌宫位/关键凶格.

依据: 倪海厦《天纪》方法论751条判语 - 迷津与流年两层架构.
"""
from __future__ import annotations

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


# 化忌宫位 → 终身注意领域
HUAJI_GONG_WARNING = {
    "命宫": "一生行事多阻碍, 易有波折, 宜稳扎稳打忌冒进",
    "兄弟": "兄弟缘薄或易有财务纠纷, 不宜合伙经营",
    "夫妻": "婚姻感情多波折, 宜晚婚或找年龄相差大的对象",
    "子女": "子女缘薄或教育子女多费心, 宜耐心引导",
    "财帛": "财运多起伏, 宜守财忌投机, 量入为出",
    "疾厄": "注意身体健康, 定期体检, 忌过劳",
    "迁移": "外出远行多阻碍, 宜谨慎出行, 忌冲动迁移",
    "仆役": "交友多损友, 宜慎择友, 忌轻易信任他人",
    "官禄": "事业多波折, 宜守成忌冒险创业, 稳步发展",
    "田宅": "房产多波折, 宜谨慎投资不动产, 忌冲动购房",
    "福德": "精神多焦虑, 宜修身养性, 忌过度思虑",
    "父母": "父母缘薄或与上司多摩擦, 宜恭敬忍耐",
}

# 命宫主星 → 性格与注意
MAIN_STAR_NOTE = {
    "紫微": "自尊心强, 宜放权忌独断; 注意心脏/血压",
    "天机": "心思细密多变动, 宜专注忌三心二意; 注意肝胆/神经",
    "太阳": "热情好面子, 宜低调忌张扬; 注意眼睛/心脏",
    "武曲": "刚毅果断, 宜柔和忌刚愎; 注意肺/呼吸道",
    "天同": "温和享福, 宜进取忌安逸; 注意脾胃/排泄",
    "廉贞": "感情丰富多变化, 宜理性忌冲动; 注意血液/内分泌",
    "天府": "稳重宽厚, 宜开创忌守成; 注意脾胃/肌肉",
    "太阴": "细腻多思, 宜开朗忌阴郁; 注意肾脏/泌尿/妇科",
    "贪狼": "多才多欲, 宜节制忌贪婪; 注意肝胆/生殖",
    "巨门": "口才佳多口舌, 宜慎言忌争辩; 注意肺/呼吸道/口腔",
    "天相": "谨慎公正, 宜果断忌犹豫; 注意皮肤/排泄",
    "天梁": "清高正直, 宜圆融忌固执; 注意脾胃/神经",
    "七杀": "刚烈独立, 宜忍耐忌冲动; 注意肝胆/外伤",
    "破军": "变革开创, 宜稳健忌破坏; 注意生殖/内分泌",
}

# 关键凶格 → 终身警示
XIONG_GE_WARNING = {
    "日月反背": "日月反背格: 一生多劳碌, 宜外地发展, 注意父母健康",
    "杀拱杀": "杀拱杀格(羊陀夹命): 一生多竞争压力, 宜修身养性忌争斗",
    "半空折翅": "半空折翅格: 中年易有大波折, 宜提前规划防风险",
    "水中作冢": "水中作冢格: 注意水险/肾脏健康, 忌近水冒险",
    "马头带箭": "马头带箭格: 一生多变动奔波, 宜动中求稳",
}


class MizhuAssertionProducer:
    """迷津断言Producer. subject=mizhu.

    输出终身注意事项(迷津), 基于:
    1. 命宫主星定性
    2. 三方四正整体吉凶
    3. 化忌所在宫位(一生最需注意的领域)
    4. 关键凶格警示
    5. 建设性建议(画险趋吉)
    """

    subject = "mizhu"

    def __init__(self) -> None:
        from tongshu.engines.ziwei_engine import ZiweiEngine
        self._engine = ZiweiEngine()

    def produce(self, inp: AssertionInput, chart, context: dict | None = None) -> Assertion:
        context = context or {}
        if chart is None:
            return insufficient_evidence(self.subject, "chart is None")

        try:
            from lunar_python import Solar
            birth = context.get("birth")
            if birth is None:
                return insufficient_evidence(self.subject, "no birth info in context")

            y, mo, d, h = birth[:4]
            gender = birth[4] if len(birth) > 4 else "male"
            solar = Solar.fromYmdHms(y, mo, d, h, 0, 0)
            lunar = solar.getLunar()
            lunar_date = (lunar.getYear(), abs(lunar.getMonth()), lunar.getDay())

            full = self._engine.full_chart(lunar_date, h, gender=gender)
            palaces = full.get("palaces", {})

            # 1. 命宫主星
            ming_gong = palaces.get("命宫", {})
            main_stars = ming_gong.get("major", [])
            ming_star = main_stars[0] if main_stars else "无主星"
            star_note = MAIN_STAR_NOTE.get(ming_star, "命宫无主星, 宜借对宫星情论命")

            # 2. 三方四正整体吉凶
            SANFANG = ["命宫", "财帛", "官禄", "迁移"]
            JI_STARS = {"禄", "权", "科", "魁", "钺", "辅", "弼", "昌", "曲"}
            XIONG_STARS = {"忌", "羊", "陀", "火", "铃", "空", "劫"}
            sanfang_ji = sanfang_xiong = 0
            for gong_key in SANFANG:
                g = palaces.get(gong_key, {})
                all_stars = g.get("major", []) + g.get("minor", [])
                for s in all_stars:
                    if any(js in s for js in JI_STARS):
                        sanfang_ji += 1
                    if any(xs in s for xs in XIONG_STARS):
                        sanfang_xiong += 1

            if sanfang_ji > sanfang_xiong:
                overall = "三方四正吉多, 一生整体运势向好, 但需戒盛"
                overall_dir = Direction.POSITIVE
            elif sanfang_xiong > sanfang_ji:
                overall = "三方四正凶多, 一生多波折, 宜稳扎稳打忌冒进"
                overall_dir = Direction.NEGATIVE
            else:
                overall = "三方四正吉凶参半, 一生有起有落, 宜把握机遇规避风险"
                overall_dir = Direction.NEUTRAL

            # 3. 化忌所在宫位
            huaji_gong = None
            for gong_key, g in palaces.items():
                all_stars = g.get("major", []) + g.get("minor", [])
                if any("化忌" in s or "忌" in s for s in all_stars):
                    huaji_gong = gong_key
                    break
            huaji_warning = HUAJI_GONG_WARNING.get(huaji_gong, "") if huaji_gong else ""

            # 4. 关键凶格检测(简化版, 基于命宫+对宫星情)
            xiong_ge_warnings = []
            qianyi = palaces.get("迁移", {})
            qianyi_stars = qianyi.get("major", [])
            # 日月反背: 命宫太阳/太阴在落陷宫(简化检测)
            if ("太阳" in main_stars and lunar.getMonth() < 0) or ("太阴" in main_stars and lunar.getMonth() > 0):
                xiong_ge_warnings.append(XIONG_GE_WARNING["日月反背"])
            # 羊陀夹命
            ming_minor = ming_gong.get("minor", [])
            if any("羊" in s for s in ming_minor) and any("陀" in s for s in ming_minor):
                xiong_ge_warnings.append(XIONG_GE_WARNING["杀拱杀"])

            # 5. 综合迷津
            warnings = []
            if star_note:
                warnings.append(f"【命宫】{star_note}")
            if overall:
                warnings.append(f"【整体】{overall}")
            if huaji_warning:
                warnings.append(f"【化忌在{huaji_gong}】{huaji_warning}")
            for w in xiong_ge_warnings:
                warnings.append(f"【凶格警示】{w}")

            # 建设性建议(画险趋吉)
            if overall_dir == Direction.NEGATIVE:
                advice = (
                    "画险趋吉：此命一生多波折，宜守成忌冒险；"
                    "进德修业、积累实力，待限运转好再图进取；"
                    "凡事三思而后行，忌冲动决策。"
                )
            elif overall_dir == Direction.POSITIVE:
                advice = (
                    "利建侯：此命整体运势向好，宜主动出击、建立事业基础；"
                    "但需戒盛，吉处藏凶，保持警戒心；"
                    "把握机遇但忌过度扩张。"
                )
            else:
                advice = (
                    "中平之命：宜稳扎稳打，不宜大进大退；"
                    "观察大势，积累资源，等待明确方向出现；"
                    "吉凶参半，关键在于把握机遇规避风险。"
                )

            mechanism = "迷津(终身注意)：" + "；".join(warnings)
            time_desc = "终身(迷津层, 非逐年流年)"

            evidence_list = [
                EvidenceRef(system="ziwei", signal_ref=f"命宫{ming_star}", agrees=True),
                EvidenceRef(system="ziwei", signal_ref=f"三方四正吉{sanfang_ji}/凶{sanfang_xiong}",
                           agrees=(sanfang_ji >= sanfang_xiong)),
            ]
            if huaji_gong:
                evidence_list.append(
                    EvidenceRef(system="ziwei", signal_ref=f"化忌在{huaji_gong}", agrees=False))

            return Assertion(
                subject=self.subject,
                assertion_type=AssertionType.STRUCTURAL,
                state=StateKind.STABLE,
                direction=overall_dir,
                mechanism=mechanism,
                time=time_desc,
                evidence=tuple(evidence_list),
                confidence=Confidence.LIKELY,
                abstain=False,
                advice=advice,
            )
        except Exception as exc:
            return insufficient_evidence(self.subject, f"mizhu error: {exc}")


__all__ = ["MizhuAssertionProducer"]
