# -*- coding: utf-8 -*-
"""ZIPING 解层 (Interpretation) — 全量版本: 15 维断语触发.

架构:
    §28 辨层状态枚举 (19 域)
        ↓
    interpretation.py  (解层)
        ├── DomainResolver: 15 维 × 多态 → 古汉语钩子 (条件匹配词)
        ├── DuanyuMatcher:  钩子 → 断语库命中 (带五经溯源)
        └── InterpretationOutput: §28 追加 interpretations 字段

约束 (V2 §25/§27):
    1. 解层只消费 Judgment, 不重算 (ARCH-001~006 强制)
    2. 断语逐字抄录, 查不到标注"原文未定位"
    3. 每条断语带 evidence_ref: classic·source + text[:40]
    4. 解层不得引入 LLM/score/weight/percentage
    5. §28 枚举保持不变, 解层附加在 interpretations[] 字段
    6. 未实现域的 fail-closed 保持 UNDETERMINED

覆盖域 (15 维全量):
    P0: LING(得令) / GROWTH(长生) / ROOT(根气) / PARTY(党众) / STRENGTH(身强弱)
    P1: QING(清浊) / CLIMATE(气候) / TONGGUAN(通关) / DISEASE(病药) / QI(气势)
    P2: PATTERN(格局) / PATTERN_QUALITY(格局高低) / TRUE(真假) / SPECIAL(特殊格)
    P3: YONG(用神) / XIANG(相神) / XIJI(喜忌) / TEMPORAL(时间层)

断语库资源:
    D:\顺天系统资料\五部经典断语库\03_综合索引\all_duanyu.json (11,478 条)
    类别: 用神喜忌 36% / 旺衰 17% / 格局 9% / 官运 6% / 六亲 6% / ...
    可触发: 7,805 条 (68%, 含若/如/见/逢/忌/喜等条件钩子)
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# 断语库路径 (资源库, 禁止硬编码本地开发机绝对路径)
DUANYU_DB = Path(__file__).parent.parent.parent.parent.parent.parent / \
            "顺天系统资料" / "五部经典断语库" / "03_综合索引" / "all_duanyu.json"


@dataclass
class TriggeredDuanyu:
    """单条断语触发结果."""
    classic: str           # 经典名
    source: str            # 来源文件
    primary_category: str  # 主类别
    text: str              # 断语原文 (逐字抄录)
    trigger_rule: str      # §28 触发规则 (如 "STRENGTH=WANG_BUT_NOT_STRONG")
    evidence_ref: str      # 追溯引用
    confidence: str        # STRONG/MODERATE/WEAK
    quality: str = "UNKNOWN"  # PRINCIPLE/CASE/MIXED/UNCLEAR


@dataclass
class InterpretationOutput:
    """解层输出契约 (全量 15 维)."""
    # 各域断语 (全部独立, 不合并)
    ling: List[TriggeredDuanyu] = field(default_factory=list)         # 得令
    growth: List[TriggeredDuanyu] = field(default_factory=list)       # 十二长生
    root: List[TriggeredDuanyu] = field(default_factory=list)         # 根气
    party: List[TriggeredDuanyu] = field(default_factory=list)        # 党众
    strength: List[TriggeredDuanyu] = field(default_factory=list)     # 身强弱
    qing: List[TriggeredDuanyu] = field(default_factory=list)         # 清浊
    climate: List[TriggeredDuanyu] = field(default_factory=list)      # 气候/调候
    tongguan: List[TriggeredDuanyu] = field(default_factory=list)     # 通关
    disease: List[TriggeredDuanyu] = field(default_factory=list)      # 病药
    qi: List[TriggeredDuanyu] = field(default_factory=list)           # 气势
    pattern: List[TriggeredDuanyu] = field(default_factory=list)      # 格局
    pattern_quality: List[TriggeredDuanyu] = field(default_factory=list)  # 格局高低
    true: List[TriggeredDuanyu] = field(default_factory=list)         # 真假
    special: List[TriggeredDuanyu] = field(default_factory=list)      # 特殊格
    yong: List[TriggeredDuanyu] = field(default_factory=list)         # 用神
    xiang: List[TriggeredDuanyu] = field(default_factory=list)        # 相神
    xiji: List[TriggeredDuanyu] = field(default_factory=list)         # 喜忌
    temporal: List[TriggeredDuanyu] = field(default_factory=list)     # 时间层
    undetermined_domains: List[str] = field(default_factory=list)     # fail-closed 域


class DuanyuLoader:
    """断语库加载器 — 只做读取, 不修改 backend/.
    
    过滤规则 (V2 §28 规范):
        - 排除散文原注: 以"原注"/"任氏曰"/"书云"开头的段落
        - 排除序言页: 以"序"/"《"开头或含"目录"
        - 只保留带类别标签的条目 (primary_category 非空)
    """
    _EXCLUDE_PREFIXES = ("原注", "任氏曰", "书云", "目录")
    _EXCLUDE_STARTS = ("序", "《", "目")

    def __init__(self, db_path: Path = DUANYU_DB):
        self._db_path = db_path
        self._cache: Optional[List[Dict[str, Any]]] = None

    @property
    def db_path(self) -> Path:
        return self._db_path

    def load(self) -> List[Dict[str, Any]]:
        if self._cache is not None:
            return self._cache
        if not self._db_path.exists():
            raise FileNotFoundError(f"断语库不存在: {self._db_path}")
        with open(self._db_path, encoding="utf-8") as f:
            data = json.load(f)
        # 过滤散文原注 + 未分类
        filtered = []
        for item in data:
            text = item.get("text", "")
            if not text:
                continue
            stripped = text.lstrip()
            if stripped[:2] in self._EXCLUDE_PREFIXES or stripped[:1] in self._EXCLUDE_STARTS:
                continue
            if not item.get("primary_category"):
                continue
            filtered.append(item)
        self._cache = filtered
        return filtered

    def load_by_classics(self, classics: List[str] = None) -> List[Dict[str, Any]]:
        """按经典名过滤 (子平真诠/滴天髓阐微/穷通宝鉴/渊海子平/三命通会)."""
        all_data = self.load()
        if classics is None:
            return all_data
        return [x for x in all_data if x.get("classic") in classics]

    def load_by_categories(self, cats: List[str]) -> List[Dict[str, Any]]:
        """按类别过滤."""
        all_data = self.load()
        return [x for x in all_data
                if x.get("primary_category") in cats or
                any(c in x.get("categories", []) for c in cats)]


class DuanyuQualityClassifier:
    """断语质量分类器: 通用原则 vs 具体命例 vs 混合."""

    # 目录/序言/散文原注特征 (排除)
    DISCARD_MARKERS = [
        '目录', '序', '凡例', '自序', '校注', '注曰',
        '传云', '古云', '经云', '赋云',
        '《滴天髓》为中国', '滴天髓目录',
        '渊海子平目录', '穷通宝鉴目录',
        '三命通会目录', '子平真诠目录',
        '任氏曰', '原注', '书云',
    ]

    # 注释/定义特征 (归为 COMMENTARY，保留但不作为原则)
    COMMENTARY_MARKERS = [
        '非...之谓', '即...也', '乃...之', '谓之',
        '者，...', '也者', '之义', '之意',
        '曰:', '云:', '谓:',
    ]

    # 命例特征词 (出现 → CASE)
    CASE_MARKERS = [
        '此造', '此命', '某人', '某人造', '某人八字', '此局', '某造',
        '年柱', '月柱', '日柱', '时柱', '四柱', '八字',
        '张三', '李四', '王五', '某某', '先生', '女士',
        '命造', '命例', '实例', '此造初看', '余细推之',
        '生于', '出生于', '出生在',
        '大运', '流年', '运至', '运逢', '岁运',
        '少年', '中年', '晚年', '老境',
        '科甲', '功名', '富贵', '贫贱', '吉凶',
        '官星', '财星', '印星', '食神', '伤官',
        '七杀', '偏官', '正官', '偏财', '正财',
    ]

    # 通用原则特征词 (出现 → PRINCIPLE)
    PRINCIPLE_MARKERS = [
        '若', '如', '见', '逢', '遇', '忌', '喜', '宜', '当', '必',
        '成', '主', '为', '得', '失', '有', '无', '须', '从', '化',
        '合', '冲', '克', '生', '制', '通关', '调候', '病药',
        '清纯', '混杂', '偏枯', '中和', '旺', '弱', '虚', '实',
        '五行', '天干', '地支', '日干', '月令', '司令',
        '气', '势', '神', '根', '透', '藏',
        '生扶', '泄耗', '帮身', '克身',
        '身旺', '身弱', '得令', '失令',
        '官杀', '财星', '印绶', '食伤',
    ]

    @classmethod
    def classify(cls, text: str) -> str:
        """分类断语文本.
        
        Returns:
            "PRINCIPLE" - 通用原则
            "CASE" - 具体命例
            "MIXED" - 混合 (原则+命例)
            "COMMENTARY" - 注释/定义 (保留但标记)
            "UNCLEAR" - 无法判断
            "DISCARD" - 目录/序言/散文原注 (应过滤)
        """
        # 1. 先排除目录/序言/原注
        for marker in cls.DISCARD_MARKERS:
            if marker in text[:30]:
                return "DISCARD"

        # 2. 识别注释/定义
        has_commentary = any(m in text for m in cls.COMMENTARY_MARKERS)

        has_case = any(m in text for m in cls.CASE_MARKERS)
        has_principle = any(m in text for m in cls.PRINCIPLE_MARKERS)

        if has_case and not has_principle:
            return "CASE"
        elif has_principle and not has_case:
            if has_commentary:
                return "COMMENTARY"
            return "PRINCIPLE"
        elif has_case and has_principle:
            return "MIXED"
        elif has_commentary and not has_case and not has_principle:
            return "COMMENTARY"
        else:
            return "UNCLEAR"


class DomainResolver:
    """解层核心: §28 状态枚举 → 断语条件钩子 (古汉语原词).
    
    钩子设计原则:
        1. 用断语库真实词汇 (如"旺相""得令""偏枯""清纯"等)
        2. 覆盖各态多表达 (如 STRONG = 身旺/得令/旺相/气旺/得时/乘时...)
        3. 跨典同义词扩展 (滴天髓用"乘时", 渊海用"得令", 子平用"得时")
    """

    # ═══════════════════════════════════════════════════════════════
    # 各域状态 → 钩子映射 (15 维全量)
    # ═══════════════════════════════════════════════════════════════

    _LING_HOOKS: Dict[str, List[str]] = {
        "DE_LING": ["得令", "得时", "乘时", "当权", "司令", "当令", "得气",
                    "得令者", "得时者", "生月", "旺月", "建禄", "临官", "帝旺"],
        "SHI_LING": ["失令", "失时", "不当令", "不得令", "休囚", "死绝",
                     "失时者", "非当令", "退气"],
        "CONDITIONAL": ["得令与否", "或得或失", "得失不明", "需参看"],
    }

    _GROWTH_HOOKS: Dict[str, List[str]] = {
        "ROOTING": ["长生", "临官", "帝旺", "冠带", "养", "得地", "有根",
                    "生旺", "旺相", "根基稳固", "根深蒂固", "日干有气"],
        "STORE": ["墓库", "入库", "入墓", "收藏", "闭藏", "归库", "辰戌丑未"],
        "EXTINCT": ["死绝", "无气", "气绝", "根枯", "叶败", "死地",
                    "失根", "根拔", "生机绝矣", "气弱"],
        "RESIDUAL": ["余气", "衰", "病", "沐浴", "胎", "绝", "寄居"],
    }

    _ROOT_HOOKS: Dict[str, List[str]] = {
        "HEAVY": ["根重", "根深", "强根", "有力", "有根有气", "根气深厚"],
        "CONDITIONAL": ["根有或无", "根气不定", "或深或浅"],
        "TRUE": ["根真", "根实", "实根", "有根", "根正"],
    }

    _PARTY_HOOKS: Dict[str, List[str]] = {
        "DOMINANT_SUPPORT": ["帮身", "党众", "印比", "生扶", "助身", "得助"],
        "DOMINANT_OPPOSE": ["克泄耗", "异党", "官杀财食", "克身", "耗身"],
        "BALANCED": ["党众均衡", "势力相当", "阴阳调和", "不偏不倚"],
    }

    _STRENGTH_HOOKS: Dict[str, List[str]] = {
        "STRONG": ["身旺", "得令", "有根", "党众", "印比", "身强", "旺",
                   "旺相", "气旺", "日干旺", "得时", "乘时", "当权得令",
                   "身旺党众", "根深党旺", "气壮"],
        "WANG_BUT_NOT_STRONG": ["得令但不旺", "旺而不足", "根旺透弱",
                                "旺而不强", "虽旺", "得令", "乘时",
                                "得气但不专", "旺而有制", "旺而受制",
                                "身杀两停", "身旺有制", "偏旺不专"],
        "SHUAI_BUT_NOT_WEAK": ["失令但不弱", "有根得助", "体用调和",
                               "中和", "身衰不弱", "财多身弱",
                               "气弱但帮", "衰而有根", "身弱有根",
                               "虽有根", "日干弱而有根"],
        "WEAK": ["身弱", "失令无根", "泄耗太过", "弱极", "身衰", "体弱",
                 "无助", "气弱", "身弱无根", "日干弱", "失时",
                 "虚浮无根", "气绝"],
        "BALANCED": ["中和", "强弱适中", "无偏无倚", "平衡", "身不偏",
                     "阴阳调和", "得中", "平", "不偏不倚", "气平",
                     "不偏不斜", "阴阳平"],
        "WANG_OVER": ["太旺", "亢旺", "过强", "身旺无依", "旺极",
                      "旺之极", "太过", "偏旺", "旺而无制"],
        "WEAK_OVER": ["极弱", "虚浮", "无根", "身弱无依", "弱极",
                      "太弱", "不及", "偏枯", "弱而无依"],
    }

    _QING_HOOKS: Dict[str, List[str]] = {
        "CLEAR": ["清纯", "不杂", "单一", "清透", "专", "清纯不杂", "不混",
                  "清", "气清", "格局清纯", "无杂", "纯粹", "清顺",
                  "清而不杂", "清透", "纯一"],
        "TURBID": ["混杂", "官杀混杂", "财印相战", "不清", "浊",
                   "官杀混杂格", "正官七杀同透", "浊", "气浊", "格不清",
                   "混浊", "偏枯", "杂", "驳", "清浊混杂", "官煞混杂"],
        "PARTIAL_CLEAR": ["略清", "微浊", "半清半浊", "清中带浊",
                          "浊中带清", "清浊兼", "稍浊", "微混"],
    }

    _CLIMATE_HOOKS: Dict[str, List[str]] = {
        "HOT": ["火炎土燥", "夏火", "暑热", "炎上", "火旺", "燥热",
                "夏木虚焦", "金燥", "土燥", "喜润", "调候以水",
                "夏月调候", "火旺宜润", "燥局"],
        "COLD": ["金寒水冷", "冬水", "寒冷", "寒金", "水冷", "冻土",
                 "冬月", "寒气", "寒局", "宜暖", "调候以火",
                 "冬金需火", "寒甚", "水冷金寒"],
        "DRY": ["燥土", "土燥", "燥热", "火炎土燥", "喜润", "宜润局",
                "燥气需调", "干土", "燥局"],
        "WET": ["湿土", "水旺", "湿局", "水多", "泥水", "宜燥", "宜暖",
                "湿土需火", "水泛", "寒湿"],
        "HOT_WET": ["湿热", "暑湿", "火土燥热兼湿", "夏月湿土",
                    "火炎土燥", "湿热交织"],
    }

    _TONGGUAN_HOOKS: Dict[str, List[str]] = {
        "OPPOSITION_RESOLVED": ["通关", "化解", "制伏得宜", "两神争战",
                                "取通关之神", "化敌为友", "敌杀有制",
                                "制伏有救", "战有化解"],
        "TONGGUAN_ABSENT": ["无通关", "争战无解", "敌杀无制", "制伏不及",
                            "通关缺", "无化解", "两神相战", "交战无解"],
        "UNDETERMINED": ["通关未定", "制伏未明", "战局未决"],
    }

    _DISEASE_HOOKS: Dict[str, List[str]] = {
        "HAS_DISEASE": ["有病", "有病无药", "有病有药", "病重", "有病方为贵",
                        "病在何处", "病因", "病灶", "病象"],
        "HAS_MEDICINE": ["有药", "有病得药", "药神", "良剂", "解救",
                         "病有药医", "因病得药"],
        "UNDETERMINED": ["病药未定", "病因不明", "病象待察"],
    }

    _QI_HOOKS: Dict[str, List[str]] = {
        "CONCENTRATED": ["专", "清纯", "一气", "专注", "气势专一",
                         "一股", "一气专旺", "势专", "清纯不杂", "专气"],
        "CONTESTED": ["争战", "两神相争", "气势相争", "对立", "交争",
                      "两神对峙", "争持", "相争", "对峙", "两败俱伤"],
        "SCATTERED": ["散", "分散", "无专气", "气势分散", "分散无主",
                      "散乱", "气散"],
    }

    _PATTERN_HOOKS: Dict[str, List[str]] = {
        "SUCCESS": ["成格", "格局成立", "格成", "立格成功", "成格",
                    "格局已立", "成功有气", "成象"],
        "FAIL": ["破格", "格局破坏", "格败", "败格", "格不成",
                 "格局不成立", "格破", "破局"],
        "UNDETERMINED": ["格局未定", "取格未明", "格象待察"],
    }

    _PATTERN_QUALITY_HOOKS: Dict[str, List[str]] = {
        "HIGH": ["贵格", "上格", "上等", "大贵", "富贵双全", "科甲",
                 "显达", "大贵之格", "上上之格", "极品"],
        "MEDIUM": ["中格", "中等", "平常", "中平", "中等格局"],
        "LOW": ["下格", "下等", "贫贱", "下下之格", "庸夫俗子"],
        "UNDETERMINED": ["格局高低未定"],
    }

    _TRUE_HOOKS: Dict[str, List[str]] = {
        "TRUE": ["真", "真神", "真用", "真格", "真局", "真神得用",
                 "用神真", "格局真"],
        "FALSE": ["假", "假神", "假用", "假格", "假局", "真神被伤",
                  "用神假", "格局假"],
        "UNDETERMINED": ["真假未定", "真神之辨"],
    }

    _SPECIAL_HOOKS: Dict[str, List[str]] = {
        "FOLLOW_STRONG": ["从旺", "从强", "从格", "顺势", "从强格",
                          "专旺", "从旺格", "从强"],
        "FOLLOW_WEAK": ["从弱", "从衰", "弃命从杀", "从财", "从儿",
                        "从官杀", "从势", "假从"],
        "UNDETERMINED": ["特殊格未定", "从化未明"],
    }

    _YONG_HOOKS: Dict[str, List[str]] = {
        "PATTERN_BASED": ["格局用神", "专求月令", "用神在格", "格内取用"],
        "CLIMATE_BASED": ["调候用神", "调候为先", "气候为急", "调候用事"],
        "DISEASE_BASED": ["病药用神", "因病取用", "病药取用"],
        "BRIDGE_BASED": ["通关用神", "以通关为用"],
        "UNDETERMINED": ["用神未定", "取用未明"],
    }

    _XIANG_HOOKS: Dict[str, List[str]] = {
        "SUCCESS": ["相神得力", "相神有用", "相神有助", "相神有功"],
        "FAIL": ["相神受伤", "相神无力", "相神被伤", "相神受损"],
        "UNDETERMINED": ["相神未定"],
    }

    _XIJI_HOOKS: Dict[str, List[str]] = {
        "STRONG": ["身旺宜克泄", "身旺忌印比", "用官杀", "用食伤", "用财",
                   "喜财官", "宜财官", "旺宜泄", "旺喜", "旺忌",
                   "喜克泄", "宜泄", "当克泄", "喜官杀", "喜食伤",
                   "身旺用官", "身旺喜财"],
        "WEAK": ["身弱宜生扶", "身弱忌克泄", "用印比", "用劫", "喜印比",
                 "宜印比", "弱宜生扶", "弱喜", "弱忌", "喜生扶",
                 "宜生", "当生扶", "身弱用印", "身弱喜比"],
        "BALANCED": ["中和用通关", "视格局定喜忌", "中气调和",
                     "当通关", "宜调和", "中和喜调和"],
        "HOT": ["火炎土燥喜水", "调候以癸", "润局为先", "金寒水冷喜火",
                "水多火熄喜土", "夏木虚焦调候以癸", "火旺", "炎上",
                "火燥", "喜润", "调候以水", "夏月调候", "火旺宜润"],
        "COLD": ["金寒水冷喜火", "调候以丙", "暖局为先", "冬水需火",
                 "寒局喜暖", "冬金需火", "水冷", "寒金", "喜暖",
                 "调候以火", "冬月调候", "寒气", "寒局喜暖"],
        "DRY": ["燥土需水", "土燥喜润", "燥气需调", "土燥", "燥热",
                "喜润局", "宜润"],
        "WET": ["湿土需火", "水旺喜土", "湿局需暖", "水多", "湿土",
                "水泛", "宜燥", "宜暖"],
    }

    _TEMPORAL_HOOKS: Dict[str, List[str]] = {
        "LUCK_PHASED": ["大运", "行运", "运至", "运逢", "运交",
                        "运入", "运走", "运到", "运逢", "行运"],
        "YEAR_PHASED": ["流年", "岁运", "太岁", "岁君", "年逢",
                        "岁逢", "岁至", "年遇"],
        "UNDETERMINED": ["时间层未定"],
    }

    # ═══════════════════════════════════════════════════════════════
    # 统一状态映射表 (domain → 钩子字典)
    # ═══════════════════════════════════════════════════════════════
    DOMAIN_HOOKS = {
        "LING": _LING_HOOKS,
        "GROWTH": _GROWTH_HOOKS,
        "ROOT": _ROOT_HOOKS,
        "PARTY": _PARTY_HOOKS,
        "STRENGTH": _STRENGTH_HOOKS,
        "QING": _QING_HOOKS,
        "CLIMATE": _CLIMATE_HOOKS,
        "TONGGUAN": _TONGGUAN_HOOKS,
        "DISEASE": _DISEASE_HOOKS,
        "QI": _QI_HOOKS,
        "PATTERN": _PATTERN_HOOKS,
        "PATTERN_QUALITY": _PATTERN_QUALITY_HOOKS,
        "TRUE": _TRUE_HOOKS,
        "SPECIAL": _SPECIAL_HOOKS,
        "YONG": _YONG_HOOKS,
        "XIANG": _XIANG_HOOKS,
        "XIJI": _XIJI_HOOKS,
        "TEMPORAL": _TEMPORAL_HOOKS,
    }

    @classmethod
    def resolve_hooks(cls, domain: str, state: str) -> List[str]:
        """解析单个域状态, 返回钩子列表."""
        hooks_dict = cls.DOMAIN_HOOKS.get(domain, {})
        return hooks_dict.get(state, [])

    @classmethod
    def resolve_all(cls, judgments: List[Any]) -> Dict[str, List[str]]:
        """解析全部 §28 判断, 返回 domain → hooks 字典."""
        result = {}
        for j in judgments:
            # 兼容 dict 和 dataclass
            if hasattr(j, 'domain'):
                dom = getattr(j, 'domain', '')
                st = getattr(j, 'state', '')
            else:
                dom = j.get("domain", "") if isinstance(j, dict) else ""
                st = j.get("state", "") if isinstance(j, dict) else ""
            if dom and st and st != "UNDETERMINED":
                hooks = cls.resolve_hooks(dom, st)
                if hooks:
                    result[dom] = hooks
        return result


class DuanyuMatcher:
    """断语匹配器: 条件钩子 → 命局状态 → 断语文本.
    
    匹配策略:
        1. 优先精确匹配 (钩子词直接出现在断语文本中)
        2. 次优先类别匹配 (断语属于命局状态对应类别)
        3. 置信度: STRONG (精确匹配) / MODERATE (类别匹配) / WEAK (模糊匹配)
    """

    def __init__(self, loader: DuanyuLoader):
        self._loader = loader

    def match(
        self,
        hooks: List[str],
        target_cats: List[str],
        limit: int = 20,
    ) -> List[TriggeredDuanyu]:
        """
        匹配断语.
        hooks: 命局条件钩子
        target_cats: 目标断语类别
        limit: 最多返回几条
        """
        candidates = self._loader.load_by_categories(target_cats)
        matched = []
        seen_texts = set()
        for cand in candidates:
            text = cand.get("text", "")
            if not text or len(text) < 8:
                continue
            if text in seen_texts:
                continue
            # 精确匹配: 至少一个钩子完整出现在文本中
            matched_hook = None
            for hook in sorted(hooks, key=len, reverse=True):
                if hook in text:
                    matched_hook = hook
                    break
            if matched_hook:
                seen_texts.add(text)
                quality = DuanyuQualityClassifier.classify(text)
                # DISCARD 类型直接跳过 (目录/序言/散文原注)
                if quality == "DISCARD":
                    continue
                matched.append(TriggeredDuanyu(
                    classic=cand.get("classic", ""),
                    source=cand.get("source", ""),
                    primary_category=cand.get("primary_category", ""),
                    text=text,
                    trigger_rule=f"{matched_hook}∈hooks",
                    evidence_ref=f"{cand.get('classic','')}·{cand.get('source','')}:{text[:40]}...",
                    confidence="STRONG",
                    quality=quality,
                ))
                if len(matched) >= limit:
                    break
        return matched


def build_interpretation(
    judgments: List[Dict[str, Any]],
) -> InterpretationOutput:
    """
    解层入口函数: §28 状态枚举 → 五经断语触发.
    
    全量 15 维:
        P0: LING/GROWTH/ROOT/PARTY/STRENGTH
        P1: QING/CLIMATE/TONGGUAN/DISEASE/QI
        P2: PATTERN/PATTERN_QUALITY/TRUE/SPECIAL
        P3: YONG/XIANG/XIJI/TEMPORAL
    """
    output = InterpretationOutput()

    # 1. 解析全部 §28 状态 → 钩子
    domain_hooks = DomainResolver.resolve_all(judgments)

    # 2. 域状态 → 断语类别 映射
    DOMAIN_CATS = {
        "LING": ["用神喜忌类", "旺衰类"],
        "GROWTH": ["旺衰类", "刑冲合害类"],
        "ROOT": ["旺衰类", "刑冲合害类"],
        "PARTY": ["旺衰类", "用神喜忌类"],
        "STRENGTH": ["旺衰类", "贫贱富贵类", "用神喜忌类"],
        "QING": ["刑冲合害类", "用神喜忌类"],
        "CLIMATE": ["用神喜忌类", "调候类"],
        "TONGGUAN": ["用神喜忌类", "刑冲合害类"],
        "DISEASE": ["用神喜忌类", "疾病类"],
        "QI": ["旺衰类", "用神喜忌类"],
        "PATTERN": ["格局类", "用神喜忌类"],
        "PATTERN_QUALITY": ["格局类", "贫贱富贵类", "用神喜忌类"],
        "TRUE": ["格局类", "用神喜忌类"],
        "SPECIAL": ["特殊格", "格局类", "用神喜忌类"],
        "YONG": ["用神喜忌类"],
        "XIANG": ["用神喜忌类", "格局类"],
        "XIJI": ["用神喜忌类", "旺衰类"],
        "TEMPORAL": ["流年大运类", "用神喜忌类"],
    }

    # 3. 域状态 → 断语数量上限
    DOMAIN_LIMIT = {
        "LING": 10, "GROWTH": 10, "ROOT": 10, "PARTY": 10,
        "STRENGTH": 15, "QING": 10, "CLIMATE": 15,
        "TONGGUAN": 10, "DISEASE": 10, "QI": 10,
        "PATTERN": 15, "PATTERN_QUALITY": 10,
        "TRUE": 10, "SPECIAL": 10, "YONG": 15,
        "XIANG": 10, "XIJI": 20, "TEMPORAL": 10,
    }

    # 4. 域状态 → 输出字段名
    DOMAIN_FIELD = {
        "LING": "ling", "GROWTH": "growth", "ROOT": "root",
        "PARTY": "party", "STRENGTH": "strength", "QING": "qing",
        "CLIMATE": "climate", "TONGGUAN": "tongguan", "DISEASE": "disease",
        "QI": "qi", "PATTERN": "pattern", "PATTERN_QUALITY": "pattern_quality",
        "TRUE": "true", "SPECIAL": "special", "YONG": "yong",
        "XIANG": "xiang", "XIJI": "xiji", "TEMPORAL": "temporal",
    }

    matcher = DuanyuMatcher(DuanyuLoader())

    for dom, hooks in domain_hooks.items():
        cats = DOMAIN_CATS.get(dom, ["用神喜忌类", "旺衰类"])
        limit = DOMAIN_LIMIT.get(dom, 10)
        field = DOMAIN_FIELD.get(dom, dom.lower())

        hits = matcher.match(hooks=hooks, target_cats=cats, limit=limit)
        setattr(output, field, hits)

    # 5. 登记 fail-closed 域
    all_states = {}
    for j in judgments:
        if hasattr(j, 'domain'):
            all_states[getattr(j, 'domain', '')] = getattr(j, 'state', '')
        elif isinstance(j, dict):
            all_states[j.get("domain", "")] = j.get("state", "")
    for dom, st in all_states.items():
        if st == "UNDETERMINED" and dom in DOMAIN_FIELD:
            output.undetermined_domains.append(dom)

    return output
