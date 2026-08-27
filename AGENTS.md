# AGENTS.md — Shuntian Governance Dispatch (Skeleton)

> 底本: `shuntian-governance-dispatch` skill（裁剪版）
> 生效基线: `baseline-v1.4-interim-20260823` (8f3b081)
> 细化留给后续专项；本文件只锁定骨架与硬约束。

---

## 1. 权限矩阵

| 角色 | 职责 | 可做 | 不可做 |
|------|------|------|--------|
| **User** | 最终裁定权 | 批准/驳回任务单、终裁冲突、授权越界操作、解除冻结 | 直接改生产代码（须经 Agent 执行链） |
| **Hermes** | 编排与复核 | 拆解任务、派发 dispatch、对照 skill 核验产出一致性、GATE 判定、登记 DECISION_LOG | 自行修复代码、绕过 GATE、未授权改 Golden/DB |
| **Claude** | 首席架构师+审计师 | 全域审计、调用图取证、生产入口链核对、起草裁决方案、复审 commit | 直接 commit 到 master（须 Hermes 复核 + User 终裁）、改 Golden 期望值、降级测试断言 |
| **Codex** | 执行 | 按批准任务单写代码/测试、原子 commit、提交复审 | 自行扩大 SCOPE、顺便重构、改测试语义、动冻结资产、`git add -A`/`git add .` |

**提交链**: Codex 执行 → Claude 复审 → Hermes 核验 → User 终裁。P0 批次须 User 显式批准令方可合并。

---

## 2. 三重取证纪律

任何"引擎 X 是否在生产路径上""测试是否覆盖真实对象"类结论，必须同时满足三重取证，缺一不可：

1. **调用图取证**: `grep`/`rg` 全仓库符号引用，确认生产调用方数量与位置。零调用方 = 孤儿代码，不得假定为生产路径。
2. **生产入口链取证**: 从 API 入口 (`app.py` 路由) → pipeline (`run()`) → stage (`compute_stage` / `render_stage`) → 引擎，逐层追踪实际调用，确认运行时绑定的具体实现（注意 Adapter 层可能改变目标）。
3. **测试对象核对**: 确认测试断言所作用的对象与生产路径为同一实体。注意 import 别名、delegate wrapper、stub/fallback 路径可能导致"测试通过但测的不是生产对象"的 false-green。

**CORRECTED 先例**: `relational_interpretation()` 经 grep 确认为零生产调用方的委托包装；B-11 违禁词断言经核对实际覆盖 `YiInterpretationEngine`（生产引擎）→ 定性 TRUE GREEN。见 `DECISION_LOG_C14_ADDENDUM.md`。

---

## 3. 冻结清单

| 资产 | 状态 | 约束 |
|------|------|------|
| **Golden Dataset** (`backend/dataset/golden_v1/`, `backend/dataset/accuracy/`) | 受保护 | 禁止修改 YAML 期望值；新增 case 须 test-first 独立 commit；13 个失败案例逐条记录，**禁止修期望值凑绿** |
| **紫微 Canonical** | **BLOCKED** | 书目/Passage Registry/流派/四化/时间规则无正式冻结记录；iztro stub 仅在 `TONGSHU_ALLOW_ZIWEI_STUB=1` 下可运行；禁止补算法/星曜/四化 |
| **NFC 端点** | **下线 (501)** | `/daily` `/relationship` `/state` 三端点统一返回 501；保留路由注册；禁止修复 `write_snapshot`/`calculate` |
| **DB 双库** | 现状冻结 | `otcg` (运行时, 28表) 与 `shuntian_kb` (知识库, 115表) 并存，互不干扰；禁止跨库连接混用；otcg 为 backend 默认 DSN |
| **子初（晚子时）换日规则** | B-02 已锚定 | 23:00 真太阳时界后日柱换次日；经 `BaziAdapter` + `TimeResolver` 执行；Golden case `test_2330_bazi_next_day` 为防回归锚；修改须经 Bazi owner + User 批准 |
| **otcg 基线行数** | BUG-06A 恢复 | rules=55 (active30/draft15/validated10), evidence=52, mappings=10；精确等值断言不得降级为 `>=` |

---

## 4. 当前权威指针

以下文件为当前阶段唯一权威事实来源；任何 Agent 产出不得与这些文件冲突，冲突时以这些文件为准：

| 指针 | 路径 | 用途 |
|------|------|------|
| **DECISION_LOG_C14_ADDENDUM** | `docs/audit/step2_decision/DECISION_LOG_C14_ADDENDUM.md` | Yi 引擎生产路径裁决、C-14 孤儿代码框架、B-11 TRUE GREEN 定性 |
| **GOLDEN_BASELINE.md** | `docs/audit/step0_baseline/GOLDEN_BASELINE.md` | Golden 真实数字: LOADED 20 / PASSED 7 / FAILED 13；13 失败清单逐条；3 类失败模式归纳 |
| **REVIEW_BATCH1** | `docs/audit/step3_rereview/REVIEW_BATCH1.md` | BATCH1 复审裁决 (B-07/B-08/B-10/B-05/B-06/B-03a)；测试语义篡改违规先例 |
| **REVIEW_BATCH2** | `docs/audit/step3_rereview/REVIEW_BATCH2.md` | BATCH2 复审裁决 (B-11/B-01/B-02)；晚子时边界对、农历中间事实、Adapter 接入核实 |
| **BASELINE_HASHES** | `backend/docs/audit/step0_baseline/BASELINE_HASHES.sha256` | STEP 0 七件套哈希链 |
| **INTERIM_HASHES** | `backend/docs/audit/step6_interim_baseline/INTERIM_HASHES.sha256` | STEP 6 中期快照哈希链 |

**RESEARCH 线修复顺序**: 先紫微证据集 → 再 Bazi 期望复核 → cross 自动收敛大半。禁止直接改 cross 期望值。

---

## 5. 红线

- 禁止 `git add -A` / `git add .`；只逐路径 add 白名单文件。
- 禁止为让测试通过而降级断言（`assertEqual` → `assertGreaterEqual`）。
- 禁止修改 Golden YAML 期望值来"修复"失败。
- 禁止在未授权情况下写 DB（migration/seed/补数据）。
- 禁止引用已被实测推翻的旧审计数字（如 "32 failed" / "20 PASS"）作为当前事实。

## 6. 编码规范

- **所有 `open()` 调用必须显式携带 `encoding="utf-8"`**——Windows GBK 代码页下无 encoding 参数的 `open()` 读 UTF-8 文件必崩（UnicodeDecodeError），且只在部分 shell 复现，形成"环境相对假绿"。已两次在同一文件栽坑（G-F4 案）。
- 测试中读取外部数据文件同样适用；路径含非 ASCII 时还需注意 MSYS/原生工具的路径转换差异。
