"""Ziwei (紫微) Engine.

Wraps the iztro npm package via subprocess to compute the
Zi Wei Dou Shu chart (本命 / 大限 / 流年 / 流月 / 流日 / 四化).

P1-C fix: produces BASELINE signals from the chart via signal
extraction (using main star + sihua), not a black box.
"""

from __future__ import annotations
import json
import logging
import os
import subprocess
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


class ZiweiEngineUnavailableError(RuntimeError):
    """Raised when iztro is not available and stub fallback is not explicitly enabled."""


# Main star -> USO type mapping (canonical, per signal_ontology.md §5.4)
MAIN_STAR_USO = {
    "ZIWEI": "SUPPORT",     # 紫微 - stability/leadership-as-nurturing
    "TIANFU": "SUPPORT",    # 天府
    "TAIYANG": "SUPPORT",   # 太阳 - public illumination
    "TIANLIANG": "SUPPORT", # 天梁 - elder care
    "WUQU": "RESOURCE",     # 武曲 - material decisiveness
    "TAIYIN": "REFLECTION", # 太阴 - inner receptivity
    "TIANTONG": "REFLECTION", # 天同
    "TIANJI": "REFLECTION", # 天机 - strategic thinking
    "TANLANG": "ACTION",   # 贪狼 - desire-driven initiative
    "LIANZHEN": "CONSTRAINT", # 廉贞 - restrictive intensity
    "POJUN": "CHANGE",      # 破军 - disruptive transformation
    "QISHA": "CONSTRAINT",  # 七杀
    "JUMEN": "CONSTRAINT",  # 巨门 - shadow
    "TIANXIANG": "SUPPORT",  # 天相 - 化气曰印，主官禄衣食，辅助稳定（《紫微斗数全书》14主星之一）
}




# iztro returns Chinese star names (紫微/贪狼/…). Map them to the canonical
# pinyin keys used by MAIN_STAR_USO. Source: docs/signal_ontology.md §5.4.
# 2026-08-27 修正: 天相(TIANXIANG)为《紫微斗数全书》14主星之一（南斗第五，化气曰印），
# 此前缺失导致命宫天相的盘紫微基线失效，已补入映射。
CHINESE_STAR_TO_KEY = {
    "紫微": "ZIWEI",
    "天府": "TIANFU",
    "太阳": "TAIYANG",
    "天梁": "TIANLIANG",
    "武曲": "WUQU",
    "太阴": "TAIYIN",
    "天同": "TIANTONG",
    "天机": "TIANJI",
    "贪狼": "TANLANG",
    "廉贞": "LIANZHEN",
    "破军": "POJUN",
    "七杀": "QISHA",
    "巨门": "JUMEN",
    "天相": "TIANXIANG",
}

# 十干四化表（中州派/王亭之主流版本，禄权科忌）。宫干自化/宫干飞化的依据。
GAN_SIHUA = {
    "甲": ("廉贞", "破军", "武曲", "太阳"),
    "乙": ("天机", "天梁", "紫微", "太阴"),
    "丙": ("天同", "天机", "文昌", "廉贞"),
    "丁": ("太阴", "天同", "天机", "巨门"),
    "戊": ("贪狼", "太阴", "右弼", "天机"),
    "己": ("武曲", "贪狼", "天梁", "文曲"),
    "庚": ("太阳", "武曲", "太阴", "天同"),
    "辛": ("巨门", "太阳", "文曲", "文昌"),
    "壬": ("天梁", "紫微", "左辅", "武曲"),
    "癸": ("破军", "巨门", "太阴", "贪狼"),
}
SIHUA_NAMES = ("禄", "权", "科", "忌")

# 紫微12宫固定顺序（三方四正的宫位索引依据）。
ZW_PALACES_ORDER = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", "迁移", "仆役", "官禄", "田宅", "福德", "父母"]


def time_index_from_hour(hour: int) -> int:
    """Convert solar hour (24h) to iztro timeIndex.

    iztro convention: 0 = 早子时 (00:00-01:00), 1 = 丑 … 8 = 申 … 11 = 亥,
    12 = 晚子时 (23:00-23:59). Mirrors the 时辰 table.
    """
    if hour == 23:
        return 12  # 晚子时
    if hour in (0, 24):
        return 0  # 早子时
    return ((hour + 1) // 2) % 12


@dataclass(frozen=True)
class ZiweiChart:
    soul_palace_main_star: str = ""           # 命宫第一主星(向后兼容)
    soul_palace_main_stars: list = field(default_factory=list)  # 命宫全部主星(V2.6: 双主星支持)
    soul_palace_sihua: list = field(default_factory=list)
    palace_data: dict = field(default_factory=dict)
    daily_luck_palace: str = ""
    source: str = "stub"

    def to_dict(self) -> dict:
        return {
            "soul_palace_main_star": self.soul_palace_main_star,
            "soul_palace_main_stars": list(self.soul_palace_main_stars),
            "soul_palace_sihua": list(self.soul_palace_sihua),
            "palace_data": self.palace_data,
            "daily_luck_palace": self.daily_luck_palace,
            "source": self.source,
        }


class ZiweiEngine:
    def __init__(self, node_modules_dir: Path | None = None):
        self._node = shutil.which("node")
        self._node_modules = node_modules_dir or Path("node_modules")
        self._iztro_available = (self._node_modules / "iztro").exists() and self._node is not None

    def compute(self, lunar_date, hour, gender="male"):
        """Compute Ziwei chart from lunar date.

        紫微斗数传统使用农历输入，与八字(阳历)不同。
        """
        if not self._iztro_available:
            if os.environ.get("TONGSHU_ALLOW_ZIWEI_STUB") == "1":
                logger.warning("ZiweiEngine: iztro unavailable, using stub fallback (TONGSHU_ALLOW_ZIWEI_STUB=1)")
                return self._stub(lunar_date, hour, gender)
            raise ZiweiEngineUnavailableError(
                "iztro is not installed; stub fallback disabled by default. "
                "Set TONGSHU_ALLOW_ZIWEI_STUB=1 to allow stub for development."
            )
        try:
            return self._compute_via_iztro(lunar_date, hour, gender)
        except Exception:
            if os.environ.get("TONGSHU_ALLOW_ZIWEI_STUB") == "1":
                logger.warning("ZiweiEngine: iztro failed, using stub_with_error fallback")
                return ZiweiChart(source="stub_with_error")
            raise ZiweiEngineUnavailableError(
                "iztro computation failed and stub fallback is disabled. "
                "Set TONGSHU_ALLOW_ZIWEI_STUB=1 to allow stub for development."
            )

    def extract_baseline_signal(self, chart: ZiweiChart, sig_index: int = 0):
        """P1-C: Extract a BASELINE Signal from ZiweiChart.

        Returns a Signal-shaped dict for SIR serialization, or None
        if the chart has no mapped main star (truly UNKNOWN, or star absent
        from spec §5.4 — per DECISION-009, unmapped stars yield no signal).
        """
        from ..reasoning.signal_engine import Signal
        if not chart.soul_palace_main_star:
            return None
        star = chart.soul_palace_main_star.upper()
        ontology = MAIN_STAR_USO.get(star)
        if ontology is None:
            return None
        # BASELINE reflects the natal structure: steady by definition.
        # Direction modulation from 四化 (SIHUA_EFFECT) belongs to the
        # CYCLE_CONTEXT layer, not BASELINE (DECISION-002). It is deferred
        # until ziwei cycle rules exist (T30x).
        return Signal(
            signal_id=f"SIG-ZW-BL-{sig_index:03d}",
            ontology_type=ontology,
            direction="STABLE",
            polarity="neutral",
            strength="moderate",
            layer="BASELINE",
            rule_refs=["ZIWEI-MAIN-STAR-MAP"],
            evidence_refs=["E-ZIWEI-001"],
        )

    def _compute_via_iztro(self, lunar_date, hour, gender):
        """使用农历日期调用 iztro (紫微斗数传统使用阴历)"""
        year, month, day = lunar_date
        # P1-FIX: lunar_python 以负月表示闰月（如 -10 = 闰十月）。
        # 取绝对值拼日期，并将 isLeapMonth 正确置 true；
        # 否则 '1984--10-15' 无效格式 → iztro 报错降级 (GOLDEN-016/API GOLDEN001)。
        is_leap = month < 0
        month = abs(month)
        iztro_gender = gender
        ti = time_index_from_hour(hour)
        # 注意: 紫微使用 byLunar 而非 bySolar
        script = f'''
        const iztro = require('iztro');
        const {{ byLunar }} = iztro.astro;
        // 紫微斗数传统使用农历输入
        const astrolabe = byLunar('{year}-{month}-{day}', {ti}, '{iztro_gender}', {str(is_leap).lower()});
        // 通过 earthlyBranch 查找命宫 (iztro API: soulPalace 属性为 undefined)
        const soulPalace = astrolabe.palaces.find(p => p.earthlyBranch === astrolabe.earthlyBranchOfSoulPalace);
        // DECISION-009 修正(2026-08-27, 倪海厦体系/《紫微斗数全书》"空宫借对,虚实相生"):
        // 命宫空宫时借对宫(迁移宫)主星论事, 不再留白。借星来源用 soulBorrowed 标志记录, 便于后续打折处理。
        let mainStars = soulPalace && soulPalace.majorStars && soulPalace.majorStars.length
            ? soulPalace.majorStars.map(s => s.name)
            : [];
        let soulBorrowed = mainStars.length === 0;
        if (soulBorrowed) {{
            const idx = astrolabe.palaces.indexOf(soulPalace);
            const opposite = astrolabe.palaces[(idx + 6) % 12];
            if (opposite && opposite.majorStars && opposite.majorStars.length) {{
                mainStars = opposite.majorStars.map(s => s.name);
            }}
        }}
        const mainName = mainStars.length > 0 ? mainStars[0] : '';
        const allMainStars = mainStars;  // V2.6: 命宫全部主星(双主星支持)
        const horoscope = astrolabe.horoscope();
        const result = {{
            soulMainStar: mainName,
            soulAllMainStars: allMainStars,
            soulBorrowed: soulBorrowed,
            soulEarthlyBranch: astrolabe.earthlyBranchOfSoulPalace,
            bodyEarthlyBranch: astrolabe.earthlyBranchOfBodyPalace,
            decadalMutagen: horoscope.decadal ? horoscope.decadal.mutagen : [],
            yearlyMutagen: horoscope.yearly ? horoscope.yearly.mutagen : [],
            monthlyMutagen: horoscope.monthly ? horoscope.monthly.mutagen : [],
            dailyMutagen: horoscope.daily ? horoscope.daily.mutagen : [],
        }};
        process.stdout.write(JSON.stringify(result));
        '''
        proc = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            encoding="utf-8",  # iztro outputs UTF-8; Windows default (GBK) would corrupt
            cwd=str(self._node_modules.parent) if self._node_modules else None,
            timeout=10,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"iztro failed: {proc.stderr}")
        data = json.loads(proc.stdout)
        main_key = CHINESE_STAR_TO_KEY.get(data.get("soulMainStar", ""), "")
        all_main_keys = [CHINESE_STAR_TO_KEY.get(s, "") for s in data.get("soulAllMainStars", []) if s in CHINESE_STAR_TO_KEY]
        return ZiweiChart(
            # Canonical pinyin key ("" when the soul star is not mapped in
            # spec §5.4 — e.g. 天相 — in which case extract_baseline_signal
            # correctly returns no signal per DECISION-009).
            soul_palace_main_star=main_key,
            soul_palace_main_stars=all_main_keys,
            soul_palace_sihua=[],
            palace_data={
                "raw_soul_main_star": data.get("soulMainStar", ""),
                "soul_borrowed": data.get("soulBorrowed", False),
                "soul_earthly_branch": data.get("soulEarthlyBranch", ""),
                "body_earthly_branch": data.get("bodyEarthlyBranch", ""),
                "decadal_mutagen": data.get("decadalMutagen", []),
                "yearly_mutagen": data.get("yearlyMutagen", []),
                "monthly_mutagen": data.get("monthlyMutagen", []),
                "daily_mutagen": data.get("dailyMutagen", []),
            },
            source="iztro",
        )

    def flow_years_mutagen(self, years, lunar_date, hour, gender):
        """获取多个指定年份的紫微流年四化（yearly mutagen，[禄,权,科,忌]）。

        解冻紫微（2026-08-27）：紫微要参与按年份断事，需按候选年份取流年四化。
        iztro astrolabe.horoscope('YYYY-6-15') 返回该流年四化（基于流年干支）。
        """
        year, month, day = lunar_date
        is_leap = month < 0
        month = abs(month)
        ti = time_index_from_hour(hour)
        iztro_gender = gender
        years_js = ", ".join(str(int(y)) for y in years)
        script = f'''
        const iztro = require('iztro');
        const {{ byLunar }} = iztro.astro;
        const astrolabe = byLunar('{year}-{month}-{day}', {ti}, '{iztro_gender}', {str(is_leap).lower()});
        const years = [{years_js}];
        const out = {{}};
        for (const y of years) {{
            try {{
                const h = astrolabe.horoscope(`${{y}}-6-15`);
                out[y] = (h.yearly && h.yearly.mutagen) ? h.yearly.mutagen : [];
            }} catch (e) {{
                out[y] = [];
            }}
        }}
        process.stdout.write(JSON.stringify(out));
        '''
        proc = subprocess.run(
            ["node", "-e", script],
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(self._node_modules.parent) if self._node_modules else None,
            timeout=20,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"iztro flow_years failed: {proc.stderr}")
        data = json.loads(proc.stdout)
        return {int(k): v for k, v in data.items()}

    def natal_palaces_main_stars(self, lunar_date, hour, gender):
        """返回本命12宫各宫主星（中文名），{宫名: [主星]}。

        用于判断流年四化落宫（某四化星在本命哪个宫 → 对应主题宫位）。
        """
        year, month, day = lunar_date
        is_leap = month < 0
        month = abs(month)
        ti = time_index_from_hour(hour)
        script = '''
        const { byLunar } = require('iztro').astro;
        const astrolabe = byLunar('%s-%s-%s', %d, '%s', %s);
        const out = {};
        astrolabe.palaces.forEach(p => {
            out[p.name] = (p.majorStars || []).concat(p.minorStars || []).map(s => s.name);
        });
        process.stdout.write(JSON.stringify(out));
        ''' % (year, month, day, ti, gender, str(is_leap).lower())
        proc = subprocess.run(
            ["node", "-e", script],
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(self._node_modules.parent) if self._node_modules else None,
            timeout=20,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"iztro natal_palaces failed: {proc.stderr}")
        return json.loads(proc.stdout)

    # ── 断事层: 生年四化落宫 + 主题评分 (V2.7) ──────────────────────

    def get_sihua_palaces(self, full_chart: dict, year_stem: str) -> dict:
        """生年四化落宫: 查化禄/权/科/忌星分别落入哪个宫位.

        Args:
            full_chart: full_chart()返回的完整命盘dict
            year_stem: 生年天干(甲/乙/丙/...)

        Returns:
            dict: {"hua_lu": 宫位名, "hua_quan": 宫位名, "hua_ke": 宫位名, "hua_ji": 宫位名}
                  星不在12宫主星中时返回None.
        """
        sihua_stars = GAN_SIHUA.get(year_stem, [])
        if len(sihua_stars) < 4:
            return {"hua_lu": None, "hua_quan": None, "hua_ke": None, "hua_ji": None}
        # 建星->宫位映射 (主星+辅星, 文昌/文曲是辅星但参与四化)
        star_to_palace = {}
        for pname, pdata in full_chart.get("palaces", {}).items():
            for star in pdata.get("major", []):
                star_to_palace[star] = pname
            for star in pdata.get("minor", []):
                if star not in star_to_palace:
                    star_to_palace[star] = pname
        return {
            "hua_lu": star_to_palace.get(sihua_stars[0]),
            "hua_quan": star_to_palace.get(sihua_stars[1]),
            "hua_ke": star_to_palace.get(sihua_stars[2]),
            "hua_ji": star_to_palace.get(sihua_stars[3]),
        }

    def get_sanfang_sizheng(self, full_chart: dict, palace_name: str) -> dict:
        """三方四正: 本宫 + 对宫 + 两个三合宫(V2.8).

        紫微斗数断事核心: 看一个宫位不能只看本宫, 必须看三方四正的星群组合.
        - 对宫: 地支+6(对冲)
        - 三合宫: 地支+4和+8

        Args:
            full_chart: full_chart()返回的完整命盘dict
            palace_name: 宫位名(如"夫妻")

        Returns:
            dict: {"ben": 本宫, "dui": 对宫, "sanhe1": 三合1, "sanhe2": 三合2,
                   "all_major": 四方主星合集, "all_sihua": 四方四化合集}
        """
        BRANCHES_LOCAL = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
        palaces = full_chart.get("palaces", {})
        ben_data = palaces.get(palace_name, {})
        ben_branch = ben_data.get("branch", "")
        if not ben_branch:
            return {"ben": palace_name, "dui": None, "sanhe1": None, "sanhe2": None,
                    "all_major": [], "all_sihua": [], "ben_data": ben_data}

        ben_idx = BRANCHES_LOCAL.index(ben_branch)
        dui_idx = (ben_idx + 6) % 12
        sanhe1_idx = (ben_idx + 4) % 12
        sanhe2_idx = (ben_idx + 8) % 12

        # 根据地支取宫位名
        branch_to_name = {}
        for pname, pdata in palaces.items():
            branch_to_name[pdata.get("branch", "")] = pname

        dui_name = branch_to_name.get(BRANCHES_LOCAL[dui_idx])
        sanhe1_name = branch_to_name.get(BRANCHES_LOCAL[sanhe1_idx])
        sanhe2_name = branch_to_name.get(BRANCHES_LOCAL[sanhe2_idx])

        # 收集四方主星
        all_major = []
        for pname in [palace_name, dui_name, sanhe1_name, sanhe2_name]:
            if pname and pname in palaces:
                all_major.extend(palaces[pname].get("major", []))

        return {
            "ben": palace_name,
            "dui": dui_name,
            "sanhe1": sanhe1_name,
            "sanhe2": sanhe2_name,
            "ben_branch": ben_branch,
            "dui_branch": BRANCHES_LOCAL[dui_idx],
            "sanhe1_branch": BRANCHES_LOCAL[sanhe1_idx],
            "sanhe2_branch": BRANCHES_LOCAL[sanhe2_idx],
            "all_major": all_major,
            "ben_data": ben_data,
            "dui_data": palaces.get(dui_name, {}),
            "sanhe1_data": palaces.get(sanhe1_name, {}),
            "sanhe2_data": palaces.get(sanhe2_name, {}),
        }

# 已删除架构违规项 (仲裁裁决 2026-09-02):
# - native_direction() -> 语义解释层，违反Calculation→Diagnosis边界
# - SIHUA_EFFECT -> INCREASE/DECREASE映射属于语义层
# - score_topic() -> 断事评分属于决策层
# 保留: GAN_SIHUA (四化事实), GAN_SIHUA_NAMES (四化名)

    def get_zigong_zihua(self, full_chart: dict, palace_name: str) -> list:
        """宫干自化: 查某宫是否自化禄/权/科/忌(V2.9).

        每个宫位的宫干引发一组四化, 若某化的对象星恰在本宫, 称为"自化X".
        自化力量弱于外来化("自己给自己的"), 但仍有影响.

        Args:
            full_chart: full_chart()返回的完整命盘dict
            palace_name: 宫位名

        Returns:
            list: ["自化禄", "自化权", "自化科", "自化忌"]中命中的项
        """
        palaces = full_chart.get("palaces", {})
        palace_data = palaces.get(palace_name, {})
        stem = palace_data.get("stem", "")
        if not stem:
            return []
        sihua_stars = GAN_SIHUA.get(stem, [])
        if len(sihua_stars) < 4:
            return []
        # 本宫主星+辅星
        palace_stars = set(palace_data.get("major", []))
        palace_stars.update(palace_data.get("minor", []))
        labels = ["自化禄", "自化权", "自化科", "自化忌"]
        result = []
        for i, star in enumerate(sihua_stars[:4]):
            if star in palace_stars:
                result.append(labels[i])
        return result

    def get_laiyin_gong(self, full_chart: dict, star_name: str,
                         sihua_type: str = "化忌") -> str | None:
        """来因宫: 查某星某化是由哪个宫的宫干引发的(V2.9).

        化忌的来因宫尤为重要: 找到来因宫, 才能找到问题的根.

        Args:
            full_chart: full_chart()返回的完整命盘dict
            star_name: 星名(如"太阳")
            sihua_type: 四化类型("化禄"/"化权"/"化科"/"化忌")

        Returns:
            str | None: 来因宫宫位名, 找不到返回None
        """
        type_idx = {"化禄": 0, "化权": 1, "化科": 2, "化忌": 3}.get(sihua_type, 3)
        palaces = full_chart.get("palaces", {})
        for pname, pdata in palaces.items():
            stem = pdata.get("stem", "")
            if not stem:
                continue
            sihua_stars = GAN_SIHUA.get(stem, [])
            if len(sihua_stars) > type_idx and sihua_stars[type_idx] == star_name:
                return pname
        return None

    def get_all_zihua(self, full_chart: dict) -> dict:
        """查所有宫位的自化情况(V2.9).

        Returns:
            dict: {宫位名: [自化禄/权/科/忌列表]}
        """
        palaces = full_chart.get("palaces", {})
        result = {}
        for pname in palaces:
            zihua = self.get_zigong_zihua(full_chart, pname)
            if zihua:
                result[pname] = zihua
        return result

    def flow_decadal_mutagen(self, years, lunar_date, hour, gender):
        """按候选年份取对应大限四化（horoscope(year).decadal.mutagen）。

        倪海厦"十年大运看三方四正"——大限四化是四重共振中高于流年的一层。
        返回 {year: [禄,权,科,忌]}。
        """
        year, month, day = lunar_date
        is_leap = month < 0
        month = abs(month)
        ti = time_index_from_hour(hour)
        years_json = json.dumps([str(y) for y in years])
        script = '''
        const { byLunar } = require('iztro').astro;
        const a = byLunar('%s-%s-%s', %d, '%s', %s);
        const out = {};
        %s.forEach(y => { const h = a.horoscope(y + '-6-15'); out[y] = (h.decadal && h.decadal.mutagen) || []; });
        process.stdout.write(JSON.stringify(out));
        ''' % (year, month, day, ti, gender, str(is_leap).lower(), years_json)
        proc = subprocess.run(
            ["node", "-e", script],
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(self._node_modules.parent) if self._node_modules else None,
            timeout=60,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"iztro flow_decadal failed: {proc.stderr}")
        data = json.loads(proc.stdout)
        # 2026-08-27 修复: JSON keys 为字符串('1985')，调用方用 int(year) 索引会 miss → None。
        # 转 int keys，否则大限四化全部失效（四重共振实验的大限层从未真正生效）。
        return {int(k): v for k, v in data.items()}

    def natal_palace_branches(self, lunar_date, hour, gender):
        """返回本命12宫各宫地支（太岁入宫技法的宫位地支），{宫名: 地支}。"""
        year, month, day = lunar_date
        is_leap = month < 0
        month = abs(month)
        ti = time_index_from_hour(hour)
        script = '''
        const { byLunar } = require('iztro').astro;
        const a = byLunar('%s-%s-%s', %d, '%s', %s);
        const out = {};
        a.palaces.forEach(p => { out[p.name] = p.earthlyBranch; });
        process.stdout.write(JSON.stringify(out));
        ''' % (year, month, day, ti, gender, str(is_leap).lower())
        proc = subprocess.run(
            ["node", "-e", script],
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(self._node_modules.parent) if self._node_modules else None,
            timeout=20,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"iztro palace_branches failed: {proc.stderr}")
        return json.loads(proc.stdout)

    def flow_month_mutagen(self, year, month, lunar_date, hour, gender):
        """指定阳历年某月的流月四化（[禄,权,科,忌]）。

        《紫微斗数精成》"看流月应以流年四化并配合大限之象来推断"——
        流月四化是紫微应期（具体到月份）的核心工具。iztro horoscope('Y-M-15')
        返回该阳历日所在农历月的流月四化（基于流月干支，斗君/流月命宫推算）。

        注：流月以农历月为界（初一），15日作为代表日避开发宫边界。
        """
        y, mo, d = lunar_date
        is_leap = mo < 0
        ti = time_index_from_hour(hour)
        script = """
        const { byLunar } = require('iztro').astro;
        const a = byLunar('%s-%s-%s', %d, '%s', %s);
        const h = a.horoscope('%s-%s-15');
        process.stdout.write(JSON.stringify((h.monthly && h.monthly.mutagen) || []));
        """ % (y, abs(mo), d, ti, gender, str(is_leap).lower(), year, month)
        proc = subprocess.run(
            ["node", "-e", script], capture_output=True, text=True, encoding="utf-8",
            cwd=str(self._node_modules.parent) if self._node_modules else None, timeout=20,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"iztro flow_month failed: {proc.stderr}")
        return json.loads(proc.stdout)

    def flow_day_mutagen(self, year, month, day, lunar_date, hour, gender):
        """指定阳历年某日的流日四化（[禄,权,科,忌]）。

        《紫微斗数精成》"看流日应以流月四化并配合流年之象来推断"——
        流日四化是紫微应期（精确到日）的工具。iztro horoscope('Y-M-D')
        返回该日的流日四化（基于流日干支）。
        """
        y, mo, d = lunar_date
        is_leap = mo < 0
        ti = time_index_from_hour(hour)
        script = """
        const { byLunar } = require('iztro').astro;
        const a = byLunar('%s-%s-%s', %d, '%s', %s);
        const h = a.horoscope('%s-%s-%s');
        process.stdout.write(JSON.stringify((h.daily && h.daily.mutagen) || []));
        """ % (y, abs(mo), d, ti, gender, str(is_leap).lower(), year, month, day)
        proc = subprocess.run(
            ["node", "-e", script], capture_output=True, text=True, encoding="utf-8",
            cwd=str(self._node_modules.parent) if self._node_modules else None, timeout=20,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"iztro flow_day failed: {proc.stderr}")
        return json.loads(proc.stdout)

    def full_chart(self, lunar_date, hour, gender):
        """返回紫微完整结构化盘（独立分析基础，2026-08-27 补齐）。

        倪海厦/《紫微斗数全书》体系核心数据：
        - 五行局（fiveElementsClass，纳音起局：水二木三金四土五火六）
        - 12宫：宫干(heavenlyStem)、宫支(earthlyBranch)、主星/辅星、
          宫干自化(selfMutaged)、大限范围(decadal.range)与大限干支
        - 命宫/身宫地支

        用于紫微独立格局识别、三方四正、宫干自化、12大限序列分析。
        """
        year, month, day = lunar_date
        is_leap = month < 0
        month = abs(month)
        ti = time_index_from_hour(hour)
        script = '''
        const { byLunar } = require('iztro').astro;
        const a = byLunar('%s-%s-%s', %d, '%s', %s);
        const out = {
            fiveElementsClass: a.fiveElementsClass || '',
            soulPalaceBranch: a.earthlyBranchOfSoulPalace || '',
            bodyPalaceBranch: a.earthlyBranchOfBodyPalace || '',
            palaces: {}
        };
        a.palaces.forEach(p => {
            out.palaces[p.name] = {
                stem: p.heavenlyStem || '',
                branch: p.earthlyBranch || '',
                major: (p.majorStars || []).map(s => s.name),
                minor: (p.minorStars || []).map(s => s.name),
                decadalRange: (p.decadal && p.decadal.range) || [],
                decadalStem: (p.decadal && p.decadal.heavenlyStem) || '',
                decadalBranch: (p.decadal && p.decadal.earthlyBranch) || ''
            };
        });
        process.stdout.write(JSON.stringify(out));
        ''' % (year, month, day, ti, gender, str(is_leap).lower())
        proc = subprocess.run(
            ["node", "-e", script],
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(self._node_modules.parent) if self._node_modules else None,
            timeout=20,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"iztro full_chart failed: {proc.stderr}")
        return json.loads(proc.stdout)

    def sanfang_sizheng(self, palace_name):
        """紫微三方四正（倪海厦"十年大运看三方四正"）。

        本宫 + 三合宫(+4,+8) + 对宫(+6)，不可单宫论断。
        """
        try:
            i = ZW_PALACES_ORDER.index(palace_name)
        except ValueError:
            return [palace_name]
        return [ZW_PALACES_ORDER[i], ZW_PALACES_ORDER[(i + 4) % 12],
                ZW_PALACES_ORDER[(i + 8) % 12], ZW_PALACES_ORDER[(i + 6) % 12]]

    def palace_self_mutagen(self, full_chart, palace_name):
        """计算某宫的宫干自化（飞星派核心技法）。

        宫干自化 = 该宫宫干四化落回该宫主星/辅星 → 该宫自化该四化。
        返回 [(星名, 四化名), ...]，四化名 ∈ {禄,权,科,忌}。
        倪海厦体系支持宫干自化；iztro 的 selfMutaged() 返回布尔(全部true)不可靠，
        故按天干四化表正统计算。
        """
        p = (full_chart or {}).get("palaces", {}).get(palace_name)
        if not p:
            return []
        sihua = GAN_SIHUA.get(p.get("stem", ""))
        if not sihua:
            return []
        stars = set(p.get("major", [])) | set(p.get("minor", []))
        result = []
        for i, s in enumerate(sihua):
            if s in stars:
                result.append((s, SIHUA_NAMES[i]))
        return result

    def corrected_hour_index(self, hour, longitude, solar_date):
        """真太阳时校正后的时辰 index（王亭之：应以出生地真太阳时排盘）。

        真太阳时 = 北京时间 + 经度差修正 + 均时差。
        经度差: (longitude - 120) × 4 分钟；均时差由 NASA/Meeus 级数计算。
        hour: 出生钟表小时(北京时间, 0-23)。longitude: 出生地东经(度)。
        solar_date: 出生阳历日期 (y,m,d)，用于均时差。

        返回校正后的时辰 index（time_index_from_hour 约定）。
        未提供 longitude 时返回原始时辰 index（默认北京 120°E）。
        """
        if longitude is None:
            return time_index_from_hour(hour)
        try:
            from datetime import datetime
            from tongshu.engines.time.solar_time import calculate_true_solar_time
            bj = datetime(solar_date[0], solar_date[1], solar_date[2], hour, 0)
            r = calculate_true_solar_time(bj, longitude)
            tst = datetime.fromisoformat(r["true_solar_time"])
            return time_index_from_hour(tst.hour)
        except Exception as e:  # 校正失败回退原始时辰
            logger.warning("ziwei corrected_hour_index 失败回退: %s", e)
            return time_index_from_hour(hour)

    def decadal_soul_effect(self, full_chart, decadal_mutagen):
        """大限四化对命宫格局的效应（文献：大限命宫化忌=此十年需稳守）。

        大限四化决定十年运势走向（影响力次于生年、强于流年）。
        大限四化落命宫三方四正 → 该大限命宫吉凶：
        - 化忌入命宫三方四正 → caution（此十年需稳守）
        - 化禄/权/科入命宫三方四正 → opportunity（此十年宜拓展）
        """
        if not full_chart:
            return {"direction": "neutral", "note": ""}
        target = set(self.sanfang_sizheng("命宫"))
        palace_of_star = {}
        for n, p in full_chart.get("palaces", {}).items():
            for s in p.get("major", []):
                palace_of_star[s] = n
        if decadal_mutagen and len(decadal_mutagen) >= 4:
            if palace_of_star.get(decadal_mutagen[3]) in target:
                return {"direction": "caution", "note": "大限化忌入命宫三方四正，此十年宜稳守，避免激进决策"}
            for s in decadal_mutagen[:3]:
                if palace_of_star.get(s) in target:
                    return {"direction": "opportunity", "note": "大限化禄/权/科入命宫三方四正，此十年宜主动拓展"}
        return {"direction": "neutral", "note": "大限四化未直接触及命宫三方四正"}

    def _stub(self, lunar_date, hour, gender):
        """Stub: derive main star deterministically from day_master.

        Real implementation calls iztro with lunar date.
        This stub keeps the architecture working for demo and unit tests.
        """
        from ..engines.bazi_engine import BaziEngine
        from ..reasoning.rule_db import DAY_MASTER_ELEMENT
        # Stub 需要阳历来做八字计算
        # 将农历日期转换为阳历
        try:
            from lunar_python import Solar
            solar = Solar.fromYmd(lunar_date[0], lunar_date[1], lunar_date[2])
            lunar = solar.getLunar()
            solar_back = lunar.getSolar()
            bazi = BaziEngine().compute(
                (solar_back.getYear(), solar_back.getMonth(), solar_back.getDay(), hour),
                gender=gender
            )
        except Exception:
            # Fallback: use fixed date
            bazi = BaziEngine().compute((1990, 5, 15, hour), gender=gender)

        # Map day_master -> representative main star
        star_map = {
            "JIA": "ZIWEI",    # 木 - 紫微 (leadership) → SUPPORT
            "YI":  "TIANFU",   # 木 - 天府 (stability) → SUPPORT, enables ALIGNED with Bazi SUPPORT signals
            "BING": "TAIYANG", # 火 - 太阳 (light) → SUPPORT
            "DING": "TIANJI",  # 火 - 天机 (intellect) → REFLECTION
            "WU":  "TIANFU",   # 土 - 天府 (stability) → SUPPORT
            "JI":  "TIANLIANG", # 土 - 天梁 (elder care) → SUPPORT
            "GENG": "WUQU",    # 金 - 武曲 (decision) → RESOURCE
            "XIN": "POJUN",    # 金 - 破军 (change) → CHANGE
            "REN": "TAIYIN",   # 水 - 太阴 (reflection) → REFLECTION
            "GUI": "JUMEN",    # 水 - 巨门 (depth) → CONSTRAINT
        }
        main_star = star_map.get(bazi.day_master, "")
        # Stub sihua: occasional 化科 if day element is fire (hypothetical)
        sihua = []
        element = DAY_MASTER_ELEMENT.get(bazi.day_master, "")
        if element == "FIRE":
            sihua.append("HUA_KE")
        return ZiweiChart(
            soul_palace_main_star=main_star,
            soul_palace_sihua=sihua,
            source="stub",
        )
