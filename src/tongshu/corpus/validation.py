"""
P0-3.1 阶段4：Cross-Validation（交叉验证引擎）

【职责】将 FOR-BAZI Corpus 的候选证据与顺天已有原书（段落数据 JSON）做交叉验证，
       输出验证状态 EXACT_MATCH / PARTIAL_MATCH / NOT_FOUND / CONFLICT

【数据源】
- 候选源：FOR-BAZI 五经 JSON（./Canonical-Mining/FOR-BAZI五书JSON/）
- 权威源：顺天段落数据 JSON（./Canonical-Mining/五部经典完整数据/*_段落数据.json）
  - 每部经典是整合了多来源的权威原书（如 DTS 整合 maokuangbiao/bazi-engine/本地HTML/FOR-BAZI）

【验证维度】
1. 原文比对：FOR-BAZI original_text 与段落数据全文做规范化比对
2. 出处比对：FOR-BAZI 出处(source) 与段落数据 passage_id 前缀比对
3. 版本比对：段落数据 sources_used 记录多版本来源

【规范化】去除空白/标点/繁简归一，避免格式差异导致误判

【验证状态】
- EXACT_MATCH：规范化后核心句在权威源中完整出现
- PARTIAL_MATCH：核心子句/关键词在权威源中出现，但非完整句子
- NOT_FOUND：在权威源中未找到
- CONFLICT：找到但存在明显冲突表述（需人工复核）
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .adapter import ClassicEntry, FiveClassicsCorpusAdapter


# ============================================================
# 规范化工具
# ============================================================

# 繁简映射（常用字，用于比对）
_TRAD_SIMP_MAP = {
    "後": "后", "發": "发", "髮": "发", "見": "见", "氣": "气",
    "無": "无", "為": "为", "於": "于", "與": "与", "時": "时",
    "東": "东", "兩": "两", "門": "门", "問": "问", "間": "间",
    "長": "长", "風": "风", "馬": "马", "鳥": "鸟", "龍": "龙",
    "萬": "万", "體": "体", "學": "学", "書": "书", "讀": "读",
    "論": "论", "識": "识", "歲": "岁", "歸": "归", "義": "义",
    "陰": "阴", "陽": "阳", "圓": "圆", "圖": "图", "國": "国",
    "專": "专", "華": "华", "農": "农", "醫": "医", "藥": "药",
    "貴": "贵", "賤": "贱", "買": "买", "賣": "卖", "錢": "钱",
    "銀": "银", "銅": "铜", "鐵": "铁", "鋼": "钢", "鐘": "钟",
    "離": "离", "難": "难", "雖": "虽", "雙": "双", "雜": "杂",
    "靈": "灵", "靜": "静", "動": "动", "雲": "云", "電": "电",
    "頭": "头", "類": "类", "顯": "显", "餘": "余", "曆": "历",
    "歷": "历", "殺": "杀", "熱": "热", "壓": "压", "廠": "厂",
    "廣": "广", "實": "实", "寶": "宝", "將": "将", "對": "对",
    "來": "来", "開": "开", "關": "关", "張": "张", "緊": "紧",
    "會": "会", "當": "当", "復": "复", "備": "备", "應": "应",
    "總": "总", "繫": "系", "紀": "纪", "經": "经", "統": "统",
    "結": "结", "給": "给", "絕": "绝", "絲": "丝", "羅": "罗",
    "紅": "红", "綠": "绿", "紙": "纸", "紋": "纹", "網": "网",
    "縣": "县", "線": "线", "練": "练", "續": "续", "網": "网",
    "聲": "声", "聽": "听", "職": "职", "勝": "胜", "腦": "脑",
    "脫": "脱", "腳": "脚", "臉": "脸", "臺": "台", "興": "兴",
    "葉": "叶", "著": "着", "蓋": "盖", "蓮": "莲", "藍": "蓝",
    "處": "处", "號": "号", "術": "术", "衛": "卫", "裡": "里",
}


def normalize_text(text: str) -> str:
    """规范化文本：去空白、去标点、繁简归一。

    用于比对，不做其他语义处理。
    """
    if not text:
        return ""
    # 去空白（含全角空格）
    text = re.sub(r"[\s\u3000]+", "", text)
    # 去标点（中英文）—— 用 unicode 字符类避免转义
    text = re.sub("[\u3000\u3001\u3002\uff0c\uff01\uff1f\uff1b\uff1a\u300a\u300b\u300c\u300d\u2014\u2026\u00b7,.!?;:()\[\]{}<>]+", "", text)
    # 繁简归一
    text = "".join(_TRAD_SIMP_MAP.get(ch, ch) for ch in text)
    return text


def sha256_text(text: str) -> str:
    """计算原文 sha256（防证据漂移）。"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ============================================================
# 段落数据源（权威原书）
# ============================================================

# 经典ID → 段落数据文件（权威原书源）
PASSAGE_DATA_FILES: Dict[str, str] = {
    "di_tian_sui": "DTS_滴天髓_段落数据.json",
    "ziping_zhenquan": "PZZQ_子平真诠_段落数据.json",
    "qiongtong_baojian": "QTBJ_穷通宝鉴_段落数据.json",
    "sanming_tonghui": "SMTH_三命通会_段落数据.json",
    "yuanhai_ziping": "YHZP_渊海子平_段落数据.json",
}

# 经典ID → 权威源默认路径
DEFAULT_PASSAGE_DATA_DIR = Path(r"D:\today\Canonical-Mining\五部经典完整数据")


@dataclass
class Passage:
    """权威原书段落。"""
    passage_id: str
    text: str
    source: str
    char_count: int = 0

    def normalized(self) -> str:
        return normalize_text(self.text)


class PassageDataLoader:
    """加载段落数据 JSON（权威原书源）。"""

    # n-gram 索引参数
    NGRAM_SIZE = 4          # 4-gram 索引粒度
    NGRAM_SAMPLE = 20       # 每段最多采样 n-gram 数

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or DEFAULT_PASSAGE_DATA_DIR
        self._passages: Dict[str, List[Passage]] = {}
        self._normalized_index: Dict[str, Dict[str, str]] = {}  # classic_id -> {norm_passage_id: norm_text}
        self._ngram_index: Dict[str, Dict[str, List[str]]] = {}  # classic_id -> {ngram: [passage_ids]}
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        for classic_id, filename in PASSAGE_DATA_FILES.items():
            path = self.data_dir / filename
            if not path.exists():
                print(f"Warning: passage data not found: {path}")
                continue
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            passages = []
            for p in data.get("passages", []):
                passages.append(Passage(
                    passage_id=p.get("passage_id", ""),
                    text=p.get("text", ""),
                    source=p.get("source", ""),
                    char_count=p.get("char_count", 0),
                ))
            self._passages[classic_id] = passages
            # 建立规范化索引 + n-gram 倒排索引
            index = {}
            ngram_idx: Dict[str, List[str]] = {}
            for p in passages:
                norm = p.normalized()
                index[p.passage_id] = norm
                if len(norm) >= self.NGRAM_SIZE:
                    # 采样若干 n-gram（每段最多记录 NGRAM_SAMPLE 个，避免索引过大）
                    step = max(1, len(norm) // self.NGRAM_SAMPLE)
                    seen = set()
                    for i in range(0, len(norm) - self.NGRAM_SIZE + 1, step):
                        gram = norm[i:i + self.NGRAM_SIZE]
                        if gram in seen:
                            continue
                        seen.add(gram)
                        ngram_idx.setdefault(gram, []).append(p.passage_id)
            self._normalized_index[classic_id] = index
            self._ngram_index[classic_id] = ngram_idx
        self._loaded = True

    def get_passages(self, classic_id: str) -> List[Passage]:
        self._ensure_loaded()
        return self._passages.get(classic_id, [])

    def get_passage(self, classic_id: str, passage_id: str) -> Optional[Passage]:
        self._ensure_loaded()
        for p in self._passages.get(classic_id, []):
            if p.passage_id == passage_id:
                return p
        return None

    def get_normalized(self, classic_id: str) -> Dict[str, str]:
        self._ensure_loaded()
        return self._normalized_index.get(classic_id, {})

    def get_candidate_passages(self, classic_id: str, norm_source: str, top_k: int = 20) -> List[str]:
        """通过 n-gram 倒排索引快速筛选候选段落ID。

        对源文本采样 n-gram，在倒排索引中检索命中的段落，按命中数排序取前 top_k。
        若源文本过短无法形成 n-gram，退化为返回全部段落。
        """
        self._ensure_loaded()
        ngram_idx = self._ngram_index.get(classic_id)
        if not ngram_idx or len(norm_source) < self.NGRAM_SIZE:
            # 退化：返回全部段落
            return list(self._normalized_index.get(classic_id, {}).keys())

        # 源文本 n-gram 全量取（源文本通常较短，全量更准确）
        # 对短文本全量取所有 4-gram；对超长文本做均匀采样
        if len(norm_source) <= 200:
            grams = set(norm_source[i:i + self.NGRAM_SIZE]
                        for i in range(len(norm_source) - self.NGRAM_SIZE + 1))
        else:
            step = max(1, len(norm_source) // self.NGRAM_SAMPLE)
            grams = set(norm_source[i:i + self.NGRAM_SIZE]
                        for i in range(0, len(norm_source) - self.NGRAM_SIZE + 1, step))

        # 统计候选段落命中数
        hit_counts: Dict[str, int] = {}
        for gram in grams:
            for pid in ngram_idx.get(gram, []):
                hit_counts[pid] = hit_counts.get(pid, 0) + 1

        if not hit_counts:
            return []

        # 按命中数降序
        ranked = sorted(hit_counts.items(), key=lambda x: x[1], reverse=True)
        return [pid for pid, _ in ranked[:top_k]]

    def get_statistics(self) -> dict:
        self._ensure_loaded()
        stats = {}
        for classic_id, passages in self._passages.items():
            stats[classic_id] = {
                "passage_count": len(passages),
                "total_chars": sum(p.char_count for p in passages),
                "sources": sorted(set(p.source for p in passages if p.source)),
            }
        return stats

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()


# ============================================================
# 交叉验证引擎
# ============================================================

@dataclass
class CrossValidationResult:
    """单条交叉验证结果。"""
    entry_id: str
    classic_id: str
    classic_name: str
    category: str
    key: str
    original_text: str
    source: str
    verification_status: str      # EXACT_MATCH/PARTIAL_MATCH/NOT_FOUND/DERIVED_TEXT/CONFLICT
    evidence_class: str           # EXACT_PRIMARY/PARTIAL/DERIVED_TEXT/NOT_FOUND/CONFLICT（P0-3.2 五分类）
    matched_passage_id: str       # 命中段落
    matched_passage_source: str   # 命中段落来源
    matched_fragment: str         # 命中的原文片段
    normalized_source: str        # 规范化后的原文本
    normalized_hit: str           # 规范化后的命中片段
    source_hash: str              # 原文本 sha256
    verification_notes: str       # 备注

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "classic_id": self.classic_id,
            "classic_name": self.classic_name,
            "category": self.category,
            "key": self.key,
            "original_text": self.original_text,
            "source": self.source,
            "verification_status": self.verification_status,
            "evidence_class": self.evidence_class,
            "matched_passage_id": self.matched_passage_id,
            "matched_passage_source": self.matched_passage_source,
            "matched_fragment": self.matched_fragment[:200] if self.matched_fragment else "",
            "normalized_source": self.normalized_source[:200] if self.normalized_source else "",
            "normalized_hit": self.normalized_hit[:200] if self.normalized_hit else "",
            "source_hash": self.source_hash,
            "verification_notes": self.verification_notes,
        }


class CrossValidator:
    """交叉验证引擎 — 将 FOR-BAZI 候选证据与权威原书做比对。

    用法：
        adapter = FiveClassicsCorpusAdapter()
        adapter.load()
        validator = CrossValidator(adapter)
        results = validator.validate_entries(entries)  # 逐条验证
        summary = validator.get_summary(results)       # 汇总统计
    """

    # 匹配阈值
    EXACT_THRESHOLD = 0.95     # 规范化后包含率 >= 95% → EXACT_MATCH
    PARTIAL_THRESHOLD = 0.30   # 规范化后包含率 >= 30% → PARTIAL_MATCH
    # 最短片段长度（小于该长度认为不可靠）
    MIN_FRAGMENT_LEN = 6
    # n-gram 候选段落数（性能优化）
    CANDIDATE_TOP_K = 20

    def __init__(self, adapter: FiveClassicsCorpusAdapter, passage_loader: Optional[PassageDataLoader] = None):
        self.adapter = adapter
        self.passage_loader = passage_loader or PassageDataLoader()
        self.passage_loader.load()
        self._current_classic_id = ""

    # ============================================================
    # 单条验证
    # ============================================================

    def validate_entry(self, entry: ClassicEntry) -> CrossValidationResult:
        """验证单条条目。"""
        # 记录当前经典（供候选检索使用）
        self._current_classic_id = entry.classic_id

        # 规范化原文本
        norm_source = normalize_text(entry.original_text)
        source_hash = entry.source_hash or sha256_text(entry.original_text)

        # 如果条目是从其他字段构建的（无原典原文），标记为 DERIVED_TEXT
        if entry.verification_status == "DERIVED_TEXT":
            return self._build_result(
                entry, "DERIVED_TEXT", "", "", "", norm_source, "", source_hash,
                f"FOR-BAZI 无'原文'字段，条目从其他字段构建（{entry.verification_notes}），无法与原典逐字比对",
            )

        # 原文为空
        if not norm_source:
            return self._build_result(
                entry, "NOT_FOUND", "", "", "", norm_source, "", source_hash,
                "FOR-BAZI 条目原文为空，无法验证",
            )

        # 查找权威源
        norm_index = self.passage_loader.get_normalized(entry.classic_id)
        if not norm_index:
            return self._build_result(
                entry, "NOT_FOUND", "", "", "", norm_source, "", source_hash,
                f"权威源未找到: {entry.classic_id} 无段落数据",
            )

        # 在权威源中搜索
        best_hit = self._find_best_hit(norm_source, norm_index)

        if best_hit is None:
            return self._build_result(
                entry, "NOT_FOUND", "", "", "", norm_source, "", source_hash,
                "权威源全文未找到规范化原文",
            )

        passage_id, hit_fragment = best_hit
        passage = self.passage_loader.get_passage(entry.classic_id, passage_id)
        passage_source = passage.source if passage else ""

        # 计算匹配率
        hit_len = len(hit_fragment)
        src_len = len(norm_source)
        coverage = hit_len / src_len if src_len > 0 else 0.0

        # 判定状态
        if coverage >= self.EXACT_THRESHOLD and src_len >= self.MIN_FRAGMENT_LEN:
            status = "EXACT_MATCH"
            notes = f"规范化覆盖率 {coverage:.0%}（≥95%），核心原文在权威源完整命中"
        elif coverage >= self.PARTIAL_THRESHOLD and src_len >= self.MIN_FRAGMENT_LEN:
            status = "PARTIAL_MATCH"
            notes = f"规范化覆盖率 {coverage:.0%}（≥30%），核心子句命中，存在版本/节选差异"
        else:
            status = "NOT_FOUND"
            notes = f"规范化覆盖率 {coverage:.0%}（<30%），仅有零散词句命中，不能视为有效证据"

        return self._build_result(
            entry, status, passage_id, passage_source, hit_fragment,
            norm_source, normalize_text(hit_fragment), source_hash, notes,
        )

    def _find_best_hit(self, norm_source: str, norm_index: Dict[str, str]) -> Optional[Tuple[str, str]]:
        """在规范化段落索引中查找最佳命中。

        分层策略：
        1. 整串子串全段扫描（Python 内建 in，快）→ 命中即高覆盖
        2. 未整串命中 → n-gram 候选 + LCS 找 PARTIAL
        Returns:
            (passage_id, 命中的原文子串)
        """
        if not norm_source or len(norm_source) < self.MIN_FRAGMENT_LEN:
            return None

        # 第1层：整串子串全段扫描（最可靠，Python in 快）
        best_direct_coverage = 0.0
        best_direct = None
        for passage_id, norm_text in norm_index.items():
            if not norm_text:
                continue
            if norm_source in norm_text:
                # 整串命中 = 100% 覆盖
                return (passage_id, norm_source)

        # 第2层：n-gram 候选 + LCS（找 PARTIAL 匹配）
        candidate_ids = self.passage_loader.get_candidate_passages(
            self._current_classic_id, norm_source, top_k=self.CANDIDATE_TOP_K
        )

        best_coverage = 0.0
        best_hit = None
        best_fragment = ""

        for passage_id in candidate_ids:
            norm_text = norm_index.get(passage_id)
            if not norm_text:
                continue
            coverage, fragment = self._compute_coverage(norm_source, norm_text)
            if coverage > best_coverage:
                best_coverage = coverage
                best_hit = (passage_id, fragment)
                best_fragment = fragment

        if best_coverage >= self.PARTIAL_THRESHOLD:
            return best_hit
        return None

    def _compute_coverage(self, norm_source: str, norm_passage: str) -> Tuple[float, str]:
        """计算源文本在段落中的包含率。

        使用最长连续匹配 + 分段匹配策略。
        """
        if not norm_source or not norm_passage:
            return 0.0, ""

        src_len = len(norm_source)

        # 1. 直接子串匹配（最可靠）
        if norm_source in norm_passage:
            return 1.0, norm_source

        # 2. 分段匹配：把源文本按长度切块，计算命中的块占比
        #    用窗口滑动找最长的连续命中
        # 尝试多个起点找最长公共子串
        longest_match = self._longest_common_substring(norm_source, norm_passage)
        if len(longest_match) >= self.MIN_FRAGMENT_LEN:
            coverage = len(longest_match) / src_len
            return coverage, longest_match

        # 3. 逐句匹配：把源按句子切分
        sentences = self._split_sentences(norm_source)
        if sentences:
            matched_chars = 0
            matched_fragments = []
            for sent in sentences:
                if len(sent) < 2:
                    continue
                if sent in norm_passage:
                    matched_chars += len(sent)
                    matched_fragments.append(sent)
            if matched_chars > 0:
                coverage = matched_chars / src_len
                return coverage, "".join(matched_fragments)

        return 0.0, ""

    def _longest_common_substring(self, s1: str, s2: str) -> str:
        """找最长公共子串（朴素实现，适用于短文本）。"""
        if not s1 or not s2:
            return ""
        # 限制最大长度避免 O(n*m) 过大
        max_len = min(len(s1), len(s2), 200)
        best = ""
        for i in range(len(s1)):
            for j in range(len(s2)):
                k = 0
                while (i + k < len(s1) and j + k < len(s2)
                       and s1[i + k] == s2[j + k] and k < max_len):
                    k += 1
                if k > len(best):
                    best = s1[i:i + k]
        return best

    def _split_sentences(self, text: str) -> List[str]:
        """把规范化文本切句（按常见句读）。"""
        # 规范化后标点已去除，按常见古文句读切分
        parts = re.split(r"(?<=[也矣焉哉乎耳而已])", text)
        return [p for p in parts if p]

    # 验证状态 → 证据分类映射（P0-3.2）
    STATUS_TO_CLASS = {
        "EXACT_MATCH": "EXACT_PRIMARY",   # 原典逐字原文，证据等级最高
        "PARTIAL_MATCH": "PARTIAL",       # 部分命中，存在版本/节选差异
        "DERIVED_TEXT": "DERIVED_TEXT",   # FOR-BAZI 无原文，从其他字段构建（隔离）
        "NOT_FOUND": "NOT_FOUND",         # 权威原书未找到
        "CONFLICT": "CONFLICT",           # 存在冲突
    }

    def _build_result(
        self,
        entry: ClassicEntry,
        status: str,
        passage_id: str,
        passage_source: str,
        matched_fragment: str,
        norm_source: str,
        norm_hit: str,
        source_hash: str,
        notes: str,
    ) -> CrossValidationResult:
        evidence_class = self.STATUS_TO_CLASS.get(status, "NOT_FOUND")
        return CrossValidationResult(
            entry_id=entry.entry_id,
            classic_id=entry.classic_id,
            classic_name=entry.classic_name,
            category=entry.category,
            key=entry.key,
            original_text=entry.original_text,
            source=entry.source,
            verification_status=status,
            evidence_class=evidence_class,
            matched_passage_id=passage_id,
            matched_passage_source=passage_source,
            matched_fragment=matched_fragment,
            normalized_source=norm_source,
            normalized_hit=norm_hit,
            source_hash=source_hash,
            verification_notes=notes,
        )

    # ============================================================
    # 批量验证 + 汇总
    # ============================================================

    def validate_entries(self, entries: List[ClassicEntry]) -> List[CrossValidationResult]:
        """批量验证条目。"""
        return [self.validate_entry(e) for e in entries]

    def get_summary(self, results: List[CrossValidationResult]) -> dict:
        """汇总统计验证结果。"""
        summary = {
            "total": len(results),
            "by_status": {},
            "by_class": {},       # P0-3.2 证据分类
            "by_classic": {},
            "by_category": {},
        }

        # 按状态统计
        status_counts = {}
        class_counts = {}
        for r in results:
            status_counts[r.verification_status] = status_counts.get(r.verification_status, 0) + 1
            class_counts[r.evidence_class] = class_counts.get(r.evidence_class, 0) + 1
        summary["by_status"] = status_counts
        summary["by_class"] = class_counts

        # 按经典统计（含 evidence_class）
        classic_stats = {}
        for r in results:
            if r.classic_id not in classic_stats:
                classic_stats[r.classic_id] = {"total": 0, "by_status": {}, "by_class": {}}
            classic_stats[r.classic_id]["total"] += 1
            classic_stats[r.classic_id]["by_status"][r.verification_status] = \
                classic_stats[r.classic_id]["by_status"].get(r.verification_status, 0) + 1
            classic_stats[r.classic_id]["by_class"][r.evidence_class] = \
                classic_stats[r.classic_id]["by_class"].get(r.evidence_class, 0) + 1
        summary["by_classic"] = classic_stats

        # 按分类统计
        category_stats = {}
        for r in results:
            if r.category not in category_stats:
                category_stats[r.category] = {"total": 0, "by_status": {}, "by_class": {}}
            category_stats[r.category]["total"] += 1
            category_stats[r.category]["by_status"][r.verification_status] = \
                category_stats[r.category]["by_status"].get(r.verification_status, 0) + 1
            category_stats[r.category]["by_class"][r.evidence_class] = \
                category_stats[r.category]["by_class"].get(r.evidence_class, 0) + 1
        summary["by_category"] = category_stats

        return summary
