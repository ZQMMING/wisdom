"""G3 — Safety Gate (V3.6 §22.3) + DB Sync。

渲染文本安全门：词 + 模式多层检查（§22.3 要求不能只靠关键词）。

数据来源优先级：
1. DB forbidden_terms（主）
2. Python 硬编码兜底（备用，仅当 DB 不可用时）

复合短语 + 模式，逐条对应 §22.3 类型。设计原则：
只收"确定性危险表达"，不收良性字词，避免误伤合规中文输出（金样
Stub / 真实 LLM 合规输出均不命中）。

依赖：re 标准库 + result.py + psycopg2（可选）

Version: 1.0.0 → 1.1.0 (DB-sync)
Created: 2026-08-20 (Phase 2 / Step 8)
Updated: 2026-08-22 (G3 DB sync)
Migrated from: audit/gates.py:142-167 (_FORBIDDEN_PATTERNS + _FORBIDDEN_WORDS + safety_gate)
"""

from __future__ import annotations

import re
from typing import Optional

from .result import GateResult


# ── Python 硬编码兜底（DB 不可用时启用） ──────────────────────────
_FALLBACK_PATTERNS: list[tuple[str, str]] = [
    (r"稳赚|包赚|稳赚不赔|必涨|保本", "financial guarantee"),
    (r"保证.{0,4}(收益|回报|赚钱|涨|盈利)", "financial guarantee"),
    (r"包治|根治|保证.{0,4}(康复|痊愈)|诊断.{0,4}(疾病|重病)", "medical claim"),
    (r"必定|必然[会]?|命中注定|绝对会|肯定会|一定.{0,3}会", "deterministic prediction"),
    (r"大祸|血光|必有灾|灾祸必|大难|不越之兆|劫数", "fear induction"),
    (r"你必须|你务必|你只能|非做不可|万万不能|绝不能", "coercive guidance"),
    (r"[0-9０-９]+[%％].{0,3}(\u53ef\u80fd|\u4f1a|\u6982\u7387)", "probability claim"),
]

_FALLBACK_WORDS: list[str] = ["建议买入", "肯定赚钱", "明天会跌", "保证收益"]


def _load_patterns_from_db() -> list[tuple[str, str]]:
    """从 shuntian_kb.forbidden_terms 加载活跃模式。
    
    Returns:
        list of (regex_pattern, category) tuples, or empty list if DB unavailable.
    """
    try:
        import sys
        sys.path.insert(0, 'backend/src')
        from tongshu.db.config import get_kb_dsn
        import psycopg2

        dsn = get_kb_dsn()
        with psycopg2.connect(dsn) as co:
            cr = co.cursor()
            cr.execute("SELECT current_database()")
            _db = cr.fetchone()[0]
            if _db != "shuntian_kb":
                raise RuntimeError(f"Expected shuntian_kb, connected to {_db}")
            cr.execute("""
                SELECT term_pattern, category
                FROM forbidden_terms
                WHERE status='ACTIVE'
                ORDER BY category, term_id
            """)
            rows = cr.fetchall()
            return [(row[0], row[1]) for row in rows]
    except Exception:
        return []


# 延迟加载模式
_patterns_cache: Optional[list[tuple[str, str]]] = None
_patterns_loaded_from_db: bool = False


def _get_patterns() -> tuple[list[tuple[str, str]], bool]:
    """获取当前使用的模式列表。优先 DB，降级 Python 兜底。
    
    Returns:
        (patterns, used_db) - patterns 是 [(regex, category)]，used_db 表示是否来自 DB
    """
    global _patterns_cache, _patterns_loaded_from_db
    
    if _patterns_cache is None:
        db_patterns = _load_patterns_from_db()
        if db_patterns:
            _patterns_cache = db_patterns
            _patterns_loaded_from_db = True
        else:
            _patterns_cache = _FALLBACK_PATTERNS
            _patterns_loaded_from_db = False
    
    return _patterns_cache, _patterns_loaded_from_db


def safety_gate(rendered_text: str) -> GateResult:
    """渲染文本安全门：词 + 模式多层检查。
    
    Args:
        rendered_text: 待检查的渲染文本
    
    Returns:
        GateResult with pass/fail status and violation reasons
    """
    text = rendered_text or ""
    reasons: list[str] = []
    
    patterns, used_db = _get_patterns()
    
    # 检查复合模式
    for pat, kind in patterns:
        m = re.search(pat, text)
        if m:
            reasons.append(f"forbidden {kind}: {m.group(0)!r}")
    
    # 如果来自 DB，也检查禁词（DB 可能未包含所有禁词）
    if used_db:
        for word in _FALLBACK_WORDS:
            if word in text:
                reasons.append(f"forbidden word: {word}")
    
    return GateResult("G3", not reasons, reasons)


__all__ = ["safety_gate"]
