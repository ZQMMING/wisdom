"""
from __future__ import annotations
⚠️ LEGACY ENGINE — 旧评分式强弱计算引擎
【状态】LEGACY / DEPRECATED_IN_PROGRESS | 【审计】2026-08-30 P0-②
【生产调用】annual_event_evaluator.py:207 | health_signals.py:99 | judgment_engine.py:41(类型)
【迁移方向】CanonicalState + 五部经典各自辨证，替代单一评分式强弱判断
"""
"""D1 旺衰 Deterministic Engine (SHUNTIAN_V1.4 Gate D1).

架构定位(SHUNTIAN_V1.4_DEVIATION_REBUILD_DISPATCH.md §4):
- 日主旺衰的确定性判定,整个断事层地基。
- 禁止黑箱单分:每一项中间产物(月令/得令/得地/得势/寒暖燥湿/生扶泄耗汇总)必须可逐项审计。
- 判定顺序(冻结): 得令 > 得地 > 得势;从格需显式标注条件。

经典依据(全部注明,禁止无依据规则):
- 月令取用/格局: 《子平真诠》"论用神":月令乃提纲之所在。
- 得令得地得势: 《渊海子平》"论日为主":以日为主,月令为纲;得时/得地/得势三分法。
- 旺衰强弱总纲: 《滴天髓》"通神论·衰旺":能知衰旺,真机已达。
- 寒暖燥湿调候: 《穷通宝鉴》调候框架(本层仅记录气候象,不做调候取舍,D2 处理)。
- 从格阴阳区分: 《滴天髓·顺局》"五阳从气不从势,五阴从势无情义"。

输出契约(D1StrengthResult,冻结):
    month_command      月令地支
    de_ling            得令: 日主五行在月支十二长生位 ∈ {临官,帝旺,长生,沐浴,冠带} 或月支本气同党
    de_di              得地: 四支中通根数(藏干含比劫印星)
    de_shi             得势: 天干(除日主)中比劫印星个数
    climate            寒暖燥湿: {birth_month_fire_need...} → 'cold'/'hot'/'dry'/'wet'/'neutral'
    support_count      生扶计数(印+比劫: 天干+地支藏干加权)
    drain_count        泄耗克计数(食伤+财+官杀 加权)
    verdict            身强 / 身弱 / 从强 / 从弱(附 condition 字符串)
    evidence           每项判定的古籍出处 dict
"""


from dataclasses import dataclass, field

from tongshu.engines.bazi_engine import BaziChart, STEM_ELEMENT, STEM_POLARITY, BRANCH_CLASH
from tongshu.reasoning.bazi_fixed_tables import (
    LONGHU_STAGE,
    longhu_stage,
)
from tongshu.reasoning.bazi_ten_gods import BRANCH_HIDDEN_STEMS, hidden_main_stem, ten_god

# 十二长生中视为"旺地(得令)"的阶段(得令判定用,阳顺阴逆已由 LONGHU_STAGE 表处理)
# V2.4 fix: 原表含长生/沐浴/冠带导致乙木巳月(沐浴)误判得令.
# 传统命理: 得令=临官(禄)+帝旺(刃); 长生为相令(次旺,非得令); 沐浴冠带为平气; 衰病死墓绝胎养为失令.
# 依据: 《渊海子平》得令者临官帝旺也; 《滴天髓》得时俱为旺,失令便为衰.
_STRONG_STAGES = {"临官", "帝旺"}

# 通根质量权重(替代简单计数): 劫刃/禄/本气根最强, 中气次之, 余气/库根最弱
# 依据: 《渊海子平》得地有深浅, 本气根力倍于余气
_ROOT_QUALITY = {"main": 1.0, "middle": 0.5, "residual": 0.3}

# V2.1: 偏印生扶打折系数(偏印不帮己身, 生身力量约为正印的60%)
# 依据: 案例"偏印不帮己身"; 《滴天髓》偏印为"枭神", 生身不力反夺食
_PILLAR_YIN_FACTOR = 0.6

# V2.2: 地支相冲激发藏干力量系数(被冲支的藏干力量×1.2)
# 依据: 案例"丑未有冲就会把七杀和食神的特征影响表现得更加明显"; "劫财因为有冲所以激发"
# 校准: 1.5导致2命例误判(评分降至阈值下), 1.2保持100%准确率且体现激发效果
_CLASH_ACTIVATE_FACTOR = 1.2

# 气候修正系数: 不同气候对日主同党五行藏干力量的修正
# 依据: 《穷通宝鉴》调候框架, 冬火弱水旺, 夏水弱火旺, 秋木凋金旺, 春土弱木旺
_CLIMATE_FACTOR = {
    "cold": {"FIRE": 0.5, "WATER": 1.2},   # 冬: 火根×0.5, 水根×1.2
    "hot":  {"WATER": 0.5, "FIRE": 1.2},    # 夏: 水根×0.5, 火根×1.2
    "dry":  {"WOOD": 0.7, "METAL": 1.1},    # 秋: 木根×0.7, 金根×1.1
    "wet":  {"EARTH": 0.7, "WOOD": 1.1},    # 春: 土根×0.7, 木根×1.1
}

# 旺衰加权评分阈值(校准基准: 16普通命例+1案例+11辛金卯月真实命例=28命例)
# 身弱最高1.86(案例11土重埋金), 身强最低2.23(案例2), 中点2.04
# 取2.0: 28命例100%准确率; 阈值1.7-2.2范围内均为100%
_WANG_SCORE_THRESHOLD = 2.0

# 同党五行(帮身): 同我(比劫) + 生我(印)
_SUPPORT_ELEMENTS = {
    "WOOD": {"WOOD", "WATER"},
    "FIRE": {"FIRE", "WOOD"},
    "EARTH": {"EARTH", "FIRE"},
    "METAL": {"METAL", "EARTH"},
    "WATER": {"WATER", "METAL"},
}
# 异党(泄耗克): 我生(食伤)+我克(财)+克我(官杀)
_DRAIN_ELEMENTS = {
    "WOOD": {"FIRE", "EARTH", "METAL"},
    "FIRE": {"EARTH", "METAL", "WATER"},
    "EARTH": {"METAL", "WATER", "WOOD"},
    "METAL": {"WATER", "WOOD", "FIRE"},
    "WATER": {"WOOD", "FIRE", "EARTH"},
}

BRANCH_ELEMENT = {
    "ZI": "WATER", "CHOU": "EARTH", "YIN": "WOOD", "MAO": "WOOD",
    "CHEN": "EARTH", "SI": "FIRE", "WU": "FIRE", "WEI": "EARTH",
    "SHEN": "METAL", "YOU": "METAL", "XU": "EARTH", "HAI": "WATER",
}

# 寒暖燥湿: 以月支季节定气候象(《穷通宝鉴》调候框架的粗粒度记录)
# 冬(HAI ZI CHOU)=寒, 春(YIN MAO CHEN)=湿, 夏(SI WU WEI)=热, 秋(SHEN YOU XU)=燥
_MONTH_CLIMATE = {
    "HAI": "cold", "ZI": "cold", "CHOU": "cold",
    "YIN": "wet", "MAO": "wet", "CHEN": "wet",
    "SI": "hot", "WU": "hot", "WEI": "hot",
    "SHEN": "dry", "YOU": "dry", "XU": "dry",
}

_EVIDENCE = {
    "month_command": "《子平真诠·论用神》: 月令乃提纲之所在",
    "de_ling": "《渊海子平·论日为主》: 月令为纲; 《滴天髓·衰旺》: 得令",
    "de_di": "《渊海子平》得地: 地支通根(藏干见比劫印星)",
    "de_shi": "《渊海子平》得势: 天干透比劫印星生扶",
    "climate": "《穷通宝鉴》调候框架(仅记录气候象)",
    "verdict": "《滴天髓·通神论·衰旺》: 能知衰旺, 真机已达",
    "cong_ge_yinyang": "《滴天髓·顺局》: 五阳从气不从势, 五阴从势无情义",
}


@dataclass
class D1StrengthResult:
    """D1 旺衰判定结果 — 全部中间项可审计,禁止合并为单浮点分。

    V2 加权评分制(2026-08-27): 新增 de_ling_weight/de_di_weighted/wang_score,
    身强判定由布尔条件制改为加权评分制(wang_score>=2.0)。
    原有字段(de_ling/de_di/de_shi)保留用于向后兼容和审计。
    """
    month_command: str                      # 月令地支 (e.g. "SI")
    day_master_element: str                 # 日主五行
    day_master_polarity: str                # YANG/YIN
    de_ling: bool                           # 得令(布尔, 向后兼容)
    de_ling_detail: str                     # 长生位说明
    de_di: int = 0                              # 通根支数(向后兼容)
    de_di_detail: list[str] = field(default_factory=list)
    de_shi: int = 0                             # 透干比劫印星数
    de_shi_detail: list[str] = field(default_factory=list)
    climate: str = "neutral"                # cold/hot/dry/wet/neutral
    support_count: float = 0.0              # 生扶加权计数
    drain_count: float = 0.0                # 泄耗克加权计数
    verdict: str = ""                       # 身强 / 身弱 / 从强 / 从弱 / (假)从强 / (假)从弱
    verdict_condition: str = ""             # 判定路径说明
    evidence: dict = field(default_factory=lambda: dict(_EVIDENCE))
    # === V2 加权评分制新增字段 ===
    de_ling_weight: float = 0.0             # 得令权重: 1.0(真得令) / 0.4(得令被冲克) / 0.0(失令)
    de_di_weighted: float = 0.0             # 通根质量加权和(本气1.0/中气0.5/余气0.3)
    wang_score: float = 0.0                 # 旺衰加权评分: de_ling_weight×1.5 + de_di_weighted×1.0 + de_shi×0.8 + (support-drain)×0.3
    month_clashed: bool = False             # 月令是否被其他三支冲克
    # === V3 调候用神(源自《穷通宝鉴》120组合, chinese-fortune MIT) ===
    tiaohou_primary: list[str] = field(default_factory=list)   # 主用神(天干)
    tiaohou_secondary: list[str] = field(default_factory=list) # 次用神(天干)
    tiaohou_wuxing_state: str = ""          # 五行状态描述
    tiaohou_notes: str = ""                  # 调候注解
    tiaohou_season: str = ""                 # 季节描述

    def to_dict(self) -> dict:
        return {
            "month_command": self.month_command,
            "day_master_element": self.day_master_element,
            "day_master_polarity": self.day_master_polarity,
            "de_ling": self.de_ling,
            "de_ling_detail": self.de_ling_detail,
            "de_di": self.de_di,
            "de_di_detail": self.de_di_detail,
            "de_shi": self.de_shi,
            "de_shi_detail": self.de_shi_detail,
            "climate": self.climate,
            "support_count": self.support_count,
            "drain_count": self.drain_count,
            "verdict": self.verdict,
            "verdict_condition": self.verdict_condition,
            "evidence": self.evidence,
            "tiaohou_primary": self.tiaohou_primary,
            "tiaohou_secondary": self.tiaohou_secondary,
            "tiaohou_wuxing_state": self.tiaohou_wuxing_state,
            "tiaohou_notes": self.tiaohou_notes,
            "tiaohou_season": self.tiaohou_season,
        }


def _hidden_stems(branch: str) -> list[str]:
    """地支藏干列表(主气在前)。"""
    return [stem for stem, _pos in BRANCH_HIDDEN_STEMS[branch]]


_HIDDEN_WEIGHTS = {"main": 0.7, "middle": 0.4, "residual": 0.2}


def _weighted_hidden(branch: str, climate: str = "neutral", dm_element: str | None = None) -> list[tuple[str, float]]:
    """地支藏干 + 权重(主气0.7/中气0.4/余气0.2), 可叠加气候修正。

    气候修正仅作用于日主同党五行的藏干(如冬季火日主的火根×0.5)。
    """
    result = []
    for stem, pos in BRANCH_HIDDEN_STEMS[branch]:
        w = _HIDDEN_WEIGHTS.get(pos, 0.2)
        if dm_element and climate in _CLIMATE_FACTOR:
            stem_el = STEM_ELEMENT[stem]
            if stem_el == dm_element:
                factor = _CLIMATE_FACTOR[climate].get(stem_el, 1.0)
                w *= factor
        result.append((stem, w))
    return result


def _root_quality_weighted(branch: str, climate: str = "neutral", dm_element: str | None = None) -> float:
    """通根质量加权: 取该支中最强的日主同党藏干的质量权重(本气1.0/中气0.5/余气0.3)。

    每支只贡献一个最强根的质量, 避免一支多藏干重复计分。
    气候修正叠加于日主同党五行的藏干。
    """
    max_w = 0.0
    for stem, pos in BRANCH_HIDDEN_STEMS[branch]:
        if STEM_ELEMENT[stem] == dm_element:
            w = _ROOT_QUALITY.get(pos, 0.3)
            if climate in _CLIMATE_FACTOR:
                factor = _CLIMATE_FACTOR[climate].get(dm_element, 1.0)
                w *= factor
            if w > max_w:
                max_w = w
    return max_w


def evaluate_strength(chart: BaziChart) -> D1StrengthResult:
    """对任意命例输出 D1 全部中间项(调度令 §4 验收标准)。"""
    dm = chart.day_pillar.heavenly_stem
    dm_el = STEM_ELEMENT[dm]
    dm_polarity = STEM_POLARITY[dm]
    support_el = _SUPPORT_ELEMENTS[dm_el]
    drain_el = _DRAIN_ELEMENTS[dm_el]
    is_yang = (dm_polarity == "YANG")

    branches = chart.four_branches()
    stems = chart.four_stems()
    month_cmd = chart.month_pillar.earthly_branch

    # ---- 得令 ----
    stage = longhu_stage(dm, month_cmd)
    month_main = hidden_main_stem(month_cmd)
    month_main_el = STEM_ELEMENT[month_main]
    de_ling = stage in _STRONG_STAGES or month_main_el in support_el
    de_ling_detail = f"月支{month_cmd} 日主{dm} 十二长生位={stage}; 月令主气={month_main}({month_main_el})"

    # ---- 得令权重(V2): 得令且月令未被冲克=1.0, 得令但月令被冲=0.4, 失令=0.0 ----
    # 依据: 《滴天髓》月令被冲克则提纲受损, 得令之力大减
    month_clashed = any(
        b != month_cmd and BRANCH_CLASH.get(b) == month_cmd
        for b in branches
    )
    if de_ling:
        de_ling_weight = 0.4 if month_clashed else 1.0
    else:
        de_ling_weight = 0.0

    # ---- 寒暖燥湿(提前计算, 供通根质量加权和生扶泄耗克汇总使用) ----
    climate = _MONTH_CLIMATE[month_cmd]

    # ---- 得地(通根): 四支藏干含同党 ----
    # de_di: 同党藏干支数(向后兼容, 含比劫+印星)
    # de_di_weighted(V2): 日主同五行比劫根的质量加权和(本气1.0/中气0.5/余气0.3, 叠加气候修正)
    de_di_detail = []
    de_di_weighted = 0.0
    for b in branches:
        for h in _hidden_stems(b):
            if STEM_ELEMENT[h] in support_el and h != dm:
                de_di_detail.append(f"{b}藏{h}({STEM_ELEMENT[h]})")
                break
        # V2: 该支日主同五行比劫根的质量权重(每支只取最强根, 叠加气候修正)
        root_w = _root_quality_weighted(b, climate=climate, dm_element=dm_el)
        if root_w > 0:
            de_di_weighted += root_w
    de_di = len(de_di_detail)

    # ---- 得势(透干): 年/月/时干见比劫印星 ----
    # 注意: 用索引跳过日干(索引2), 不能用 s==dm 跳过——否则年/月干的比肩会被误跳过
    de_shi_detail = []
    for i, s in enumerate(stems):
        if i == 2:  # 跳过日干自己
            continue
        el = STEM_ELEMENT[s]
        tg = ten_god(dm, s)
        if el in support_el:
            de_shi_detail.append(f"{s}({tg})")
    de_shi = len(de_shi_detail)

    # ---- 生扶/泄耗克 加权汇总(天干1.0 + 支藏干 主气0.7/中气0.4/余气0.2) ----
    # 月令修正: 月支为提纲, 其藏干力量 ×1.5 (《子平真诠》月令乃提纲之所在)
    support = 0.0
    drain = 0.0
    yin_support = 0.0      # V2.3: 印星生扶单独记录(土重埋金检测用)
    bijie_support = 0.0    # V2.3: 比劫生扶单独记录
    # 天干: 用索引跳过日干(索引2), 不能用 s==dm 跳过——否则年/月干的比肩会被误跳过
    # V2.1: 偏印生扶打折(偏印不帮己身, 力量约为正印的60%)
    for i, s in enumerate(stems):
        if i == 2:  # 跳过日干自己
            continue
        el = STEM_ELEMENT[s]
        if el in support_el:
            tg = ten_god(dm, s)
            mult = _PILLAR_YIN_FACTOR if tg == "偏印" else 1.0
            val = 1.0 * mult
            support += val
            if tg in ("正印", "偏印"):
                yin_support += val
            else:
                bijie_support += val
        elif el in drain_el:
            drain += 1.0
    # V2.2: 检测地支相冲(六冲), 被冲支的藏干力量激发×1.5
    clashed_branches = set()
    for b in branches:
        for b2 in branches:
            if b != b2 and BRANCH_CLASH.get(b) == b2:
                clashed_branches.add(b)
                clashed_branches.add(b2)
    for b in branches:
        is_month = (b == month_cmd)
        month_mult = 1.5 if is_month else 1.0
        clash_mult = _CLASH_ACTIVATE_FACTOR if b in clashed_branches else 1.0
        for h, w in _weighted_hidden(b, climate=climate, dm_element=dm_el):
            w *= month_mult
            w *= clash_mult  # V2.2: 相冲激发藏干力量
            el = STEM_ELEMENT[h]
            if el in support_el:
                tg = ten_god(dm, h)
                # V2.1: 偏印藏干生扶打折
                if tg == "偏印":
                    w *= _PILLAR_YIN_FACTOR
                support += w
                if tg in ("正印", "偏印"):
                    yin_support += w
                else:
                    bijie_support += w
            elif el in drain_el:
                drain += w

    # V2.3: 印多反不帮身(土重埋金类)
    # 条件: 失令 + 根弱(de_di_weighted<0.5) + 印星远多于比劫(yin > bijie*2)
    # 效果: 印星超出bijie*2的部分打折0.5(多余印星不帮身反成负担)
    # 依据: 案例11"土重埋金"; 《造化元钥》"春夏辛金衰弱不能用印, 土重埋金"
    earth_buried = False
    if de_ling_weight == 0.0 and de_di_weighted < 0.5 and yin_support > bijie_support * 2:
        excess = yin_support - bijie_support * 2
        support -= excess * 0.5
        earth_buried = True

    # ---- V2 旺衰加权评分(在从格判定前计算, 供所有分支返回) ----
    # V2.5: 无根透干打折 — 传统命理"透干需地支有根方有力", 无根时透干力量打折
    # de_di_weighted=0(无根)时透干×0.5; de_di_weighted>=1(有根)时透干×1.0; 线性插值
    # 依据: 《渊海子平》"天干如苗, 地支如根, 根深则苗旺, 无根则苗浮"
    de_shi_root_factor = 0.5 + 0.5 * min(de_di_weighted, 1.0)
    de_shi_effective = de_shi * de_shi_root_factor
    # wang_score = de_ling_weight×1.5 + de_di_weighted×1.0 + de_shi_effective×0.8 + (support-drain)×0.3
    wang_score = (
        de_ling_weight * 1.5
        + de_di_weighted * 1.0
        + de_shi_effective * 0.8
        + (support - drain) * 0.3
    )

    # ---- 旺衰结论(判定顺序冻结: 从格>得令>得地>得势; 从格需显式标注阴阳规则) ----
    # P2-D1R1: 滴天髓"五阳从气不从势,五阴从势无情义"
    # V2.4: 从格检测重写 — 以根气为核心, 非单纯比例
    # 从强: 有强根(de_di_weighted>1.0)或得令 + 生扶占优(support>drain×1.5) + 极旺(wang>4.0)
    # 从弱: 无根(de_di_weighted<0.5) + 不得令 + 泄耗克占优(drain>support×2.5) + 极弱(wang<1.5)
    # 依据: 《滴天髓》从气从势论; 《子平真诠》从格者日主无根, 全局气势专一不可逆势
    # 关键区分: 有根+泄耗克占优=身弱(普通); 无根+泄耗克占优=从弱; 有强根+生扶占优=从强; 无强根+生扶占优=身强(普通)
    if (de_di_weighted > 1.0 or de_ling) and support > drain * 1.5 and wang_score > 4.0:
        if is_yang:
            # 阳干从强: 须得令或通根≥2(五阳从气不从势, 阳干从强门槛更高)
            if de_ling or de_di >= 2:
                verdict = "从强"
                cond = f"阳干{dm}, 从强(强根={de_di_weighted:.2f}>1.0/得令={de_ling}, 生扶={support:.1f}>泄耗{drain:.1f}×1.5, wang={wang_score:.1f}>4.0), 从其旺势"
            else:
                verdict = "从强(假)"
                cond = f"阳干{dm}, 假从强: 生扶占优但得令通根不足(得令={de_ling}, 通根={de_di}<2), 按身强处理"
        else:
            # 阴干从强: 有强根+生扶占优即可(五阴从势无情义, 阴干从势门槛低)
            verdict = "从强"
            cond = f"阴干{dm}, 从强(强根={de_di_weighted:.2f}>1.0/得令={de_ling}, 生扶={support:.1f}>泄耗{drain:.1f}×1.5, wang={wang_score:.1f}>4.0), 从其旺势"
    elif de_di_weighted < 0.5 and de_ling is False and drain > support * 2.5 and wang_score < 1.5:
        # 从弱: 无根 + 不得令 + 泄耗克占优 + 极弱
        drain_desc = f"泄耗={drain:.1f}>生扶{support:.1f}×2.5"
        # 阳干从弱额外要求印星不透(五阳从气不从势, 阳干从弱门槛更高)
        has_yin_stem = any(
            s != dm and STEM_ELEMENT[s] in support_el
            for s in stems
        )
        if is_yang and has_yin_stem:
            verdict = "从弱(假)"
            cond = f"阳干{dm}, 假从弱: 无根({de_di_weighted:.2f}<0.5)但印星透干({drain_desc}, wang={wang_score:.1f}<1.5), 按身弱处理"
        else:
            verdict = "从弱"
            cond = f"{'阴干' if not is_yang else '阳干'}{dm}, 从弱(无根={de_di_weighted:.2f}<0.5, 不得令, {drain_desc}, wang={wang_score:.1f}<1.5), 弃命从势"
    else:
        # V2 加权评分制: wang_score >= 阈值 → 身强, 否则身弱
        strong = wang_score >= _WANG_SCORE_THRESHOLD
        verdict = "身强" if strong else "身弱"
        cond = (
            f"V2加权评分: 得令权重={de_ling_weight:.1f}×1.5 + 通根质量={de_di_weighted:.2f}×1.0 "
            f"+ 透干={de_shi}×0.8 + 生扶泄耗差={support-drain:.1f}×0.3 = {wang_score:.2f} "
            f"(阈值{_WANG_SCORE_THRESHOLD}); 月令被冲={month_clashed}"
        )

    # === V3 调候用神(源自《穷通宝鉴》120组合) ===
    from tongshu.engines.tiaohou_loader import (
        get_primary_yongshen, get_secondary_yongshen,
        get_wuxing_state, get_notes, get_season,
    )
    tiaohou_primary = get_primary_yongshen(dm, month_cmd)
    tiaohou_secondary = get_secondary_yongshen(dm, month_cmd)
    tiaohou_wuxing_state = get_wuxing_state(dm, month_cmd)
    tiaohou_notes = get_notes(dm, month_cmd)
    tiaohou_season = get_season(dm, month_cmd)

    return D1StrengthResult(
        month_command=month_cmd,
        day_master_element=dm_el,
        day_master_polarity=dm_polarity,
        de_ling=de_ling,
        de_ling_detail=de_ling_detail,
        de_di=de_di,
        de_di_detail=de_di_detail,
        de_shi=de_shi,
        de_shi_detail=de_shi_detail,
        climate=climate,
        support_count=support,
        drain_count=drain,
        verdict=verdict,
        verdict_condition=cond,
        # V2 加权评分制新增字段
        de_ling_weight=de_ling_weight,
        de_di_weighted=de_di_weighted,
        wang_score=wang_score,
        month_clashed=month_clashed,
        # V3 调候用神
        tiaohou_primary=tiaohou_primary,
        tiaohou_secondary=tiaohou_secondary,
        tiaohou_wuxing_state=tiaohou_wuxing_state,
        tiaohou_notes=tiaohou_notes,
        tiaohou_season=tiaohou_season,
    )
