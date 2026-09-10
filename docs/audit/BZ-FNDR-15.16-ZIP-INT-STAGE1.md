# ZIP-INT Stage 1 施工归档（BZ-FNDR-15.16）

> **BZ-FNDR-15.16：ZIP-INT-01 / 02 / 03 施工完成记录**
> **Code / Evidence / Rule / Algorithm Change ≠ 0（首次生产代码改动）**
>
> 前置授权：User 2026-09-10 批准 Stage 1 进入（G0 验收 PASS + 15.15 接入审计 PASS + 选择 option A 纯可见性切换）。
> 约束来源：15.15 §3 三条硬约束 (T-1/T-2/T-3) + User ②-A 方案（rule 面维持 136 条）。
> 目标：把 G0-1 Evidence Index（树B Corpus Base）+ G0-2 Resolved Provenance 接进生产链，同时保持生产 rule 面 136 条不变。

---

## 0. 施工元数据

| 项 | 值 |
|---|---|
| 施工 ID | BZ-FNDR-15.16 |
| 前置 | 15.15（七验证点 PASS + T-1~T-3 硬约束）|
| 选项 | User 选 A：纯证据可见性切换，rule glob 维持 136 |
| 施工 commit | （本记录待 commit；代码改动 3 文件） |
| 测试 | 新增 INT-01/02/03 单测 + 73 既有回归 |
| G1 | 未触碰（production path 不变） |
| evidence/rule 正文 | 未触碰（option A 严守） |
| GitHub push | 🔴 不推（Stage 1 完成后仍需完整边界审计 + 远端反向核验） |

---

## 1. 施工条目

### INT-01 — Evidence Index 生产侧消费面

**目标**：让 `TONGSHUPipeline` 持有活的 `EvidenceIndex`（Corpus Base = `data/evidence`），供后续消费。

**改动**：
```python
# src/tongshu/pipeline.py
from .governance.evidence_index import EvidenceIndex

# TONGSHUPipeline.__init__ 新增可选参数:
evidence_index: "EvidenceIndex | None" = None,
...
self.evidence_index = evidence_index  # 默认 None（向后兼容现有调用）
```

**边界**：
- 默认 `None` = 无消费面；只有 `for_demo` 显式注入
- 0 改 RuleLoader / 0 改 G1 / 0 改 rules/ 证据正文
- P0 路径独立性：Index 只持 `Path(corpus_root)`，不写死绝对路径

### INT-02 — Tree B 语料接入（option A 实施）

**目标**：在 `for_demo` 中构建 Corpus Base Index，切证据可见性到树 B。

**改动**（仅 `pipeline.py` `for_demo` 方法）：
```python
# G0-1/02: Evidence Index (树B Corpus Base) + Provenance Resolver
corpus_root = repo_root / "data" / "evidence"
evidence_index = EvidenceIndex.build(corpus_root, tree="corpus_base")
provenance_resolver = ProvenanceResolver(evidence_index)

return cls(
    ...
    evidence_index=evidence_index,      # ← 新增
    provenance_resolver=provenance_resolver,  # ← 新增
)
```

**option A 严守**：
- ❌ 不切 `data_dir` → 规则面维持树A 136 条（4 条 draft PT/YONG 不进入生产）
- ✅ evidence 可见性切到树B（根级 86 + 子目录 5614 全量）
- ✅ Tree A legacy snapshot 仍作为 RuleLoader 事实来源（production RuleLoader 不变）
- ✅ 树B Index 通过 `EvidenceIndex.build` 显式构建，非 rglob 黑盒

**T-3 基线核查**（实跑 RuleLoader 双树对比）：
- 树A RuleLoader: rules=136, evidence_ids=86, verify_evidence_refs=0
- 树B RuleLoader: rules=140 (+4 draft), evidence_ids=86（严格相等）, verify_evidence_refs=4（draft 引用的子目录 evidence 不可见）
- G1 evidence_gate 面：两树严格相同 → **Production G1 零漂移**

### INT-03 — Resolved Provenance 接入（消费面）

**目标**：ValidationStage 消费 `ProvenanceResolver`，输出运行期 provenance 统计（T-2 唯一来源契约）。

**改动**：

```python
# src/tongshu/pipeline.py
from .governance.provenance_resolver import ProvenanceResolver

# __init__ 新增参数 + 字段注入:
provenance_resolver: "ProvenanceResolver | None" = None,
...
self.provenance_resolver = provenance_resolver

# ValidationStage 构造注入:
self.validation_stage = ValidationStage(
    ...
    provenance_resolver=self.provenance_resolver,  # G0-2 接入
)
```

```python
# src/tongshu/pipeline_stages/validation_stage.py
class ValidationStage:
    def __init__(..., provenance_resolver=None):
        ...
        self.provenance_resolver = provenance_resolver

    def run(self, ...):
        ...
        provenance_summary = None
        if self.provenance_resolver is not None and gates:
            provenance_summary = self.provenance_resolver.tier_summary()
        return ValidationStageResult(..., provenance_summary=provenance_summary)
```

```python
# src/tongshu/types.py
class ValidationStageResult:
    ...
    provenance_summary: dict[str, int] = None  # G0-2 运行期 provenance 统计
```

**边界**：
- ❌ 不改 `atomic_claims` 结构（T-2 要求 "Composer → ResolvedProvenance 唯一来源"，Composer 落地在 ZIP-INT-05，本阶段只做消费面）
- ❌ 不改 G1 行为（G1 仍用 `evidence_ids` 集合判定）
- ✅ 运行期 provenance 统计通过 `ValidationStageResult.provenance_summary` 向上传递，供审计日志/诊断

---

## 2. 测试（T-3 回归 + 新单测）

### 回归基线（T-3 零漂移）

```bash
python -m pytest tests/test_p0_evidence_chain.py \
             tests/test_ziping_15_2_evidence_provenance.py \
             tests/test_audit_gates.py \
             tests/test_api.py -q
→ 73 passed, 1 warning  ✅ (与施工前 73 passed 一致)
```

### 新增单测（覆盖 INT-01/02/03）

**test_int_01_02_03_pipeline_wiring.py**：
- INT-01: `PipelineResult.provenance_summary` 字段存在
- INT-02: `for_demo` 注入的证据 Index corpus_root 是树B (`data/evidence`)
- INT-02: Option A 下生产 `RuleLoader.evidence_ids` 仍为 86（不扩大）
- INT-03: `ValidationStageResult.provenance_summary` 当 `provenance_resolver=None` 时为 None
- INT-03: 接入后 `provenance_summary` 类型 = dict（含 8 档分布）
- G1 隔离：`PipelineResult.provenance_summary` 不影响 G1 `passed` 结果

---

## 3. 边界审计（施工红线守备）

| 红线 | 守备动作 | 结果 |
|---|---|---|
| G1 未触碰 | 不改 `src/tongshu/audit_validation/gates/g1_evidence.py` | ✅ |
| 不夹带 SHIJIAN/event | 本 commit 0 引用 `event_type`/`SHIJIAN`/`event_mapping` | ✅ |
| 不修改 Evidence 正文 | 不增删改 `data/evidence/*.json` | ✅ |
| 不修改 Rule 正文 | 不增删改 `data/rules/*.json` | ✅ |
| P0 路径独立性 | 0 硬编码绝对路径；Index 的 `corpus_root` 由 `repo_root` 注入 | ✅ |
| 单引擎边界 | 只改 ZiPing 治理层 + Pipeline 接缝 | ✅ |

---

## 4. 当前门状态

```text
G0-1 Index              🟢 已施工 (1ca93627)
G0-2 Provenance         🟢 已施工 (6e3896ee)
G0 Integration Audit    🟢 已审计 (0803f059)
ZIP-INT Stage 1         🟢 已施工 (本 commit)
  ├─ INT-01 生产 Index 注入    ✅
  ├─ INT-02 Tree B 接入       ✅ (option A, rule 面 136 维持)
  └─ INT-03 Provenance 消费面 ✅
① Event-Signal           🔴 FAIL (SHIJIAN 冻结)
② Evidence Loader        🔒 C1a
③ verification_status    🔒 V3+V4
G1                       🔒 LOCKED
ZIP-INT-04               🔴 冻结
ZIP-INT-05~08            🔴 未授权
GitHub push              🔴 暂不推（等完整边界审计 + 远端反向核验）
本地 commits             12 领先 origin/main
```

## 5. 待你裁决

1. **远端推送**：Stage 1 的 3 个 commit（G0-1 + G0-2 + INT Stage 1）现在可一次性推远端 + 反向核验，还是继续冻结等 ZIP-INT-05+？
2. **ZIP-INT Stage 2**：是否授权进入 INT-05（JudgmentClaimComposer）+ INT-06（ComputeStage 拆分）？INT-05 是 T-2 "claim provenance 唯一来源"的落地点，一旦接入会真正改变生产 claim 产出面。

*Generated by BOT-MASTER on 2026-09-10*
*Code change: src/tongshu/pipeline.py / src/tongshu/pipeline_stages/validation_stage.py / src/tongshu/types.py*
*Tests: test_int_01_02_03_pipeline_wiring.py (新增)*
*Evidence/Rules/G1 unchanged: ✅*
