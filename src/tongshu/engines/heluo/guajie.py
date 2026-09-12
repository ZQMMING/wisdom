"""H8: 河洛解卦层（原典查询式字典引擎）

职责：把已排好的主链（先天/后天/大运/流年/流月/流日）转成原典判词。
数据源：data/heluo/guajie_data.json（《河洛真数·易卦释义》，续修四库全书·天一阁本）
+ 起例卷"数足不足论"（中华典藏 21177 天一阁本）。

解卦四要素（原典《河洛真数》起例）：
  1. 得时     = 生月与卦之旺时相符（卦气属X月 / 旺时区间）
  2. 纳甲本命 = 生年干支在卦之纳甲范围
  3. 叶/不叶  = 命局与卦爻时机相合（叶吉）或不合（不叶）
  4. 岁运逢爻 = 走大运/流年到此爻，按在仕/在士/在庶俗/女命分断

数之凶吉（起例卷之中·数足不足论）：
  天数二十五为正、地数三十为正；无余无不足=最佳（安和自宁）
  天数不足<25 / 地数不足<30；有余档（孤阳不偶/孤阴背阳/以弱敌强）
  有余/不足均须按生月节气合时判断凶吉（阳月/阴月）

元气化工（命之根基，yuan_qi.py/hua_gong.py）：
  流年遇元气 → 必然得财利；遇化工 → 中举中进士生贵子
  爻辞虽凶不免灾眚，但于富贵天年不碍。不要拘泥爻辞吉凶。

正对反对卦（生死大凶断）：
  流年先后天大象遇正对/反对 + 爻辞凶 + 卦无元气化工 → 必死，不死亦有横灾
  命卦正对/反对是十二卦（复临泰大壮夬乾姤遁否观剥坤）之一 → 不吉
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .yuan_qi import STEM_TO_TRIGRAM, BRANCH_TO_TRIGRAM

_REPO_ROOT = Path(__file__).resolve().parents[4]
_GUAJIE_DATA = _REPO_ROOT / "data" / "heluo" / "guajie_data.json"

# 十二凶卦（命卦正对/反对为其中之一 → 不吉）
TWELVE_XIONG_GUA = ["复", "临", "泰", "大壮", "夬", "乾", "姤", "遁", "否", "观", "剥", "坤"]

# 错卦（先天方位对宫，六爻全变）— 与 yuan_qi/hua_gong 一致
OPPOSITE_TRIGRAM = {"乾": "坤", "坤": "乾", "坎": "离", "离": "坎", "震": "巽", "巽": "震", "艮": "兑", "兑": "艮"}

# 纯卦 → 上/下三画
PURE_GUA = {"乾": ("乾", "乾"), "坤": ("坤", "坤"), "坎": ("坎", "坎"), "离": ("离", "离"),
            "震": ("震", "震"), "艮": ("艮", "艮"), "巽": ("巽", "巽"), "兑": ("兑", "兑")}

# 64卦 → (上卦, 下卦) 三画分解（由 64 卦名表推导，仅列非纯卦）
COMPOUND_GUA: dict[str, tuple[str, str]] = {
    "屯": ("坎", "震"), "蒙": ("艮", "坎"), "需": ("坎", "乾"), "讼": ("乾", "坎"),
    "师": ("坤", "坎"), "比": ("坎", "坤"), "小畜": ("巽", "乾"), "履": ("乾", "兑"),
    "泰": ("坤", "乾"), "否": ("乾", "坤"), "同人": ("乾", "离"), "大有": ("离", "乾"),
    "谦": ("坤", "艮"), "豫": ("震", "坤"), "随": ("兑", "震"), "蛊": ("艮", "巽"),
    "临": ("坤", "兑"), "观": ("巽", "坤"), "噬嗑": ("离", "震"), "贲": ("艮", "离"),
    "剥": ("艮", "坤"), "复": ("坤", "震"), "无妄": ("乾", "震"), "大畜": ("艮", "乾"),
    "颐": ("艮", "震"), "大过": ("兑", "巽"), "咸": ("兑", "艮"), "恒": ("震", "巽"),
    "遁": ("乾", "艮"), "大壮": ("震", "乾"), "晋": ("离", "坤"), "明夷": ("坤", "离"),
    "家人": ("巽", "离"), "睽": ("离", "兑"), "蹇": ("坎", "艮"), "解": ("震", "坎"),
    "损": ("艮", "兑"), "益": ("巽", "震"), "夬": ("兑", "乾"), "姤": ("乾", "巽"),
    "萃": ("兑", "坤"), "升": ("坤", "巽"), "困": ("兑", "坎"), "井": ("坎", "巽"),
    "革": ("兑", "离"), "鼎": ("离", "巽"), "渐": ("巽", "艮"), "归妹": ("震", "兑"),
    "丰": ("震", "离"), "旅": ("离", "艮"), "涣": ("巽", "坎"), "节": ("坎", "兑"),
    "中孚": ("巽", "兑"), "小过": ("震", "艮"), "既济": ("坎", "离"), "未济": ("离", "坎"),
}
COMPOUND_GUA.update(PURE_GUA)

# 三画卦 → 正五行（纳音相生用）
TRIGRAM_ELEMENT: dict[str, str] = {
    "乾": "金", "兑": "金", "坤": "土", "艮": "土",
    "震": "木", "巽": "木", "坎": "水", "离": "火",
}

# 五行相生关系（key 生 value）
ELEMENT_GENERATES: dict[str, str] = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

# 60甲子纳音五行（两柱一组，30组）
_NAYIN = {
    "甲子": "金", "乙丑": "金", "丙寅": "火", "丁卯": "火", "戊辰": "木", "己巳": "木",
    "庚午": "土", "辛未": "土", "壬申": "金", "癸酉": "金", "甲戌": "火", "乙亥": "火",
    "丙子": "水", "丁丑": "水", "戊寅": "土", "己卯": "土", "庚辰": "金", "辛巳": "金",
    "壬午": "木", "癸未": "木", "甲申": "水", "乙酉": "水", "丙戌": "土", "丁亥": "土",
    "戊子": "火", "己丑": "火", "庚寅": "木", "辛卯": "木", "壬辰": "水", "癸巳": "水",
    "甲午": "金", "乙未": "金", "丙申": "火", "丁酉": "火", "戊戌": "木", "己亥": "木",
    "庚子": "土", "辛丑": "土", "壬寅": "金", "癸卯": "金", "甲辰": "火", "乙巳": "火",
    "丙午": "水", "丁未": "水", "戊申": "土", "己酉": "土", "庚戌": "金", "辛亥": "金",
    "壬子": "木", "癸丑": "木", "甲寅": "水", "乙卯": "水", "丙辰": "土", "丁巳": "土",
    "戊午": "火", "己未": "火", "庚申": "木", "辛酉": "木", "壬戌": "水", "癸亥": "水",
}


def get_nayin_element(year_gan: str, year_zhi: str) -> str:
    """年柱纳音五行（甲子乙丑海中金…）。"""
    return _NAYIN.get(year_gan + year_zhi, "")


def compute_huti(six_lines: list[int]) -> tuple[str, str]:
    """
    互体（《河洛真数·起例卷之上·互体伏体论》）：
      "以正体内外卦除初上二爻，用中四爻，交互成卦，谓之互体"
    取法：下互=二三四爻（lines[1:4]），上互=三四五爻（lines[2:5]）。
    原典例（渐卦）："九五六四九三互离，六四九三六二互坎，合之为未济" ✓
    返回 (上互卦名, 下互卦名)。
    """
    rev = {"111": "乾", "110": "兑", "101": "离", "100": "震",
           "011": "巽", "010": "坎", "001": "艮", "000": "坤"}
    def _tri(chunk: list[int]) -> str:
        return rev.get("".join("1" if l == 1 else "0" for l in chunk), "")
    lower = _tri(six_lines[1:4])
    upper = _tri(six_lines[2:5])
    return upper, lower


def judge_nayin_yuanqi(
    year_gan: str, year_zhi: str, gua_name: str,
) -> list[str]:
    """
    纳音五行元气（《河洛真数·起例卷之上》）：
      "元气谓壬甲戌亥及金音人得乾兑之卦是也"
      "又看彼此相生。如火人得木卦，金人得土卦之类，亦能相生为福。
       但得水火卦者，极忌相反"
    返回证据列表（空=无纳音元气）。
    """
    ev: list[str] = []
    nayin = get_nayin_element(year_gan, year_zhi)
    if not nayin:
        return ev
    gua = COMPOUND_GUA.get(gua_name)
    if not gua:
        return ev
    upper, lower = gua
    el_upper, el_lower = TRIGRAM_ELEMENT.get(upper, ""), TRIGRAM_ELEMENT.get(lower, "")
    ev.append(f"年柱{year_gan}{year_zhi}纳音{nayin}；{gua_name}卦体={upper}({el_upper})/{lower}({el_lower})")

    # 金音人得乾兑（原文明文）
    if nayin == "金" and el_upper in ("金",) or nayin == "金" and el_lower in ("金",):
        ev.append("金音人得乾兑（金体）之卦 → 元气（原典：元气谓…金音人得乾兑之卦是也）")
    # 卦体五行生纳音（生我者=相生为福）
    for el in (el_upper, el_lower):
        if el and ELEMENT_GENERATES.get(el) == nayin:
            ev.append(f"{el}体({el})生纳音{nayin} → 相生为福（原典：彼此相生）")
    # 水火相克相反（极忌）
    for el in (el_upper, el_lower):
        if el == "水" and nayin == "火":
            ev.append(f"得水卦而纳音火 → 极忌相反（原典：得水火卦者极忌相反）")
        if el == "火" and nayin == "水":
            ev.append(f"得火卦而纳音水 → 极忌相反（原典：得水火卦者极忌相反）")
    return ev


# 三画卦 → 六爻序列（1阳 0阴，下卦在前）
_TRIGRAM_LINES = {
    "乾": [1, 1, 1], "兑": [1, 1, 0], "离": [1, 0, 1], "震": [1, 0, 0],
    "巽": [0, 1, 1], "坎": [0, 1, 0], "艮": [0, 0, 1], "坤": [0, 0, 0],
}

# 四正节卦：起于二分二至，每卦90日、每爻15日（起例卷之下·节候卦爻）
# "节卦坎初六起冬至…震初九起春分…离初九起夏至…兑初九起秋分。每卦总管九十日"
_JIE_GUA_START = [  # (月, 日, 卦, 爻名序列[初→上])
    (12, 22, "坎", ["初六", "九二", "六三", "六四", "九五", "上六"]),
    (3, 21, "震", ["初九", "六二", "六三", "九四", "六五", "上六"]),
    (6, 21, "离", ["初九", "六二", "九三", "九四", "六五", "上九"]),
    (9, 23, "兑", ["初九", "九二", "六三", "九四", "九五", "上六"]),
]


def trigram_to_lines(trigram: str) -> list[int]:
    """三画卦 → 六爻序列（下卦3爻+上卦3爻，1阳0阴）。"""
    return list(_TRIGRAM_LINES.get(trigram, [0, 0, 0]))


def hexagram_to_lines(gua_name: str) -> list[int]:
    """卦名 → 六爻序列（下卦3爻+上卦3爻）。"""
    u, l = COMPOUND_GUA.get(gua_name, ("", ""))
    return trigram_to_lines(l) + trigram_to_lines(u)


def judge_jiehua_gong(birth_date: str) -> list[str]:
    """
    生时值节卦 → 化工（《河洛真数·起例卷之下·节候卦爻》）：
      "节卦坎初六起冬至，九二小寒…震初九起春分…离初九起夏至…兑初九起秋分。
       每卦总管九十日，自下而上，每一爻各直十五日。……生时值节卦者，谓之化工，
       生月值卦者，谓之得令"
    四正节卦：坎起冬至/震起春分/离起夏至/兑起秋分（公历近似，边界±1日）。
    返回证据列表（空=无节候卦化工记录）。
    """
    ev: list[str] = []
    try:
        y, m, d = birth_date.split("-")[0:3]
        y, m, d = int(y), int(m), int(d)
    except (ValueError, AttributeError):
        return ev
    import datetime as _dt
    cur = _dt.date(y, m, d)
    # 四正节卦各自起点（含上年，坎跨年12/22~3/21）
    for sm, sd, gua, yaos in _JIE_GUA_START:
        for yy in (y - 1, y):
            start = _dt.date(yy, sm, sd)
            days = (cur - start).days
            if 0 <= days < 90:
                idx = min(days // 15, 5)
                ev.append(
                    f"生时值节卦：{gua}节卦起于{sm}月{sd}日，出生日距起{days}日"
                    f"（第{idx + 1}段，{yaos[idx]}爻）→ 化工（原典：生时值节卦者谓之化工）")
                return ev
    return ev


def judge_nayin_huti(
    year_gan: str, year_zhi: str,
    prenatal_name: str, postnatal_name: str,
) -> list[str]:
    """
    互体纳音元气（《河洛真数·起例卷之上》）：
      "甲子生人得小过，虽卦中无乾兑金元气，然互体有兑，亦是纳音元气"
    取先天/后天命卦之互体，纳入纳音元气判定。
    """
    ev: list[str] = []
    seen: set[str] = set()
    for g in (prenatal_name, postnatal_name):
        lines = hexagram_to_lines(g)
        if len(lines) != 6:
            continue
        up, lo = compute_huti(lines)
        for cand, (cu, cl) in COMPOUND_GUA.items():
            if cu == up and cl == lo:
                huti_name = cand
                break
        else:
            huti_name = up + lo
        key = f"{g}->{huti_name}"
        if key in seen:
            continue
        seen.add(key)
        nayin = get_nayin_element(year_gan, year_zhi)
        el_up, el_lo = TRIGRAM_ELEMENT.get(up, ""), TRIGRAM_ELEMENT.get(lo, "")
        if nayin == "金" and (el_up == "金" or el_lo == "金"):
            ev.append(f"{g}互体（{up}{lo}={huti_name}）含金体 → 金音人互体得金，亦是纳音元气（原典：互体有兑亦是纳音元气）")
        matched = False
        for el in (el_up, el_lo):
            if el and ELEMENT_GENERATES.get(el) == nayin and not matched:
                ev.append(f"{g}互体（{up}{lo}={huti_name}）{el}体生纳音{nayin} → 互体相生为福（原典：彼此相生）")
                matched = True
    return ev


# 综卦（六爻倒转）：64卦互为综卦对
ZONG_GUA: dict[str, str] = {
    "乾": "乾", "坤": "坤", "坎": "坎", "离": "离", "震": "震", "艮": "艮", "巽": "巽", "兑": "兑",
    "屯": "蒙", "蒙": "屯", "需": "讼", "讼": "需", "师": "比", "比": "师",
    "小畜": "履", "履": "小畜", "泰": "否", "否": "泰", "同人": "大有", "大有": "同人",
    "谦": "豫", "豫": "谦", "随": "蛊", "蛊": "随", "临": "观", "观": "临",
    "噬嗑": "贲", "贲": "噬嗑", "剥": "复", "复": "剥", "无妄": "大畜", "大畜": "无妄",
    "颐": "大过", "大过": "颐", "咸": "恒", "恒": "咸", "遁": "大壮", "大壮": "遁",
    "晋": "明夷", "明夷": "晋", "家人": "睽", "睽": "家人", "蹇": "解", "解": "蹇",
    "损": "益", "益": "损", "夬": "姤", "姤": "夬", "萃": "升", "升": "萃",
    "困": "井", "井": "困", "革": "鼎", "鼎": "革", "渐": "归妹", "归妹": "渐",
    "丰": "旅", "旅": "丰", "涣": "节", "节": "涣", "中孚": "中孚", "小过": "小过",
    "既济": "未济", "未济": "既济",
}

# 月名数字映射（卦气属X月）
_CN_MONTH = {"正": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12, "腊": 12}


# ═══════════════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════════════

@dataclass
class YaoDuan:
    """单爻判词（原典释义）。"""
    yao: str            # 初九/六二/…
    ci: str             # 爻辞
    xiang: str          # 象曰
    yi: str             # 释义
    ye: str             # 叶吉断语
    buye: str           # 不叶断语
    suiyun: str         # 岁运逢之断语
    shao: str           # 邵曰


@dataclass
class GuaDuan:
    """单卦判词（原典释义）。"""
    name: str
    gua_ci: str         # 卦辞
    gua_qi_month: Optional[int]  # 卦气属X月
    najia: list[str]    # 纳甲干支
    gua_lines: list[str]  # 卦头断语（含旺时/得时信息）
    yaos: dict[str, YaoDuan] = field(default_factory=dict)


@dataclass
class YeBuYeResult:
    """叶/不叶判定结果。"""
    ye: bool                    # 叶（相合）
    buye: bool                  # 不叶（不合）
    gua_qi_month: Optional[int]
    birth_month: int
    najia_hit: bool             # 年干支是否在纳甲
    evidence: list[str] = field(default_factory=list)


@dataclass
class ShuXiongResult:
    """数之凶吉判定结果（起例卷·数足不足论）。"""
    tian_shu: int
    di_shu: int
    tian_state: str             # 有余/足/不足
    di_state: str
    shu_xiong: bool             # 数凶
    pattern: str                # 孤阳不偶/孤阴背阳/以弱敌强/安和自宁…
    evidence: list[str] = field(default_factory=list)


@dataclass
class GuaJieResult:
    """解卦层综合输出。"""
    liunian_yao: Optional[YaoDuan] = None   # 流年动爻判词
    liunian_ye_buye: Optional[YeBuYeResult] = None
    liuyue_yao: Optional[YaoDuan] = None    # 流月动爻判词（应期定位）
    liuri_yao: Optional[YaoDuan] = None     # 流日动爻判词（应期定位）
    liushi_yao: Optional[YaoDuan] = None    # 流时动爻判词（应期定位）
    shu_xiong: Optional[ShuXiongResult] = None
    yuan_qi_hit: bool = False               # 流年遇元气
    hua_gong_hit: bool = False              # 流年遇化工
    zhengdui_fandui: list[str] = field(default_factory=list)  # 正对反对警示
    twelve_xiong: bool = False              # 命卦属十二凶卦
    si_duan: list[str] = field(default_factory=list)  # 死断诸法（起例卷之下·后天详说）
    nayin_yuanqi: list[str] = field(default_factory=list)  # 纳音五行元气（起例卷之上）
    jiehua_gong: list[str] = field(default_factory=list)  # 生时值节卦化工（起例卷之下·节候卦爻）
    summary: list[str] = field(default_factory=list)  # 综合判词（人话）
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "liunian_yao": {
                "yao": self.liunian_yao.yao, "ci": self.liunian_yao.ci,
                "ye": self.liunian_yao.ye, "buye": self.liunian_yao.buye,
                "suiyun": self.liunian_yao.suiyun, "shao": self.liunian_yao.shao,
            } if self.liunian_yao else None,
            "liunian_ye_buye": {
                "ye": self.liunian_ye_buye.ye, "buye": self.liunian_ye_buye.buye,
                "najia_hit": self.liunian_ye_buye.najia_hit,
                "evidence": self.liunian_ye_buye.evidence,
            } if self.liunian_ye_buye else None,
            "liuyue_yao": {
                "yao": self.liuyue_yao.yao, "ci": self.liuyue_yao.ci,
                "ye": self.liuyue_yao.ye, "buye": self.liuyue_yao.buye,
                "suiyun": self.liuyue_yao.suiyun, "shao": self.liuyue_yao.shao,
            } if self.liuyue_yao else None,
            "liuri_yao": {
                "yao": self.liuri_yao.yao, "ci": self.liuri_yao.ci,
                "ye": self.liuri_yao.ye, "buye": self.liuri_yao.buye,
                "suiyun": self.liuri_yao.suiyun, "shao": self.liuri_yao.shao,
            } if self.liuri_yao else None,
            "liushi_yao": {
                "yao": self.liushi_yao.yao, "ci": self.liushi_yao.ci,
                "ye": self.liushi_yao.ye, "buye": self.liushi_yao.buye,
                "suiyun": self.liushi_yao.suiyun, "shao": self.liushi_yao.shao,
            } if self.liushi_yao else None,
            "shu_xiong": {
                "tian_shu": self.shu_xiong.tian_shu, "di_shu": self.shu_xiong.di_shu,
                "tian_state": self.shu_xiong.tian_state, "di_state": self.shu_xiong.di_state,
                "shu_xiong": self.shu_xiong.shu_xiong, "pattern": self.shu_xiong.pattern,
                "evidence": self.shu_xiong.evidence,
            } if self.shu_xiong else None,
            "yuan_qi_hit": self.yuan_qi_hit,
            "hua_gong_hit": self.hua_gong_hit,
            "zhengdui_fandui": self.zhengdui_fandui,
            "twelve_xiong": self.twelve_xiong,
            "si_duan": self.si_duan,
            "nayin_yuanqi": self.nayin_yuanqi,
            "jiehua_gong": self.jiehua_gong,
            "summary": self.summary,
            "evidence": self.evidence,
        }


# ═══════════════════════════════════════════════════════════════════
# 数据加载
# ═══════════════════════════════════════════════════════════════════

_LOADED: Optional[dict[str, GuaDuan]] = None


def _split_duans(duans: list[str]) -> tuple[str, str, str]:
    """把断语列表分成 叶吉/不叶/岁运 三类（原典措辞变体）。"""
    ye, buye, suiyun = [], [], []
    for d in duans:
        if any(k in d for k in ("岁运逢", "岁运值")):
            suiyun.append(d)
        elif any(k in d for k in ("叶吉", "叶者", "归元", "入局", "得时", "当此爻", "入贵格")):
            ye.append(d)
        elif any(k in d for k in ("不叶", "不归元", "不入局", "生不及时", "不及时", "难当此爻", "失正", "失位")):
            buye.append(d)
        elif any(k in d for k in ("数凶", "寿危", "身亡")):
            suiyun.append(d)
        else:
            ye.append(d)
    return " ".join(ye), " ".join(buye), " ".join(suiyun)


def _parse_gua_header(lines: list[str]) -> tuple[Optional[int], list[str]]:
    """从卦头断语提取 卦气属X月 + 纳甲干支。"""
    text = " ".join(lines)
    month = None
    m = re.search(r"(?:卦气|宫)[^属]{0,6}属([正二三四五六七八九十腊]+)月", text)
    if m:
        month = _CN_MONTH.get(m.group(1))
    if month is None:
        m = re.search(r"属(\d+)月", text)
        if m:
            month = int(m.group(1))
    najia = []
    m = re.search(r"纳甲(?:是|有)[：:]?\s*([^，。；]{2,60})", text)
    if m:
        seg = m.group(1)
        for part in re.split(r"[、，,\s]+", seg):
            part = part.strip()
            if re.fullmatch(r"[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]", part):
                najia.append(part)
            if "借用" in part or "如生" in part:
                break
    return month, najia


def load_guajie_data() -> dict[str, GuaDuan]:
    """加载 64 卦判词库（懒加载）。"""
    global _LOADED
    if _LOADED is not None:
        return _LOADED
    raw = json.loads(_GUAJIE_DATA.read_text(encoding="utf-8"))
    out: dict[str, GuaDuan] = {}
    for g in raw:
        month, najia = _parse_gua_header(g.get("lines", []))
        gd = GuaDuan(
            name=g["name"],
            gua_ci=g.get("gua_ci", ""),
            gua_qi_month=month,
            najia=najia,
            gua_lines=g.get("lines", []),
        )
        for y in g.get("yaos", []):
            ye, buye, suiyun = _split_duans(y.get("duans", []))
            gd.yaos[y["yao"]] = YaoDuan(
                yao=y["yao"], ci=y.get("ci", ""), xiang=y.get("xiang", ""),
                yi=y.get("yi", ""), ye=ye, buye=buye, suiyun=suiyun, shao=y.get("shao", ""),
            )
        out[g["name"]] = gd
    _LOADED = out
    return out


def query_yao_duan(hexagram_name: str, yao_name: str) -> Optional[YaoDuan]:
    """查 64 卦逐爻判词（查询式字典）。"""
    data = load_guajie_data()
    g = data.get(hexagram_name)
    if g is None:
        return None
    return g.yaos.get(yao_name)


# ═══════════════════════════════════════════════════════════════════
# 叶/不叶判定
# ═══════════════════════════════════════════════════════════════════

def judge_ye_buye(
    hexagram_name: str,
    birth_month: int,
    year_ganzhi: str = "",
) -> Optional[YeBuYeResult]:
    """
    判定某卦的叶/不叶（得时 + 纳甲本命）。

    原典（乾卦）：
      "卦气属四月，纳甲是甲子甲寅甲辰壬午壬申壬戌…如生于四月及纳甲本命者，
       多属富贵…乾金秋正旺，如生月不及时又不在纳甲者，主贫贱"
      "生于二月以后八月以前者，得时也"
    """
    data = load_guajie_data()
    g = data.get(hexagram_name)
    if g is None:
        return None
    ev: list[str] = []
    ye = False
    buye = False

    # 1. 卦气月匹配
    if g.gua_qi_month is not None:
        if birth_month == g.gua_qi_month:
            ye = True
            ev.append(f"生月{birth_month}月 = 卦气月（{g.name}卦气属{g.gua_qi_month}月）→ 得时")
        else:
            ev.append(f"生月{birth_month}月 ≠ 卦气月{g.gua_qi_month}月")
    else:
        ev.append(f"{g.name}卦无卦气月记录")

    # 2. 纳甲本命（生年干支是否在纳甲）
    najia_hit = False
    if g.najia and year_ganzhi:
        najia_hit = year_ganzhi in g.najia
        ev.append(f"年干支{year_ganzhi} {'在' if najia_hit else '不在'}纳甲[{','.join(g.najia)}]")
    elif g.najia:
        ev.append(f"未提供年干支，纳甲[{','.join(g.najia)}]不参与判定")

    # 3. 旺时区间（卦头 lines 中的"生于X月以后X月以前者得时"）
    gua_text = " ".join(g.gua_lines)
    m = re.search(r"生于([正二三四五六七八九十腊]+)月以后([正二三四五六七八九十腊]+)月以前[^\n，。]*得时", gua_text)
    if m:
        lo, hi = _CN_MONTH[m.group(1)], _CN_MONTH[m.group(2)]
        if lo <= birth_month <= hi:
            ye = True
            ev.append(f"生月{birth_month} ∈ 旺时[{lo}月,{hi}月]（{g.name}得时）")
        else:
            ev.append(f"生月{birth_month} ∉ 旺时[{lo}月,{hi}月]")
    m2 = re.search(r"如生(月)?不及时[^，。]*不在纳甲[^，。]*", gua_text)
    if m2:
        ev.append(f"卦头提示：{m2.group(0)}")

    if not ye and not najia_hit:
        buye = True
        ev.append("生月不当时令、年干支不在纳甲 → 不叶（凶象，须结合元气化工与爻辞断吉凶）")
    elif ye and najia_hit:
        ev.append("得时 + 纳甲本命 → 叶（吉象，富贵之兆）")
    elif ye and not najia_hit:
        ev.append("得时但不在纳甲 → 半叶（吉中带损，依爻辞细断）")
    elif not ye and najia_hit:
        ev.append("不在卦气时令但年干支合纳甲 → 半叶")

    return YeBuYeResult(ye=ye, buye=buye, gua_qi_month=g.gua_qi_month,
                        birth_month=birth_month, najia_hit=najia_hit, evidence=ev)


# ═══════════════════════════════════════════════════════════════════
# 数之凶吉（起例卷·数足不足论）
# ═══════════════════════════════════════════════════════════════════

def judge_shu_xiong(tian_shu: int, di_shu: int, birth_month: int) -> ShuXiongResult:
    """
    数足不足论（原典）：
      天数二十五为正、地数三十为正；无余无不足=最佳（安和自宁）。
      天数不足<25；地数不足<30。
      孤阳不偶：天26-40且地=30（阳有余阴无余）
      孤阴背阳：地30-60且天=25（阴有余阳无余）
      以弱敌强：地30-60+且天<24（地太过天不足）→ 阳月令逢之必主灭顶之凶
      太过有余伤（诗）：有余为凶。
    """
    ev: list[str] = []
    t_state = "有余" if tian_shu > 25 else ("不足" if tian_shu < 25 else "足")
    d_state = "有余" if di_shu > 30 else ("不足" if di_shu < 30 else "足")
    ev.append(f"天数{tian_shu}（正=25，{t_state}）；地数{di_shu}（正=30，{d_state}）")

    pattern = ""
    shu_xiong = False
    if t_state == "足" and d_state == "足":
        pattern = "安和自宁"
        ev.append("天地二数无余无不足，最佳，吉凶极定（依卦中断）")
    elif 26 <= tian_shu <= 40 and di_shu == 30:
        pattern = "孤阳不偶"
        ev.append("天数26-40、地数30：阳数有余、阴数无余 → 孤阳不偶")
    elif 30 <= di_shu <= 60 and tian_shu == 25:
        pattern = "孤阴背阳"
        ev.append("地数30-60、天数25：阴数有余、阳数无余 → 孤阴背阳")
    elif di_shu >= 30 and tian_shu <= 24:
        pattern = "以弱敌强"
        ev.append("地数30以上、天数24以下：地数太过天数不足 → 以弱敌强")
    elif t_state == "有余" or d_state == "有余":
        pattern = "太过有余"
        ev.append("天数或地数有余 → 太过有余伤（诗曰：太过有余伤，性暴应多狠，祸去有余殃）")

    # 数凶：有余/不足 + 生月合时（阳月/阴月）
    # 卢某：地40有余 + 生三月（谷雨-芒种，阳月）→ 数凶
    yang_month = birth_month in (1, 2, 3, 4, 5, 6)  # 春夏季为阳月（简化，原典按节气细分）
    if pattern in ("孤阳不偶", "孤阴背阳", "以弱敌强", "太过有余"):
        if yang_month:
            shu_xiong = True
            ev.append(f"生月{birth_month}月（阳月），数有余逢阳月 → 数凶（不可妄行致凶）")
        else:
            ev.append(f"生月{birth_month}月（阴月），数有余逢阴月 → 数凶程度减轻（依爻辞细断）")
    elif t_state == "不足" or d_state == "不足":
        shu_xiong = True
        ev.append("数不足 → 主夭贫贱薄（虚贫之象），须参元气化工与卦爻断")
    ev.append("判词：数凶者身亡，但德小者不能当之")

    return ShuXiongResult(tian_shu=tian_shu, di_shu=di_shu, tian_state=t_state,
                          di_state=d_state, shu_xiong=shu_xiong, pattern=pattern, evidence=ev)


# ═══════════════════════════════════════════════════════════════════
# 正对反对（生死大凶断）
# ═══════════════════════════════════════════════════════════════════

def check_zhengdui_fandui(hexagram: str, other_hexagram: str = "") -> list[str]:
    """
    检查流年卦/命卦是否与对宫构成正对/反对。

    原典依据（《河洛真数·起例卷之上·八卦游年图》）：
      "皆变为体　三爻毕变为体。以卦考之，即正对也。故谓之绝体，
       宜与绝命相同，而诸凶此为最焉" → 正对=三画卦三爻全变（六画卦六爻全变等价）
    《起例卷之下·出后天六合论》：反对+爻凶理失→寿终；《后天详说》：
      "如遇小象与大象反对，定死无疑" → 反对=卦象倒转（综），生死断关键。

    实现映射：
    - 正对（原著=绝体）：六爻全变（三画对宫）
    - 反对（原著=游魂/倒转）：六爻倒转
    - 十二凶卦：⚠️ 今人口径（三门观易整理），10 卷原文未见，仅供判词参考
    返回警示列表（空=无）。
    """
    warns: list[str] = []
    # 正对：错卦
    if hexagram in COMPOUND_GUA and other_hexagram in COMPOUND_GUA:
        u1, l1 = COMPOUND_GUA[hexagram]
        u2, l2 = COMPOUND_GUA[other_hexagram]
        if OPPOSITE_TRIGRAM.get(u1) == u2 and OPPOSITE_TRIGRAM.get(l1) == l2:
            warns.append(f"{hexagram}与{other_hexagram}互为错卦（正对），六爻全变")
    # 反对：综卦
    if ZONG_GUA.get(hexagram) == other_hexagram:
        warns.append(f"{hexagram}与{other_hexagram}互为综卦（反对），卦象倒转")
    # 十二凶卦
    if hexagram in TWELVE_XIONG_GUA:
        warns.append(f"命卦{hexagram}属十二凶卦（复临泰大壮夬乾姤遁否观剥坤）→ 不吉，若卦中相生或与月卦相投可去凶")
    return warns


# ═══════════════════════════════════════════════════════════════════
# 死断诸法（起例卷之下·后天详说）
# ═══════════════════════════════════════════════════════════════════

def _yao_buji(ci: str, buye: str = "", suiyun: str = "") -> bool:
    """判爻辞凶（含不叶/岁运逢凶）。原典：爻凶理失/爻辞凶。"""
    text = f"{ci} {buye} {suiyun}"
    bad = ("凶", "危", "死", "灾", "咎", "厉", "悔", "亡", "败", "伤", "困", "病", "讼")
    return any(w in text for w in bad)


def judge_si_duan(
    *,
    prenatal_name: str,
    postnatal_name: str,
    tian_yuan_fan: str = "",        # 天元反卦（年干纳甲之错卦）
    di_yuan_fan: str = "",          # 地元反卦（年支宫位之错卦）
    shu_xiong: bool = False,        # 数凶
    dayun_line_index: int | None = None,      # 当前大运行至爻位（0初~5上）
    recent_years: list[dict] | None = None,   # 近3年流年判词 [{year, hexagram, yao, ci, buye, suiyun}]
) -> list[str]:
    """
    死断诸法（《河洛真数·起例卷之下·后天详说》原文逐条）：

      1. "如后天之气数行至君爻之位，此为数足，到此必死。
         无阴骘者，生日之前便死。……有阴骘者，到君爻阳爻延九年"
         → 大运行至五爻（君爻）→ 数足必死警示
      2. "纵到君爻，亦不许行至上极一爻，寿必不久"
         → 行至上爻（上极）→ 寿必不久警示
      3. "若行后天，连三爻不吉，必多坎壈。若过了第四爻，遇凶，十死八九"
         → 近3爻不吉→坎壈；过四爻（五爻）遇凶→十死八九
      4. "如遇小象与大象反对，定死无疑"
         → 流年卦与命卦成反对 + 爻辞凶 → 定死无疑（由调用方传入 recent_years 判定）
      5. "若流年连三年不吉，卦爻又不吉，本身卦不佳，重反支干元气，便可以死断之"
         → 近3年流年卦爻皆不吉 + 数凶（卦不佳） + 干支元气俱反 → 死断
    """
    warns: list[str] = []

    # 1+2+3. 大运爻位死断
    if dayun_line_index is not None:
        if dayun_line_index == 5:
            warns.append("后天之气数行至上极一爻（上爻），寿必不久（原典：纵到君爻，亦不许行至上极一爻）")
        if dayun_line_index >= 4:
            warns.append("后天之气数行至君爻（五爻）之位，此为数足，到此必死。无阴骘者生日之前便死，有阴骘者到君爻阳爻延九年（原典：后天详说）")
        elif dayun_line_index == 3 and recent_years and _yao_buji(
            recent_years[-1].get("ci", ""), recent_years[-1].get("buye", ""), recent_years[-1].get("suiyun", "")):
            warns.append("行数过第四爻（五爻）遇凶 → 十死八九（原典：若过了第四爻，遇凶，十死八九）")

    # 3b. 连三爻不吉 → 多坎壈（近3个大运爻判词凶）
    if dayun_line_index is not None and dayun_line_index < 4 and recent_years and len(recent_years) >= 3:
        if all(_yao_buji(y.get("ci", ""), y.get("buye", ""), y.get("suiyun", "")) for y in recent_years[-3:]):
            warns.append("若行后天，连三爻不吉，必多坎壈（原典：后天详说）")

    # 4. 小象与大象反对 → 定死无疑（流年卦与命卦反对 + 爻辞凶）
    if recent_years:
        cur = recent_years[-1]
        hx = cur.get("hexagram", "")
        if hx:
            fan_warns = check_zhengdui_fandui(hx, prenatal_name) + check_zhengdui_fandui(hx, postnatal_name)
            if any("反对" in w for w in fan_warns) and _yao_buji(cur.get("ci", ""), cur.get("buye", ""), cur.get("suiyun", "")):
                warns.append(f"如遇小象与大象反对（流年卦{hx}与命卦反对）+ 爻凶 → 定死无疑（原典：后天详说）")

    # 5. 流年连三年不吉 + 卦爻不吉 + 本身卦不佳 + 重反支干元气 → 死断
    if (
        recent_years and len(recent_years) >= 3
        and all(_yao_buji(y.get("ci", ""), y.get("buye", ""), y.get("suiyun", "")) for y in recent_years[-3:])
        and shu_xiong
        and tian_yuan_fan and di_yuan_fan
        and _in_gua(tian_yuan_fan, prenatal_name, postnatal_name)
        and _in_gua(di_yuan_fan, prenatal_name, postnatal_name)
    ):
        warns.append(
            f"流年连三年不吉 + 本身卦不佳（数凶） + 重反支干元气"
            f"（天元反{tian_yuan_fan}、地元反{di_yuan_fan}俱在命卦）→ 便可以死断之（原典：后天详说）")

    return warns


def _in_gua(trigram: str, *gua_names: str) -> bool:
    """三画卦是否出现在某命卦（上/下卦）中。"""
    for g in gua_names:
        if g in COMPOUND_GUA and trigram in COMPOUND_GUA[g]:
            return True
    return False


# ═══════════════════════════════════════════════════════════════════
# 综合断卦
# ═══════════════════════════════════════════════════════════════════

def compose_guajie(
    *,
    # 命主主链
    prenatal_name: str,
    postnatal_name: str,
    yuantang_yao: str,            # 先天元堂爻名（如"九三"）
    birth_month: int,
    tian_shu: int,
    di_shu: int,
    year_ganzhi: str = "",        # 年干支（纳甲本命）
    # 流年
    liunian_hexagram: str = "",
    liunian_yao: str = "",
    # 流月（应期）
    liuyue_hexagram: str = "",
    liuyue_yao: str = "",
    # 元气化工
    yuan_qi_trigrams: list[str] | None = None,   # 天/地元气卦
    hua_gong_trigram: str = "",
) -> GuaJieResult:
    """
    组合解卦：先天/后天 + 元堂 + 流年判词 + 流月应期 + 数凶 + 元气化工 + 正对反对。
    """
    res = GuaJieResult()
    ev = res.evidence

    # ── 流年动爻判词（查询式字典） ──────────────────────────────
    if liunian_hexagram and liunian_yao:
        y = query_yao_duan(liunian_hexagram, liunian_yao)
        if y:
            res.liunian_yao = y
            ev.append(f"流年卦{liunian_hexagram} {liunian_yao}爻：{y.ci}")
            if y.ye:
                ev.append(f"  叶者：{y.ye}")
            if y.buye:
                ev.append(f"  不叶者：{y.buye}")
            if y.suiyun:
                ev.append(f"  岁运逢之：{y.suiyun}")
        # 叶/不叶
        yb = judge_ye_buye(liunian_hexagram, birth_month, year_ganzhi)
        if yb:
            res.liunian_ye_buye = yb
            ev.extend(f"  叶/不叶：{e}" for e in yb.evidence)
        # 正对反对（流年卦 vs 命卦）
        zdfd = check_zhengdui_fandui(liunian_hexagram, prenatal_name)
        zdfd += check_zhengdui_fandui(liunian_hexagram, postnatal_name)
        res.zhengdui_fandui = zdfd
        ev.extend(f"  正对反对：{w}" for w in zdfd)

    # ── 流月应期 ──────────────────────────────────────────────
    if liuyue_hexagram and liuyue_yao:
        y = query_yao_duan(liuyue_hexagram, liuyue_yao)
        if y:
            res.liuyue_yao = y
            ev.append(f"流月卦{liuyue_hexagram} {liuyue_yao}爻：{y.ci}")
            if y.suiyun:
                ev.append(f"  岁运逢之：{y.suiyun}")

    # ── 数凶 ──────────────────────────────────────────────────
    sx = judge_shu_xiong(tian_shu, di_shu, birth_month)
    res.shu_xiong = sx
    ev.extend(f"  数之凶吉：{e}" for e in sx.evidence)

    # ── 元气化工（流年遇） ─────────────────────────────────────
    if yuan_qi_trigrams:
        res.yuan_qi_hit = bool(yuan_qi_trigrams)
        if res.yuan_qi_hit:
            ev.append("流年遇元气 → 必然得财利")
    if hua_gong_trigram:
        res.hua_gong_hit = True
        ev.append(f"流年遇化工（{hua_gong_trigram}）→ 中举中进士生贵子")

    # ── 纳音五行元气（互体亦算，起例卷之上） ─────────────────────
    if year_ganzhi and len(year_ganzhi) == 2:
        nayin_ev = judge_nayin_yuanqi(year_ganzhi[0], year_ganzhi[1], prenatal_name)
        if nayin_ev:
            res.nayin_yuanqi.extend(nayin_ev)
            ev.extend(f"  纳音元气：{e}" for e in nayin_ev)
        huti_ev: list[str] = []
        for g in (prenatal_name, postnatal_name):
            if g in COMPOUND_GUA:
                pass  # 互体需六爻序列，主链另行挂载（build 层）
        if huti_ev:
            res.nayin_yuanqi.extend(huti_ev)
            ev.extend(f"  互体纳音：{e}" for e in huti_ev)

    # ── 元堂断语（六位贵贱，起例卷之上） ───────────────────────
    # 原典："初为元士，二为侯牧，三为公乡节制，四为近侍大臣，
    #        五为君位，六为天枢，又为宗庙宫庭大内，又为山林八极之外。
    #        惟五位为佳，二次之，三四又次之"
    if yuantang_yao:
        _wei = yuantang_yao[1] if len(yuantang_yao) > 1 and yuantang_yao[0] in ("九", "六") else yuantang_yao[0]
        if _wei == "初":
            ev.append(f"元堂居{yuantang_yao}（元士位）：多从寒微起家（原典：初为元士，元堂居初爻者多从寒微起家）")
        elif _wei == "二":
            ev.append(f"元堂居{yuantang_yao}（侯牧位）：卦佳数足可牧民一方（原典：二为侯牧，惟五位为佳二次之）")
        elif _wei == "三":
            ev.append(f"元堂居{yuantang_yao}（公乡节制位）：掌节制之权，次五二之贵（原典：三为公乡节制）")
        elif _wei == "四":
            ev.append(f"元堂居{yuantang_yao}（近侍大臣位）：近君侍从之贵（原典：四为近侍大臣）")
        elif _wei == "五":
            ev.append(f"元堂居{yuantang_yao}（君位）：卦名佳、二数足、化工元气得时 → 贤良上贵之命（原典：五为君位，惟五位为佳）")
        elif _wei == "上":
            ev.append(f"元堂居{yuantang_yao}（天枢/宗庙宫庭大内/山林八极之外）：贵极为三公，否则闲散卑职（原典：六为天枢…山林八极之外）")

    # ── 十二凶卦（命卦） ───────────────────────────────────────
    if prenatal_name in TWELVE_XIONG_GUA:
        res.twelve_xiong = True
        ev.append(f"先天命卦{prenatal_name}属十二凶卦之一 → 不吉（相生或与月卦相投可去凶）")

    # ── 综合判词（人话摘要） ───────────────────────────────────
    s = res.summary
    if res.liunian_yao:
        if res.liunian_yao.ye:
            s.append(f"流年{liunian_hexagram}{liunian_yao}爻叶者：{res.liunian_yao.ye}")
        if res.liunian_yao.buye:
            s.append(f"流年{liunian_hexagram}{liunian_yao}爻不叶者：{res.liunian_yao.buye}")
        if res.liunian_yao.suiyun:
            s.append(f"岁运逢之：{res.liunian_yao.suiyun}")
    if sx.shu_xiong:
        s.append(f"数凶（{sx.pattern}：天{sx.tian_shu}/{sx.di_shu}）→ 数凶者身亡，但德小者不能当之")
    if res.zhengdui_fandui:
        s.append("流年卦与命卦成正对/反对 + 爻辞凶 + 无元气化工 → 生死大凶（不死亦有横灾）")
    if res.yuan_qi_hit and not sx.shu_xiong:
        s.append("流年遇元气/化工 → 得财利、科甲之喜；爻辞虽凶，于富贵天年不碍")
    if not s:
        s.append("（无流年/流月输入，仅命卦判词）")

    return res


# 月支 → 节气月（寅=正月…丑=十二月，河洛以节气定月）
BRANCH_TO_MONTH = {"寅": 1, "卯": 2, "辰": 3, "巳": 4, "午": 5, "未": 6,
                   "申": 7, "酉": 8, "戌": 9, "亥": 10, "子": 11, "丑": 12}

# 全称 → 简称（64 卦，与 yi_interpreter ALIASES 一致反查）
_FULL_TO_SHORT = {
    "乾为天": "乾", "坤为地": "坤", "水雷屯": "屯", "山水蒙": "蒙",
    "水天需": "需", "天水讼": "讼", "地水师": "师", "水地比": "比",
    "风天小畜": "小畜", "天泽履": "履", "地天泰": "泰", "天地否": "否",
    "天火同人": "同人", "火天大有": "大有", "地山谦": "谦", "雷地豫": "豫",
    "泽雷随": "随", "山风蛊": "蛊", "地泽临": "临", "风地观": "观",
    "火雷噬嗑": "噬嗑", "山火贲": "贲", "山地剥": "剥", "地雷复": "复",
    "天雷无妄": "无妄", "山天大畜": "大畜", "山雷颐": "颐", "泽风大过": "大过",
    "坎为水": "坎", "离为火": "离", "泽山咸": "咸", "雷风恒": "恒",
    "天山遁": "遁", "雷天大壮": "大壮", "火地晋": "晋", "地火明夷": "明夷",
    "风火家人": "家人", "火泽睽": "睽", "水山蹇": "蹇", "雷水解": "解",
    "山泽损": "损", "风雷益": "益", "泽天夬": "夬", "天风姤": "姤",
    "泽地萃": "萃", "地风升": "升", "泽水困": "困", "水风井": "井",
    "泽火革": "革", "火风鼎": "鼎", "震为雷": "震", "艮为山": "艮",
    "风山渐": "渐", "雷泽归妹": "归妹", "雷火丰": "丰", "火山旅": "旅",
    "巽为风": "巽", "兑为泽": "兑", "风水涣": "涣", "水泽节": "节",
    "风泽中孚": "中孚", "雷山小过": "小过", "水火既济": "既济", "火水未济": "未济",
}


def _short(name: str) -> str:
    return _FULL_TO_SHORT.get(name, name)


def _yao_name(idx: int, line: int) -> str:
    """爻索引+爻性 → 爻名（1=阳 -1=阴）。"""
    pos = ("初", "二", "三", "四", "五", "上")[idx]
    ch = "九" if line == 1 else "六"
    if idx in (0, 5):
        return f"{pos}{ch}"
    return f"{ch}{pos}"


def build_guajie_from_result(
    result,
    bazi: list[tuple[str, str]] | None = None,
    target_year: int | None = None,
    target_month: int | None = None,
    target_day: int | None = None,
    target_hour: int | None = None,
    liuyue_hexagram: str = "",
    liuyue_yao: str = "",
) -> dict:
    """
    从 HeluoResult 构建解卦层输出（挂载到 result.guajie）。

    bazi: 中文四柱 [(年干,年支),(月干,月支),(日干,日支),(时干,时支)]，
          缺省时退化为仅命卦判词（无流年解）。
    target_year: 指定解某公历流年（缺省解命卦基础判词）。
    target_month: 流月应期定位（1-12，农历月），从该流年 timeline.months 自动取卦。
    target_day: 流日应期定位（1-30），按《河洛真数》起日卦例每爻管5日，从流月 days 自动取卦。
    liuyue_hexagram/liuyue_yao: 手动指定流月（可选，优先于 target_month）。
    """
    try:
        prenatal = _short(result.prenatal.hexagram_name)
        postnatal = _short(result.postnatal.hexagram_name)
        yuantang_yao = result.yuantang.yuantang
        tian = result.numbers.tian_shu
        di = result.numbers.di_shu

        birth_month = None
        year_ganzhi = ""
        if bazi and len(bazi) >= 2:
            year_ganzhi = bazi[0][0] + bazi[0][1]
            mb = bazi[1][1]
            birth_month = BRANCH_TO_MONTH.get(mb)

        # 流年（timeline 定位）
        liunian_hex = ""
        liunian_yao_name = ""
        liuyue_hex_name = liuyue_hexagram
        liuyue_yao_name = liuyue_yao
        liuri_hex_name = ""
        liuri_yao_name = ""
        liushi_hex_name = ""
        liushi_yao_name = ""
        if target_year is not None and result.timeline is not None:
            entries = result.timeline.yearly_hexagrams or []
            for i, e in enumerate(entries):
                if e.get("year") == target_year:
                    liunian_hex = _short(e.get("hexagram", ""))
                    # 流年卦断爻：优先取流年卦元堂爻（规格书：流年断爻=流年卦元堂，
                    # 流月亦以流年卦元堂为本）；无则回退逐年差异动爻；再无则先天元堂
                    yyt = e.get("yuantang_index")
                    cur_lines = e.get("lines") or []
                    if yyt is not None and len(cur_lines) > yyt:
                        liunian_yao_name = _yao_name(yyt, cur_lines[yyt])
                    if not liunian_yao_name and i > 0:
                        prev_lines = entries[i - 1].get("lines") or []
                        diffs = [k for k in range(6) if len(cur_lines) > k and len(prev_lines) > k and cur_lines[k] != prev_lines[k]]
                        if len(diffs) == 1 and len(cur_lines) > diffs[0]:
                            liunian_yao_name = _yao_name(diffs[0], cur_lines[diffs[0]])
                    if not liunian_yao_name:
                        liunian_yao_name = yuantang_yao
                    # 流月应期：从当年 months 自动定位
                    if target_month and not liuyue_hex_name:
                        for m in (e.get("months") or []):
                            if m.get("month") == target_month:
                                liuyue_hex_name = _short(m.get("name", ""))
                                yi = m.get("yue_yao_index")
                                ml = m.get("lines") or []
                                if yi is not None and len(ml) > yi:
                                    liuyue_yao_name = _yao_name(yi, ml[yi])
                                # 流日应期：当月 days 段（每爻管5日）自动定位
                                if target_day and m.get("days"):
                                    for dseg in m["days"]:
                                        d_from = dseg.get("day_from", 1)
                                        d_to = dseg.get("day_to", 5)
                                        if d_from <= target_day <= d_to:
                                            liuri_hex_name = _short(dseg.get("name", ""))
                                            dl = dseg.get("lines") or []
                                            diffs = [k for k in range(6) if len(dl) > k and len(ml) > k and dl[k] != ml[k]]
                                            if len(diffs) == 1 and len(dl) > diffs[0]:
                                                liuri_yao_name = _yao_name(diffs[0], dl[diffs[0]])
                                            # 流时应期：值日卦 hours（起时卦例：前六时进/后六时退）
                                            if target_hour and dseg.get("hours"):
                                                for hs in dseg["hours"]:
                                                    if hs.get("hour") == target_hour:
                                                        liushi_hex_name = _short(hs.get("name", ""))
                                                        si = hs.get("shi_yao_index")
                                                        sl = hs.get("lines") or []
                                                        if si is not None and len(sl) > si:
                                                            liushi_yao_name = _yao_name(si, sl[si])
                                                        break
                                            break
                                break
                    break

        gj = compose_guajie(
            prenatal_name=prenatal, postnatal_name=postnatal,
            yuantang_yao=yuantang_yao,
            birth_month=birth_month or 1, tian_shu=tian, di_shu=di,
            year_ganzhi=year_ganzhi,
            liunian_hexagram=liunian_hex, liunian_yao=liunian_yao_name,
            liuyue_hexagram=liuyue_hex_name, liuyue_yao=liuyue_yao_name,
        )
        # 流日判词（应期定位，独立查询不并入综合判词）
        if liuri_hex_name and liuri_yao_name:
            gj.liuri_yao = query_yao_duan(liuri_hex_name, liuri_yao_name)
            gj.evidence.append(
                f"流日定位：{liuri_hex_name}{liuri_yao_name}（原典起日卦例·每爻管5日，第{target_day}日）")
        # 流时判词（起时卦例：值日卦前六时进数/后六时退数）
        if liushi_hex_name and liushi_yao_name:
            gj.liushi_yao = query_yao_duan(liushi_hex_name, liushi_yao_name)
            gj.evidence.append(
                f"流时定位：{liushi_hex_name}{liushi_yao_name}（原典起时卦例·{['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'][(target_hour or 1)-1]}时）")

        # ── 生时化工（四正节卦，起例卷之下·节候卦爻） ────────────────
        try:
            bd = getattr(result.input, "birth_date", "") or ""
            if bd:
                jh = judge_jiehua_gong(bd)
                gj.jiehua_gong = jh
                gj.evidence.extend(f"  节候卦化工：{e}" for e in jh)
                if jh and "化工" in jh[0]:
                    gj.summary.append(jh[0])
        except Exception as _e:
            gj.evidence.append(f"  节候卦化工：跳过（{_e}）")

        # ── 互体纳音元气（起例卷之上：互体有兑亦是纳音元气） ─────────
        try:
            if bazi and len(bazi) >= 1:
                hn = judge_nayin_huti(bazi[0][0], bazi[0][1], prenatal, postnatal)
                if hn:
                    gj.nayin_yuanqi.extend(hn)
                    gj.evidence.extend(f"  互体纳音：{e}" for e in hn)
        except Exception as _e:
            gj.evidence.append(f"  互体纳音：跳过（{_e}）")

        # ── 死断诸法（起例卷之下·后天详说） ─────────────────────────
        try:
            si = _collect_si_duan(
                result=result, prenatal=prenatal, postnatal=postnatal,
                bazi=bazi, target_year=target_year,
                shu_xiong=gj.shu_xiong.shu_xiong if gj.shu_xiong else False,
                year_ganzhi=year_ganzhi,
            )
            gj.si_duan = si
            gj.evidence.extend(f"  死断：{w}" for w in si)
            for w in si:
                if "死断" in w or "必死" in w or "定死" in w:
                    gj.summary.append(w)
        except Exception as _e:  # 死断不阻塞主链
            gj.evidence.append(f"  死断：计算跳过（{_e}）")

        return gj.to_dict()
    except Exception as e:  # 解卦层不阻塞主链（防御性兜底）
        return {"error": f"guajie 构建失败: {e}"}


def _collect_si_duan(
    *,
    result,
    prenatal: str,
    postnatal: str,
    bazi: list[tuple[str, str]] | None,
    target_year: int | None,
    shu_xiong: bool,
    year_ganzhi: str,
) -> list[str]:
    """收集死断诸法（后天详说）：大运爻位 + 近3年流年判词 + 重反支干元气。"""
    if not bazi or len(bazi) < 1:
        return []
    year_stem, year_branch = bazi[0][0], bazi[0][1]
    tian = STEM_TO_TRIGRAM.get(year_stem, "")
    tian_fan = OPPOSITE_TRIGRAM.get(tian, "")
    di = BRANCH_TO_TRIGRAM.get(year_branch, "")
    di_fan = OPPOSITE_TRIGRAM.get(di, "")

    # 当前大运爻位（qi_phase.dayun：age_start..age_end → line_index）
    dayun_line_index: int | None = None
    qi = (result.timeline.qi_phase if result.timeline else None) or {}
    dayun_entries = qi.get("dayun") or []
    age_now: int | None = None
    if target_year is not None and result.timeline is not None:
        for e in (result.timeline.yearly_hexagrams or []):
            if e.get("year") == target_year:
                age_now = e.get("age")
                break
    if age_now is not None:
        for de in dayun_entries:
            if de.get("age_start") and de.get("age_end") and de["age_start"] <= age_now <= de["age_end"]:
                dayun_line_index = de.get("line_index")
                break

    # 近3年流年判词（target_year-2 .. target_year）
    recent: list[dict] = []
    if target_year is not None and result.timeline is not None:
        for e in (result.timeline.yearly_hexagrams or []):
            y = e.get("year")
            if y is not None and target_year - 2 <= y <= target_year:
                hx = _short(e.get("hexagram", ""))
                yyt = e.get("yuantang_index")
                cur_lines = e.get("lines") or []
                yao_name = ""
                if yyt is not None and len(cur_lines) > yyt:
                    yao_name = _yao_name(yyt, cur_lines[yyt])
                d = query_yao_duan(hx, yao_name) if yao_name else None
                recent.append({
                    "year": y, "hexagram": hx, "yao": yao_name,
                    "ci": (d.ci if d else ""), "buye": (d.buye if d else ""),
                    "suiyun": (d.suiyun if d else ""),
                })
        recent.sort(key=lambda r: r["year"])

    return judge_si_duan(
        prenatal_name=prenatal, postnatal_name=postnatal,
        tian_yuan_fan=tian_fan, di_yuan_fan=di_fan,
        shu_xiong=shu_xiong,
        dayun_line_index=dayun_line_index,
        recent_years=recent or None,
    )


__all__ = [
    "GuaDuan", "YaoDuan", "YeBuYeResult", "ShuXiongResult", "GuaJieResult",
    "load_guajie_data", "query_yao_duan", "judge_ye_buye",
    "judge_shu_xiong", "check_zhengdui_fandui", "judge_si_duan",
    "compute_huti", "judge_nayin_yuanqi", "get_nayin_element",
    "judge_jiehua_gong", "judge_nayin_huti", "hexagram_to_lines",
    "compose_guajie", "build_guajie_from_result",
    "TWELVE_XIONG_GUA", "OPPOSITE_TRIGRAM", "ZONG_GUA", "BRANCH_TO_MONTH",
    "TRIGRAM_ELEMENT", "ELEMENT_GENERATES",
]
