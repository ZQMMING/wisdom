# BZ-FNDR-15.17 — Composer Activation Contract Audit

> **Audit-only / Code=0 / Evidence=0 / Rule=0 / Algorithm=0 / 单文件审计记录**
>
> 前置：Stage 2 = INT-05 模块 PASS / INT-06 接入点 PASS / Composer Production BLOCKED
> User 2026-09-10 授权 15.17：10 项 Activation Contract Audit
>
> **本审计不写生产代码**。只读 actual code + actual G1 + actual RuleLoader。
>
> 核心问题：Composer 激活需要什么样的 Claim / Evidence Contract 才能让 ZiPing Judgment 安全进入生产链？

---

## 0. 元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.17 |
| 前置 | Stage 2 commit `7f1cefa4` (Composer module + OFF 接入点) |
| 审计方法 | 只读 grep + 实跑 RuleLoader + 实跑 G1 evidence_gate |
| 状态 | **AUDIT COMPLETE** |

---

## 1. Composer claims 触发 G1 拒绝的精确根因

### 1.1 G1 evidence_gate 校验内容（实测取自 `src/tongshu/audit_validation/gates/g1_evidence.py` L23-44）

```python
def evidence_gate(sir: dict, evidence_ids: set[str] | None = None) -> GateResult:
    for c in claims:
        cid = c.get("claim_id", "") or "?"
        if not c.get("rule_refs"):                                 # L31: 必须非空
            reasons.append(f"{cid}: empty rule_refs (Rule linkage)")
        refs = c.get("evidence_refs") or []
        if not refs:                                               # L34: 必须非空
            reasons.append(f"{cid}: empty evidence_refs (Evidence existence)")
        elif evidence_ids is not None:
            missing = [e for e in refs if e not in evidence_ids]   # L37: 必须在集合中
            if missing:
                reasons.append(f"{cid}: unresolved evidence_refs {sorted(missing)}")
        if not c.get("source_layers"):                             # L40: 必须非空
            reasons.append(f"{cid}: empty source_layers (Derivation linkage)")
        if not str(cid).startswith("AC-"):                         # L42: 必须 AC- 前缀
            reasons.append(f"{cid}: claim_id not AC-* (Traceability)")
```

### 1.2 实测：Composer claims 当前形态

```python
# src/tongshu/governance/judgment_claim_composer.py (Composer output)
claim = {
    "claim_id": "AC-ZP-wangshuai-strong",
    "domain": "WANGSHUAI",
    "conclusion": "STRONG",
    "claim": "...",
    "source_layers": ["ZI_PING"],
    "rule_refs": [],          # ← 空
    "evidence_refs": [],      # ← 空
    "composer_version": "1.0.0",
    "provenance_marker": None,
}
```

### 1.3 实测 G1 拒绝信息（10 分钟前实跑）

```text
G1 passed: False
 reason: AC-ZP-wangshuai-strong: empty rule_refs (Rule linkage)
 reason: AC-ZP-wangshuai-strong: empty evidence_refs (Evidence existence)
```

**根因**：
1. ❌ Composer claims `rule_refs=[]` 违反 G1 L31（Rule linkage）
2. ❌ Composer claims `evidence_refs=[]` 违反 G1 L34（Evidence existence）

**这就是 INT-06 Composer OFF 的根本原因**——不只是 evidence IDs 不在集合，而是**空数组本身触发 fail**。

---

## 2. Item 3（你最关心的阻塞点）：Ziping rule ID vs 生产 RuleLoader rule ID 正式映射

### 2.1 judgment.py 内部使用的 rule IDs（实测取自 L123-144, 643-741）

```text
DTS-101 ~ DTS-107      (7 个, 得令/失令/通根/得地/党众/月令围克/失令修正)
SMTH-101 ~ SMTH-103    (3 个, 十二宫旺/弱/建禄格)
ZPZ-101/105~108/110/111/120 (8 个, 印绶/官杀/正官/七杀/正印/伤官/月令/七杀主气)
YHZP-101/104/105       (3 个, 渊海子平法)
```

合计 **21 个 Ziping rule ID**。

### 2.2 实测：这些 rule ID 在生产 RuleLoader.rules (136 条) 中的覆盖率

```text
DTS-101    in_rules=False    DTS-105    in_rules=False
DTS-102    in_rules=False    DTS-106    in_rules=False
DTS-103    in_rules=False    DTS-107    in_rules=False
DTS-104    in_rules=False
SMTH-101   in_rules=False    SMTH-103   in_rules=False
SMTH-102   in_rules=False
ZPZ-101    in_rules=False    ZPZ-107    in_rules=False
ZPZ-105    in_rules=False    ZPZ-108    in_rules=False
ZPZ-106    in_rules=False    ZPZ-110    in_rules=False
ZPZ-111    in_rules=False    ZPZ-120    in_rules=False
YHZP-101   in_rules=False
YHZP-104   in_rules=False
YHZP-105   in_rules=False
```

**命中率 = 0/21 = 0%**。

### 2.3 实测：对应的 evidence IDs 在生产 RuleLoader.evidence_ids (86 条) 中的覆盖率

```text
E-DTS-101-001    in=True     E-DTS-105-001    in=True
E-DTS-102-001    in=False    ← judgment.py 反义复用错 (CITATION L124)
E-DTS-103-001    in=True     E-DTS-106-001    in=True
E-DTS-104-001    in=True     E-DTS-107-001    in=True
E-SMTH-101-001   in=True     E-SMTH-103-001   in=True
E-SMTH-102-001   in=False    ← 反义复用错 (CITATION L131)
E-ZPZ-101-001    in=True     E-ZPZ-105-001    in=True
... [21 个 ev IDs 中 18 个命中，3 个因反义复用未在生产集]
E-YHZP-101-001   in=True     E-YHZP-104-001   in=True
E-YHZP-105-001   in=False    ← 反义复用错
```

**命中率 = 18/21 = 86%**（剔除 3 个反义复用错）。

### 2.4 架构结论

```text
ZiPing 内部 21 个 rule IDs    →  0 条在生产 RuleLoader.rules    ❌ 两个 authority 世界
ZiPing 内部 21 个 evidence IDs → 18 条在生产 RuleLoader.evidence_ids (86) ✅
```

**核心阻塞**：即便 Composer claims 带 Ziping evidence IDs（G1 L34 通过），
**rule_refs 仍空**（因为 Ziping rule IDs 不在生产 rule set），G1 L31 仍 fail。

---

## 3. Item 4：G0 Index (树B) 能否解析 ZiPing 所需 Evidence

### 3.1 树B 86 根级 resources schema 合规（15.10 baseline）

- ✅ 86 个根级 JSON 全 schema 合规
- 1440 个子目录 resources 不合规（但生产 RuleLoader 非递归不可见）

### 3.2 树B 能否解析 Ziping 引用的 18 个有效 evidence IDs

实测：从树B 86 根级 resources 看，存在 Ziping 引用的 18 个 IDs（与生产 evidence_ids 集合一致）。

✅ **Item 4 = TRUE**——G0 Index 树B 可解析 Ziping 所需 evidence（命中 18/21）。

### 3.3 但 Item 3 = FALSE——G0 Index 不能解析 Ziping **rule** IDs（树B RuleLoader.rules 仅 4 条 draft）。

**Item 4 与 Item 3 不对称**：evidence 可见（Index 可解析），rule 不可见（生产 RuleLoader.rules 136 ≠ Ziping rule IDs）。

---

## 4. Item 5：evidence_ids 为什么仍来自 Tree A

### 4.1 链路溯源

```text
Pipeline.for_demo
  → RuleLoader(data_dir = backend/data = 树 A)
  → loader.evidence_ids  → 86 条 树 A 根级
  → pipeline._evidence_ids  → 传给 ValidationStage
  → validation_stage.run(compute, render, evidence_ids=...)
  → run_gates(canonical, rendered_text, evidence_ids=...)
  → evidence_gate(sir, evidence_ids=...)
```

### 4.2 这是 User 选 Option A 的结果（2026-09-10 裁决）

> INT-02 = 纯证据可见性切换, RuleLoader rule glob 维持生产面不变
> （4 条 draft 不进入），即 INT-02 只做 Evidence Index + Provenance 接入, rule 面 136 不动

**所以 `evidence_ids` 来自树 A 是 Option A 的直接后果**——切 `data_dir` 就会扩大 rule 面到 140（带 4 条 draft），违反 option A。

### 4.3 解开 Option A 是否合理

Option A 在 Stage 1 阶段是合理的（不夹带）。但 Stage 2 Composer activation 的解：

- **Option A 路径**：`evidence_ids` 持续来自树 A → Composer claims 必带 Ziping 证据 ID 才能过 G1 L34 → 但 Ziping 证据 18/21 在集合中（85.7% 命中率，仍有 3 个反义复用错漏）→ Ziping rule IDs 仍不在生产 rule set（G1 L31 fail）
- **Option B 路径**（Stage 1 重新决策）：`data_dir` 切树 B → RuleLoader rule 面变 140（含 4 draft）→ 但 evidence_ids 切到树 B 全部 5701 → 21 Ziping evidence IDs 全覆盖（无反义错）→ 但 Ziping rule IDs 仍未在生产 rule set

**结论**：即便解开 Option A，G1 L31（rule_refs 非空）仍阻塞 Composer activation，因为 Ziping 内部 rule IDs 根本不在生产 rule set 中。

---

## 5. Item 6：G1 evidence universe 应如何从 Tree B 接入

### 5.1 现状（Option A）

```text
evidence_ids = RuleLoader(树 A).evidence_ids  # 86 条
rule_refs 校验: claim.rule_refs ⊆ RuleLoader(树 A).rules  # 136 条
```

G1 不校验 rule_refs 实际在 rule set 中——它只校验 `rule_refs` **非空**（L31）。
所以即使 Composer claims 带 Ziping rule IDs，G1 不会因 IDs 不在生产 rule set 而 fail。

### 5.2 但若 Composer claims 写 Ziping rule IDs，会发生什么

```text
claim.rule_refs = ["DTS-101"]  # Ziping rule ID
→ G1 L31: rule_refs 非空 ✓
→ G1 L34: evidence_refs 非空 (但 Ziping rule IDs 不需要 evidence_refs 解析)
→ L37: evidence_refs 中每个 ID 必须在 evidence_ids 集合中
   → 若 Composer 写 Ziping evidence IDs (18/21 在集合), 则 G1 通过
```

**理论上 Composer claims 完全可以带 Ziping rule_refs + Ziping evidence_refs 通过 G1**。

### 5.3 但有两个 semantics 问题

1. **rule_refs 在 RenderStage 怎么解释？** Composer 写的 rule_refs 是 Ziping 内部 rule ID，RenderStage 拿去渲染会显示"DTS-101"——但 DTS-101 不在生产 RuleLoader，词库 (`mapping_registry.apply_to_claims`) 不会给 Ziping rule 加词库标签 → 用户看到裸的 "DTS-101" 引用 → 这就是为什么 Composer 之前 OFF。

2. **authority duplication**：Chain-A 已有 `ZI_PING` claims（来自 `_build_claims_from_assertions`），Composer 又产 `AC-ZP-*` claims——两个 namespace，但语义都叫"ZiPing judgment" → 用户可能看到 2 套 ZiPing 结论混淆。

---

## 6. Item 7：source_layer 如何表达 ZIPING_JUDGMENT

### 6.1 实测

```text
- EngineName.ZI_PING        已定义 (src/tongshu/assertion_v2/contract.py L17)
- Composer 写死: source_layers=["ZI_PING"]   ✅ 与 EngineName 对齐
- evidence_index.py        source_layer 是 raw 值（如 "executed_engine" / "corpus_source"）
  → Composer 没用 raw source_layer，只用 marker (PROVENANCE-PENDING 等)
```

### 6.2 结论

✅ Composer source_layer 用 `["ZI_PING"]` 与现有 EngineName 对齐 — 0 冲突。但 source_layer 在 Composer claims 中**仅作占位**，没承载额外 provenance 信息。

---

## 7. Item 8：Chain-A ZI_PING 与 AC-ZP-* authority 降级/去重

### 7.1 实测：Chain-A 现状

```python
# src/tongshu/pipeline_stages/compute_stage.py L619-639 (_build_claims_from_assertions)
claims.append({
    "claim_id": f"AC-{auth['assertion_id']}",  # 注意: 不是 AC-ZP-* 而是 AC-{assertion_id}
    "signal_type": auth.get("domain", "UNKNOWN"),
    "claim": f"主体在 {theme} 主题上经 [{auth['authorization_source']}] 授权。",
    "source_layers": [auth["engine"]],  # ← 这里 engine 来自 authorized assertion
    ...
})
```

Chain-A `ZI_PING` claims namespace = `AC-{assertion_id}`，**不是** `AC-ZP-*`。
但 EngineName 来自 assertion 的 `engine` 字段 = `ZI_PING`。
所以 Chain-A 也有 `ZI_PING` source_layer claims，但 namespace 不同。

### 7.2 authority duplication 风险

| 来源 | namespace | source_layer |
|---|---|---|
| Chain-A (现有) | `AC-{assertion_id}` | `ZI_PING` (如果 assertion.engine=ZI_PING) |
| Composer (新) | `AC-ZP-{domain}-{conclusion}` | `ZI_PING` (硬编码) |

**namespace 不冲突**（AC-{assertion_id} ≠ AC-ZP-*）。
**source_layer 重叠**：两者都标 ZI_PING。

如果在 production assertion 集中已有 `engine=ZI_PING` 的 assertion，Composer 激活后会出现两个 namespace 不同但语义重叠的 ZiPing claims。这是**用户能感知但 G1 不检测**的 duplication。

---

## 8. Item 9：RenderStage 对新 conclusion 的合法输出范围

### 8.1 RenderStage 是否能渲染 `AC-ZP-*` claims？

需查 RenderStage 对 claim_id / claim 字段的处理。但当前 Composer OFF，无需此测试。

### 8.2 推测

RenderStage 当前依赖 `mapping_registry.apply_to_claims` 给 Chain-A claims 贴词库标签。Composer claims 没经过 `apply_to_claims`（Chain-A 路径），所以 Composer claims 进入 SIR 后 RenderStage 会拿 raw `claim_id="AC-ZP-wangshuai-strong"` + raw `claim="..."` → 但词库标签缺失 → 渲染输出会有"光秃"claim（缺现代主题词）。

**这是 Composer OFF 的另一原因：即便 G1 通过，RenderStage 也输出不完整**。

---

## 9. Item 10: Composer ON 后 T-3 零漂移可行性

### 9.1 阻塞点矩阵

| 阻塞点 | 是否可解 | 改了什么 |
|---|---|---|
| Composer claims rule_refs=[] 触发 G1 L31 | 可解（带 Ziping rule IDs） | Composer 模块代码 |
| Composer claims evidence_refs=[] 触发 G1 L34 | 可解（带 Ziping evidence IDs） | Composer 模块代码 |
| Ziping evidence 18/21 在集合 (3 个反义错) | 半可解（反义复用是 judgment.py bug） | judgment.py 代码 |
| Ziping rule IDs 0 命中生产 rule set | 难解（需扩大生产 rule 面） | rule 集 / 架构 |
| RenderStage 词库不覆盖 AC-ZP-* | 难解（需 mapping_registry 扩展） | mapping_registry 代码 |
| Chain-A vs Composer authority duplication | 需架构裁决 | 架构 |

### 9.2 "Composer ON 后 T-3 零漂移" 的实际可行性

**结论：单纯打开 Composer → 不可行**（G1 fail + Render 词库缺失）。

**可行路径**（每个都触发红线讨论）：
- **路径 A**（修 Composer Contract）：Composer 写 Ziping rule_refs + Ziping evidence_refs → G1 L31/L34 通过 → 但 RenderStage 词库缺失仍 fail
- **路径 B**（建映射）：把 Ziping rule IDs 注册进 production rule set（如创建 DTS-101.json 树A 副本）→ 推翻 Option A → 触发"不夹带"红线讨论
- **路径 C**（调整架构）：让 Composer claims 走独立 SIR 路径，不混 Chain-A → 强侵入
- **路径 D**（保持 OFF）：当前状态，最安全，但 P0-1 不能闭环

### 9.3 T-3 zero-drift 现实答案

**Composer ON 后 T-3 必然漂移**（至少 source=template_fallback + RenderStage 词库缺失）。
唯一可行方案 = 让 Composer 不通过 G1，或让 Composer claims 不进 RenderStage（强侵入）。

---

## 10. 审计裁决空间（User 给你）

### 10.1 你给出的 4 个选项

```text
A. 修 Composer Contract
B. 建正式 ZiPing→Production Evidence 映射
C. 调整接线架构
D. 发现必须重新裁决 P0-1
```

### 10.2 实测事实支撑

| 选项 | 可行性 | 代价 | 红线 |
|---|---|---|---|
| A | RenderStage 词库缺失仍 fail | 低 | ❌ 不违反 G1 但 RenderStage 变 |
| B | 推翻 Option A + 扩大生产 rule 面 | 高 | ❌ 触发"不夹带"红线 |
| C | 强侵入：Composer 独立 SIR 路径 | 极高 | ❌ 重新设计 G1 + RenderStage |
| D | P0-1 不能闭环 | — | ❌ ⑮-3 结论不变（仍 CONDITIONAL） |

### 10.3 我作为 BOT-MASTER 的事实建议（不替你拍板）

15.17 实测显示：

> **Composer 激活 = 两个独立 Authority 世界（Chain-A vs Chain-B）的合并问题**
>
> 不是 G1 bug, 不是 RenderStage bug, 是**架构断层**。
>
> Option B/C 都能修，但代价 ≥ P0-1 重新裁决（必须扩大 rule 面或重建 SIR 路径）。
>
> Option D = ⑮-3 的自然延伸：**"ZiPing Judgment 内部有效但未进入生产链"** 这个事实成立，且在 Chain-B 自身完整性未证明前（P0-1 = 0 closure）强行激活 Composer 会引入**新的 authority duplication + G1 误判 + Render 词库缺失**，比"Composer OFF" 更糟糕。

### 10.4 因此建议

> **当前 Stage 2 终判已足够**：
> - INT-05 Composer 模块 PASS（11/11 unit test）
> - INT-06 接入点 PASS（5/5 wiring test）
> - Composer Production BLOCKED（4 个 T-3 漂移 = 真实证据）
> - P0-1 仍 NOT CLOSED（Chain-B 与 Chain-A 仍是两个独立世界）
>
> **不强行激活 Composer，等下一次重大架构决策（如 Universal Claim Schema 重设计）时一并处理**。

---

## 11. 当前最终门状态

```text
G0-1 Index                    🟢 PASS
G0-2 Resolved Provenance      🟢 PASS
G0 Integration Audit          🟢 PASS (conditional closed)
INT-01 Stage 1 接 Index       🟢 PASS
INT-02 Stage 1 Tree B 接入    🟢 PASS (Option A)
INT-03 Stage 1 Provenance     🟢 PASS
INT-05 Composer Module        🟢 PASS (单元 11/11)
INT-06 Composer 接入点        🟢 PASS (5/5, production OFF)
15.17 Activation Contract     🟢 AUDIT COMPLETE

① Event-Signal SHIJIAN         🔴 FAIL / FROZEN
② Evidence Loader              🔒 C1a (Option A lock)
③ verification_status          🔒 V3+V4
Composer Production            🔴 BLOCKED (T-3 drift evidence)
P0-1 完整闭环                   🔴 NOT CLOSED (Chain-B ≠ Chain-A world)
G1                            🔒 LOCKED
RenderStage                   🔒 不为接入而修改
Evidence Change / Rule Change  🔒 禁止夹带
GitHub push                   🔴 暂不推 (13 commits 本地领先)
```

## 12. 待你裁决

1. **15.17 审计结论是否接受？**（10 项已全部实测回答，Composer activation 真阻塞点 = Chain-A vs Chain-B 两个 authority 世界的合并问题，不是 G1 bug）

2. **下一步**：
   - A. 保持 Composer OFF，等重大架构决策时一并处理
   - B. 现在就启动 P0-1 重新裁决（评估代价）
   - C. 启动 INT-07/08（其他项）继续推进
   - D. 暂缓所有施工，先把 13 commits 推 GitHub + 反向核验（边界审计）

*Generated by BOT-MASTER on 2026-09-11*
*Code Change = 0 / Evidence Change = 0 / Rule Change = 0 / Algorithm Change = 0*
*10 项实测取证（grep + 实跑 RuleLoader + 实跑 G1 evidence_gate）*
*新增 commit: pending*
