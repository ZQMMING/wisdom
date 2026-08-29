"""
P0-3.0 阶段3：Evidence Candidate Retrieval（证据候选检索引擎）

【职责】根据辨证概念从五经 Corpus 中自动检索候选证据，按相关度排序，输出标准化格式
【核心原则】候选证据≠原典授权；候选证据必须经过交叉验证才能升级授权等级
【依赖】FiveClassicsCorpusAdapter（阶段1）

数据结构：
  EvidenceCandidate:
    candidate_id: str          # 候选证据ID
    concept: str               # 辨证概念
    classic_id: str            # 经典ID
    classic_name: str          # 经典名称
    entry_id: str              # 条目ID
    category: str              # 分类
    key: str                   # 关键词
    original_text: str         # 原文
    interpretation: str        # 解析（仅作参考）
    source: str                # 出处
    tags: list[str]            # 标签
    match_score: float         # 匹配度（0.0-1.0）
    match_reasons: list[str]   # 匹配原因
    match_fields: list[str]    # 匹配字段
    authorization_hint: str    # 授权等级提示（仅基于匹配度，非最终授权）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .adapter import FiveClassicsCorpusAdapter, ClassicEntry


# ============================================================
# 辨证概念 → 关键词映射表
# ============================================================

# 核心辨证概念及其检索关键词
# 注意：这是检索用的关键词映射，不是原典定义
CONCEPT_KEYWORD_MAP: Dict[str, Dict[str, List[str]]] = {
    # 旺衰相关
    "得时": {
        "primary": ["得时", "得令", "当令", "月令", "得令者旺"],
        "secondary": ["失令", "失时", "不得令", "月令休囚"],
        "related": ["四时", "旺相休囚", "进退"],
    },
    "有根": {
        "primary": ["有根", "通根", "根气", "得地", "根深"],
        "secondary": ["无根", "根浅", "根轻", "根被拔"],
        "related": ["长生", "禄", "旺", "墓库", "余气", "本气"],
    },
    "有气": {
        "primary": ["有气", "得气", "气盛", "气旺"],
        "secondary": ["无气", "失气", "气衰", "气弱"],
        "related": ["真气", "假气", "气势", "气数", "气象", "进气", "退气"],
    },
    "气势": {
        "primary": ["气势", "势", "势成", "势强", "势聚"],
        "secondary": ["势散", "势断", "势弱", "势孤"],
        "related": ["党众", "成群", "连续", "方向", "集中度", "转化"],
    },
    "生扶": {
        "primary": ["生扶", "生助", "帮扶", "比劫帮", "印生"],
        "secondary": ["无生扶", "生扶少", "孤立无援"],
        "related": ["印绶", "比肩", "劫财", "同类", "党众"],
    },
    "制泄": {
        "primary": ["克制", "克泄", "泄耗", "被克", "被泄", "被耗"],
        "secondary": ["无制", "制太过", "泄太过"],
        "related": ["官杀", "食伤", "财星", "七杀", "正官", "食神", "伤官", "偏财", "正财"],
    },

    # 调候相关
    "调候": {
        "primary": ["调候", "寒暖", "燥湿", "调候用神", "候"],
        "secondary": ["过寒", "过热", "过燥", "过湿"],
        "related": ["四时", "月令", "寒暖燥湿", "丙火暖局", "壬水润局"],
    },
    "用神": {
        "primary": ["用神", "喜神", "忌神", "喜用"],
        "secondary": ["无用神", "用神受伤", "用神被克"],
        "related": ["格局", "成败", "救应", "喜忌"],
    },

    # 格局相关
    "格局": {
        "primary": ["格局", "成格", "败格", "格", "局"],
        "secondary": ["破格", "无格", "格不成"],
        "related": ["月令", "用神", "成败", "救应", "喜忌", "正官格", "七杀格", "食神格", "伤官格", "财格", "印格"],
    },
    "成败救应": {
        "primary": ["成格", "败格", "救应", "成", "败"],
        "secondary": ["无救", "救应不及"],
        "related": ["格局", "用神", "喜忌", "护", "伤"],
    },

    # 十神相关
    "十神": {
        "primary": ["十神", "比肩", "劫财", "食神", "伤官", "偏财", "正财", "七杀", "正官", "偏印", "正印"],
        "secondary": [],
        "related": ["生克", "六亲", "宫位"],
    },

    # 刑冲合害相关
    "刑冲合害": {
        "primary": ["刑", "冲", "合", "害", "会", "三合", "六合", "三刑", "六冲", "六害"],
        "secondary": ["刑伤", "冲破", "合化", "合而不化"],
        "related": ["地支", "天干", "藏干", "化气"],
    },

    # 旺衰综合
    "旺衰": {
        "primary": ["旺衰", "强弱", "身强", "身弱", "旺", "衰"],
        "secondary": ["偏旺", "偏弱", "太旺", "太弱", "从强", "从弱"],
        "related": ["得时", "有根", "生扶", "制泄", "气势", "调候"],
    },

    # 其他核心概念
    "月令": {
        "primary": ["月令", "月支", "提纲", "月柱"],
        "secondary": [],
        "related": ["得时", "格局", "调候", "旺相休囚"],
    },
    "通根": {
        "primary": ["通根", "有根", "根气", "得地"],
        "secondary": ["不通根", "无根"],
        "related": ["藏干", "本气", "中气", "余气", "长生", "禄", "旺"],
    },
    "干多不如根重": {
        "primary": ["干多不如根重", "天干多", "根重"],
        "secondary": [],
        "related": ["有根", "通根", "天干", "地支"],
    },
    "得时不旺": {
        "primary": ["得时不旺", "得令不旺", "虽得令"],
        "secondary": [],
        "related": ["得时", "有根", "生扶", "制泄"],
    },
    "失时不弱": {
        "primary": ["失时不弱", "失令不弱", "虽失令"],
        "secondary": [],
        "related": ["得时", "有根", "生扶", "党众"],
    },
}


# ============================================================
# 候选证据数据结构
# ============================================================

@dataclass(frozen=True)
class EvidenceCandidate:
    """标准化的候选证据。"""
    candidate_id: str
    concept: str
    classic_id: str
    classic_name: str
    entry_id: str
    category: str
    key: str
    original_text: str
    interpretation: str
    source: str
    tags: List[str]
    match_score: float
    match_reasons: List[str]
    match_fields: List[str]
    authorization_hint: str  # 仅基于匹配度的提示，非最终授权

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "concept": self.concept,
            "classic_id": self.classic_id,
            "classic_name": self.classic_name,
            "entry_id": self.entry_id,
            "category": self.category,
            "key": self.key,
            "original_text": self.original_text,
            "interpretation": self.interpretation,
            "source": self.source,
            "tags": list(self.tags),
            "match_score": round(self.match_score, 3),
            "match_reasons": list(self.match_reasons),
            "match_fields": list(self.match_fields),
            "authorization_hint": self.authorization_hint,
        }


# ============================================================
# 证据候选检索引擎
# ============================================================

class EvidenceCandidateRetriever:
    """证据候选检索引擎 — 根据辨证概念从五经 Corpus 中自动检索候选证据。

    用法：
        adapter = FiveClassicsCorpusAdapter()
        adapter.load()
        retriever = EvidenceCandidateRetriever(adapter)

        # 按概念检索
        candidates = retriever.retrieve_by_concept("得时")

        # 按概念检索，限定经典
        candidates = retriever.retrieve_by_concept("调候", classic_ids=["qiongtong_baojian"])

        # 按自定义关键词检索
        candidates = retriever.retrieve_by_keywords(["得时", "有根"], concept="旺衰基础")

        # 获取所有支持的概念
        concepts = retriever.get_supported_concepts()
    """

    # 匹配权重
    WEIGHT_TAG_EXACT = 0.4       # 标签精确匹配
    WEIGHT_ORIGINAL_TEXT = 0.3   # 原文匹配
    WEIGHT_KEY = 0.15            # 关键词匹配
    WEIGHT_CATEGORY = 0.1        # 分类匹配
    WEIGHT_INTERPRETATION = 0.05 # 解析匹配（权重最低，因为解析是现代解释）

    def __init__(self, adapter: FiveClassicsCorpusAdapter):
        self.adapter = adapter
        self._candidate_counter = 0

    # ============================================================
    # 概念检索
    # ============================================================

    def retrieve_by_concept(
        self,
        concept: str,
        classic_ids: Optional[List[str]] = None,
        top_k: int = 20,
        min_score: float = 0.05,
    ) -> List[EvidenceCandidate]:
        """按辨证概念检索候选证据。

        Args:
            concept: 辨证概念（如"得时""有根""调候"）
            classic_ids: 限定经典ID列表，None表示全部经典
            top_k: 返回前K条候选证据
            min_score: 最低匹配度阈值

        Returns:
            按匹配度降序排列的候选证据列表
        """
        if concept not in CONCEPT_KEYWORD_MAP:
            # 未知概念，尝试用概念本身作为关键词检索
            return self.retrieve_by_keywords([concept], concept=concept, classic_ids=classic_ids, top_k=top_k, min_score=min_score)

        keyword_config = CONCEPT_KEYWORD_MAP[concept]
        all_keywords = (
            keyword_config.get("primary", [])
            + keyword_config.get("secondary", [])
            + keyword_config.get("related", [])
        )

        return self.retrieve_by_keywords(
            keywords=all_keywords,
            concept=concept,
            classic_ids=classic_ids,
            top_k=top_k,
            min_score=min_score,
            primary_keywords=keyword_config.get("primary", []),
        )

    def retrieve_by_keywords(
        self,
        keywords: List[str],
        concept: str = "custom",
        classic_ids: Optional[List[str]] = None,
        top_k: int = 20,
        min_score: float = 0.05,
        primary_keywords: Optional[List[str]] = None,
    ) -> List[EvidenceCandidate]:
        """按自定义关键词检索候选证据。

        Args:
            keywords: 关键词列表
            concept: 概念名称（用于标注）
            classic_ids: 限定经典ID列表
            top_k: 返回前K条
            min_score: 最低匹配度阈值
            primary_keywords: 主要关键词（匹配权重更高）
        """
        all_entries = self.adapter.get_all_entries()

        # 限定经典
        if classic_ids:
            all_entries = [e for e in all_entries if e.classic_id in classic_ids]

        primary_set = set(primary_keywords or keywords)
        all_keywords_lower = set(kw.lower() for kw in keywords)

        candidates = []
        for entry in all_entries:
            score, reasons, fields = self._compute_match_score(
                entry, all_keywords_lower, primary_set
            )

            if score >= min_score:
                candidate = self._build_candidate(
                    entry, concept, score, reasons, fields
                )
                candidates.append(candidate)

        # 按匹配度降序排列
        candidates.sort(key=lambda c: c.match_score, reverse=True)
        return candidates[:top_k]

    # ============================================================
    # 匹配度计算
    # ============================================================

    def _compute_match_score(
        self,
        entry: ClassicEntry,
        keywords: Set[str],
        primary_keywords: Set[str],
    ) -> Tuple[float, List[str], List[str]]:
        """计算条目与关键词的匹配度。

        Returns:
            (match_score, match_reasons, match_fields)
        """
        total_score = 0.0
        reasons = []
        fields = []

        # 1. 标签精确匹配（权重最高）
        entry_tags_lower = set(t.lower() for t in entry.tags)
        tag_matches = keywords.intersection(entry_tags_lower)
        if tag_matches:
            primary_tag_matches = tag_matches.intersection(primary_keywords)
            tag_score = self.WEIGHT_TAG_EXACT
            if primary_tag_matches:
                tag_score *= 1.5  # 主要关键词标签匹配，权重提升
            total_score += min(tag_score, self.WEIGHT_TAG_EXACT * 1.5)
            reasons.append(f"标签匹配: {', '.join(sorted(tag_matches))}")
            fields.append("tags")

        # 2. 原文匹配
        original_lower = entry.original_text.lower() if entry.original_text else ""
        original_matches = [kw for kw in keywords if kw in original_lower]
        if original_matches:
            primary_original = [kw for kw in original_matches if kw in primary_keywords]
            orig_score = self.WEIGHT_ORIGINAL_TEXT * (1 + 0.5 * len(primary_original))
            total_score += min(orig_score, self.WEIGHT_ORIGINAL_TEXT * 2)
            reasons.append(f"原文匹配: {', '.join(sorted(set(original_matches)))}")
            fields.append("original_text")

        # 3. 关键词(key)匹配
        key_lower = entry.key.lower() if entry.key else ""
        key_matches = [kw for kw in keywords if kw in key_lower]
        if key_matches:
            total_score += self.WEIGHT_KEY
            reasons.append(f"关键词匹配: {', '.join(sorted(set(key_matches)))}")
            fields.append("key")

        # 4. 分类匹配
        category_lower = entry.category.lower() if entry.category else ""
        cat_matches = [kw for kw in keywords if kw in category_lower]
        if cat_matches:
            total_score += self.WEIGHT_CATEGORY
            reasons.append(f"分类匹配: {', '.join(sorted(set(cat_matches)))}")
            fields.append("category")

        # 5. 解析匹配（权重最低）
        interp_lower = entry.interpretation.lower() if entry.interpretation else ""
        interp_matches = [kw for kw in keywords if kw in interp_lower]
        if interp_matches:
            total_score += self.WEIGHT_INTERPRETATION
            reasons.append(f"解析匹配: {', '.join(sorted(set(interp_matches)))}")
            fields.append("interpretation")

        # 归一化到 0.0-1.0
        max_possible = (
            self.WEIGHT_TAG_EXACT * 1.5
            + self.WEIGHT_ORIGINAL_TEXT * 2
            + self.WEIGHT_KEY
            + self.WEIGHT_CATEGORY
            + self.WEIGHT_INTERPRETATION
        )
        normalized_score = min(total_score / max_possible, 1.0)

        return normalized_score, reasons, fields

    # ============================================================
    # 候选证据构建
    # ============================================================

    def _build_candidate(
        self,
        entry: ClassicEntry,
        concept: str,
        score: float,
        reasons: List[str],
        fields: List[str],
    ) -> EvidenceCandidate:
        """构建标准化候选证据。"""
        self._candidate_counter += 1

        # 基于匹配度的授权等级提示（仅提示，非最终授权）
        if score >= 0.5 and "original_text" in fields and "tags" in fields:
            auth_hint = "HIGH_MATCH — 原文+标签双匹配，建议优先做交叉验证"
        elif score >= 0.3 and "original_text" in fields:
            auth_hint = "MEDIUM_MATCH — 原文匹配，建议做交叉验证"
        elif score >= 0.15:
            auth_hint = "LOW_MATCH — 部分匹配，需人工审核"
        else:
            auth_hint = "WEAK_MATCH — 弱匹配，仅作参考"

        return EvidenceCandidate(
            candidate_id=f"CAND-{self._candidate_counter:04d}",
            concept=concept,
            classic_id=entry.classic_id,
            classic_name=entry.classic_name,
            entry_id=entry.entry_id,
            category=entry.category,
            key=entry.key,
            original_text=entry.original_text,
            interpretation=entry.interpretation,
            source=entry.source,
            tags=list(entry.tags),
            match_score=score,
            match_reasons=reasons,
            match_fields=fields,
            authorization_hint=auth_hint,
        )

    # ============================================================
    # 批量检索
    # ============================================================

    def retrieve_multiple_concepts(
        self,
        concepts: List[str],
        classic_ids: Optional[List[str]] = None,
        top_k_per_concept: int = 10,
    ) -> Dict[str, List[EvidenceCandidate]]:
        """批量检索多个概念的候选证据。

        Returns:
            {concept: [candidate1, candidate2, ...]}
        """
        results = {}
        for concept in concepts:
            results[concept] = self.retrieve_by_concept(
                concept, classic_ids=classic_ids, top_k=top_k_per_concept
            )
        return results

    # ============================================================
    # 概念列表
    # ============================================================

    def get_supported_concepts(self) -> List[str]:
        """获取所有支持的辨证概念。"""
        return sorted(CONCEPT_KEYWORD_MAP.keys())

    def get_concept_keywords(self, concept: str) -> Optional[Dict[str, List[str]]]:
        """获取指定概念的检索关键词配置。"""
        return CONCEPT_KEYWORD_MAP.get(concept)
