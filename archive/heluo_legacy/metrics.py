"""S5-04: 解释引擎评估指标

评估指标体系：
1. 古籍一致性 (classical_consistency)
2. 解释质量 (interpretation_quality)
3. 证据闭合度 (evidence_closure)
4. 可追溯性 (traceability)
"""
from __future__ import annotations
import json
import logging
import psycopg2
from dataclasses import dataclass, field
from typing import Optional

from tongshu.db.config import get_kb_dsn

log = logging.getLogger(__name__)


@dataclass
class InterpretationMetrics:
    """解释引擎评估指标。"""
    # 古籍一致性 (0-1)
    classical_consistency: float = 0.0
    # 解释质量 (0-1)
    interpretation_quality: float = 0.0
    # 证据闭合度 (0-1)
    evidence_closure: float = 0.0
    # 可追溯性 (0-1)
    traceability: float = 0.0
    # 综合评分 (0-1)
    overall_score: float = 0.0
    
    # 评估详情
    strengths: list = field(default_factory=list)
    weaknesses: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)


def evaluate_interpretation(
    interpretation_output: dict,
    classical_source: Optional[dict] = None,
    evidence_chain: Optional[list] = None
) -> InterpretationMetrics:
    """评估解释引擎输出。"""
    metrics = InterpretationMetrics()
    
    # 1. 古籍一致性评估
    if classical_source:
        metrics.classical_consistency = evaluate_classical_consistency(
            interpretation_output, classical_source
        )
    
    # 2. 解释质量评估
    metrics.interpretation_quality = evaluate_interpretation_quality(interpretation_output)
    
    # 3. 证据闭合度评估
    if evidence_chain:
        metrics.evidence_closure = evaluate_evidence_closure(evidence_chain)
    else:
        metrics.evidence_closure = 0.5  # 默认中等
    
    # 4. 可追溯性评估
    metrics.traceability = evaluate_traceability(interpretation_output)
    
    # 5. 综合评分（加权平均）
    metrics.overall_score = (
        metrics.classical_consistency * 0.30 +
        metrics.interpretation_quality * 0.25 +
        metrics.evidence_closure * 0.25 +
        metrics.traceability * 0.20
    )
    
    return metrics


def evaluate_classical_consistency(
    interpretation: dict,
    classical_source: dict
) -> float:
    """评估与古籍原文的一致性。"""
    score = 0.0
    
    # 检查是否引用了正确的古籍
    refs = interpretation.get('interpretation_chain', [])
    cited_sources = [r.get('source', '') for r in refs]
    
    if classical_source.get('book_name') in cited_sources:
        score += 0.3
    
    # 检查原文关键术语
    original_text = classical_source.get('original_text', '')
    if original_text and len(original_text) > 10:
        # 简单检查：解释中是否包含原文关键词
        keywords = extract_keywords(original_text)
        matched = sum(1 for kw in keywords if kw in str(interpretation))
        if matched > 0:
            score += 0.2 * (matched / len(keywords))
    
    # 检查算法版本
    version = interpretation.get('meta', {}).get('algorithm_version', '')
    if 'V1' in version or 'V0' in version:
        score += 0.2
    
    return min(score, 1.0)


def evaluate_interpretation_quality(interpretation: dict) -> float:
    """评估解释质量。"""
    score = 0.0
    
    # 检查必需字段
    required_fields = ['current_state', 'opportunity', 'risk', 'recommended_action']
    present = sum(1 for f in required_fields if f in interpretation)
    score += 0.3 * (present / len(required_fields))
    
    # 检查解释链完整性
    chain = interpretation.get('interpretation_chain', [])
    if len(chain) >= 3:
        score += 0.25
    elif len(chain) >= 1:
        score += 0.1
    
    # 检查置信度
    meta = interpretation.get('meta', {})
    confidence = meta.get('confidence_score', 0)
    if confidence >= 0.7:
        score += 0.25
    elif confidence >= 0.5:
        score += 0.15
    
    # 检查警告信息
    warnings = interpretation.get('warnings', [])
    if len(warnings) == 0:
        score += 0.2
    elif len(warnings) <= 2:
        score += 0.1
    
    return min(score, 1.0)


def evaluate_evidence_closure(evidence_chain: list) -> float:
    """评估证据闭合度。"""
    if not evidence_chain:
        return 0.5
    
    total = len(evidence_chain)
    verified = sum(1 for e in evidence_chain if e.get('verified', False))
    
    return verified / total if total > 0 else 0.5


def evaluate_traceability(interpretation: dict) -> float:
    """评估可追溯性。"""
    score = 0.0
    
    # 检查解释链
    chain = interpretation.get('interpretation_chain', [])
    if len(chain) >= 5:
        score += 0.3
    elif len(chain) >= 3:
        score += 0.2
    
    # 检查每个步骤是否有来源引用
    with_source = sum(1 for step in chain if step.get('source'))
    if with_source > 0:
        score += 0.3 * (with_source / len(chain))
    
    # 检查meta信息
    meta = interpretation.get('meta', {})
    if meta.get('algorithm_version') and meta.get('confidence_score'):
        score += 0.2
    
    # 检查证据引用
    evidence_refs = meta.get('evidence_refs', [])
    if len(evidence_refs) >= 2:
        score += 0.2
    
    return min(score, 1.0)


def extract_keywords(text: str, max_keywords: int = 5) -> list:
    """提取关键词。"""
    # 简单实现：按标点分割，取长度>=2的词语
    import re
    words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
    return list(set(words))[:max_keywords]


def compute_dataset_metrics(conn) -> dict:
    """计算整个数据集的评估指标。"""
    cur = conn.cursor()
    stats = {}
    
    # 统计 heluo_golden_cases
    cur.execute("SELECT COUNT(*) FROM heluo_golden_cases")
    total = cur.fetchone()[0]
    
    cur.execute("SELECT AVG(classical_consistency) FROM heluo_golden_cases")
    avg_consistency = cur.fetchone()[0] or 0
    
    cur.execute("SELECT COUNT(*) FROM heluo_golden_cases WHERE status = 'approved'")
    approved = cur.fetchone()[0]
    
    stats["total_cases"] = total
    stats["approved_cases"] = approved
    stats["approval_rate"] = approved / total if total > 0 else 0
    stats["avg_classical_consistency"] = float(avg_consistency) if avg_consistency else 0
    
    # 统计 classical_sources
    cur.execute("SELECT COUNT(*) FROM classical_sources WHERE verification_status = 'verified'")
    verified_sources = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM classical_sources")
    total_sources = cur.fetchone()[0]
    
    stats["verified_sources"] = verified_sources
    stats["total_sources"] = total_sources
    stats["source_verification_rate"] = verified_sources / total_sources if total_sources > 0 else 0
    
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = psycopg2.connect(get_kb_dsn())
    with conn.cursor() as _cur:
        _cur.execute("SELECT current_database()")
        _db = _cur.fetchone()[0]
        if _db != "shuntian_kb":
            raise RuntimeError(f"Expected shuntian_kb, connected to {_db}")
    try:
        metrics = compute_dataset_metrics(conn)
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    finally:
        conn.close()
