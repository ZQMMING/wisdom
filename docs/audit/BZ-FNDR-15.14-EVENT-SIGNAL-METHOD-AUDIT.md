# ⑮-1-EVENT-SIGNAL 方法审计（BZ-FNDR-15.14）

> **BZ-FNDR-15.14：⑮-1-EVENT-SIGNAL 子项 —— 事件信号方法链纯审计**
> **Audit-only / Code=0 / Evidence=0 / Rule=0 / Algorithm=0 / 单文件记录 / 本地 commit / 不推送**
>
> 前置：① 裁决（15.12 §1，严格 FAIL-CLOSED + 独立方法审计 + 否决白名单 + BLIND 禁用）。
> 核心问题：**现有 Canonical Bazi Facts / ZiPing Features，究竟有没有足够的经典依据 + 明确方法规则，
> 合法、确定性地推出 ZiPing 的 Event Signal？**
> 执行：BOT-MASTER（User 授权，选择 C：先审方法再写代码）。全部只读取证。

---

## 0. 审计元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.14 |
| 前置 | 15.12（① 落槌）/ 15.7 ZIP-PRE-01（event 生产链取证） |
| 审计对象 | 6 候选：冲 / 刑 / 害 / 合 / 三合 / 空亡 |
| 取证面 | 代码（bazi_engine / judgment / signal_engine / spec）+ 规则（data/rules 全量）+ 语料（data/evidence 全量关键词普查） |
| 禁止项遵守 | 未建 mapping / 未改 judgment·signal_engine / 未新增 event_type / 未借 BLIND / 语料只作检索对象 / 未写 EVENT_ABSENT / 未动 Corpus / 未动 G1 |
| Code/Evidence/Rule/Algorithm Change | **0** |

---

## 1. 审计链条逐层事实

### 1.1 ① 结构事实层（Canonical Fact → Feature）—— **PASS**

`bazi_engine.py` 全部 6 候选的结构计算**真实存在并接入 BaziChart**（确定性，O(1) 查表）：

```text
calc_branch_clash_map  L502  →  branch_clash_map   (L805/831)
calc_branch_harm_map   L520  →  branch_harm_map    (L806/832)
calc_branch_he_map     L535  →  branch_he_map      (L808/833)
calc_branch_sanhe_map  L554  →  branch_sanhe_map   (L809/834)
calc_branch_sanxing_map L585 →  branch_sanxing_map (L810/835)
calc_kong_wang         L719  →  kong_wang          (L812/836)
+ 日支级: calc_day_branch_clash L457 / calc_day_branch_harm L471
```

⇒ **"结构事实存在"对所有 6 候选成立**（①-d 第①类 = PASS）。
但 15.6b N-2 已坐实：`build_context` 只取 4 柱+日主，**这 6 个 map 一个都没进 Judgment Context**——
结构事实"已算"≠"已消费"，Feature 通道尚未打通（属 ② ZIP-INT-02 范畴，非本审计对象）。

### 1.2 ② 经典语义层（Corpus B 检索，仅作证据存在性普查）

`data/evidence` 全量 5693 资源关键词命中（资源数）：

```text
冲: 293 (逢冲29/相冲17/冲克14)   刑: 638 (三刑29/相刑26/自刑17)
害: 321 (六害16/相害3)           合: 1290 (六合53/相合34/合局35/合财10)
三合: 97 (三合局1/成化4)         空亡: 85 (落空16/旬空1)
```

⇒ 经典文本对这 6 类结构的语义讨论**存在且量大**（①-d 第①类 = 存在）。
**但按 ①-d 铁律：关键词命中 ≠ 语义证据成立，更 ≠ 方法证据。**
本审计只做存在性普查，未逐条做语义验证（那属于未来方法审计的 Evidence Provider 环节）。

### 1.3 ③ 方法规则层（"如何判成事件"）—— **ABSENT，FAIL**

决定性取证：

```text
grep -rli 'shijian|event_signal|event_type|事件信号'  data/rules/  backend/data/rules/
     = 0 命中
```

**不存在任何 ZiPing SHIJIAN 方法规则。** 全仓含冲/刑/害/合语义的规则（MAR-103/104、HLT-101~306、
SMTH-105、SX-101/102、MK-103~105、WLT-104、DTS-106 等）逐条核读后定性：

```text
它们全部是【其他断事域】的 EVENT_TOPIC 断事规则:
  HLT-*  = 健康断事   produces_signal_type = HEALTH_RISK
  MAR-*  = 婚姻断事   produces_signal_type = MARRIAGE_RISK / MARRIAGE_OPPORTUNITY
  CRR/EDU/SUY/WLT = 事业/教育/寿夭/流年   CHANGE / SUPPORT
  SMTH-105 = 神煞判定   SUPPORT(降级)
  DTS-106  = 旺衰判定   CONSTRAINT (已裁 ENGINEERING-DEFINED)
```

这些规则消费的 `conditions.field`（`branch_clash_map` / `day_branch_clash` / `day_branch_harm` 等）
产出的是 **domain 断事 signal（HEALTH_RISK/MARRIAGE_RISK…）**，走 `produces_layer_output_template`，
**与 SHIJIAN Judgment 消费的 `event_types` 是两套不同机制**（SHIJIAN 走 `s.get("event_types")`，L1019）。
⇒ "有冲刑害断事规则" **不能** 冒充 "SHIJIAN 事件方法已定义"（正是 ①-b 禁止的偷换）。

**SHIJIAN 的 `event_types` 生产点 = 0**（`signal_engine.py` L358 `event_types=[]` 恒空，全 src 无第二生产点，15.7 坐实）。

### 1.4 ④ Event Mapping 层（"合法转换成 SHIJIAN Event Type"）—— **ABSENT，FAIL**

```text
SHIJIAN 域: 无 event_type 枚举定义、无映射表、无方法审计记录。
BLIND: 全仓唯一产 event_type 的引擎（blind_bazi_engine.py）——①-f 明确禁用为 ZiPing oracle。
```

⇒ 没有任何已审证据表明 "冲→某 event_type / 刑→某 event_type …" 的 ZiPing 专属映射成立。

---

## 2. 逐候选审计矩阵（15.14 主产出）

| Candidate | ① 结构事实 | ② 经典语义 | ③ 方法规则 | ④ Event Mapping | 审计结论 |
|---|---|---|---|---|---|
| 冲 | PASS（clash_map/dash_clash 已算） | 存在（293 资源，未逐条语义验证） | **ABSENT**（SHIJIAN 方法规则 0） | **ABSENT**（无 ZiPing 冲→event_type 映射） | **FAIL** |
| 刑 | PASS（sanxing_map 已算） | 存在（638 资源） | **ABSENT** | **ABSENT** | **FAIL** |
| 害 | PASS（harm_map 已算） | 存在（321 资源） | **ABSENT** | **ABSENT** | **FAIL** |
| 合 | PASS（he_map 已算） | 存在（1290 资源） | **ABSENT** | **ABSENT** | **FAIL** |
| 三合 | PASS（sanhe_map 已算） | 存在（97 资源） | **ABSENT** | **ABSENT** | **FAIL** |
| 空亡 | PASS（kong_wang 已算） | 存在（85 资源） | **ABSENT** | **ABSENT** | **FAIL** |

**读法**：6 候选全部 **① PASS、② 存在、③ ABSENT、④ ABSENT**。
按 ①-d 铁律"只有④成立才能进入 Event Resolver"——**③④ 双缺失 ⇒ 无一候选可进未来 Event Resolver。**

> 结论取 **FAIL 而非 UNKNOWN** 的理由：③④ 层经 grep 全仓普查证明"不存在"（确定性缺席），
> 不是"不确定是否有"。UNKNOWN 保留给未来方法审计中"输入不足/证据不足"的情形（①-e 表）。

### 2.1 附：既有其他域规则的正确定位（防混淆）

```text
HLT/MAR/SMTH/SX/MK/WLT 的冲刑害规则
  = 健康/婚姻/神煞/流年断事域的 EVENT_TOPIC 断事规则
  ≠ ZiPing SHIJIAN 事件信号方法
  ⇒ 它们的存在不构成 SHIJIAN 的方法依据，也不得被借来"顺手"打开 ① 门。
  （DTS-106 旺衰域已单独裁 ENGINEERING-DEFINED，同理各域规则归属各自域，跨域不污染。）
```

---

## 3. 对 ① 门与 ZIP-INT-04 的回写（仅登记，不实施）

```text
⑮-1-EVENT-SIGNAL 方法审计结果 = FAIL(③④ 缺失)
  ↓
① SHIJIAN 维持严格 FAIL-CLOSED（UNKNOWN），15.12 ①-a 语义不变
  ↓
ZIP-INT-04 event 部分 G0-3 未解锁 —— 维持锁定，禁止施工中夹带 event mapping
  ↓
未来打开 ① 需要(全部满足):
  (a) 为 6 候选(或其子集)建立 ZiPing SHIJIAN 专属 event_type 枚举 + 映射方法
  (b) 每类完成 ② 经典语义 + ③ 方法规则 + ④ 事件映射 三层独立审计(①-d 三类证据分层)
  (c) 非 BLIND oracle、非语料检索直接生成、非跨域规则借用
  (d) Resolved Provenance 携带 ③-V3 标记(pending 不得升级 verified)
  在此之前: 无 event_signal → SHIJIAN = UNKNOWN(非 EVENT_ABSENT)
```

---

## 4. 边界与冻结

```text
✅ Code/Evidence/Rule/Algorithm Change = 0（本审计 0 改动，语料仅作只读检索对象）
✅ 未建任何 Event Mapping / 未新增 event_type / 未借 BLIND / 未写 EVENT_ABSENT
✅ judgment.py / signal_engine.py / G1 / Evidence Corpus 均未触碰
✅ 15.12 ① 裁决不回改；本记录 = ①-a fail-closed 的实证支撑
✅ 本地 commit：a719bc53…16e1d47e…本记录 全部不推
⇒ G0-3（⑮-1-EVENT-SIGNAL 审计 PASS）= 未达成；G0-1/G0-2 是否可施工仍由 User 审核本记录后裁决
```

*Generated by BOT-MASTER on 2026-09-10*
*Code: 0 | Evidence: 0 | Rule: 0 | Algorithm: 0 — single-file method audit record*
