# BZ-FNDR-15.17b — 21 Ziping Rule ID 深度调研 + Composer Activation 重新评估

> **Audit-only / Code=0 / Evidence=0 / Rule=0 / Algorithm=0 / 单文件审计记录**
>
> 前置：User 2026-09-11 锁定 15.17 正式架构结论（Layer 1 + Layer 2 双层问题）
> User 指示：继续挖 21 个 Ziping rule IDs 与 backend/data/rules / data/rules / CITATION / RuleLoader 关系
> 目的：确认这些规则是否本应属于 ZiPing 独立规则域，还是强行纳入 136 Production Rules

---

## 0. 元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.17b |
| 前置 | 15.17 commit `1842c2bc` |
| 状态 | **AUDIT COMPLETE** |

---

## 1. 15.17 错误修正（实测取证）

### 1.1 错误结论（15.17 §2.2 实测时）

> "Ziping rule IDs 在生产 RuleLoader.rules (136 条) 中 0/21 命中（0%）"

### 1.2 错误根因

我之前实测用 `for r in loader.rules: r.rule_id` 和 `'DTS-101' in loader.rules`，但 `loader.rules` 实际是 `list[dict]`：
- `loader.rules` 是 list 不是 dict（不是 `.keys()` 而是迭代 dict 元素）
- `r` 是 dict 元素，没有 `.rule_id` attribute
- `'DTS-101' in loader.rules` 检查 string in list（永远 False）

### 1.3 重新实测（取 prod_ids 集合）

```python
prod_ids = {r["rule_id"] for r in pipeline.rule_matcher.rules if isinstance(r, dict)}
→ 21 个 Ziping rule IDs 全部命中
```

### 1.4 修正后事实

```text
21/21 全部命中生产 RuleLoader.rules (136 条)
全部 status=draft
全部 applies_to_layers=['BASELINE']
分布在:
  DITIANSUI       book: 15 条 (含 DTS-101~107 等)
  YUANHAI-ZIPING  book: 19 条 (含 YHZP-101/104/105 等)
  ZIPING-ZHENQUAN book: 32 条 (含 ZPZ-101/105~108/110/111/120 等)
```

**修正后的 Layer 2 关键事实**：
- Ziping rule IDs 不是"两个 authority 世界"
- 是"**Production Rule Set 已包含 ZiPing draft rules**，但 status=draft 表明它们尚未被正式 Admission"
- Composer activation = **让 draft rules 通过 AC-ZP-* claims 进入生产 face**

---

## 2. Composer activation 实测（带 Ziping refs）

### 2.1 测试方法（一次性探针）

```python
# 关掉 production Composer OFF, monkey-patch 注入 Ziping 真实 refs
prod_rule_ids = {r["rule_id"] for r in pipeline.rule_matcher.rules ...}
prod_ev_ids = pipeline._evidence_ids

# Composer claim 输出 rule_refs/evidence_refs = dj.rule_refs ∩ prod_rule_ids
# Composer claim 输出 evidence_refs = dj.evidence_refs ∩ prod_ev_ids

# 强制打开 ComputeStage.run(judgment_composer=...)
result = pipeline.run(...)
```

### 2.2 实测结果

```text
validation_passed: False
source: template_fallback
ZP claims: 3
  - AC-ZP-wangshuai-weak
    rules: ['DTS-102', 'DTS-106', 'DTS-105']
    ev:    ['E-DTS-101-001', 'E-DTS-106-001', 'E-DTS-105-001']
  - AC-ZP-geju-broken
    rules: ['ZPZ-111', 'ZPZ-106', 'ZPZ-110', 'DTS-106']
    ev:    []
  - AC-ZP-yongshen-primary
    rules: []
    ev:    []
```

### 2.3 Gate-by-gate 失败原因（实测 run_gates）

```text
FAIL G1:
  - AC-ZP-geju-broken: empty evidence_refs (Evidence existence)
  - AC-ZP-yongshen-primary: empty rule_refs (Rule linkage)
  - AC-ZP-yongshen-primary: empty evidence_refs (Evidence existence)

PASS G2 / G3

FAIL G4: Traceability: meta missing, G1 blocked
```

### 2.4 Layer 2 实测结论

**Composer activation 在技术上"部分可行"**：
- ✅ 4 个域中**有完整 Ziping refs 的 claim（如 wangshuai）G1 通过**
- ❌ **refs 不全的域（geju, yongshen）仍 fail**——但根因不在 G1 校验，而在 **DomainJudgment 自身 refs 缺失**
- ❌ G4 仍 fail（Traceability meta 缺失）

**为什么 "refs 不全"** —— 这是 judgment.py 自身问题：
- `judgment.py L691` 对 YONGSHEN 域 `rule_refs.append("DTS-106")` 但 evidence_refs 不齐
- `judgment.py L588-621` YHZP/ZPZ 部分域 judgment 退出 UNKNOWN 时未填 refs
- 这是 **judgment.py 算法问题，不是 Composer activation 问题**——但 Composer 暴露了它

---

## 3. ZiPing rule status 全盘点（实测）

```text
生产 RuleLoader.rules (136 条) by status:
  active:     75
  draft:      51
  validated:  10

by layer:
  BASELINE:        75
  EVENT_TOPIC:     56
  DAILY_ACTIVATION: 5
```

51 条 draft 规则中包含：
- 所有 21 个 Ziping rule IDs（DTS/YHZP/ZPZ/SMTH）
- 部分其它引擎的占位 rule
- 激活 Composer = 让这 21 条 **draft** ZiPing rules 通过 AC-ZP-* claims **进入生产 face**

**架构风险**：
- "draft" 表示规则尚未通过 Rule Admission 流程
- 强行激活 = 让 draft rules 的 authority 进生产
- 即便 AC-ZP-* 与 AC-* namespace 不冲突，**逻辑 authority 是 draft 级别**
- 用户最终看到的"判断" = 基于 draft 规则的 claim → 工程风险 = 真信 = 误判

---

## 4. RenderStage 词库缺失（仍未触碰）

不管 G1/G4 是否通过，RenderStage 对 AC-ZP-* claims 没有 mapping_registry 词库标签：
- `mapping_registry.apply_to_claims(atomic_claims)` 只为 Chain-A claims 加 `mapping_refs` + `modern_theme`
- Composer claims 不经过 `apply_to_claims`，所以 AC-ZP-* claims **裸进 RenderStage**
- RenderStage 渲染 → 输出"光秃"claim，**缺现代主题词**

实测中 source=template_fallback 大概率源于 RenderStage 词库缺失触发 fallback，而不只是 G1 fail。

---

## 5. 修正后的架构结论（User 已锁定的延伸）

### 5.1 Layer 1 (15.17 已锁定)

> Composer claims `rule_refs=[]` / `evidence_refs=[]` 本身违反 G1 硬门槛

**但实测修正**：这不是"避免 ID 冲突"——是因为 `judgment.py` 部分 DomainJudgment 自身 refs 不全。

### 5.2 Layer 2 (本次修正)

> **Composer activation 不是"两个 authority 世界的合并问题"，而是"draft rule authority 进入 production face 的工程风险"**。

具体表现：
1. 部分域 refs 完整（如 wangshuai）→ G1 通过
2. 部分域 refs 不全（如 geju/yongshen）→ judgment.py 算法问题暴露
3. 即使全部 refs 补齐 → 21 条 draft rules 通过 AC-ZP-* 进生产 face
4. RenderStage 词库缺失 → AC-ZP-* claim 渲染"光秃"

### 5.3 修正后的正式结论

> **Composer activation 在技术上"部分可行但部分域 fail"——根因不是 G1 设计错误，而是 (a) judgment.py 部分域 refs 不全（算法问题）+ (b) 21 条 ZiPing draft rules 尚未通过正式 Rule Admission（生产准入问题）+ (c) RenderStage mapping_registry 不覆盖 AC-ZP-* 命名空间（词库覆盖问题）。**
>
> 解决路径不是"修 G1"，而是 (a) 修 judgment.py 算法 (b) 走 Rule Admission 把 21 条 draft 升 active (c) mapping_registry 扩展。
>
> 但 (b) 是 **rule admission 重新评估**，不是简单的"激活 Composer"。
>
> **因此原 15.17 §10 4 选项仍然成立**：D (Composer OFF) 仍是当前最稳的唯一选择。

---

## 6. 4 选项现状（不替 User 拍板）

| 选项 | 可行性（实测后） | 代价 | 触发红线？ |
|---|---|---|---|
| A. 修 Composer Contract | 部分可行（要补 judgment.py 算法缺陷） | judgment.py 改动 | ⚠️ Stage 1 红线 |
| B. 建映射 + 走 Rule Admission | 21 条 draft 升 active | 重新走 admission 流程 | ⚠️ Rule 准入面变更 |
| C. 重构 SIR/G1 | 不必要（G1 不是 bug） | 极高 | ❌ 明确否决 |
| D. Composer OFF | 当前状态 | 0 | ✅ 维持 |

---

## 7. 当前门状态（修正）

```text
G0-1 Index                       🟢 PASS
G0-2 Provenance                  🟢 PASS
INT-01~03 Stage 1                🟢 CLOSED
INT-05 Composer Module           🟢 MODULE PASS
INT-06 接入点                     🟢 CODE PASS
15.17 Activation Contract        🟢 AUDIT COMPLETE
15.17b 21 Rule ID 深度调研        🟢 AUDIT COMPLETE (本次, 含 Layer 2 修正)

Composer Production              🔴 BLOCKED (T-3 drift + draft rule authority)
P0-1 完整闭环                     🔴 NOT CLOSED
SHIJIAN Event-Signal             🔴 FAIL / FROZEN
G1                               🔒 LOCKED (实测非 G1 bug)
RenderStage                      🔒 不为 Composer 接入而修改
GitHub push                      🔴 暂不推 (14 commits 本地领先)
```

---

## 8. 待你裁决

1. **15.17b Layer 2 修正**是否接受？（15.17 §2.2 的 "0/21 命中" 实测方法错误，修正为 "21/21 命中但全 status=draft"）

2. **下一步方向**：
   - 维持 D (Composer OFF)，把 P0-1 NOT CLOSED 作为已知架构债
   - 启动 **15.18 Rule Admission Audit**：评估 21 条 ZiPing draft rules 升 active 的工程流程
   - 启动 **15.18b Judgment Algorithm Audit**：评估 judgment.py 部分域 refs 不全的算法缺陷修复路径
   - 暂缓，启动 INT-07/08 其他项

*Generated by BOT-MASTER on 2026-09-11*
*Code Change = 0 / Evidence Change = 0 / Rule Change = 0 / Algorithm Change = 0*
*Layer 2 实测取证（run_gates + composer ON 探针）*
*探针脚本 (scripts/test_composer_on_with_real_refs.py) 已删除*
