"""Evidence Index — G0-1 基础设施（BZ-FNDR-15.11 §1.4 契约）。

证据语料身份治理层。生产 Evidence Loader 不再以"目录扫描本身"作为证据事实来源，
而是消费本 Index。本模块只负责【身份/可见性/定位】，不负责【权威/核验判定】
（后者属 G0-2 Resolved Provenance，见 provenance_resolver.py）。

已锁定契约（15.11）:
    Stable Resource ID
      + Logical URI
      + Project-relative Path
      + Runtime Resolver
      + Provenance Resolution(钩子, 交由 G0-2)

Corpus 分层（User 2026-09-10 裁决 C1a）:
    data/evidence/        = Evidence Corpus Base（唯一语料事实来源）
    backend/data/evidence = Legacy / Visibility Snapshot（生产可见性快照, 非事实来源）

红线（15.11 §1.3 禁止项, 本模块永久遵守）:
    ❌ 禁止把 backend/data/evidence 当作 Evidence Truth
    ❌ 禁止 rglob("*.json") 后把"找到文件"当成"建立了 Evidence Index"
    ❌ Stable Resource ID ≠ 文件系统路径（换机/迁移/重定位不得改变 Identity）

P0 路径独立性红线（scripts/path_independency_audit.py）:
    本模块不硬编码任何开发机绝对路径。Corpus 根由参数注入
    （默认经 repo-relative 定位, 或 Runtime Resolver / settings.data_root）。
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set, Tuple

log = logging.getLogger(__name__)

# 名称级预排除（15.10 §6 非资源清单的前段）：manifest / reports。
# 其余非资源（provenance_* / *_summary / _insufficient_source / topic_correction_log /
# reclassification_matrix）由 _register 的内容判定（无 evidence_id）统一兜住,
# 与 15.10 对账的判定式保持一致。
_NON_RESOURCE_BASENAMES: Set[str] = {"manifest.json"}
_EXCLUDED_DIR_PARTS: Set[str] = {"reports"}

_SCHEMA6_REQUIRED = (
    "evidence_id",
    "rule_refs",
    "citation",
    "source_layer",
    "evidence_strength",
    "version",
)

# Logical URI 规范（Stable Identity 的字符串形态, 与文件系统路径解耦）
_LOGICAL_URIS = "evid://"


@dataclass(frozen=True)
class ResourceIdentity:
    """稳定的证据资源身份 —— 不随文件系统路径变化。

    resource_id:  资源逻辑 ID（= 资源文件内的 evidence_id, 当存在且唯一时）。
    logical_uri:  规范 URI（evid://<tree>/<relative_path>），跨部署稳定。
    relative_path: 相对 corpus 根的 POSIX 路径（跨 OS 稳定, 不用本地 sep）。
    tree:          corpus base / legacy snapshot。
    """

    resource_id: str
    logical_uri: str
    relative_path: str
    tree: str

    @property
    def key(self) -> Tuple[str, str]:
        """身份键：(tree, relative_path) —— 同一 relative_path 在不同 tree 视为不同实例。"""
        return (self.tree, self.relative_path)


@dataclass
class EvidenceIndex:
    """证据语料索引。

    由 corpus 根目录显式构建（非 rglob 黑盒）；按 Resource Identity 组织。
    一个 evidence_id 可能对应多个 relative_path（15.10 §2 的 12 组同 ID 多文件 /
    根级-子目录双份）—— 因此 Index 以 relative_path 为资源实例键, 以 evidence_id
    为逻辑分组键, 显式保留"ID → 多实例"（不强行 1:1）。
    """

    corpus_root: Path
    tree: str
    # relative_path(ResourceIdentity.relative_path) -> ResourceIdentity
    by_relpath: Dict[str, ResourceIdentity] = field(default_factory=dict)
    # evidence_id -> [relative_path, ...]   (保持 ID → 多实例 的可见性, 不折叠)
    by_evidence_id: Dict[str, List[str]] = field(default_factory=dict)
    # relative_path -> schema6 合规性
    schema_compliant: Dict[str, bool] = field(default_factory=dict)
    # relative_path -> 原始 verification_status 字段保留（顶层 + 嵌套）
    raw_top_status: Dict[str, str] = field(default_factory=dict)
    raw_cit_status: Dict[str, str] = field(default_factory=dict)
    # authority_type / source_layer 原值保留（15.11 §3 Resolved Provenance 输入面,
    # G0-2 消费；本层不判定权威, 只原样携带）
    raw_authority: Dict[str, str] = field(default_factory=dict)
    raw_source_layer: Dict[str, str] = field(default_factory=dict)
    # 非资源/不可解析 文件登记（内容判定或解析失败, 不入 Index, 供审计计数）
    _excluded: Dict[str, str] = field(default_factory=dict)

    # ---- 构建 ----
    @classmethod
    def build(
        cls,
        corpus_root: Path,
        tree: str = "corpus_base",
        resource_globs: Optional[List[str]] = None,
    ) -> "EvidenceIndex":
        """从 corpus 根显式构建 Index。

        resource_globs: 可选, 显式登记要纳入的资源文件模式（相对 root）。
        缺省 = 该 tree 下所有 *.json, 但按 _is_excluded 排除非证据资源。
        这不是 rglob 黑盒事实来源：排除规则 + Identity 规范化是 Index 契约的一部分。
        """
        corpus_root = Path(corpus_root)
        idx = cls(corpus_root=corpus_root, tree=tree)

        if resource_globs is None:
            candidates = sorted(p for p in corpus_root.rglob("*.json") if p.is_file())
        else:
            candidates: List[Path] = []
            for g in resource_globs:
                candidates.extend(corpus_root.glob(g))
            candidates = sorted(set(candidates))

        for p in candidates:
            rel_posix = p.relative_to(corpus_root).as_posix()
            if cls._is_excluded(rel_posix, p.name):
                continue
            data = cls._safe_load(p)
            if data is None:
                # 解析失败: 记录为"存在但不可解析", 不静默丢弃, 也不误判为非资源
                idx._excluded[rel_posix] = "parse_error"
                continue
            idx._register(rel_posix, data, tree)
        return idx

    @staticmethod
    def _is_excluded(rel_posix: str, name: str) -> bool:
        """名称级预排除（15.10 §6 登记的 manifest / reports 段, 内容判定前的快速面）。"""
        if name in _NON_RESOURCE_BASENAMES:
            return True
        parts = rel_posix.split("/")
        if any(part in _EXCLUDED_DIR_PARTS for part in parts[:-1]):
            return True
        return False

    @staticmethod
    def _safe_load(p: Path) -> Optional[dict]:
        try:
            with open(p, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception as e:  # noqa: BLE001 — Index 层不硬抛, 降级为解析失败并告警
            log.warning("EvidenceIndex: unparseable %s (%s)", p, e)
            return None

    def _register(self, rel_posix: str, data: dict, tree: str) -> None:
        """内容级非资源判定（15.10 对账精确判定式：无 evidence_id = 非证据资源）。

        15.10 §1 树A 1588 / 树B 5693 的"证据文件"数 = 该判定式下的计数,
        本 Index 与其审计记录保持一致。
        """
        if not data or data.get("evidence_id") is None:
            # 非资源文件（provenance_*/_summary/reports/manifest 等）：不入 Index,
            # 由 summary 的 excluded_count 计数, 不静默丢弃。
            self._excluded[rel_posix] = "no_evidence_id"
            return
        schema_ok = all(k in data for k in _SCHEMA6_REQUIRED)
        eid = data.get("evidence_id")
        eid_key = str(eid) if eid is not None else ""
        cit = data.get("citation")
        cit_status = cit.get("verification_status") if isinstance(cit, dict) else None

        identity = ResourceIdentity(
            resource_id=eid_key or rel_posix,
            logical_uri=f"{_LOGICAL_URIS}{tree}/{rel_posix}",
            relative_path=rel_posix,
            tree=tree,
        )
        self.by_relpath[rel_posix] = identity
        self.schema_compliant[rel_posix] = schema_ok
        self.raw_top_status[rel_posix] = (
            str(data.get("verification_status")) if "verification_status" in data else "<MISSING>"
        )
        self.raw_cit_status[rel_posix] = (
            str(cit_status) if cit_status is not None else "<MISSING>"
        )
        self.raw_authority[rel_posix] = (
            str(data.get("authority_type")) if "authority_type" in data else "<MISSING>"
        )
        self.raw_source_layer[rel_posix] = (
            str(data.get("source_layer")) if "source_layer" in data else "<MISSING>"
        )
        if eid_key:
            self.by_evidence_id.setdefault(eid_key, []).append(rel_posix)

    # ---- 查询 ----
    def get(self, relative_path: str) -> Optional[ResourceIdentity]:
        return self.by_relpath.get(relative_path)

    def resolve(self, logical_uri: str) -> Optional[Path]:
        """Runtime Resolver：Logical URI -> 部署内实际路径（Identity 与物理位置解耦）。"""
        m = re.match(r"^evid://[^/]+/(.+)$", logical_uri)
        if not m:
            return None
        rel = m.group(1)
        return self.corpus_root / rel if rel in self.by_relpath else None

    def instances_of(self, evidence_id: str) -> List[ResourceIdentity]:
        """ID -> 多实例（保留 15.10 §2 的同 ID 多文件事实, 不强行折叠）。"""
        return [self.by_relpath[r] for r in self.by_evidence_id.get(str(evidence_id), [])]

    def iter(self) -> Iterator[ResourceIdentity]:
        return iter(self.by_relpath.values())

    def iter_compliant(self) -> Iterator[ResourceIdentity]:
        for rid, ok in self.schema_compliant.items():
            if ok:
                yield self.by_relpath[rid]

    def iter_noncompliant(self) -> Iterator[ResourceIdentity]:
        for rid, ok in self.schema_compliant.items():
            if not ok:
                yield self.by_relpath[rid]

    # ---- 统计 ----
    def summary(self) -> dict:
        total = len(self.by_relpath)
        compliant = sum(1 for v in self.schema_compliant.values() if v)
        dup_ids = {k: v for k, v in self.by_evidence_id.items() if len(v) > 1}
        return {
            "tree": self.tree,
            "corpus_root": str(self.corpus_root),
            "total_resources": total,
            "schema_compliant": compliant,
            "schema_noncompliant": total - compliant,
            "unique_evidence_ids": len(self.by_evidence_id),
            "multi_instance_ids": dup_ids,
            "excluded_non_resource": len(self._excluded),
        }

    def iter_raw_statuses(self) -> Iterator[Dict[str, str]]:
        """供 G0-2 Resolved Provenance 消费：逐资源产出原始（未覆盖）status + 权威面。"""
        for rel in self.by_relpath:
            yield {
                "relative_path": rel,
                "raw_top_verification_status": self.raw_top_status.get(rel, "<MISSING>"),
                "raw_citation_verification_status": self.raw_cit_status.get(rel, "<MISSING>"),
                "raw_authority_type": self.raw_authority.get(rel, "<MISSING>"),
                "raw_source_layer": self.raw_source_layer.get(rel, "<MISSING>"),
            }
