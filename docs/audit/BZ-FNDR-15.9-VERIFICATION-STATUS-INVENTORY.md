# verification_status 全仓盘点（BZ-FNDR-15.9）

> **BZ-FNDR-15.9：ZIP-PRE-04 前置纯审计盘点 —— verification_status × authority_type × G1**
> **Audit-only / Code=0 / Evidence=0 / Rule=0 / Algorithm=0 / 单文件记录 / 本地 commit / 不推送**
>
> 本 commit 是 **事实盘点记录（Inventory Record）**，不是 G1 裁决、不是实施。
> 执行者：BOT-MASTER（User 2026-09-10 授权"替代 BOT-ZIPING 完成 ③ 纯审计盘点"）。
> 目的：把真实数据语义摸清，供 User 直接对 ③ 落最终裁决。**未预设 pending=BLOCK 或 pending=PASS。**
> 取证方式：`backend/data/evidence/` 全量 `rglob` 逐文件解析（1596 文件）+ `git show HEAD` 已提交代码 + `docs/evidence.schema.json`，全部只读。

---

## 0. 盘点元数据

| 项 | 值 |
|---|---|
| 盘点 ID | BZ-FNDR-15.9 |
| 前置记录 | 15.6c（a719bc53）/ 15.7（14b0b313）/ 15.8（a6933e9b） |
| 扫描面 | `backend/data/evidence/` 全量 = **1596 个 .json**（rglob） |
| 对照代码 | `HEAD:src/tongshu/audit_validation/gates/g1_evidence.py` / `_rule_backends.py` / `docs/evidence.schema.json` |
| Code/Evidence/Rule/Algorithm Change | **0 / 0 / 0 / 0** |
| 附带订正 | 1 处（15.7 §2 的"1503"算术错误 → 实为 **1417**，见 §9） |
| Git push | **不推**（User 口径：本地存在 ≠ GitHub 已验证） |

---

## ① 实际取值（全仓）

**顶层 `verification_status` 字段（1596 文件）：**

| 取值 | 数量 | 说明 |
|---|---|---|
| `UNVERIFIED` | **1412** | 抽取批占位值（非 schema enum） |
| `<缺失>` | **164** | 字段不存在（多为 blind_seg 86 + 根级 M2 时代资源） |
| `SOURCE_VERIFICATION_REQUIRED` | 14 | 非 enum（blind_seg 时代） |
| `CASE_SOURCE_VERIFICATION_REQUIRED` | 4 | 非 enum（blind_seg 案例层） |
| `PENDING_VERIFICATION`（全大写） | 1 | **大小写变体**：di_tian_sui/E-DTS-145-001（classical_original） |
| `{'pending_source_verification': 8, 'direct_verified': 58}`（dict） | 1 | blind_seg/manifest.json（聚合 manifest，非证据资源） |
| **合计** | **1596** | JSON 解析错误 = **0** |

**嵌套 `citation.verification_status` 字段（schema v1.1 M2-A 规定的字段）：**

| 取值 | 数量 |
|---|---|
| `<缺失>` | 1515 |
| `pending_verification` | 43 |
| `verified` | 30 |
| `not_applicable` | 6 |
| `cross_verified` | 2 |

**schema enum（`docs/evidence.schema.json` v1.1/v1.2，M2-A）：**

```text
["verified", "cross_verified", "pending_verification", "disputed", "not_applicable"]
机械映射规则: BAZI-00x 双源→cross_verified / paraphrase(待校)→pending_verification
              / 工程种子→not_applicable / 无核验记录(35条ZPZ逐字)→缺省
```

**关键对照事实**：顶层出现的 6 种值**全部不在 schema enum 内**；enum 值全部只出现在嵌套 `citation.verification_status`。`disputed` 全仓 **0 出现**。

---

## ② 资源分布（按位置 × 可见性）

| 位置 | 文件数 | 生产 RuleLoader 可见性（非递归 glob，15.7 §2 坐实） | 取值特征 |
|---|---|---|---|
| **根级**（E-DTS/E-GW/E-YHZP/… M2 时代） | **86** | ✅ **可见（唯一可见面）** | 顶层多缺失，嵌套承载 enum 值（43 pending + 30 verified + 6 not_applicable + 2 cross_verified 的主体） |
| qiong_tong_bao_jian | 1233 | ❌ | 100% 顶层 UNVERIFIED + authority_type=CLIMATE_SEASONAL + source_layer 缺失 |
| yuan_hai_zi_ping | 119 | ❌ | 顶层 UNVERIFIED 为主 |
| di_tian_sui | 45 | ❌ | UNVERIFIED 44 + PENDING_VERIFICATION 1（大小写变体）；classical_original + PRINCIPLE_CONSTRAINT |
| blind_seg | 86 | ❌ | 顶层缺失/REQUIRED 系；含 1 manifest（dict 值） |
| ziping_zhenquan | 11 | ❌ | UNVERIFIED（PATTERN_OPERATIONAL） |
| san_ming_tong_hui | 9 | ❌ | UNVERIFIED |
| **reports/**（7 个） | 7 | ❌ | **审计输出产物**（context_validation_*/_cross_validation_input/semantic_*），**不是证据资源** |
| 合计 | **1596** | 可见 86 / 不可见 1510 | — |

**五经子目录证据资源 = 1233+119+45+11+9 = 1417**（不含 blind_seg 86 与 reports 7）。
⚠️ 15.7 §2 登记的"1503"为算术错误，**本记录订正为 1417**（见 §9）。

---

## ③ status × source_layer × authority_type 组合（实测）

```text
vs=UNVERIFIED (1412):
  × layer=缺失 × auth=CLIMATE_SEASONAL        1233   (qtb 抽取批)
  × layer=缺失 × auth=DAYMASTER_STRUCTURE      117   (yuan_hai 等)
  × layer=缺失 × auth=ELEMENT_IDENTITY           8
  × layer=classical_original × PATTERN_OPERATIONAL 10
  × layer=classical_original × PRINCIPLE_CONSTRAINT   44

vs=缺失 (164, 顶层):
  × layer=classical_original × CONTEXTUAL       30
  × layer=classical_original × DAYMASTER_STRUCTURE  2
  × layer=engineering_seed  (各组合)             11
  × layer=paraphrase        (各组合)             43   ← 根级 paraphrase 顶层不填

vs=SOURCE_VERIFICATION_REQUIRED (14) / CASE_... (4):
  × layer/auth 全缺失 (blind_seg 时代 schema 前)

vs=PENDING_VERIFICATION 大写 (1): di_tian_sui/E-DTS-145-001
vs=dict (1): blind_seg/manifest.json
```

**嵌套侧**：`pending_verification(43) 主体 = 根级 paraphrase 资源`；`verified(30) = 30 条 E-ZPZ cluster 成员（M2-B 程序化逐字一致断言，继承 passage verified，schema 注释明确"机械继承，非模型推断"）`；`cross_verified(2) = BAZI-00x 双源`；`not_applicable(6) = 工程种子`。

---

## ④ 语义一致性（同值异义？——有，分三层）

1. **顶层 vs 嵌套是两套字段，互补而非互斥**：同文件双值一致（0 处不等）；顶层缺 164 中含嵌套有值的 81 个（43+30+6+2）。顶层 `UNVERIFIED` ↔ 嵌套缺失 是抽取批的"未核验"占位；嵌套 enum 值 是 M2-A/B 时代"有核验记录"的正式状态。**顶层 UNVERIFIED 与嵌套 verified 语义不能合并解读。**
2. **`UNVERIFIED` 是批占位，不是状态判定**：qtb 1233 条同值但来自不同核验语境（semantic batch 统一打标），**不能读作"逐条审过但未验"**——这是 ④ 最大的语义陷阱。
3. **大小写变体**：`PENDING_VERIFICATION`（di_tian_sui，1 条）vs enum `pending_verification`（43 条）——**同义异写**，任何按字符串分级的 G1 策略必须先归一。
4. 结论：`verification_status` **当前没有全仓统一的单一语义**，分"抽取批占位 / 根级核验记录 / blind_seg 时代 REQUIRED 系"三套语系。

---

## ⑤ G1 当前行为（代码复核，HEAD 已提交版）

`g1_evidence.py` `evidence_gate()` 全函数 5 校验面（15.7 §3 已登记，本次复核一致）：

```text
claims 非空 / rule_refs 非空 / evidence_refs 非空且可解析(传 evidence_ids 时)
/ source_layers 非空 / claim_id 必须 AC-*
```

- `verification_status`（顶层 + 嵌套）：**0 读**。
- `source_layer`（资源层 classical_original/paraphrase/engineering_seed）：**0 读**（G1 的 `source_layers` 是 claim 级枚举标签，不是资源字段）。
- `authority_type`：**0 读**。

---

## ⑥ 生产影响（当前事实）

```text
生产可见 evidence = 根级 86 文件（非递归 glob）。
其中 ZiPing 相关（根级 E-DTS-* / E-YHZP-* / E-GW-* 等）的
citation.verification_status = pending_verification 者 → G1 静默放行，与 verified 生产等价。

⇒ 用户问"pending / verified / unverified 是否事实等价放行" = 是，全部等价。
⇒ DTS-106 根级资源（paraphrase + pending_verification）当前也以"证据已挂"外观过 G1，
   与 15.7 §4 DTS-106 ENGINEERING-DEFINED 登记联动：若 ③ 采分级策略，
   该资源在分级下应标 PROVENANCE-PENDING（非 BLOCK，非静默经典），与裁决③自洽。
```

---

## ⑦ 异常值登记

| 异常 | 事实 | 处置建议（仅登记） |
|---|---|---|
| dict 值 | `blind_seg/manifest.json` `verification_status = {'pending_source_verification': 8, 'direct_verified': 58}` | manifest 非证据资源；实施 Loader 策略（②）时按"非资源文件"排除 |
| reports/ 7 文件 | 审计输出 JSON（context_validation_* / semantic_* / _cross_validation_input / _unified_summary） | 同上，Loader 实施时排除；不计入 evidence 面 |
| 大小写变体 | `PENDING_VERIFICATION` × 1（di_tian_sui） | 分级策略必须先做取值归一（PENDING_VERIFICATION ≡ pending_verification） |
| 非 enum 顶层值 | UNVERIFIED(1412) / SOURCE_VERIFICATION_REQUIRED(14) / CASE_SOURCE_VERIFICATION_REQUIRED(4) | 属 schema v1.1 前体系；③ 裁决需明确"legacy 值归哪一档" |
| 缺失 | 顶层 164 / 嵌套 1515 | 缺失本身即信号（无核验记录），分级须含"缺失"档 |
| `disputed` | enum 有、全仓 0 出现 | 无现状样本；策略可预留档 |

---

## ⑧ 裁决输入矩阵：verification_status × authority_type × G1

**归一化取值域（建议基线，供裁决，非预设）**：

```text
G-VERIFIED        = verified / cross_verified        （嵌套, 30+2）
G-PENDING         = pending_verification / PENDING_VERIFICATION / SOURCE_VERIFICATION_REQUIRED / CASE_SOURCE_VERIFICATION_REQUIRED（归并）
G-NOT_APPLICABLE  = not_applicable（工程种子, 6）
G-UNVERIFIED      = UNVERIFIED（抽取批占位, 1412）
G-MISSING         = 字段缺失（顶层 164 / 嵌套 1515）
G-DISPUTED        = disputed（预留, 0）
```

**G1 分级策略候选（全部列清，不预设选择）：**

| 候选 | 语义 | 代价/风险 |
|---|---|---|
| **V1 现状** | 不读 status（全等价放行） | 0 改动；DTS-106 等工程规则以"证据已挂"外观放行（已知缺陷，15.7 §3） |
| **V2 全 BLOCK pending 系** | G-PENDING/G-UNVERIFIED/G-MISSING → BLOCK | 误伤面最大：生产可见 86 根级里 pending/paraphrase 居多 → **ZiPing 链整体 G1 不可用**（与 P0-1 接通目标互斥） |
| **V3 分级放行 + 标记** | G-VERIFIED → 全放行；G-PENDING/G-UNVERIFIED/G-MISSING → 放行但 claim 标 `PROVENANCE-PENDING`（非 BLOCK）；G-DISPUTED → BLOCK；G-NOT_APPLICABLE → 放行 + 标 `ENGINEERING` | 改动最小、不阻塞 P0-1 接通、claim 层可辨识（与 DTS-106 S6 "Claim 必须能看出工程规则判断" 对齐）；代价：标记字段进 claim schema（需随 composer 版本走，与 X-1a `AC-ZP-*` 命名一致扩展） |
| **V4 与 ② Loader 联动** | status 分级只作用于"Loader 可见 + Index 可解析"的资源；不可见资源维持 15.7 结论（unresolved → BLOCK） | ②③ 必须同批裁决，避免索引结构与分级策略返工 |

**BOT-MASTER 倾向（可被否决，仅登记）**：**V3 + V4 联动**——"分级放行 + PROVENANCE-PENDING 标记"是唯一既保 G1 唯一 Gate、又不把 ZiPing 生产链整体 BLOCK 掉的形态；V2 与 P0-1 目标互斥。

---

## 9. 订正记录（1 处，报告事实纠错）

```text
15.7 §2 登记 "1503 个 evidence 资源生产不可见" = 算术错误。
实测: 五经子目录 = 1233+119+45+11+9 = 1417; 子目录全部 = 1417+86(blinseg)+7(reports) = 1510。
⇒ 订正为: 五经证据资源 1417 个生产不可见（子目录全量 1510，其中 14 个为 manifest/审计输出，非证据资源 = 1496）。
15.7 其余结论（非递归 glob、生产只见根级 86）不受影响。
```

---

## 10. 边界与冻结记录

```text
✅ 0 代码 / 0 evidence / 0 rule / 0 algorithm 改动（全量 rglob 只读扫描）
✅ G1 未修改；本记录未预设 pending=BLOCK / pending=PASS
✅ 15.6c / 15.7 / 15.8 不回改（15.7 的 1503 以本记录 §9 为订正注记）
✅ a719bc53 / 14b0b313 / a6933e9b / 本 commit 全部保持本地不推
✅ 施工门未变: ① Event-Signal ☐ / ② Loader ☐ / ③ verification_status ☐ / ZIP-INT-01~08 🔴 未授权
⇒ ③ 裁决材料 = 本记录 §8 矩阵；User 裁决 ③ 后与 ②（Loader）联动定案，再入 BOT-ZIPING 任务单
```

*Generated by BOT-MASTER on 2026-09-10*
*Code change: 0 | Evidence change: 0 | Rule change: 0 | Algorithm change: 0*
*Files modified: 1 (this inventory record only)*
