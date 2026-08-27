"""Pipeline Stages — TONGSHUPipeline 的 4 个 Stage 子模块。

按 pipeline-blueprint.md §2 设计：

    TONGSHUPipeline（薄编排）
        ├── ComputeStage       阶段 1-6: 计算 + SIR 构造
        ├── RenderStage        阶段 7-8: 渲染 + fallback
        ├── ValidationStage    阶段 9:   3 层 + 4 Gate + fail-closed
        └── AuditComposer      阶段 10:  审计日志组装

Stage 间通过 tongshu.types 中的 frozen dataclass（ComputeResult /
RenderStageResult / ValidationStageResult）传递数据，避免循环 import。

本模块不引入新公共 API；所有调用方继续从 tongshu.pipeline 导入
TONGSHUPipeline / PipelineResult。Stage 是 pipeline 的内部实现细节。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 3)
"""

from .compute_stage import ComputeStage
from .render_stage import RenderStage
from .validation_stage import ValidationStage
from .audit_composer import AuditComposer

__all__ = [
    "ComputeStage",
    "RenderStage",
    "ValidationStage",
    "AuditComposer",
]
