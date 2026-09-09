"""陈旧测试归档目录。

这些测试在 2026-09-09 E9 审计期间被标记为 pre-existing 失败:

- test_c12_c13.py: 引用 backend/scripts/shuntian_backfill_clusters.py (已删除)
- test_m2_asset_complete_integration.py: 引用 src.tongshu.canonical.root_evaluator (已改名 root_evaluator_v2)

User 在 2026-09-09 "临时授权"下决定归档 (而非删除) 以保留历史可追溯。

pytest 默认会 collect 这个目录, 用本 conftest.py 跳过.
"""
import pytest

collect_ignore_glob = ["*.py"]
