"""
八字分析器 — 统一八字排盘 + 五行分析 + 大运流年 + 喜用神 v1
核心：lunar-python 四柱 + 自研五行/大运/喜用神
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from .types import GanZhi
from .constants import (
    TIAN_GAN, DI_ZHI, GAN_WUXING, ZHI_WUXING,
    GAN_YINYANG, ZHI_YINYANG, WUXING_SHENG, WUXING_KE,
    HIDDEN_STEMS, HIDDEN_STEM_WEIGHTS, ALL_24_JIE_QI, JIE_NAMES, JIE_TO_ZHI,
)
from .lunar import get_day_ganzhi

CST = timezone(timedelta(hours=8))


# ============================================================
# 输入/输出类型
# ============================================================

@dataclass
class BirthInfo:
    """出生信息"""
    date: date          # 公历出生日期（当地钟表日期）
    time: str           # "HH:MM"（当地钟表时间）
    gender: str         # "male" / "female"
    city: str = ""      # 城市名（可选，用于真太阳时）
    lat: float = 0      # 纬度
    lon: float = 0      # 经度（东经正，西经负）
    tz_offset: float = 8.0  # 出生地时区相对 UTC 的小时偏移（标准时间，不含夏令时）
    daylight_saving: bool = False  # 出生时是否执行夏令时（如适用，自动 +1h）


@dataclass
class BaZiChart:
    """完整八字命盘"""
    input: dict
    pillars: dict[str, GanZhi]          # 四柱
    day_master: dict                    # 日主
    five_elements: dict                 # 五行力量
    day_master_strength: str            # 偏强/偏弱
    yongshen: dict                      # 喜用神
    relationships: list[dict]           # 刑冲合害
    major_luck: dict                    # 大运
    liunian: Optional[dict] = None      # 流年


# ============================================================
# 真太阳时修正
# ============================================================

def equation_of_time(dt: datetime) -> float:
    """均时差（Spencer 公式，分钟）"""
    day_of_year = dt.timetuple().tm_yday
    B = 2 * 3.1415926535 * (day_of_year - 81) / 365.0
    return 9.87 * __import__('math').sin(2 * B) - 7.53 * __import__('math').cos(B) - 1.5 * __import__('math').sin(B)


def correct_true_solar_time(dt_local: datetime, longitude: float, tz_offset: float) -> datetime:
    """
    当地钟表时间 → 当地真太阳时（当地时间轴）
    真太阳时 = 当地时间 + (经度 − 时区标准子午线)×4min + EoT
    """
    standard_meridian = tz_offset * 15.0
    lon_corr = (longitude - standard_meridian) * 4.0  # 分钟
    eot = equation_of_time(dt_local)
    return dt_local + timedelta(minutes=lon_corr + eot)


# ============================================================
# 五行分析
# ============================================================

def analyze_five_elements(pillars: dict[str, GanZhi]) -> dict:
    """
    五行力量分析
    天干：1分；地支藏干：本气0.6，中气0.3，余气0.1
    """
    scores = {"木": 0.0, "火": 0.0, "土": 0.0, "金": 0.0, "水": 0.0}

    for pos in ["year", "month", "day", "hour"]:
        gz = pillars[pos]
        # 天干
        scores[GAN_WUXING[gz.stem]] += 1.0
        # 地支藏干
        stems = HIDDEN_STEMS.get(gz.branch, [])
        stems = [s for s in stems if s is not None]
        weights = HIDDEN_STEM_WEIGHTS.get(len(stems), [1.0])
        for s, w in zip(stems, weights):
            scores[GAN_WUXING[s]] += w

    total = sum(scores.values()) or 1
    result = {}
    for wx in ["木", "火", "土", "金", "水"]:
        en = {"木": "wood", "火": "fire", "土": "earth", "金": "metal", "水": "water"}[wx]
        result[en] = {
            "score": round(scores[wx], 1),
            "percent": f"{round(scores[wx] / total * 100)}%",
            "chinese": wx,
        }
    return result


def judge_day_master_strength(day_stem: str, month_branch: str, pillars: dict[str, GanZhi]) -> str:
    """简易日主强弱判断（得令/得地/得生/得助）"""
    me_wx = GAN_WUXING[day_stem]
    support = 0

    # 1. 得令：月支本气生我 or 同我
    month_hidden = [s for s in HIDDEN_STEMS.get(month_branch, []) if s is not None]
    if month_hidden:
        main_qi_wx = GAN_WUXING[month_hidden[0]]
        if main_qi_wx == me_wx or WUXING_SHENG.get(main_qi_wx) == me_wx:
            support += 1

    # 2. 得地：日支藏干有同我五行
    day_hidden = [s for s in HIDDEN_STEMS.get(pillars["day"].branch, []) if s is not None]
    if any(GAN_WUXING[s] == me_wx for s in day_hidden):
        support += 1

    # 3. 得生：其他天干有生我五行
    sheng_me_wx = next((wx for wx, t in WUXING_SHENG.items() if t == me_wx), None)
    for pos in ["year", "month", "hour"]:
        if GAN_WUXING[pillars[pos].stem] == sheng_me_wx:
            support += 1
            break

    # 4. 得助：其他天干有同我五行
    for pos in ["year", "month", "hour"]:
        if GAN_WUXING[pillars[pos].stem] == me_wx:
            support += 1
            break

    return "偏强" if support >= 2 else "偏弱"


# ============================================================
# 喜用神 v1（五行补益法）
# ============================================================

def calculate_yongshen_v1(day_stem: str, strength: str, five_elements: dict) -> dict:
    """
    喜用神 v1 — 五行补益法
    日主偏强 → 喜克泄耗（我克/克我/我生）
    日主偏弱 → 喜生扶（生我/同我）
    """
    me_wx = GAN_WUXING[day_stem]

    # 找出力量最强的五行（中文，排除日主本身）
    element_scores = [(fe["chinese"], float(fe["score"])) for fe in five_elements.values()]
    element_scores.sort(key=lambda x: -x[1])

    if strength == "偏弱":
        # 喜生我/同我
        favorable = [me_wx]  # 同我
        sheng_me = next((wx for wx, t in WUXING_SHENG.items() if t == me_wx), None)
        if sheng_me:
            favorable.append(sheng_me)  # 生我
        # 忌克我/我生/我克（过多的）
        avoid = [wx for wx, _ in element_scores[:2] if wx != me_wx and wx not in favorable]
    else:
        # 喜我克/克我/我生
        favorable = [WUXING_KE.get(me_wx, "")]  # 我克
        ke_me = next((wx for wx, t in WUXING_KE.items() if t == me_wx), None)
        if ke_me:
            favorable.append(ke_me)  # 克我
        wo_sheng = WUXING_SHENG.get(me_wx, "")
        if wo_sheng:
            favorable.append(wo_sheng)  # 我生
        # 忌同我/生我（过多的）
        avoid = [wx for wx, _ in element_scores[:2] if wx != me_wx and wx not in favorable]

    return {
        "favorable": [f for f in favorable if f],
        "avoid": [a for a in avoid if a],
        "method": "wuxing-support-v1",
    }


# ============================================================
# 刑冲合害
# ============================================================

def analyze_relationships(pillars: dict[str, GanZhi]) -> list[dict]:
    """四柱刑冲合害分析"""
    results = []
    branches = {pos: gz.branch for pos, gz in pillars.items()}
    stems = {pos: gz.stem for pos, gz in pillars.items()}
    positions = ["year", "month", "day", "hour"]
    pos_names = {"year": "年", "month": "月", "day": "日", "hour": "时"}

    # 六合
    liu_he = {
        ("子", "丑"): "子丑合土", ("丑", "子"): "子丑合土",
        ("寅", "亥"): "寅亥合木", ("亥", "寅"): "寅亥合木",
        ("卯", "戌"): "卯戌合火", ("戌", "卯"): "卯戌合火",
        ("辰", "酉"): "辰酉合金", ("酉", "辰"): "辰酉合金",
        ("巳", "申"): "巳申合水", ("申", "巳"): "巳申合水",
        ("午", "未"): "午未合土", ("未", "午"): "午未合土",
    }
    for i in range(4):
        for j in range(i + 1, 4):
            key = (branches[positions[i]], branches[positions[j]])
            if key in liu_he:
                results.append({
                    "type": "六合",
                    "positions": [f"{pos_names[positions[i]]}支{branches[positions[i]]}", f"{pos_names[positions[j]]}支{branches[positions[j]]}"],
                    "result": liu_he[key],
                })

    # 三合
    san_he = [
        ({"申", "子", "辰"}, "申子辰合水局"),
        ({"亥", "卯", "未"}, "亥卯未合木局"),
        ({"寅", "午", "戌"}, "寅午戌合火局"),
        ({"巳", "酉", "丑"}, "巳酉丑合金局"),
    ]
    branch_set = set(branches.values())
    for required, result_str in san_he:
        if len(required & branch_set) >= 3:
            pos_strs = [f"{pos_names[p]}支{branches[p]}" for p in positions if branches[p] in required]
            results.append({"type": "三合", "positions": pos_strs, "result": result_str})

    # 六冲
    liu_chong = {
        frozenset(["子", "午"]): "子午冲", frozenset(["丑", "未"]): "丑未冲",
        frozenset(["寅", "申"]): "寅申冲", frozenset(["卯", "酉"]): "卯酉冲",
        frozenset(["辰", "戌"]): "辰戌冲", frozenset(["巳", "亥"]): "巳亥冲",
    }
    for i in range(4):
        for j in range(i + 1, 4):
            key = frozenset([branches[positions[i]], branches[positions[j]]])
            if key in liu_chong:
                results.append({
                    "type": "六冲",
                    "positions": [f"{pos_names[positions[i]]}支{branches[positions[i]]}", f"{pos_names[positions[j]]}支{branches[positions[j]]}"],
                    "result": liu_chong[key],
                })
    return results


# ============================================================
# 大运
# ============================================================

def calculate_major_luck(birth_date: date, time_str: str, gender: str, year_gan: str, num_periods: int = 8) -> dict:
    """
    大运计算
    规则：阳年男/阴年女顺排，3天=1年起运
    v1 简化：起运年龄取 5 岁（精确计算需节气时刻，v1.1 完善）
    """
    is_yang_year = GAN_YINYANG[year_gan]
    is_male = (gender == "male")
    is_forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)

    # 起运年龄（简化：5岁，后续精确到节气）
    start_age = 5

    # 月柱大运干支
    month_gan_idx = 0
    month_zhi_idx = 0
    # 从出生日期的四柱取月柱
    gz = get_day_ganzhi(birth_date)
    month_gan_idx = TIAN_GAN.index(gz["month"].stem)
    month_zhi_idx = DI_ZHI.index(gz["month"].branch)

    periods = []
    for i in range(num_periods):
        step = i + 1
        if is_forward:
            gan_idx = (month_gan_idx + step) % 10
            zhi_idx = (month_zhi_idx + step) % 12
        else:
            gan_idx = (month_gan_idx - step) % 10
            zhi_idx = (month_zhi_idx - step) % 12

        age_s = start_age + i * 10
        age_e = age_s + 9
        year_s = birth_date.year + age_s
        year_e = birth_date.year + age_e

        periods.append({
            "age": f"{age_s}-{age_e}",
            "years": f"{year_s}-{year_e}",
            "stem": TIAN_GAN[gan_idx],
            "branch": DI_ZHI[zhi_idx],
            "full": TIAN_GAN[gan_idx] + DI_ZHI[zhi_idx],
        })

    return {
        "start_age": start_age,
        "direction": "顺排" if is_forward else "逆排",
        "periods": periods,
    }


# ============================================================
# 主入口
# ============================================================

def calculate_bazi(birth: BirthInfo) -> BaZiChart:
    """
    完整八字排盘（国际化版本）
    步骤：时区迁移 → 真太阳时修正 → 四柱 → 五行 → 十神 → 喜用神 → 大运
    """
    # ========== 0. 时区迁移 + 真太阳时修正 ==========
    solar_date = birth.date
    hh, mm = map(int, birth.time.split(":"))

    # 出生当地时间（钟表时间）
    # 如果夏令时，钟表时间已 +1h，需还原为标准时间用于计算
    dst_offset = 1.0 if birth.daylight_saving else 0.0

    # 出生当地时间
    birth_local = datetime.combine(solar_date, datetime.min.time()) + timedelta(hours=hh, minutes=mm)

    # 城市表: 城市名 → (纬度, 经度, 时区偏移)
    _CITY_COORDS = {
        # 中国大陆
        "北京": (39.9, 116.4, 8.0), "上海": (31.2, 121.5, 8.0), "广州": (23.1, 113.3, 8.0),
        "深圳": (22.5, 114.1, 8.0), "成都": (30.6, 104.1, 8.0), "杭州": (30.3, 120.2, 8.0),
        "武汉": (30.6, 114.3, 8.0), "西安": (34.3, 108.9, 8.0), "南京": (32.1, 118.8, 8.0),
        "重庆": (29.6, 106.5, 8.0), "天津": (39.1, 117.2, 8.0), "沈阳": (41.8, 123.4, 8.0),
        "乌鲁木齐": (43.8, 87.6, 8.0), "拉萨": (29.7, 91.1, 8.0), "哈尔滨": (45.8, 126.6, 8.0),
        "昆明": (25.0, 102.7, 8.0), "南宁": (22.8, 108.4, 8.0), "兰州": (36.0, 103.8, 8.0),
        "贵阳": (26.7, 106.6, 8.0), "福州": (26.1, 119.3, 8.0), "太原": (37.9, 112.5, 8.0),
        "石家庄": (38.0, 114.5, 8.0), "郑州": (34.8, 113.7, 8.0), "长沙": (28.2, 112.9, 8.0),
        "南昌": (28.7, 115.9, 8.0), "合肥": (31.8, 117.3, 8.0), "济南": (36.7, 117.0, 8.0),
        "呼和浩特": (40.8, 111.8, 8.0), "银川": (38.5, 106.3, 8.0), "西宁": (36.6, 101.8, 8.0),
        "海口": (20.0, 110.3, 8.0),
        # 港澳台
        "台北": (25.0, 121.5, 8.0), "香港": (22.3, 114.2, 8.0), "澳门": (22.2, 113.5, 8.0),
        # 东亚
        "东京": (35.7, 139.7, 9.0), "大阪": (34.7, 135.5, 9.0), "首尔": (37.6, 127.0, 9.0),
        # 东南亚
        "新加坡": (1.35, 103.8, 8.0), "吉隆坡": (3.1, 101.7, 8.0), "曼谷": (13.8, 100.5, 7.0),
        "雅加达": (-6.2, 106.8, 7.0), "马尼拉": (14.6, 121.0, 8.0), "胡志明市": (10.8, 106.7, 7.0),
        "河内": (21.0, 105.8, 7.0),
        # 南亚
        "新德里": (28.6, 77.2, 5.5), "孟买": (19.1, 72.9, 5.5),
        # 中东
        "迪拜": (25.2, 55.3, 4.0), "特拉维夫": (32.1, 34.8, 2.0),
        # 欧洲
        "伦敦": (51.5, -0.1, 0.0), "巴黎": (48.9, 2.3, 1.0), "柏林": (52.5, 13.4, 1.0),
        "汉堡": (53.6, 10.0, 1.0), "慕尼黑": (48.1, 11.6, 1.0), "法兰克福": (50.1, 8.7, 1.0),
        "阿姆斯特丹": (52.4, 4.9, 1.0), "布鲁塞尔": (50.8, 4.4, 1.0),
        "维也纳": (48.2, 16.4, 1.0), "苏黎世": (47.4, 8.5, 1.0), "布拉格": (50.1, 14.4, 1.0),
        "罗马": (41.9, 12.5, 1.0), "马德里": (40.4, -3.7, 1.0), "里斯本": (38.7, -9.1, 0.0),
        "斯德哥尔摩": (59.3, 18.1, 1.0), "奥斯陆": (59.9, 10.8, 1.0), "哥本哈根": (55.7, 12.6, 1.0),
        "赫尔辛基": (60.2, 24.9, 2.0), "华沙": (52.2, 21.0, 1.0), "布达佩斯": (47.5, 19.0, 1.0),
        "莫斯科": (55.8, 37.6, 3.0), "雅典": (38.0, 23.7, 2.0), "伊斯坦布尔": (41.0, 29.0, 3.0),
        "都柏林": (53.3, -6.3, 0.0),
        # 北美
        "纽约": (40.7, -74.0, -5.0), "洛杉矶": (34.1, -118.2, -8.0), "旧金山": (37.8, -122.4, -8.0),
        "芝加哥": (41.9, -87.6, -6.0), "休斯顿": (29.8, -95.4, -6.0), "西雅图": (47.6, -122.3, -8.0),
        "波士顿": (42.4, -71.1, -5.0), "华盛顿": (38.9, -77.0, -5.0), "迈阿密": (25.8, -80.2, -5.0),
        "多伦多": (43.7, -79.4, -5.0), "温哥华": (49.3, -123.1, -8.0), "蒙特利尔": (45.5, -73.6, -5.0),
        "墨西哥城": (19.4, -99.1, -6.0),
        # 南美
        "圣保罗": (-23.5, -46.6, -3.0), "里约热内卢": (-22.9, -43.2, -3.0),
        "布宜诺斯艾利斯": (-34.6, -58.4, -3.0), "圣地亚哥": (-33.4, -70.7, -4.0),
        # 大洋洲
        "悉尼": (-33.9, 151.2, 10.0), "墨尔本": (-37.8, 145.0, 10.0), "布里斯班": (-27.5, 153.0, 10.0),
        "奥克兰": (-36.8, 174.8, 12.0),
        # 非洲
        "开罗": (30.0, 31.2, 2.0), "约翰内斯堡": (-26.2, 28.0, 2.0), "内罗毕": (-1.3, 36.8, 3.0),
        "开普敦": (-33.9, 18.4, 2.0),
    }

    lon, tz = birth.lon, birth.tz_offset
    solar_correction = False
    city_coords = None

    if birth.city and birth.city in _CITY_COORDS:
        city_coords = _CITY_COORDS[birth.city]
        if lon == 0:
            lon = city_coords[1]
        tz = city_coords[2]  # 城市表时区优先
        if birth.lon == 0:
            birth.tz_offset = tz

    # 实际时区偏移（含夏令时）
    actual_tz = tz + dst_offset

    if lon != 0:
        # 有经度 → 真太阳时修正（先还原标准时间，再做经度+EoT修正）
        std_local = birth_local - timedelta(hours=dst_offset)  # 还原夏令时
        true_local = correct_true_solar_time(std_local, lon, tz)
        # 迁移到北京时间轴（UTC+8）用于排盘（不另加 DST，已在还原中去掉）
        china_dt = true_local + timedelta(hours=8.0 - tz)
        hh, mm = china_dt.hour, china_dt.minute
        solar_date = china_dt.date()
        solar_correction = True
    else:
        # 无经度 → 只做时区迁移（北京时间轴，含 DST 用实际时区）
        china_dt = birth_local + timedelta(hours=8.0 - actual_tz)
        hh, mm = china_dt.hour, china_dt.minute
        solar_date = china_dt.date()

    gz = get_day_ganzhi(solar_date, hh, mm)

    # 日主
    day_stem = gz["day"].stem
    day_master = {
        "stem": day_stem,
        "element": GAN_WUXING[day_stem],
        "polarity": "阳" if GAN_YINYANG[day_stem] else "阴",
    }

    # 五行
    five_elements = analyze_five_elements(gz)

    # 日主强弱
    strength = judge_day_master_strength(day_stem, gz["month"].branch, gz)

    # 喜用神
    yongshen = calculate_yongshen_v1(day_stem, strength, five_elements)

    # 刑冲合害
    relationships = analyze_relationships(gz)

    # 大运
    major_luck = calculate_major_luck(chart_date := solar_date, birth.time, birth.gender, gz["year"].stem)

    return BaZiChart(
        input={"date": str(birth.date), "time": birth.time, "gender": birth.gender,
               "city": birth.city, "tz_offset": tz, "solar_correction": solar_correction,
               "true_solar_time": f"{hh:02d}:{mm:02d} (北京时间)",
               "bazi_date_used": str(solar_date)},
        pillars=gz,
        day_master=day_master,
        five_elements=five_elements,
        day_master_strength=strength,
        yongshen=yongshen,
        relationships=relationships,
        major_luck=major_luck,
    )


from dataclasses import dataclass