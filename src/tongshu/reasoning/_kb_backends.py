"""KbLoader 的双源 backend 封装。

原本 KbLoader 中的 JSON 加载与索引逸在 KbLoader.__init__ 中，
本模块将其抽象为 JsonKbBackend（shuntian_kb Postgres 未上线前的唯一后端）。

PostgresKbBackend 为占位。实际上线时需 Claude C6 交付 KbPostgresAdapter 后再启用。

依赖：无。

Version: 1.0.0  Created: 2026-08-20 (Phase 2 / Step 2)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

log = logging.getLogger(__name__)


class _JsonKbBackend:
    """KbLoader 的 JSON 后端实现。

    加载 data/knowledge/*.json + 按 docs/knowledge.schema.json (v2.0) 校验，
    构建 id → record 索引。
    """

    def __init__(self, data_dir: Path, schema_dir: Path) -> None:
        try:
            from jsonschema import Draft202012Validator
        except ImportError as e:  # pragma: no cover - 环境问题
            raise RuntimeError("jsonschema is required for KbLoader (json)") from e

        self._kb_dir = Path(data_dir) / "knowledge"
        self._schema = json.loads(
            (Path(schema_dir) / "knowledge.schema.json").read_text(encoding="utf-8")
        )
        self._validator = Draft202012Validator(self._schema)

        # 避免微软环圍依赖（避免在本文件顶部 import knowledge_base 产生环状）
        from .knowledge_base import _ENTITY_TYPES, _ID_FIELD

        self._entities: dict[str, list[dict]] = {}
        self._index: dict[str, dict[str, dict]] = {}
        for t in _ENTITY_TYPES:
            self._load_file(t)
            self._index[t] = {rec[_ID_FIELD[t]]: rec for rec in self._entities[t]}

    def _load_file(self, entity_type: str) -> None:
        from .knowledge_base import _ENTITY_TYPES, _ENTITY_FILE, KnowledgeLoadError

        if entity_type not in _ENTITY_TYPES:
            raise KeyError(f"unknown entity_type: {entity_type}")
        path = self._kb_dir / _ENTITY_FILE[entity_type]
        if not path.is_file():
            raise KnowledgeLoadError(f"knowledge file missing: {path}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        errs = sorted(self._validator.iter_errors(raw), key=lambda e: list(e.path))
        if errs:
            raise KnowledgeLoadError(f"{path.name}: schema invalid — {errs[0].message}")
        if raw.get("kind") != entity_type:
            raise KnowledgeLoadError(
                f"{path.name}: kind mismatch — expected {entity_type!r}, got {raw.get('kind')!r}"
            )
        self._entities[entity_type] = raw.get("items", [])

    # ----- properties -----
    @property
    def books(self) -> list[dict]:
        return list(self._entities["book"])

    @property
    def editions(self) -> list[dict]:
        return list(self._entities["edition"])

    @property
    def source_copies(self) -> list[dict]:
        return list(self._entities["source_copy"])

    @property
    def chapters(self) -> list[dict]:
        return list(self._entities["chapter"])

    @property
    def passages(self) -> list[dict]:
        return list(self._entities["passage"])

    @property
    def concepts(self) -> list[dict]:
        return list(self._entities["concept"])

    @property
    def principles(self) -> list[dict]:
        return list(self._entities["principle"])

    # ----- methods -----
    def ids(self, entity_type: str) -> set[str]:
        return set(self._index[entity_type])

    def get(self, entity_type: str, entity_id: str) -> dict | None:
        return self._index[entity_type].get(entity_id)

    def counts(self) -> dict[str, int]:
        from .knowledge_base import _ENTITY_TYPES
        return {t: len(self._entities[t]) for t in _ENTITY_TYPES}


class _PostgresKbBackend:
    """KbLoader 的 Postgres 后端占位。

    待 Claude C6 交付 KbPostgresAdapter 后启用。目前代表“未实现”。

    所有方法都会 NotImplementedError，以防静默返回空数据。
    """

    def __init__(self, *_args, **_kwargs) -> None:
        self._ready = False  # 交付后翻转

    @property
    def _unavailable(self) -> str:
        return (
            "PostgresKbBackend 尚未实现：等 Claude C6 KbPostgresAdapter "
            "交付后启用。"
        )

    @property
    def books(self):
        raise NotImplementedError(self._unavailable)

    @property
    def editions(self):
        raise NotImplementedError(self._unavailable)

    @property
    def source_copies(self):
        raise NotImplementedError(self._unavailable)

    @property
    def chapters(self):
        raise NotImplementedError(self._unavailable)

    @property
    def passages(self):
        raise NotImplementedError(self._unavailable)

    @property
    def concepts(self):
        raise NotImplementedError(self._unavailable)

    @property
    def principles(self):
        raise NotImplementedError(self._unavailable)

    def ids(self, entity_type: str):
        raise NotImplementedError(self._unavailable)

    def get(self, entity_type: str, entity_id: str):
        raise NotImplementedError(self._unavailable)

    def counts(self):
        raise NotImplementedError(self._unavailable)
