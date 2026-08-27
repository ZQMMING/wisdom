"""Snapshot 持久化层（占位实现）

完整实现需要 PostgreSQL + SQLAlchemy
"""

from __future__ import annotations
from typing import Protocol
from .models import CalculationSnapshot


class SnapshotRepository(Protocol):
    """快照仓库接口"""
    
    async def save(self, snapshot: CalculationSnapshot) -> uuid.UUID: ...
    async def get(self, snapshot_id: uuid.UUID) -> CalculationSnapshot | None: ...
    async def list_by_user(self, user_id: uuid.UUID, limit: int = 100) -> list[CalculationSnapshot]: ...


class InMemorySnapshotStore:
    """内存存储（测试用）"""
    
    def __init__(self):
        self._store: dict[uuid.UUID, CalculationSnapshot] = {}
    
    async def save(self, snapshot: CalculationSnapshot) -> uuid.UUID:
        errors = snapshot.validate()
        if errors:
            raise ValueError(f"快照验证失败: {errors}")
        self._store[snapshot.snapshot_id] = snapshot
        return snapshot.snapshot_id
    
    async def get(self, snapshot_id: uuid.UUID) -> CalculationSnapshot | None:
        return self._store.get(snapshot_id)
    
    async def list_by_user(self, user_id: uuid.UUID, limit: int = 100) -> list[CalculationSnapshot]:
        return list(self._store.values())[:limit]


# 全局单例
_store = InMemorySnapshotStore()


def get_snapshot_store() -> InMemorySnapshotStore:
    return _store
