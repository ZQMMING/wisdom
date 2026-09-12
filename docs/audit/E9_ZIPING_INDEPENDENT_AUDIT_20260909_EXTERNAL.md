# E9 独立审计 — ZIPING 子平引擎（外部独立审计）

> **审计角色**: 外部独立审计（独立于 BOT-MASTER / BOT-ZIPING 自述）
> **审计日期**: 2026-09-09
> **审计基线**: `main @ e5ba6e0d`（工作区**脏**：`src/tongshu/engines/bazi_engine.py`、`src/tongshu/facts/bazi_facts.py`、`tests/test_bazi_branch_relations_oracle.py` 等存在未提交改动）
> **规范依据**: 顺天 V2《验收和生产准入规范》§1/§3/§44/§46/§47/§48/§49/§51/§52/§56/§59/§60
> **纪律**: 开发 Bot 不拥有最终验收权；测试全绿 ≠ 引擎正确；"其他引擎 PASS → 本引擎可上线" 被禁止（§47/§48）。本报告所有 PASS 均附本人复现输出，未采信任何 Bot 自述。

---

## 0. 被审对象界定（先说清楚"子平引擎"= 什么）

按 V2 架构 **算 → 辨 → 解**：

| 层 | 归属 | 生产路径 | 状态 |
|---|---|---|---|
| **算**（四柱/十神/大运/流年/干支关系） | BAZI 基础设施 + `facts/bazi_facts` + `bazi_ten_gods` | ✅ 在 `ComputeStage`（`BaziEngine` / `BaziAdapter` / `ten_god`） | 生产可达 |
| **辨**（旺衰/格局/用神/十神/事件 五域判断） | `reasoning/judgment.py` + `reasoning/ziping_bridge.py` | ❌ **不在生产**（仅 scripts/tests 可达） | **孤儿** |
| **解**（渲染/输出） | `render/*`（LLM/模板） | ✅ 在 `RenderStage` | 非子平专属 |

规范 §56 要求子平验收含 **旺衰/格局/用神**（即"辨"域）。**User 2026-09-09 定案**：子平生产验收范围收口为**算层**，"辨"层（旺衰/格局/用神）**不接线生产**（离线/研究，OUT-OF-SCOPE）。据此：
- 子平"生产准入"只考核**算层**是否在生产路径（= BAZI 基础设施，已达）；
- "辨"层不作为生产准入项，其 E8 记为范围外；
- 但**整体子平验收仍未通过**——因为 **E5 Golden 案例验收未通过（User 裁定）**，子平连 BASIC_VALIDATED 都未达成。

---

## 1. 逐层取证（E0–E10，附复现输出）

复现环境：`D:\shuntian\.venv`，`PYTHONPATH=src`，`PYTHONIOENCODING=utf-8`。

### E0 契约 — **PASS**
- 五契约齐备（Input/Output/Version/Provenance/Error）。`run_ziping_judgment` 对空 chart **fail-closed → UNKNOWN**（不崩、不猜、不静默默认）。
- 复现：`tests/test_ziping_bridge.py` 含 `Empty() → UNKNOWN` 用例；空 day_master 时 `judge_all` 各域 fail-closed。

### E1 单元 — **PASS**
```
pytest tests/test_ziping_bridge.py tests/test_ziping_golden.py -q
→ 46 passed in 1.32s（bridge 6 + golden 40，0 failed，0 skipped）
```
（注：内部审计把 46 记为"test_ziping_bridge"，实为 bridge+golden 合计；另 `test_phase3_p0_judgment.py` 14 例同属判断层，未计入此 46。）

### E2 算法 — **PASS**
- 五域 Judgment 为**确定性条件判断**，核心三域有序依赖（旺衰→格局→用神），无跨域投票/加权/概率。
- 判断引用真实 rule_ref（`DTS-101/104/105`、`YHZP-101` 等，已核文件存在）。
- 复现（确定性 + 域结论）：
```
庚午 戊寅 乙丑 壬午 (1990-05-12 10时) → 旺衰=MODERATE / 格局=ESTABLISHED(阳刃格) / 用神=PRIMARY(格局用神)
同输入两次 → bazi 与 ziping 结果完全一致（deterministic=True）
```

### E3 边界 — **PASS（继承自 BAZI 基础设施）**
- 子平边界 = 八字基础设施边界（节气前后/瞬间、23:59/00:00、23:00/01:00、DST/时区/真太阳时）。
- 复现：`pytest tests/test_bazi_boundary.py test_bazi_global_timezone.py ...` 归入 BAZI 基础套件全绿（§52 BAZI 专项）。子平未自造边界解释 → 未触发 §3 P0 架构违规（✅ 符合"统一出生事实"入口）。

### E4 负向 — **PASS**
- 空/缺字段 → UNKNOWN；非法输入 fail-closed。`tests/test_ziping_bridge.py::test_run_ziping_judgment_fail_closed` 类用例通过。

### E5 Golden — **FAIL（P1，User 裁定 2026-09-09）**
```
python scripts/golden_replay.py --engine ziping --check
→ ziping: LOAD 25, EXECUTE 25/25 [OK]  hash=2008d32871b512b3（与基线一致）
```
- LOAD=100%、EXECUTE=100%、Unexpected SKIP=0（执行面合格，但执行 ≠ 案例验收）。
- **但** 25 例 schema 仅有 `case_id/category/description/input/expected_calculation/source/human_verified_result`。
  对照 §22 必需字段，**缺 `canonical_state / expected_evidence / expected_rule / expected_judgment / provenance`**。
  （对比：`ziwei_golden_set.json` 80 例含 `canonical_state + expected_evidence + expected_judgment + provenance + engine_version`；`ziping` 无。）
- **User 裁定（权威）**：「子平整个审计验收 —— **案例验收未通过**」。即 25 例 Golden 的**真值/人工核验**未获接受（`human_verified_result` 为叙述性文本，非对 `canonical_state` 的可复核值断言，且 §56 回溯链未编码）。
  → **E5 判 FAIL**（案例验收未通过，非仅 schema 缺口）。此裁定直接否决 §60 中"Golden 100% executed"作为 BASIC_VALIDATED 的充分条件。

### E6 回归 — **PASS**
- 上条 `golden_replay --check` 与基线 hash 一致；`cross_engine_baseline --check` ziping `63f6ae0ae64b81b3` 稳定。无"结果不同所以新版对"（§21）。

### E7 集成 — **PASS**
- 复现：`python scripts/cross_engine_baseline.py --check`
```
ziwei/meihua/huangli/blind/heluo/yi/ziping 全部 OK，无引擎被污染
```

### E8 生产 Trace — **FAIL（P0）→ User 定案：辨层不接线生产**
- **三重取证**（§AGENTS.md 纪律）：
  1. 调用图：`run_ziping_judgment / synthesis_to_dict / JudgmentFactory` 全仓引用仅 `scripts/golden_replay.py`、`scripts/cross_engine_baseline.py`、`tests/*`、`docs/*`。**生产目录（`src/tongshu/api`、`services`、`pipeline_stages`）零引用。**
  2. 生产入口链：`POST /v1/daily-guide`、`/v1/calculate` → `pipeline.run` → `ComputeStage.run`。`ComputeStage` 仅调用 bazi/ziwei/huangli/heluo/yi/meihua + signal + cross_domain + temporal，**不调用 `reasoning/judgment` 或 `ziping_bridge`**。
  3. 测试对象核对：46 例测的是 `BaziEngine→run_ziping_judgment` 独立链路，**非生产实体**（生产链路根本不经过它）。
- `app.py:645` 注释自证："需要 Debug/Research 观测面时应基于新架构（assertion_v2/judgment_architecture）重建"——即新判断架构**未接入生产**。
- 结论：子平"辨"层（§56 的旺衰/格局/用神）**无生产入口链**。`d3cd7fba` 声称"解决 judgment.py 零生产调用方"，实为**新建了零调用方的 bridge 模块**，并未真正接线生产。E8 = **FAIL**。
- （对照：ziwei/huangli/meihua/yi/heluo 均在 `ComputeStage` 内，生产可达；唯"辨"层为孤儿。）
- **User 裁定（2026-09-09）**：「**不能接线生产**」——辨层**不**纳入生产接入。据此，辨层的 E8 由"待修复 P0"转为"**范围外（OUT-OF-SCOPE）**：辨层为离线/研究能力，正式不进入生产"。子平生产验收范围收口为**算层**（四柱/十神/大运/流年，已在生产）；辨层五域判断**不得**作为生产准入依据。

### E9 独立审计 — **完成（本报告）**
- 不采信 BOT 自述；全部 PASS 附本人复现；E8 FAIL 与内部 `ZIPING_ENGINE_AUDIT_20260909.md` 的"PRODUCTION_ADMITTED(历史)"直接冲突（见 §3）。

### E10 裁决 — **FAIL（生产准入拒绝）**
- E5（案例验收）FAIL（User 裁定）+ 辨层 E8 范围外（User 定案不接线生产）。子平**不得** PRODUCTION_ADMITTED（§59/§60）。

---

## 2. P0/P1 发现清单

### P0（阻塞生产准入）— 已由 User 定案收口
- **P0-1 E8 生产入口缺失 → User 定案（2026-09-09）「不能接线生产」**：子平"辨"层（`reasoning/judgment.py` + `ziping_bridge.py`，五域判断）确认**不**纳入生产接入，转 OUT-OF-SCOPE。子平生产验收范围收口为**算层**（四柱/十神/大运/流年，已在 `ComputeStage` 生产路径）。
  > 该 P0 不是"待修复缺陷"，而是**范围裁决**：辨层为离线/研究能力，正式不进入生产，不得再在总览/审计中写 PRODUCTION_ADMITTED。

### P1 3 项
- **P1-1 Golden schema 不完整 + 案例验收未通过（User 裁定，E5=FAIL）**：ziping 25 例缺 `canonical_state/expected_evidence/expected_rule/expected_judgment/provenance`（§22 必需）；且真值/人工核验未获接受。ziwei 已具备全 schema，ziping 未对齐。**此项为当前子平未达 BASIC_VALIDATED 的主因。**
- **P1-2 权威指针失效**：`AGENTS.md §4` 权威指针 `docs/audit/step0_baseline/GOLDEN_BASELINE.md`（"LOADED 20 / PASSED 7 / FAILED 13"）**磁盘上不存在**（`step0_baseline/` 仅存 `BASELINE_HASHES.sha256`、`TEST_BASELINE.md` 等）。Agent 被要求引用的权威事实源缺失/过期。
- **P1-3 审计基线非干净 commit**：本次审计跑在 `main@e5ba6e0d` **脏工作区**（`bazi_engine.py`/`bazi_facts.py` 等未提交）。结果反映未提交改动，非可复现的干净基线——与 §42/§50 仓库完整性、可复核要求冲突。

### P2（顺带记录，非子平专属）
- 数字矛盾：V2 总览(0908) ZIPING "21 tests / E10=COND" vs 内部审计(0909) "46 PASS / PRODUCTION_ADMITTED(历史)" vs E9 报告(0909) "ZIPING=BASIC 候选(附保留)、无引擎 PRODUCTION_ADMITTED"。三份同日文档互相冲突。
- 系统级 §21 未闭合：E9 报告 R-05 指出 ziwei golden hash 未 re-record、cross_engine 与 golden 两套基线不一致（属 ZIWEI/系统，阻塞整体准入，非子平缺陷）。

---

## 3. 与内部文档的矛盾（须 User 澄清）

`docs/audit/ZIPING_ENGINE_AUDIT_20260909.md`（BOT-MASTER/Hermes 自述）称：
> "ZIPING = PRODUCTION_ADMITTED (历史) ✅ ... 唯一已 PRODUCTION_ADMITTED 引擎 (user_verified=true)"

但同日 `docs/audit/E9_AUDIT_REPORT_20260909.md`（项目自委的独立 E9 审计方）裁定：
> "无引擎 PRODUCTION_ADMITTED；ZIPING/BLIND/HELUO/MEIHUA/YIJING/HUANGLI：维持 **BASIC 候选（附保留）**"

两者**直接矛盾**。按 §24"开发/运维 Bot 不拥有最终验收权"，E9 独立审计方裁定优先于 BOT-MASTER 自述；且本审计 §1 E8 复现证实"辨"层无生产入口，**当前状态下 PRODUCTION_ADMITTED 不成立**。"历史 PRODUCTION_ADMITTED"若无当时 E8 生产 Trace + 独立审计 + 仓库完整性留痕，则按 §60 不能延续到今天（且 BZ-FNDR 系列重构 BAZI 事实层后，下游依 §51/§31 需重新 Golden Replay + 回归 + 审计）。

> **User 确认（2026-09-09）**：`E9_AUDIT_REPORT_20260909.md` 即权威独立审计，User 已亲自阅读并采信其裁定（"无引擎 PRODUCTION_ADMITTED，ZIPING 仅 BASIC 候选(附保留)"）。BOT-MASTER `ZIPING_ENGINE_AUDIT_20260909.md` 的"PRODUCTION_ADMITTED(历史)"定性为**越权自述、作废**。矛盾就此定论，无需再澄清。

---

## 4. §46 十八问应答

1. 验收哪个 Engine？ **ZIPING（子平）；经 User 2026-09-09 定案，生产验收范围 = 算层（四柱/十神/大运/流年），"辨"层（旺衰/格局/用神）为离线能力、OUT-OF-SCOPE 不接线生产**
2. Engine Version？ **无显式版本声明**（判断层无 `engine_version`；pipeline 硬编码 `reasoning=1.0.0`）→ 溯源缺口
3. Calculation Version？ **未声明**（`judgment.py` 无 calculation_version）
4. 使用哪个 Canonical State？ **BaziEngine.compute → BaziChart（canonical_bazi_engine 单例）**；但 Golden 夹具未记录 `canonical_state`（P1-1）
5. Golden Case 多少？ **25**
6. 是否 100% Execute？ **是（25/25）**
7. Unexpected Skip 是否 0？ **是（0）**
8. Boundary 是否通过？ **通过（继承 BAZI 边界，BAZI 基础套件全绿）**
9. Negative 是否通过？ **通过（fail-closed → UNKNOWN，已测）**
10. Regression 是否通过？ **通过（replay/cross_engine hash 稳定）**
11. Integration 是否通过？ **通过（无跨引擎污染）**
12. Production Replay 是否完成？ **否——算层走 BAZI 生产路径，但子平专属"辨"层已定案 OUT-OF-SCOPE（不接线生产）；Production Replay 对算层随 BAZI 基础，子平未单独完成生产 Trace**
13. Provenance 是否完整？ **不完整（缺 calculation_version；Golden 缺 expected_evidence/provenance）**
14. Isolation 是否通过？ **通过**
15. Independent Audit 是否完成？ **完成（本报告）**
16. P0 数量？ **1（P0-1，已由 User 定案收口为"辨层 OUT-OF-SCOPE 不接线生产"，不再作为待修复缺陷）**
17. P1 数量？ **3（P1-1 Golden 案例验收未通过 + schema 不完整 / P1-2 权威指针失效 / P1-3 脏基线）**
18. 最终状态？ **NOT BASIC_VALIDATED；E10 = FAIL（生产准入拒绝）。依据：E5 案例验收未通过（User 裁定）→ §60 BASIC_VALIDATED 不成立；辨层 E8 OUT-OF-SCOPE（不接线生产）。子平当前仅"算层"在生产路径，整体验收未通过，不得 PRODUCTION_ADMITTED。**

---

## 5. 生命周期裁决（§60，经 User 2026-09-09 裁定更新）

```
BASIC_VALIDATED      → 不可达（E5 Golden 案例验收未通过，User 裁定；§60 要求 Golden 通过）
PRODUCTION_VALIDATED → 不可达（E5 FAIL + 辨层 E8 OUT-OF-SCOPE）
PRODUCTION_ADMITTED  → 不可达（生产准入拒绝）
```

**最终：E10 = FAIL；子平未达 BASIC_VALIDATED（案例验收未通过）；生产准入拒绝。**
- "辨"层（旺衰/格局/用神 五域判断）= 离线/研究能力，**不接线生产**（User 定案）。
- 子平"算层"（四柱/十神/大运/流年）随 BAZI 基础设施在生产路径，但其专属验收（案例/Golden）当前未通过。

---

## 6. 闭环建议（User 2026-09-09 裁决后更新）

**P0-1（E8 生产接线）— ✅ 已由 User 定案**：「不能接线生产」→ 取原 B/C 口径，辨层（旺衰/格局/用神）为离线/研究能力，**OUT-OF-SCOPE，不接线生产**。子平生产验收范围收口为**算层**。后续总览/审计**不得**再把"辨层"作为生产准入项，也不得写 PRODUCTION_ADMITTED。

**当前主阻塞 = P1-1（E5 案例验收未通过，User 裁定）**：子平要推进到 BASIC_VALIDATED，需先闭合 Golden 案例验收：
- 为 25 例补 `canonical_state + expected_evidence + expected_rule + expected_judgment + provenance`（对齐 ziwei schema）；
- 将 `human_verified_result` 升级为**对 canonical_state 的可复核值断言**（而非叙述性文本），并记录核验人/时间/版本；
- 逐条确认 25 例真值来源（经典条款/权威命例），未获人工接受的例不得计入"通过"。

**P1-2**：恢复/重建 `GOLDEN_BASELINE.md`（或更新 `AGENTS.md §4` 指针指向真实存在的文件）。
**P1-3**：审计改在**干净 commit** 上执行（先提交或 `git stash` 未提交改动后复测），使结果可复核。
**系统级**：闭合 §21（ziwei golden re-record + 两套基线统一），由 ZIWEI/系统 owner 负责。

---

## 6b. 附注 — E9 R-04（BAZI 立春边界）复检（当前树）

E9 报告在 `769cea0d` 裁定 **R-04 (P1, BAZI 时柱立春边界回归 20/23)**。本次在**当前树 `e5ba6e0d`**（BZ-FNDR 系列之后）复测：

```
PYTHONPATH=src .venv/Scripts/python tests/test_time_boundary.py
→ 测试结果: 23/23 PASS, 0 FAIL
```

**结论：R-04 已在当前树修复（立春 P2 组 23 例全绿）。** BAZI 基础设施 P0 Gate 的时柱边界当前为绿，子平 E3（继承 BAZI 边界）的 PASS 判定因此更稳固。

> 注意：此复测跑在**脏工作区**（P1-3），正式结论须落到干净 commit 复核（§7 复现命令第 1 步）。

---

## 7. 复现命令快查

```bash
cd D:/shuntian
# 先固定干净基线（当前为脏树）:
git status --porcelain      # 应为空
# E1 单元:
PYTHONPATH=src .venv/Scripts/python -m pytest tests/test_ziping_bridge.py tests/test_ziping_golden.py -q
# E5/E6 Golden + 回归:
.venv/Scripts/python scripts/golden_replay.py --engine ziping --check
.venv/Scripts/python scripts/cross_engine_baseline.py --check
# E8 生产入口验证（应证 0 命中 = 无生产调用方）:
git grep -n "run_ziping_judgment\|ziping_bridge\|JudgmentFactory" -- src/tongshu/api src/tongshu/services src/tongshu/pipeline_stages src/tongshu/pipeline.py
# BAZI 基础(P0 Gate)回归:
PYTHONPATH=src .venv/Scripts/python -m pytest tests/test_canonical_state.py tests/test_bazi_engine.py tests/test_bazi_boundary.py tests/test_bazi_ten_god_oracle.py -q
```

---

**签核**: 外部独立审计 | 2026-09-09 | 依据 V2 §44/§46/§59/§60
> 本报告只记录与取证，**未修改**被审代码、未改 Golden 期望值、未 commit（提交链归 User/其 Agent）。
