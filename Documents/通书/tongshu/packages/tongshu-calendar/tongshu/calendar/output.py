"""
输出服务 — 每日 4 模块内容组装 + 个性化匹配
v1.0 模板版（无 LLM），德文内容
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone, timedelta
from typing import Optional

from .types import DayInfo, GanZhi, DailyOutput
from .constants import (
    TIAN_GAN, DI_ZHI, GAN_WUXING, ZHI_WUXING,
    WUXING_SHENG, WUXING_KE, GAN_YINYANG,
)
from .almanac import get_day_info
from .rules import get_daily_advice, DISCLAIMER_DE
from .lunar import get_lunar_month_name, get_lunar_day_name, get_lunar_year_name

CST = timezone(timedelta(hours=8))


# ============================================================
# 模块 1：今日卦象（简化版：日柱五行 → 卦象）
# ============================================================

HEXAGRAM_BY_ELEMENT = {
    "木": {"name_zh": "震为雷", "name_de": "Donner (Zhèn)", "brief_de": "Impuls und neue Bewegung. Ein guter Moment, um etwas zu beginnen.", "brief_zh": "雷动风行，宜开启新事物"},
    "火": {"name_zh": "离为火", "name_de": "Feuer (Lí)", "brief_de": "Klarheit und Erkenntnis. Nutze innere Helligkeit für deine Entscheidung.", "brief_zh": "光明照耀，宜明辨决断"},
    "土": {"name_zh": "坤为地", "name_de": "Erde (Kūn)", "brief_de": "Stabilität und Geduld. Trage Sorge, was du heute pflanzt.", "brief_zh": "厚德载物，宜稳扎稳打"},
    "金": {"name_zh": "乾为天", "name_de": "Himmel (Qián)", "brief_de": "Stärke und Klarheit. Der Himmel unterstützt entschlossenes Handeln.", "brief_zh": "天行健，宜积极进取"},
    "水": {"name_zh": "坎为水", "name_de": "Wasser (Kǎn)", "brief_de": "Fließen und Anpassung. Gehe den Weg der geringsten Reibung.", "brief_zh": "水润万物，宜顺势而为"},
}


# ============================================================
# 模块 2：今日节奏（时辰吉凶 → 早/午/晚）
# ============================================================

def _build_rhythm_module(day_info: DayInfo) -> dict:
    lucky_hours = [h for h in day_info.hour_lucky if h["lucky"]]
    unlucky_hours = [h for h in day_info.hour_lucky if not h["lucky"]]

    morning = [h for h in lucky_hours if int(h["hour"][:2]) < 12]
    afternoon = [h for h in lucky_hours if 12 <= int(h["hour"][:2]) < 18]
    evening = [h for h in lucky_hours if int(h["hour"][:2]) >= 18]

    def _fmt(hours):
        return ", ".join(h["hour"].replace(":00", "") for h in hours) if hours else "—"

    return {
        "id": "rhythm",
        "title_de": "Rhythmus des Tages",
        "title_zh": "今日节奏",
        "morning_de": f"Günstige Zeit am Morgen: {_fmt(morning)}",
        "afternoon_de": f"Günstige Zeit am Nachmittag: {_fmt(afternoon)}",
        "evening_de": f"Günstige Zeit am Abend: {_fmt(evening)}",
        "content_de": f"Günstige Zeitfenster: {_fmt(lucky_hours)}. Ruhige Zeitfenster: {_fmt(unlucky_hours)}.",
        "content_zh": f"吉时：{_fmt(lucky_hours)}。宜静时段：{_fmt(unlucky_hours)}。",
    }


# ============================================================
# 模块 3：顺时养生（节气 → 养生建议）
# ============================================================

SEASONAL_TIPS = {
    "立春": ("Beginn des Frühlings", "Leichtes, frisches Essen bevorzugen. Frühlingsgemüse hilft, die Leber zu entlasten.", "宜食春季新蔬，柔肝养气"),
    "雨水": ("Regenwasser", "Feuchtigkeit ausgleichen: Getreide und Ingwer stärken die Mitte.", "雨水时节，健脾祛湿"),
    "惊蛰": ("Erwachen der Insekten", "Bewegung an der frischen Luft. Frühes Aufstehen belebt den Kreislauf.", "惊蛰养生，早睡早起"),
    "春分": ("Frühlings-Tagundnachtgleiche", "Gleichgewicht von Yin und Yang: Maßhalten in Essen und Arbeit.", "春分平衡阴阳，劳逸结合"),
    "清明": ("Helle Klarheit", "Viel Grün und Spaziergänge in der Natur. Die Luft ist rein und belebend.", "清明踏青，舒展身心"),
    "谷雨": ("Getreideregen", "Feuchte Zeiten: leichtes Essen, viel Wasser, Kräutertee.", "谷雨祛湿，多饮温水"),
    "立夏": ("Beginn des Sommers", "Herz stärken: bittere Speisen, kühle Abende, frühe Erholung.", "立夏养心，苦味入心"),
    "小满": ("Kleine Fülle", "Nicht übermäßig essen. Fülle und Leere in Balance halten.", "小满忌满，饮食有度"),
    "芒种": ("Ährenreife", "Viel trinken, leichte Kost. Der Sommer beginnt Energie zu fordern.", "芒种补水，清淡饮食"),
    "夏至": ("Sommersonnenwende", "Kürzeste Nacht: früher Feierabend, kühle Räume, viel Ruhe.", "夏至养阴，静养为主"),
    "小暑": ("Kleine Hitze", "Wassermelone und Gurken kühlen. Mittagshitze meiden.", "小暑清热，瓜果消暑"),
    "大暑": ("Große Hitze", "Größte Hitze: ausreichend trinken, schwere Arbeit vermeiden.", "大暑防暑，多饮补水"),
    "立秋": ("Beginn des Herbstes", "Lunge pflegen: weißes Gemüse, mildes Essen, tiefe Atmung.", "立秋养肺，白色食物"),
    "处暑": ("Ende der Hitze", "Hitze lässt nach: langsam zu herbstlicher Ernährung wechseln.", "处暑降温，渐入秋养"),
    "白露": ("Weißer Tau", "Temperatur fällt: Kleidung anpassen, Wärme erhalten.", "白露添衣，防寒保暖"),
    "秋分": ("Herbst-Tagundnachtgleiche", "Balance von Yin und Yang: ausreichend Schlaf, ruhige Abende.", "秋分平衡，早睡早起"),
    "寒露": ("Kalter Tau", "Trockene Luft: Birne und Honig pflegen die Lunge.", "寒露润燥，梨蜜养肺"),
    "霜降": ("Reif", "Früh winterlich: warme Mahlzeiten, Wurzeln und Suppen.", "霜降进补，温养脾胃"),
    "立冬": ("Beginn des Winters", "Winter beginnt: wärmende Suppen, mehr Ruhe, Energie speichern.", "立冬进补，温养收藏"),
    "小雪": ("Kleiner Schnee", "Kälte kommt: warme Füße, Ingwertee, gemütliche Abende.", "小雪保暖，暖足养阳"),
    "大雪": ("Großer Schnee", "Tiefe Ruhe: entspannende Bäder, warme Kleidung, viel Schlaf.", "大雪进补，滋补强身"),
    "冬至": ("Wintersonnenwende", "Kürzester Tag: früh zur Ruhe kommen, Energie für das neue Jahr sammeln.", "冬至养藏，静待春回"),
    "小寒": ("Kleine Kälte", "Kälteste Zeit: warme Speisen, Ingwer und Datteln.", "小寒温补，姜枣暖身"),
    "大寒": ("Große Kälte", "Letzte Kälte: gut schlafen, warm essen, Kräfte sammeln.", "大寒进补，蓄势待发"),
}


def get_current_solar_term(solar_date: date) -> Optional[str]:
    """
    获取当天所处的节气区间（如 8月13日 → 立秋后）
    """
    from .solar_terms import get_all_jieqi
    dt = datetime.combine(solar_date, datetime.min.time(), tzinfo=CST)

    # 收集当年和上一年节气
    all_terms = []
    for y in (solar_date.year - 1, solar_date.year):
        for name, moment in get_all_jieqi(y).items():
            all_terms.append((name, moment))
    all_terms.sort(key=lambda x: x[1])

    current = None
    for name, moment in all_terms:
        if moment <= dt:
            current = name
        else:
            break
    return current


def _build_seasonal_module(day_info: DayInfo) -> dict:
    # 优先用当天节气，否则用当前节气区间
    term = day_info.solar_term or get_current_solar_term(day_info.solar_date)
    if term and term in SEASONAL_TIPS:
        name_de, tip_de, tip_zh = SEASONAL_TIPS[term]
        return {
            "id": "seasonal",
            "title_de": f"Jahreszeit: {name_de}",
            "title_zh": f"顺时养生·{term}",
            "content_de": tip_de,
            "content_zh": tip_zh,
        }
    return {
        "id": "seasonal",
        "title_de": "Jahreszeit: Achtsamkeit",
        "title_zh": "顺时养生",
        "content_de": "Achte auf einen ausgeglichenen Rhythmus von Essen, Bewegung und Ruhe.",
        "content_zh": "顺应天时，起居有常。",
    }


# ============================================================
# 模块 4：每日一句
# ============================================================

QUOTES = [
    ("老子", "Der Weg entsteht im Gehen.", "千里之行，始于足下"),
    ("老子", "Wer andere kennt, ist klug. Wer sich selbst kennt, ist erleuchtet.", "知人者智，自知者明"),
    ("老子", "Das Weiche besiegt das Harte.", "柔能克刚"),
    ("孔子", "Es ist eine Freude, Gelerntes anzuwenden.", "学而时习之，不亦说乎"),
    ("孔子", "Wer den Weg kennt, zweifelt nicht.", "知者不惑"),
    ("孔子", "Der Edle sucht den Fehler bei sich selbst.", "君子求诸己"),
    ("庄子", "Der Fisch vergisst das Wasser, der Mensch vergisst den Weg.", "鱼相忘于江湖"),
    ("庄子", "Freude ist, was im Augenblick lebt.", "得其所得，逍遥而乐"),
    ("墨子", "Handeln ist besser als zweifeln.", "行胜于言"),
    ("孟子", "Wer den Willen hat, findet den Weg.", "有志者事竟成"),
]


def _build_quote_module(day_info: DayInfo) -> dict:
    # 按日柱循环选句
    day_idx = TIAN_GAN.index(day_info.day_ganzhi.stem) * 1 + DI_ZHI.index(day_info.day_ganzhi.branch) * 3
    quote = QUOTES[day_idx % len(QUOTES)]
    return {
        "id": "quote",
        "title_de": "Weisheit des Tages",
        "title_zh": "每日一句",
        "content_de": f"{quote[1]} — {quote[0]}",
        "content_zh": f"「{quote[2]}」— {quote[0]}",
    }


# ============================================================
# 个性化匹配（喜用神 × 当日五行）
# ============================================================

def match_personal(day_ganzhi: GanZhi, yongshen: dict) -> dict:
    """
    个性化匹配：日主五行 × 当日五行
    result: harmonious / clashing / neutral
    """
    day_wx = GAN_WUXING[day_ganzhi.stem]
    favorable = yongshen.get("favorable", [])
    avoid = yongshen.get("avoid", [])

    if day_wx in favorable:
        match = "harmonious"
        advice_de = "Heute ist dein Element günstig. Nutze die Energie für einen klaren Fortschritt."
        advice_zh = "今日五行与你相合，顺势而为。"
    elif day_wx in avoid:
        match = "clashing"
        advice_de = "Heute ist ein ruhiger Tag für dich. Plane sorgfältig, vermeide impulsive Entscheidungen."
        advice_zh = "今日五行与你相克，宜守不宜攻。"
    else:
        match = "neutral"
        advice_de = "Heute ist ein ausgeglichener Tag. Folge deinem gewohnten Rhythmus."
        advice_zh = "今日五行平和，平常心度日。"

    return {
        "match": match,
        "match_zh": {"harmonious": "相生", "clashing": "相克", "neutral": "平和"}[match],
        "advice_de": advice_de,
        "advice_zh": advice_zh,
    }


# ============================================================
# 主入口
# ============================================================

def build_daily_output(solar_date: date, yongshen: Optional[dict] = None) -> DailyOutput:
    """
    组装每日输出
    """
    info = get_day_info(solar_date)
    advice = get_daily_advice(info)

    # 4 模块
    day_wx = GAN_WUXING[info.day_ganzhi.stem]
    hexagram = HEXAGRAM_BY_ELEMENT[day_wx]
    moduls = [
        {
            "id": "hexagram",
            "title_de": hexagram["name_de"],
            "title_zh": f"今日卦象·{hexagram['name_zh']}",
            "content_de": hexagram["brief_de"],
            "content_zh": hexagram["brief_zh"],
        },
        _build_rhythm_module(info),
        _build_seasonal_module(info),
        _build_quote_module(info),
    ]

    # 宜忌
    moduls.append({
        "id": "yiji",
        "title_de": "Heutige Empfehlungen",
        "title_zh": "今日宜忌",
        "yi_zh": advice["yi"],
        "ji_zh": advice["ji"],
        "content_de": f"Günstig: {', '.join(advice['yi']) if advice['yi'] else '—'}. Weniger günstig: {', '.join(advice['ji']) if advice['ji'] else '—'}.",
        "content_zh": f"宜：{'、'.join(advice['yi']) if advice['yi'] else '无'}；忌：{'、'.join(advice['ji']) if advice['ji'] else '无'}。",
    })

    # 个性化
    personal = None
    if yongshen:
        personal = match_personal(info.day_ganzhi, yongshen)

    lunar_month = get_lunar_month_name(info.lunar.month, info.lunar.is_leap)
    lunar_day = get_lunar_day_name(info.lunar.day)

    return DailyOutput(
        date=str(solar_date),
        lunar=f"{get_lunar_year_name(info.lunar.year)}年 {lunar_month}{lunar_day}",
        ganzhi={
            "year": info.year_ganzhi.full,
            "month": info.month_ganzhi.full,
            "day": info.day_ganzhi.full,
        },
        solar_term=info.solar_term,
        moduls=moduls,
        personal=personal,
        disclaimer=DISCLAIMER_DE,
    )


if __name__ == "__main__":
    from datetime import date

    out = build_daily_output(date(2026, 8, 13))
    print(f"日期: {out.date} ({out.lunar})")
    print(f"干支: {out.ganzhi}")
    print(f"节气: {out.solar_term}")
    for m in out.moduls:
        print(f"  [{m['id']}] {m['title_de']}: {m['content_de'][:60]}")
    print(f"免责: {out.disclaimer}")

    # 带个性化
    out2 = build_daily_output(date(2026, 8, 13), yongshen={"favorable": ["水", "金"], "avoid": ["火"]})
    print(f"\n个性化: {out2.personal}")