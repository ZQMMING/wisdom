# -*- coding: utf-8 -*-
"""断言优化核心模块 — 结构化advice/权重/去重/冲突检测/交叉验证.

解决当前断言系统"全塞进去"的问题:
1. 结构化AdviceItem: 每条建议带source/weight/priority/category
2. 体系权重系统: 不同体系在不同主题上权重不同
3. 去重机制: 基于文本相似度合并重复建议
4. 冲突检测: 检测矛盾建议并标记
5. 交叉验证: 多体系内容一致才高置信度
6. advice聚合排序: 按权重×优先级排序, 输出结构化+字符串双格式
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
# 1. 结构化AdviceItem
# ═══════════════════════════════════════════════════════════════════

class AdviceCategory(str, Enum):
    """建议类别."""
    FORTUNE = "时运"        # 流年运势
    WEALTH = "财运"         # 财运建议
    CAREER = "事业"         # 事业建议
    MARRIAGE = "婚恋"       # 婚恋建议
    HEALTH = "健康"         # 健康建议
    HOME = "家宅"           # 家宅建议
    LAWSUIT = "诉讼"        # 官司建议
    WISDOM = "智慧"         # 人生智慧
    ACTION = "行动"         # 具体行动建议
    CAUTION = "警示"        # 风险警示


class AdviceSource(str, Enum):
    """建议来源体系."""
    ZIPING = "子平"          # 八字子平
    BLIND = "盲派"           # 盲派
    ZIWEI = "紫微"           # 紫微斗数
    HELUO = "河洛"           # 河洛理数
    YIJING = "易经"          # 易经卦辞
    FUPEIRONG = "傅佩荣"     # 傅佩荣多维度断言
    MASTER = "大师智慧"      # 南怀瑾/曾仕强
    CLASSICAL = "古籍"       # 古籍引用
    HUMAN_WAY = "人间道"     # 64卦人间道指引


@dataclass
class AdviceItem:
    """结构化建议项.

    Attributes:
        content: 建议内容
        source: 来源体系
        category: 建议类别
        weight: 权重(0.0-1.0), 来源体系的可信度
        priority: 优先级(1-5), 5=最高, 建议的重要程度
        direction: 建议方向(positive/negative/neutral)
        confidence: 该条建议的置信度(0.0-1.0)
        deduplicated: 是否已去重
        conflict_with: 与哪些建议冲突(来源列表)
    """
    content: str
    source: AdviceSource
    category: AdviceCategory = AdviceCategory.ACTION
    weight: float = 0.5
    priority: int = 3
    direction: str = "neutral"  # positive/negative/neutral
    confidence: float = 0.5
    deduplicated: bool = False
    conflict_with: list[str] = field(default_factory=list)

    @property
    def score(self) -> float:
        """综合评分 = 权重 × 优先级 × 置信度."""
        return self.weight * (self.priority / 5.0) * self.confidence

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "source": self.source.value,
            "category": self.category.value,
            "weight": round(self.weight, 3),
            "priority": self.priority,
            "direction": self.direction,
            "confidence": round(self.confidence, 3),
            "score": round(self.score, 3),
            "conflict_with": self.conflict_with,
        }


# ═══════════════════════════════════════════════════════════════════
# 2. 体系权重系统
# ═══════════════════════════════════════════════════════════════════

# 不同体系在不同主题上的权重(0.0-1.0)
# 基于各体系的专长领域:
# - 紫微: 婚姻/事业/性格分析强
# - 盲派: 应期/财运/事件预测强
# - 河洛: 流年/整体趋势/卦象指引强
# - 子平: 旺衰/格局/用神分析强
SYSTEM_WEIGHTS = {
    "career": {
        "ziwei": 0.85,    # 紫微官禄宫分析强
        "blind": 0.75,    # 盲派官杀应期
        "heluo": 0.65,    # 河洛事业卦
        "ziping": 0.80,   # 子平官星格局
    },
    "wealth": {
        "ziwei": 0.75,    # 紫微财帛宫
        "blind": 0.85,    # 盲派财星应期强
        "heluo": 0.70,    # 河洛财运卦
        "ziping": 0.80,   # 子平财星格局
    },
    "marriage": {
        "ziwei": 0.90,    # 紫微夫妻宫分析最强
        "blind": 0.70,    # 盲派婚姻宫
        "heluo": 0.60,    # 河洛婚姻卦
        "ziping": 0.75,   # 子平配偶星
    },
    "health": {
        "ziwei": 0.70,    # 紫微疾厄宫
        "blind": 0.75,    # 盲派疾病引动
        "heluo": 0.80,    # 河洛健康卦(卦象对应身体)
        "ziping": 0.85,   # 子平五行旺衰对应健康最强
    },
    "general": {
        "ziwei": 0.75,
        "blind": 0.75,
        "heluo": 0.75,
        "ziping": 0.75,
    },
}

# 建议来源的基础权重
SOURCE_BASE_WEIGHTS = {
    AdviceSource.ZIPING: 0.80,
    AdviceSource.BLIND: 0.75,
    AdviceSource.ZIWEI: 0.80,
    AdviceSource.HELUO: 0.70,
    AdviceSource.YIJING: 0.75,
    AdviceSource.FUPEIRONG: 0.65,    # 傅佩荣是现代解读, 权重稍低
    AdviceSource.MASTER: 0.60,        # 大师智慧是哲学补充, 权重较低
    AdviceSource.CLASSICAL: 0.90,     # 古籍引用权重最高
    AdviceSource.HUMAN_WAY: 0.70,     # 人间道指引
}


def get_system_weight(system: str, topic: str = "general") -> float:
    """获取体系在指定主题上的权重."""
    topic_weights = SYSTEM_WEIGHTS.get(topic, SYSTEM_WEIGHTS["general"])
    return topic_weights.get(system, 0.5)


def get_source_weight(source: AdviceSource, topic: str = "general") -> float:
    """获取建议来源在指定主题上的权重(基础权重×主题系数)."""
    base = SOURCE_BASE_WEIGHTS.get(source, 0.5)
    # 来源对应的体系
    system_map = {
        AdviceSource.ZIPING: "ziping",
        AdviceSource.BLIND: "blind",
        AdviceSource.ZIWEI: "ziwei",
        AdviceSource.HELUO: "heluo",
        AdviceSource.YIJING: "heluo",
        AdviceSource.FUPEIRONG: "heluo",
        AdviceSource.MASTER: "heluo",
        AdviceSource.CLASSICAL: "ziping",
        AdviceSource.HUMAN_WAY: "heluo",
    }
    system = system_map.get(source, "general")
    topic_factor = get_system_weight(system, topic)
    # 归一化: 基础权重 × 主题系数 / 0.75(平均主题权重)
    return min(1.0, base * (topic_factor / 0.75))


# ═══════════════════════════════════════════════════════════════════
# 3. 去重机制
# ═══════════════════════════════════════════════════════════════════

def _text_similarity(text1: str, text2: str) -> float:
    """简单文本相似度(基于字符集合的Jaccard相似度).

    对于中文建议, 用词集合比较更准确. 这里用字符级Jaccard作为快速近似.
    """
    if not text1 or not text2:
        return 0.0
    # 去除标点和空格
    def _clean(t: str) -> set:
        return set(c for c in t if c not in "，。！？、；：""''（）【】 \n\t")
    s1 = _clean(text1)
    s2 = _clean(text2)
    if not s1 or not s2:
        return 0.0
    intersection = len(s1 & s2)
    union = len(s1 | s2)
    return intersection / union if union > 0 else 0.0


def deduplicate_advice(items: list[AdviceItem], threshold: float = 0.6) -> list[AdviceItem]:
    """去重: 合并相似度超过阈值的建议.

    策略:
    - 保留权重最高的那条
    - 被合并的条目标记deduplicated=True
    - 合并后的内容取权重最高的那条, 但confidence提升(多源印证)
    """
    if len(items) <= 1:
        return items

    result = []
    used = set()

    for i, item in enumerate(items):
        if i in used:
            continue
        # 查找与当前item相似的其他item
        similar = [item]
        for j in range(i + 1, len(items)):
            if j in used:
                continue
            sim = _text_similarity(item.content, items[j].content)
            if sim >= threshold:
                similar.append(items[j])
                used.add(j)

        if len(similar) > 1:
            # 合并: 保留权重最高的, confidence提升
            best = max(similar, key=lambda x: x.score)
            # 多源印证提升置信度(最多提升0.2)
            boost = min(0.2, 0.05 * (len(similar) - 1))
            merged = AdviceItem(
                content=best.content,
                source=best.source,
                category=best.category,
                weight=best.weight,
                priority=best.priority,
                direction=best.direction,
                confidence=min(1.0, best.confidence + boost),
                deduplicated=True,
            )
            result.append(merged)
        else:
            result.append(item)
        used.add(i)

    return result


# ═══════════════════════════════════════════════════════════════════
# 4. 冲突检测
# ═══════════════════════════════════════════════════════════════════

# 冲突关键词对(相反含义的词)
CONFLICT_PAIRS = [
    ("积极", "保守"),
    ("进取", "避险"),
    ("投资", "守财"),
    ("主动", "等待"),
    ("把握", "放弃"),
    ("扩张", "收缩"),
    ("变动", "稳定"),
    ("结婚", "暂缓"),
    ("创业", "守成"),
    ("跳槽", "稳固"),
    ("大额", "小额"),
    ("利好", "利空"),
]


def detect_conflicts(items: list[AdviceItem]) -> list[AdviceItem]:
    """检测建议之间的冲突.

    策略:
    - 同类别(categories)的建议, 如果包含冲突关键词对, 标记冲突
    - 冲突的建议互相标记conflict_with
    - 冲突建议的confidence降低
    """
    for i, item1 in enumerate(items):
        for j in range(i + 1, len(items)):
            item2 = items[j]
            # 只检测同类别或相关类别的冲突
            if item1.category != item2.category and not _related_categories(item1.category, item2.category):
                continue
            # 检测冲突关键词
            if _has_conflict_keywords(item1.content, item2.content):
                if item1.source.value not in item2.conflict_with:
                    item2.conflict_with.append(item1.source.value)
                if item2.source.value not in item1.conflict_with:
                    item1.conflict_with.append(item2.source.value)
                # 冲突降低置信度
                item1.confidence = max(0.1, item1.confidence - 0.15)
                item2.confidence = max(0.1, item2.confidence - 0.15)
    return items


def _related_categories(cat1: AdviceCategory, cat2: AdviceCategory) -> bool:
    """判断两个类别是否相关(可能产生冲突)."""
    related_groups = [
        {AdviceCategory.FORTUNE, AdviceCategory.WISDOM, AdviceCategory.ACTION},
        {AdviceCategory.WEALTH, AdviceCategory.CAREER, AdviceCategory.ACTION},
        {AdviceCategory.MARRIAGE, AdviceCategory.HOME, AdviceCategory.ACTION},
        {AdviceCategory.HEALTH, AdviceCategory.CAUTION, AdviceCategory.ACTION},
    ]
    for group in related_groups:
        if cat1 in group and cat2 in group:
            return True
    return False


def _has_conflict_keywords(text1: str, text2: str) -> bool:
    """检测两段文本是否包含冲突关键词对."""
    for word1, word2 in CONFLICT_PAIRS:
        if (word1 in text1 and word2 in text2) or (word2 in text1 and word1 in text2):
            return True
    return False


# ═══════════════════════════════════════════════════════════════════
# 5. 交叉验证
# ═══════════════════════════════════════════════════════════════════

def cross_validate(items: list[AdviceItem]) -> tuple[list[AdviceItem], float]:
    """交叉验证: 多体系内容一致才高置信度.

    策略:
    - 同类别(categories)的建议, 如果来自不同体系且内容相似, 提升置信度
    - 单体系的建议, 置信度封顶0.7
    - 返回(验证后的建议列表, 整体交叉验证度0.0-1.0)
    """
    if not items:
        return [], 0.0

    # 按类别分组
    by_category: dict[AdviceCategory, list[AdviceItem]] = {}
    for item in items:
        by_category.setdefault(item.category, []).append(item)

    validated = []
    cross_validation_count = 0
    total_count = 0

    for category, cat_items in by_category.items():
        total_count += len(cat_items)
        # 检查是否有多个不同体系的相似建议
        sources = set(item.source for item in cat_items)
        if len(sources) >= 2:
            # 多体系印证, 提升置信度
            cross_validation_count += len(cat_items)
            for item in cat_items:
                boost = min(0.15, 0.05 * (len(sources) - 1))
                item.confidence = min(1.0, item.confidence + boost)
        else:
            # 单体系, 置信度封顶0.7
            for item in cat_items:
                item.confidence = min(0.7, item.confidence)
        validated.extend(cat_items)

    cross_val_score = cross_validation_count / total_count if total_count > 0 else 0.0
    return validated, cross_val_score


# ═══════════════════════════════════════════════════════════════════
# 6. advice聚合排序
# ═══════════════════════════════════════════════════════════════════

def optimize_advice(
    items: list[AdviceItem],
    topic: str = "general",
    max_items: int = 5,
    dedup_threshold: float = 0.6,
) -> dict:
    """优化advice: 去重→冲突检测→交叉验证→排序→输出.

    Args:
        items: 原始建议列表
        topic: 主题(career/wealth/marriage/health/general)
        max_items: 最多输出几条建议
        dedup_threshold: 去重相似度阈值

    Returns:
        {
            "items": [AdviceItem.to_dict()],  # 优化后的建议列表
            "text": str,                        # 拼接后的文本(兼容旧接口)
            "stats": {                          # 统计信息
                "original_count": int,
                "final_count": int,
                "deduped_count": int,
                "conflict_count": int,
                "cross_validation_score": float,
                "avg_confidence": float,
            }
        }
    """
    original_count = len(items)

    # 1. 应用主题权重
    for item in items:
        item.weight = get_source_weight(item.source, topic)

    # 2. 去重
    items = deduplicate_advice(items, threshold=dedup_threshold)
    deduped_count = original_count - len(items)

    # 3. 冲突检测
    items = detect_conflicts(items)
    conflict_count = sum(1 for item in items if item.conflict_with)

    # 4. 交叉验证
    items, cross_val_score = cross_validate(items)

    # 5. 按综合评分排序
    items.sort(key=lambda x: x.score, reverse=True)

    # 6. 截取前max_items条
    final_items = items[:max_items]

    # 7. 拼接文本(高权重优先, 用分号分隔)
    text_parts = []
    for item in final_items:
        prefix = f"[{item.source.value}·{item.category.value}]"
        text_parts.append(f"{prefix}{item.content}")
    text = "；".join(text_parts)

    # 8. 统计
    avg_confidence = sum(item.confidence for item in final_items) / len(final_items) if final_items else 0.0

    return {
        "items": [item.to_dict() for item in final_items],
        "text": text,
        "stats": {
            "original_count": original_count,
            "final_count": len(final_items),
            "deduped_count": deduped_count,
            "conflict_count": conflict_count,
            "cross_validation_score": round(cross_val_score, 3),
            "avg_confidence": round(avg_confidence, 3),
        },
    }


# ═══════════════════════════════════════════════════════════════════
# 7. 便捷工厂函数
# ═══════════════════════════════════════════════════════════════════

def make_advice(
    content: str,
    source: AdviceSource,
    category: AdviceCategory = AdviceCategory.ACTION,
    priority: int = 3,
    direction: str = "neutral",
    confidence: float = 0.5,
) -> AdviceItem:
    """便捷创建AdviceItem."""
    return AdviceItem(
        content=content,
        source=source,
        category=category,
        priority=priority,
        direction=direction,
        confidence=confidence,
    )


__all__ = [
    "AdviceCategory", "AdviceSource", "AdviceItem",
    "SYSTEM_WEIGHTS", "SOURCE_BASE_WEIGHTS",
    "get_system_weight", "get_source_weight",
    "deduplicate_advice", "detect_conflicts", "cross_validate",
    "optimize_advice", "make_advice",
]
