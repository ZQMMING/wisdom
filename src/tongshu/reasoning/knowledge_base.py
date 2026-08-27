"""KbLoader — Knowledge Base(五部经典)加载 + 链接闭合(P1-01 D1 + M1 Edition Registry + SOURCE_COPY)。

data/knowledge/{books,editions,source_copies,chapters,passages,concepts,principles}.json 是
§8.2-8.6 Knowledge Base 的权威登记,经 docs/knowledge.schema.json(v2.0)校验
加载(格式错误硬报错,绝不静默——与 RuleLoader T203 同策略)。

verify_link_closure() 闭合 §8.2 链跨引用(UR-011 的 KB 扩展;M1 增 ED-V + SOURCE_COPY):
    passage.book_id        -> book 存在
    passage.chapter_id     -> chapter 存在(同书)
    passage.edition_id     -> edition 存在(同书,ED-V-1)
    passage.source_copy_id -> source_copy 存在且 edition 与 passage.edition_id 一致(M1 可扩展,字段存在才查)
    concept.source_refs    -> book 存在
    principle.book_refs    -> book 存在
    principle.passage_refs -> passage 存在
    edition.book_id        -> book 存在(ED-V-1)
    edition_id 全局唯一(ED-V-1)
    edition.source_copies  -> 每条 source_copy 存在且 edition 一致(M1 可扩展,字段存在才查)
    book.pinned_edition_id -> edition 存在且同书;pinned 每书至多 1 条(ED-V-2/3)
    layer_structure 键 ⊆ 五层且含 classical_original;commentator 非空 ⇔ commentary 层(ED-V-4/5)
    source_copy.edition_id -> edition 存在
    rule.book_id / passage_id / concept_id / principle_id(仅当字段存在时)
                             -> KB 对应实体存在

经典原文纪律:待校 passage 的 original_text 为空、只放 paraphrase,禁止虚构。
SOURCE_COPY 纪律:具体出版社/年份/页码/副本未经双源核验一律 pending_verification,严禁模型推断写入 verified。
"""

from __future__ import annotations
import json
import logging
from pathlib import Path

from jsonschema import Draft202012Validator

log = logging.getLogger(__name__)

_ENTITY_TYPES = ("book", "edition", "source_copy", "chapter", "passage", "concept", "principle")
_ENTITY_FILE = {
    "book": "books.json",
    "edition": "editions.json",
    "source_copy": "source_copies.json",
    "chapter": "chapters.json",
    "passage": "passages.json",
    "concept": "concepts.json",
    "principle": "principles.json",
}
_ID_FIELD = {
    "book": "book_id",
    "edition": "edition_id",
    "source_copy": "source_copy_id",
    "chapter": "chapter_id",
    "passage": "passage_id",
    "concept": "concept_id",
    "principle": "principle_id",
}

_ALLOWED_LAYERS = {
    "classical_original", "commentary", "paraphrase",
    "engineering_seed", "secondary_reference",
}

# M2-A: V-5L(KB_VALIDATION_SPEC §3)与 S1 反链校验的辅助常量
_VERIFIED_STATES = {"verified", "cross_verified"}
_PENDING_STATE = "pending_verification"
_PENDING_PREFIX = "(待校,paraphrase)"
# V-5L ④:评注不得混入 classical_original.text——注解者/评注标志
_COMMENTARY_MARKERS = ("任铁樵", "徐乐吾", "沈孝瞻注", "原注", "眉批", "增补编者", "万民英注")
# 旧 v1/v2.0 passage 顶层的遗留字段(五层化后已不存在)
_LEGACY_PASSAGE_TOP_FIELDS = ("original_text", "normalized_text", "verification")
_LEGACY_VERIFICATION_VALUES = ("待校",)
# 工程种子证据不填 edition_id(引文来自 spec/工程,非经典版本)
_NO_EDITION_EVIDENCE = {
    "E-ZPZ-001-001", "E-ZPZ-002-001", "E-ZPZ-003-001",
    "E-ZPZ-004-001", "E-ZPZ-005-001", "E-QTB-014-001",
    "E-ZIWEI-001", "E-ZW-405-001", "E-ZW-406-001",
    "E-ZW-407-001", "E-ZW-408-001",
    # KB link closure(2026-08-26):TF 引"意象派国学字幕"视频观点,非经典版本文本 → 工程种子
    "E-TF-101-001", "E-TF-102-001",
}

# M2-B:Evidence Review Queue verdict ↔ evidence.citation.verification_status 一致性。
# verdict=blank 表示证据未填 verification_status(工程种子留空,诚实)。
_QUEUE_VERDICT_TO_EVIDENCE_STATUS = {
    "verified": "verified",
    "cross_verified": "cross_verified",
    "pending_verification": "pending_verification",
    "disputed": "disputed",
    "not_applicable": "not_applicable",
    "blank": None,
}


class KnowledgeLoadError(RuntimeError):
    """Raised when a knowledge record fails schema validation or file shape is wrong."""


class KbLoader:
    """五部经典知识库加载器（façade 模式）。

    Args:
        data_dir: 传统 JSON 数据目录（必填。即使 source='postgres'，
            也保留作为异地落地归档。
        schema_dir: 文档 schema 目录（必填：json 路径校验使用）。
        source: 数据源选择。
            - "json"（默认）：加载 backend/data/knowledge/*.json（原行为不变）
            - "postgres"：shuntian_kb Postgres 表（等 Claude C6 KbPostgresAdapter 交付）

    公共接口 100% 向后兼容：未传 source 时与原 KbLoader 行为完全一致。
    """

    def __init__(
        self,
        data_dir: Path,
        schema_dir: Path,
        source: str = "json",
    ) -> None:
        if source == "json":
            from ._kb_backends import _JsonKbBackend
            self._backend = _JsonKbBackend(data_dir, schema_dir)
        elif source == "postgres":
            from ._kb_backends import _PostgresKbBackend
            self._backend = _PostgresKbBackend()
        else:
            raise ValueError(
                f"unknown KbLoader source: {source!r} (expected 'json' | 'postgres')"
            )
        # 同步保留原字段以兼容可能被使用的内部代码
        self._kb_dir = Path(data_dir) / "knowledge"
        self._schema_dir = Path(schema_dir)
        self._source = source

    # ------------------------------------------------------------------ #
    # 送差代理（façade 模式）—所有访问入口委托至 self._backend
    # ------------------------------------------------------------------ #


    # ------------------------------------------------------------------ #
    # loading
    # ------------------------------------------------------------------ #

    def _load_file(self, entity_type: str) -> None:
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

    # ------------------------------------------------------------------ #
    # access (全部委托至 backend)—façade 模式
    # ------------------------------------------------------------------ #

    def __getitem__(self, entity_type: str) -> list[dict]:
        return list(getattr(self._backend, entity_type + 's' if entity_type == 'book' else entity_type + 's'))
        # 处上代码难看，换下面的多路径

    @property
    def books(self) -> list[dict]:
        return self._backend.books

    @property
    def editions(self) -> list[dict]:
        return self._backend.editions

    @property
    def source_copies(self) -> list[dict]:
        return self._backend.source_copies

    @property
    def chapters(self) -> list[dict]:
        return self._backend.chapters

    @property
    def passages(self) -> list[dict]:
        return self._backend.passages

    @property
    def concepts(self) -> list[dict]:
        return self._backend.concepts

    @property
    def principles(self) -> list[dict]:
        return self._backend.principles

    def ids(self, entity_type: str) -> set[str]:
        return self._backend.ids(entity_type)

    def get(self, entity_type: str, entity_id: str) -> dict | None:
        return self._backend.get(entity_type, entity_id)

    def counts(self) -> dict[str, int]:
        return self._backend.counts()

    # ------------------------------------------------------------------ #
    # link closure (UR-011 KB 扩展)
    # ------------------------------------------------------------------ #

    def verify_link_closure(self, rules: list[dict] | None = None) -> list[str]:
        """返回所有缺失链接的违规列表;空列表 = 闭合。

        rules 可选:检查 rule.book_id/passage_id/concept_id/principle_id
        (字段存在才查;工程种子规则无 book_id 属正常,不算违规)。
        """
        violations: list[str] = []

        book_ids = self.ids("book")
        edition_ids = self.ids("edition")
        source_copy_ids = self.ids("source_copy")
        chapter_ids = self.ids("chapter")
        passage_ids = self.ids("passage")
        concept_ids = self.ids("concept")
        principle_ids = self.ids("principle")

        # edition -> book;edition_id 全局唯一(ED-V-1)
        all_eids = [e["edition_id"] for e in self.editions]
        if len(all_eids) != len(set(all_eids)):
            violations.append(f"duplicate edition_id: {sorted(set(all_eids))}")
        pinned_per_book: dict[str, str] = {}
        for e in self.editions:
            eid = e["edition_id"]
            if e["book_id"] not in book_ids:
                violations.append(f"edition {eid} -> unknown book {e['book_id']}")
            if e["pinned"]:
                if e["book_id"] in pinned_per_book:
                    violations.append(
                        f"edition {eid}: book {e['book_id']} has multiple pinned editions "
                        f"(also {pinned_per_book[e['book_id']]})"
                    )
                else:
                    pinned_per_book[e["book_id"]] = eid
        edition_book = pinned_per_book

        # source_copy -> edition;edition.source_copies 存在时逐条校验
        source_copy_edition: dict[str, str] = {}
        for sc in self.source_copies:
            scid = sc["source_copy_id"]
            if sc["edition_id"] not in edition_ids:
                violations.append(f"source_copy {scid} -> unknown edition {sc['edition_id']}")
            source_copy_edition[scid] = sc["edition_id"]
        for e in self.editions:
            for scid in e.get("source_copies", []):
                if scid not in source_copy_edition:
                    violations.append(f"edition {e['edition_id']} -> unknown source_copy {scid}")
                elif source_copy_edition[scid] != e["edition_id"]:
                    violations.append(
                        f"edition {e['edition_id']} -> source_copy {scid} belongs to edition "
                        f"{source_copy_edition[scid]!r}"
                    )

        # book.pinned_edition_id <-> pinned edition(ED-V-2/3)
        for b in self.books:
            bid = b["book_id"]
            peid = b.get("pinned_edition_id")
            if not peid:
                violations.append(f"book {bid}: missing pinned_edition_id")
            elif peid not in edition_ids:
                violations.append(f"book {bid} -> unknown pinned_edition_id {peid}")
            elif edition_book.get(bid) != peid:
                violations.append(
                    f"book {bid}: pinned_edition_id {peid} != registered pinned edition "
                    f"{edition_book.get(bid)!r}"
                )

        # passage -> book / chapter
        chapter_book: dict[str, str] = {
            c["chapter_id"]: c["book_id"] for c in self.chapters
        }
        for p in self.passages:
            pid = p["passage_id"]
            if p["book_id"] not in book_ids:
                violations.append(f"passage {pid} -> unknown book {p['book_id']}")
            eid = p.get("edition_id")
            if not eid:
                violations.append(f"passage {pid}: missing edition_id")
            elif eid not in edition_ids:
                violations.append(f"passage {pid} -> unknown edition {eid}")
            elif edition_book.get(p["book_id"]) != eid:
                violations.append(
                    f"passage {pid} -> edition {eid} is not the pinned edition of "
                    f"book {p['book_id']} ({edition_book.get(p['book_id'])!r})"
                )
            scid = p.get("source_copy_id")
            if scid:
                if scid not in source_copy_ids:
                    violations.append(f"passage {pid} -> unknown source_copy {scid}")
                elif source_copy_edition.get(scid) != eid:
                    violations.append(
                        f"passage {pid} -> source_copy {scid} edition mismatch "
                        f"(expected {eid!r}, got {source_copy_edition.get(scid)!r})"
                    )
            cid = p["chapter_id"]
            if cid not in chapter_ids:
                violations.append(f"passage {pid} -> unknown chapter {cid}")
            elif chapter_book.get(cid) != p["book_id"]:
                violations.append(
                    f"passage {pid} -> chapter {cid} belongs to book "
                    f"{chapter_book.get(cid)!r}, passage says {p['book_id']!r}"
                )

        # M2-A S1 反链:passage.principle_ids / concept_ids 前向存在性
        for p in self.passages:
            pid = p["passage_id"]
            for ref in p.get("principle_ids", []):
                if ref not in principle_ids:
                    violations.append(f"passage {pid} -> unknown principle {ref}")
            for ref in p.get("concept_ids", []):
                if ref not in concept_ids:
                    violations.append(f"passage {pid} -> unknown concept {ref}")

        # M2-A V-5L 一致性(KB_VALIDATION_SPEC §3)
        for p in self.passages:
            pid = p["passage_id"]
            layer = p.get("source_layer")
            co = p.get("classical_original") or {}
            co_text = (co.get("text") or "").strip()
            co_verif = co.get("verification")
            para = p.get("paraphrase") or {}
            para_text = para.get("text") or ""
            sec = p.get("secondary_reference") or {}
            eng = p.get("engineering_note") or {}
            vs = p.get("verification_status")

            # ① classical_original.text 非空 ⇔ verification ∈ {verified,cross_verified}
            if co_text and co_verif not in _VERIFIED_STATES:
                violations.append(
                    f"passage {pid}: classical_original.text non-empty but verification={co_verif!r} "
                    f"(V-5L①)"
                )
            elif not co_text and co_verif in _VERIFIED_STATES:
                violations.append(
                    f"passage {pid}: verification={co_verif!r} but classical_original.text is empty "
                    f"(V-5L①)"
                )
            # ② verification_status∈{verified,cross_verified} ⇒ classical_original.verification 亦然
            if vs in _VERIFIED_STATES and co_verif not in _VERIFIED_STATES:
                violations.append(
                    f"passage {pid}: verification_status={vs!r} but classical_original.verification="
                    f"{co_verif!r} (V-5L②)"
                )
            # ③ pending ⇒ paraphrase.text 以 (待校,paraphrase) 开头
            if vs == _PENDING_STATE and not para_text.startswith(_PENDING_PREFIX):
                violations.append(
                    f"passage {pid}: verification_status=pending_verification but paraphrase.text "
                    f"does not start with {_PENDING_PREFIX!r} (V-5L③)"
                )
            # ④ 评注不得混入 classical_original.text
            if co_text and any(m in co_text for m in _COMMENTARY_MARKERS):
                violations.append(
                    f"passage {pid}: classical_original.text contains commentary markers "
                    f"(V-5L④)"
                )
            # ⑤ source_layer↔槽位一致性
            if layer == "classical_original" and not co_text:
                violations.append(f"passage {pid}: source_layer=classical_original but text empty (V-5L⑤)")
            if layer == "paraphrase" and co_text:
                violations.append(
                    f"passage {pid}: source_layer=paraphrase but classical_original.text non-empty "
                    f"(V-5L⑤)"
                )
            if layer == "secondary_reference" and not (sec.get("text") or "").strip():
                violations.append(
                    f"passage {pid}: source_layer=secondary_reference but secondary_reference empty "
                    f"(V-5L⑤)"
                )
            if layer == "engineering_seed" and not (eng.get("text") or "").strip():
                violations.append(
                    f"passage {pid}: source_layer=engineering_seed but engineering_note empty (V-5L⑤)"
                )
            if layer == "commentary" and not p.get("commentary_layers"):
                violations.append(
                    f"passage {pid}: source_layer=commentary but commentary_layers empty (V-5L⑤)"
                )
            if layer not in _ALLOWED_LAYERS:
                violations.append(f"passage {pid}: invalid source_layer {layer!r} (V-5L⑤)")

        # ED-V-4/5:layer_structure 键 ⊆ 五层且含 classical_original;
        # commentator 非空 ⇔ commentary 层
        for e in self.editions:
            eid = e["edition_id"]
            ls = e.get("layer_structure", {})
            bad = set(ls) - _ALLOWED_LAYERS
            if bad:
                violations.append(f"edition {eid}: invalid layer keys {sorted(bad)}")
            if "classical_original" not in ls:
                violations.append(f"edition {eid}: layer_structure missing classical_original")
            has_commentator = bool(e.get("commentator"))
            has_commentary = "commentary" in ls
            if has_commentator != has_commentary:
                violations.append(
                    f"edition {eid}: commentator presence ({has_commentator}) != "
                    f"commentary layer ({has_commentary})"
                )

        # concept.source_refs -> book
        # M2-A S1 反链:concept.passage_refs/principle_ids/contexts 前向存在性
        for c in self.concepts:
            cid = c["concept_id"]
            for ref in c.get("source_refs", []):
                if ref not in book_ids:
                    violations.append(f"concept {cid} -> unknown book {ref}")
            for ref in c.get("passage_refs", []):
                if ref not in passage_ids:
                    violations.append(f"concept {cid} -> unknown passage {ref}")
            for ref in c.get("principle_ids", []):
                if ref not in principle_ids:
                    violations.append(f"concept {cid} -> unknown principle {ref}")
            for ctx in c.get("contexts", []):
                if ctx.get("book_id") not in book_ids:
                    violations.append(f"concept {cid} -> context unknown book {ctx.get('book_id')!r}")
                pr = ctx.get("principle_id")
                if pr is not None and pr not in principle_ids:
                    violations.append(f"concept {cid} -> context unknown principle {pr!r}")

        # M2-A S1 反链双向:concept.passage_refs ⇔ passage.concept_ids
        passage_by_id = {p["passage_id"]: p for p in self.passages}
        for c in self.concepts:
            cid = c["concept_id"]
            for ref in c.get("passage_refs", []):
                p = passage_by_id.get(ref)
                if p is not None and cid not in p.get("concept_ids", []):
                    violations.append(
                        f"concept {cid} -> passage {ref} lacks back-link concept_ids "
                        f"(S1 反链不对称)"
                    )
        for p in self.passages:
            pid = p["passage_id"]
            for cid in p.get("concept_ids", []):
                c = self.get("concept", cid)
                if c is not None and pid not in c.get("passage_refs", []):
                    violations.append(
                        f"passage {pid} -> concept {cid} lacks back-link passage_refs "
                        f"(S1 反链不对称)"
                    )

        # principle.book_refs / passage_refs
        for pr in self.principles:
            for ref in pr.get("book_refs", []):
                if ref not in book_ids:
                    violations.append(f"principle {pr['principle_id']} -> unknown book {ref}")
            for ref in pr.get("passage_refs", []):
                if ref not in passage_ids:
                    violations.append(f"principle {pr['principle_id']} -> unknown passage {ref}")

        # rule -> KB(仅检查存在的字段)
        if rules:
            for r in rules:
                rid = r.get("rule_id")
                for field, known in (
                    ("book_id", book_ids),
                    ("passage_id", passage_ids),
                    ("concept_id", concept_ids),
                    ("principle_id", principle_ids),
                ):
                    ref = r.get(field)
                    if ref and ref not in known:
                        violations.append(f"rule {rid} -> unknown {field} {ref}")

        return violations

    # ------------------------------------------------------------------ #
    # M2-A:legacy residue 识别(validator 可识别旧数据残留,验收 #4)
    # ------------------------------------------------------------------ #

    @staticmethod
    def verify_legacy_residue(data_dir: Path) -> list[str]:
        """原始文件级扫描 v1/v2.0 旧 schema 残留(不经 schema 加载)。

        loader 对旧数据在 schema 校验处**硬失败**(T203 严格策略),因此旧数据
        根本无法加载进 _entities;legacy 识别必须直接读原始 JSON 文件,才能在
        数据仍处旧形状时给出「哪些字段是残留」的诊断。

        空列表 = 数据已是新 schema 形状。检测项:旧 passage 顶层 original_text /
        normalized_text / verification、旧枚举『待校』(passage/chapter)、缺
        source_layer / classical_original 的 passage、缺 source_layer 的 evidence。
        """
        findings: list[str] = []
        kb_dir = Path(data_dir) / "knowledge"
        passages_file = kb_dir / "passages.json"
        if passages_file.is_file():
            raw = json.loads(passages_file.read_text(encoding="utf-8"))
            for p in raw.get("items", []):
                pid = p.get("passage_id", "?")
                for field in _LEGACY_PASSAGE_TOP_FIELDS:
                    if field in p:
                        findings.append(f"passage {pid}: legacy top-level field {field!r}")
                if p.get("verification_status") in _LEGACY_VERIFICATION_VALUES:
                    findings.append(
                        f"passage {pid}: legacy verification_status {p['verification_status']!r}"
                    )
                if "source_layer" not in p:
                    findings.append(f"passage {pid}: missing source_layer (legacy v2.0 shape)")
                if "classical_original" not in p:
                    findings.append(
                        f"passage {pid}: missing classical_original (legacy v2.0 shape)"
                    )
        chapters_file = kb_dir / "chapters.json"
        if chapters_file.is_file():
            raw = json.loads(chapters_file.read_text(encoding="utf-8"))
            for c in raw.get("items", []):
                if c.get("verification_status") in _LEGACY_VERIFICATION_VALUES:
                    findings.append(
                        f"chapter {c.get('chapter_id', '?')}: legacy verification_status "
                        f"{c['verification_status']!r}"
                    )
        ev_dir = Path(data_dir) / "evidence"
        if ev_dir.is_dir():
            for f in sorted(ev_dir.glob("*.json")):
                try:
                    d = json.loads(f.read_text(encoding="utf-8"))
                except Exception as exc:  # noqa: BLE001 — 汇总为一条
                    findings.append(f"evidence {f.name}: unreadable ({exc})")
                    continue
                if "source_layer" not in d:
                    findings.append(f"evidence {d.get('evidence_id', f.name)}: missing source_layer")
        return findings

    # ------------------------------------------------------------------ #
    # M2-A:evidence 元数据校验(evidence.schema v1.1)
    # ------------------------------------------------------------------ #

    def verify_evidence(self, evidence_schema: Path | None = None) -> list[str]:
        """校验 data/evidence/*.json 是否符合 evidence.schema v1.1 + edition 一致性。

        - jsonschema 校验(schema 必填 source_layer)
        - edition_id 存在时 → 必须是已登记 edition;
          缺省时 → evidence_id 必须在 _NO_EDITION_EVIDENCE(工程种子,引文非经典版本)
        - citation.verification_status 若填 → 必须是 v1.1 枚举
        """
        findings: list[str] = []
        ev_dir = self._kb_dir.parent / "evidence"
        if not ev_dir.is_dir():
            return findings
        schema_path = Path(evidence_schema) if evidence_schema else (
            self._kb_dir.parent.parent / "docs" / "evidence.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        edition_ids = self.ids("edition")
        for f in sorted(ev_dir.glob("*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            eid = d.get("evidence_id", f.name)
            for err in validator.iter_errors(d):
                findings.append(f"evidence {eid}: schema — {err.message}")
                break
            ed = d.get("edition_id")
            if ed is not None:
                if ed not in edition_ids:
                    findings.append(f"evidence {eid}: unknown edition_id {ed!r}")
            elif eid not in _NO_EDITION_EVIDENCE:
                findings.append(
                    f"evidence {eid}: missing edition_id but not a documented no-edition "
                    f"(工程种子) evidence"
                )
            vs = (d.get("citation") or {}).get("verification_status")
            if vs is not None and vs not in {
                "verified", "cross_verified", "pending_verification",
                "disputed", "not_applicable",
            }:
                findings.append(f"evidence {eid}: invalid citation.verification_status {vs!r}")
        return findings

    # ------------------------------------------------------------------ #
    # M2-B:evidence chain(cluster + review queue + Evidence→Concept/Principle)
    # ------------------------------------------------------------------ #

    def verify_evidence_chain(
        self,
        meta_dir: Path | None = None,
        cluster_schema: Path | None = None,
        queue_schema: Path | None = None,
    ) -> list[str]:
        """M2-B:校验 Evidence Cluster + Evidence Review Queue + Evidence→Concept/Principle 链。

        - data/evidence_meta/evidence_clusters.json(v1.0 schema)+ evidence_review_queue.json(v1.0)
        - cluster 成员与 evidence 双向闭合:member 存在、evidence.cluster_id 反链一致、
          citation.original_text 与 anchor_text 逐字一致、passage/book/chapter/edition 解析
        - queue 覆盖全量 evidence;verdict ↔ citation.verification_status 一致;
          D-10:queue 条目不含 Rule 生命周期字段(Evidence 验证与 Rule 激活两个独立审批链)
        - concept/principle.evidence_refs ⊆ evidence ids(Evidence→Concept/Principle 链)

        默认目录=data/evidence_meta,schema 默认=repo_root/docs;测试/临时树显式传参。
        """
        findings: list[str] = []
        base = self._kb_dir.parent                       # data/
        ev_dir = base / "evidence"
        meta = Path(meta_dir) if meta_dir else base / "evidence_meta"
        if not ev_dir.is_dir() or not meta.is_dir():
            return findings

        evidence: dict[str, dict] = {}
        for f in sorted(ev_dir.glob("*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            evidence[d["evidence_id"]] = d

        # --- evidence_clusters.json ---
        clusters: dict[str, dict] = {}
        cl_file = meta / "evidence_clusters.json"
        if cl_file.is_file():
            raw = json.loads(cl_file.read_text(encoding="utf-8"))
            schema_path = Path(cluster_schema) if cluster_schema else (
                self._kb_dir.parent.parent.parent / "docs" / "evidence_clusters.schema.json"
            )
            validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))
            for err in validator.iter_errors(raw):
                findings.append(f"evidence_clusters: schema — {err.message}")
                break
            if raw.get("kind") == "evidence_clusters":
                clusters = {c["cluster_id"]: c for c in raw.get("clusters", [])}
                for cid, c in clusters.items():
                    pid = c["passage_id"]
                    p = self.get("passage", pid)
                    if p is None:
                        findings.append(f"cluster {cid}: unknown passage {pid}")
                        continue
                    if p["book_id"] != c["book_id"]:
                        findings.append(f"cluster {cid}: book mismatch vs passage {pid}")
                    if p["chapter_id"] != c["chapter_id"]:
                        findings.append(f"cluster {cid}: chapter mismatch vs passage {pid}")
                    if p["edition_id"] != c["edition_id"]:
                        findings.append(f"cluster {cid}: edition mismatch vs passage {pid}")
                    anchor = c["anchor_text"]
                    for mid in c.get("member_evidence_ids", []):
                        ev = evidence.get(mid)
                        if ev is None:
                            findings.append(f"cluster {cid}: unknown member evidence {mid}")
                            continue
                        if ev.get("cluster_id") != cid:
                            findings.append(
                                f"cluster {cid}: member {mid} cluster_id backlink missing/mismatch "
                                f"({ev.get('cluster_id')!r})"
                            )
                        cit = (ev.get("citation") or {}).get("original_text", "")
                        if cit != anchor:
                            findings.append(
                                f"cluster {cid}: member {mid} citation not byte-identical to anchor"
                            )

        # evidence.cluster_id → 已登记 cluster(双向:未登记 OR 登记但非成员)
        for eid, ev in evidence.items():
            cid = ev.get("cluster_id")
            if cid is None:
                continue
            if cid not in clusters:
                findings.append(f"evidence {eid}: cluster_id {cid!r} not registered")
            elif eid not in clusters[cid].get("member_evidence_ids", []):
                findings.append(
                    f"evidence {eid}: cluster_id {cid!r} registered but not a member"
                )

        # --- evidence_review_queue.json ---
        q_file = meta / "evidence_review_queue.json"
        if q_file.is_file():
            raw = json.loads(q_file.read_text(encoding="utf-8"))
            schema_path = Path(queue_schema) if queue_schema else (
                self._kb_dir.parent.parent.parent / "docs" / "evidence_review_queue.schema.json"
            )
            validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))
            for err in validator.iter_errors(raw):
                findings.append(f"evidence_review_queue: schema — {err.message}")
                break
            qitems = raw.get("items", []) if raw.get("kind") == "evidence_review_queue" else []
            queued = {e["evidence_id"]: e for e in qitems}
            missing = sorted(set(evidence) - set(queued))
            extra = sorted(set(queued) - set(evidence))
            if missing:
                findings.append(f"review queue missing evidence: {missing}")
            if extra:
                findings.append(f"review queue unknown evidence: {extra}")
            for eid, entry in queued.items():
                ev = evidence.get(eid)
                if ev is None:
                    continue
                expected = _QUEUE_VERDICT_TO_EVIDENCE_STATUS.get(entry.get("verdict"))
                actual = (ev.get("citation") or {}).get("verification_status")
                if expected is None:  # verdict=blank
                    if actual is not None:
                        findings.append(
                            f"review {eid}: verdict=blank but evidence has "
                            f"verification_status={actual!r}"
                        )
                elif actual != expected:
                    findings.append(
                        f"review {eid}: verdict={entry.get('verdict')!r} != evidence status "
                        f"{actual!r}"
                    )
                # D-10:queue 条目不得携带 Rule 生命周期字段
                # (schema additionalProperties:false 已结构保证;运行时再确认)
                lifecycle = set(entry) & {
                    "rule_status", "activation_eligible", "rule_activated", "lifecycle",
                }
                if lifecycle:
                    findings.append(
                        f"review {eid}: D-10 violation — rule lifecycle fields "
                        f"{sorted(lifecycle)}"
                    )

        # --- Evidence→Concept/Principle 链(knowledge 实体 evidence_refs ⊆ evidence) ---
        for c in self.concepts:
            for ref in c.get("evidence_refs", []):
                if ref not in evidence:
                    findings.append(f"concept {c['concept_id']} -> unknown evidence {ref}")
        for pr in self.principles:
            for ref in pr.get("evidence_refs", []):
                if ref not in evidence:
                    findings.append(f"principle {pr['principle_id']} -> unknown evidence {ref}")

        return findings
