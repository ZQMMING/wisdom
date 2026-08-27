"""Snapshot Engine - 计算快照管理"""

from __future__ import annotations
from .models import CalculationSnapshot
from .repository import get_snapshot_store, SnapshotRepository


class SnapshotManager:
    """快照管理器"""
    
    def __init__(self, repository: SnapshotRepository | None = None):
        self._repo = repository or get_snapshot_store()
    
    async def save_snapshot(self, snapshot: CalculationSnapshot) -> uuid.UUID:
        """保存快照，返回 snapshot_id"""
        return await self._repo.save(snapshot)
    
    async def get_snapshot(self, snapshot_id: uuid.UUID) -> CalculationSnapshot | None:
        """获取快照"""
        return await self._repo.get(snapshot_id)
    
    async def list_snapshots(
        self,
        user_id: uuid.UUID | None = None,
        limit: int = 100,
    ) -> list[CalculationSnapshot]:
        """列出快照"""
        if user_id:
            # TODO: 实现按用户过滤
            return []
        return await self._repo.list_by_user(uuid.UUID("00000000-0000-0000-0000-000000000000"), limit)


async def create_calculation_snapshot(
    profile_snapshot,
    heluo_result,
    interpretation_result=None,
) -> CalculationSnapshot:
    """便捷函数：创建完整计算快照"""
    return CalculationSnapshot(
        profile_snapshot=profile_snapshot,
        heluo_result=heluo_result,
        interpretation_result=interpretation_result,
    )
