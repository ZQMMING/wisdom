"""G2 — Translation Gate (V3.6 §22.2)。

词库标签链完整性：claim 的 mapping_refs 必须能在 registry 解析，
modern_theme 与 mapping_refs 必须成对出现且与 registry 记录一致。

特别说明：registry 为 None（词库层未配置）时，跳过解析类检查 —
“没有可标的链”。

依赖：result.py。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 8)
Migrated from: audit/gates.py:103-138
"""

from __future__ import annotations

from .result import GateResult


def translation_gate(sir: dict, registry=None) -> GateResult:
    """G2 词库标签链完整性检查。"""
    reasons: list[str] = []
    claims = sir.get("atomic_claims", []) or []
    for c in claims:
        cid = c.get("claim_id", "") or "?"
        refs = c.get("mapping_refs")
        theme = c.get("modern_theme")
        if refs:
            if registry is not None:
                for mid in refs:
                    entry = registry.get(mid)
                    if entry is None:
                        reasons.append(f"{cid}: mapping_id {mid} not in registry (mapping_id exists)")
                # modern_theme 是 claim 级聚合标签，取 mapping_refs 排序后首条的
                # modern_theme（apply_to_claims 的 deterministic 契约）。因此只与
                # 首条比对；其余 ref 仅需解析存在。
                if theme is not None:
                    first = registry.get(refs[0])
                    if first is not None and theme != first.get("modern_theme"):
                        reasons.append(
                            f"{cid}: modern_theme {theme!r} != first mapping "
                            f"{refs[0]} registry {first.get('modern_theme')!r} (source concept matches)"
                        )
            if not theme:
                reasons.append(f"{cid}: mapping_refs present but modern_theme missing")
        elif theme is not None:
            reasons.append(f"{cid}: modern_theme present but mapping_refs missing")
    return GateResult("G2", not reasons, reasons)


__all__ = ["translation_gate"]
