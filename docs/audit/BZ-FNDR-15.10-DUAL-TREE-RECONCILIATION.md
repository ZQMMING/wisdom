# BZ-FNDR-15.10 双树 Evidence Corpus Reconciliation — Audit-only

> **BZ-FNDR-15.10：双树对账（②-C1c 先行）** — 树A `backend/data/evidence` vs 树B `data/evidence`
> **Audit-only / Code=0 / Evidence=0 / Rule=0 / Algorithm=0 / 单文件记录 / 本地 commit / 不推送**
>
> 本记录是 **对账（Reconciliation）产物**，不建 Index、不改 Loader、不裁决基准树。
> 前置：15.9（③ V3+V4 锁定材料）/ User 2026-09-10 裁决"②-C + ②-C1c 先行，C1a/C1b 不预判"。
> 执行：BOT-MASTER（User 授权接管 BOT-ZIPING 任务）；取证 = 全量只读扫描 + 逐文件 SHA-256 比较。

---

## 0. 对账元数据

| 项 | 值 |
|---|---|
| 对账 ID | BZ-FNDR-15.10 |
| 树A | `backend/data/evidence`（生产 RuleLoader 指向，`_JsonRuleBackend` 非递归 glob，15.7 坐实） |
| 树B | `data/evidence`（仓库根；phase_b1/phase_b2 `EvidenceLoader` 所指；5 经典目录 glob `E-*.json`） |
| 树A 末改 | 2026-09-06 17:39 +0800 |
| 树B 末改 | 2026-09-09 15:15 +0800（**更新 3 天**） |
| 排除面 | 两树各 21 个非资源项（`manifest.json` / `provenance_*.json` / `reports/` 7 件 / 各 `_summary.json` / `_insufficient_source.json`） |
| 对账方法 | ID 归并（`evidence_id` 字段）+ 逐文件 SHA-256 + JSON 结构比较 + schema6 合规 + authority/provenance 分布 |
| Code/Evidence/Rule/Algorithm Change | **0** |
| 脚本 | 一次性 `scripts/dts_recon_15_10*.py`（**未 commit**，跑完即弃，不进本 commit） |

---

## 1. ID 全集（对账项 ①②③）

```text
树A: 证据文件 1588 → 唯一 Resource ID 1563（树内 12 个 ID 各占 2 文件，25 文件为多文件对）
树B: 证据文件 5693 → 唯一 Resource ID 5668（树内 12 个 ID 各占 2 文件）
交集: 1562   A-only: 1   B-only: 4106
```

**A-only = 仅 1 条：`E-DTS-145-001`**（树A `di_tian_sui/E-DTS-145-001.json`，
`vs_top=PENDING_VERIFICATION`，auth=BRANCH_STRUCTURE，classical_original）。
树B 无任何 ID 缺失于树A（B-only 4106 为纯增量）⇒ **B 不是严格超集，差 1 条**。

---

## 2. 同 ID 内容（对账项 ④ — 本次最关键产出）

对 1562 共有 ID 中 1550 个单文件对逐 SHA-256 比较：

```text
byte-identical      = 1478
json-same-diff-text =    0
DRIFT               =  72
multi-entry 排除    =  12
```

**72 条 drift 全部在 `blind_seg/`（E-BLIND 家族 72/72，无其他家族）**，且方向单一：

```text
A 侧: source_verification = None / 未填
B 侧: source_verification = {'status': 'VERIFIED'|'SEMANTIC_MATCH',
      'verification_method': 'semantic_comparison',
      'source_url': ..., 'verifier': 'Hermes Agent + web_search', ...}
```

⇒ **B 侧在 72 条 blind_seg 证据上填充了来源核验记录（含 douban 原文定位、逐字摘录、语义核验说明），A 侧为空。方向 = B ⊃ A（信息增量，非改写旧值）。** 72 条中每条 B 侧均显式标注"SEMANTIC_MATCHED ≠ VERIFIED，非逐字匹配"——该标注本身是 ③ provenance 语义的关键样本。

**同 ID 同树双文件（12 组，两树内均存在，构成 Evidence Identity 问题）：**

| ID 模式 | 文件对 | 性质 |
|---|---|---|
| `E-BLIND-C-WORK_CASE-001` | `…-fix-record.json` + `….json` | **同 ID 挂两个不同资源**（fix-record 是修正记录，不是同一证据的两个版本） |
| `E-BLIND-COMPLEX_WORK-002` | 自身 + `E-BLIND-WORK_METHOD-004-fix-record.json` | **fix-record 文件内 `evidence_id` 字段指向了别的 ID**（数据缺陷：记录文件的 ID 被写成被修目标的 ID） |
| `E-DTS-101/103/104/105/106/107-001` | 根级 `E-*.json` + 子目录 `di_tian_sui/E-*.json` | **根级 ↔ 子目录双份同 ID**（两树内均各两份，SHA 树内一致） |
| `E-YHZP-101..104-001` | 根级 + `yuan_hai_zi_ping/` 双份 | 同上 |

⇒ **Resource Identity 三缺陷**（Index 实施前必须裁决）：
1. **同 ID 多资源**（fix-record 混挂）→ ID 不是 1:1 资源句柄；
2. **ID 字段错配**（COMPLEX_WORK-002 文件里写着 WORK_METHOD-004 的 ID）；
3. **根级/子目录双份同 ID**（14 组）→ 即使单树内也需 Logical URI 消歧，路径不再是身份（与你 ②-C 锁定的 `Stable Resource ID ≠ 文件系统路径` 直接相关）。

---

## 3. 树B 独占增量（4106 条 B-only）

```text
家族分布: E-SMTH 1392 / E-DTS 1275 / E-YHZP 964 / E-ZPZ 271 / E-QTB 193 / E-HL 6 / E-ZIWEI 5
schema6 合规: 4100/4106（99.85%）——B-only 增量几乎全合规
树B 独有目录: zi_ping_zhen_quan(271) / huangli(6) / ziwei(5)（新引擎语料）
```

**树B = 树A 全集 + 4106 条增量（其中 4100 条 schema 合规）**；唯一例外 `E-DTS-145-001`（§1）。

---

## 4. schema6 合规对比（对账项 ⑥）

| 树 | 合规 | 不合规 | 缺失分布 |
|---|---|---|---|
| A | 141 | 1434 | rule_refs/citation/source_layer/evidence_strength/version 各 1434（同批抽取资源） |
| B | 4240 | 1440 | 同上（B 的 1440 = A 的 1434 + B-only 中 6 条） |

⇒ 不合规面集中在**同一批抽取语料**（qtb/yh 等 UNVERIFIED 批），两树同源同缺；B 的 4240 合规主力 = 根级 M2 资源 + 五经主力经典目录 + B-only 增量。

---

## 5. authority / provenance 分布对比（对账项 ⑧⑨）

```text
authority_type（两树同 ID 面完全一致）:
  CLIMATE_SEASONAL 1234 / DAYMASTER_STRUCTURE 121 / PRINCIPLE_CONSTRAINT 50
  CONTEXTUAL 50 / COMPLEMENTARY 21 / ELEMENT_IDENTITY 12 / PATTERN_OPERATIONAL 10
  B-only 增量: AUTHORIZED_SOURCE 5（B 独有值）
  A-only: BRANCH_STRUCTURE 1（即 E-DTS-145-001，§1 唯一 A-only）
  <MISSING>: A=76 / B=4177（B 的缺失面 = 大量 B-only 增量未标 authority）

provenance 差异（1550 单文件共有对）:
  vs_top 差异 = 0   vs_cit 差异 = 0
  ⇒ 共有 ID 面两树 provenance 字段无分歧；全部 provenance 差异都在 §2 的 72 条 blind_seg drift（source_verification 填充）
Logical URI / 相对路径（共有 1550 对）: same_rel_path = 1550, diff = 0
```

---

## 6. 非资源排除清单（对账项 ⑦，两树一致）

```text
blind_seg: manifest.json + provenance_final_status / rollback_log / rules /
          validation_report + reclassification_matrix + source_verification_*
          (final_report/report/results) + topic_correction_log   = 10 项
reports/:  _cross_validation_input / _unified_summary / context_validation_*
          (final/report/summary) / semantic_authority_registry /
          semantic_normalization_report                            = 7 项
各目录 _summary.json ×3 / _insufficient_source.json ×1            = 4 项
合计 21 项，Index 实施时全部按"非资源"排除。
JSON 解析错误: 0（两树）
```

---

## 7. 给 C1a / C1b 裁决的输入矩阵

```text
树B: 全集更完整 ✔（A 全量 + 4106 增量，B-only 合规率 99.85%）
      + ID 稳定 ✔（1562 共有 ID 0 冲突；12 组多文件为既有缺陷，两树同构）
      + 无不可接受 drift ✔（72 drift 单向 B→信息增量；0 条 A 独有改写；
         vs_top/vs_cit 共有面 0 分歧）
      + schema/provenance 可治理 ✔（B 合规 4240 > A 141；不合规面同源同批）
      + B 更新 ✔（末改 09-09 vs 09-06）

但存在 3 个 Identity 前置问题（§2），不属"树B 更新就覆盖"可解：
  Q1  12 组同 ID 多文件（fix-record 混挂 / ID 错配 / 根级-子目录双份）
      → Index 的 "ID → 唯一资源" 契约需 Logical URI 消歧规则（你 ②-C 已锁定方向）
  Q2  唯一 A-only = E-DTS-145-001
      → 若选 C1a，该资源需补入树B（1 条，classical_original + BRANCH_STRUCTURE）
  Q3  1440 条 schema6 不合规（同源抽取批）
      → 属 ③ provenance 治理面（V3 分级已含"缺失显式标记"），非树选择问题
```

**Bot 建议（可被否决，不预判结果）：C1a（树B 为 Corpus Base），条件 = 先解 Q1/Q2。**
Q1 按你锁定的 ②-C 原则走 Logical URI + Stable Resource ID 消歧（实施设计阶段）；
Q2 补 1 条资源入树B（属 Evidence Change，需你单独授权，不混入 Index 实施）。
**C1b（维持双树）= 固化 A 残缺镜像为生产事实来源，与你 ②-C "目录扫描不作为事实来源" 原则冲突，Bot 不建议。**

---

## 8. 边界与冻结

```text
✅ Code/Evidence/Rule/Algorithm Change = 0（对账脚本未 commit、不改树内任何文件）
✅ 未建 Index / 未改 Loader / 未裁决基准树（C1a/C1b 待 User 拍板）
✅ 15.6c/15.7/15.8/15.9 不回改；数字引用以本记录 + 15.9 为准
✅ 本地 commit 保持不推（a719bc53 / 14b0b313 / a6933e9b / 7928e1e8 / 本记录）
✅ ① Event-Signal 仍未裁决；G1 未修改；ZIP-INT-01~08 未授权
```

*Generated by BOT-MASTER on 2026-09-10*
*Code: 0 | Evidence: 0 | Rule: 0 | Algorithm: 0 — single-file audit record*
