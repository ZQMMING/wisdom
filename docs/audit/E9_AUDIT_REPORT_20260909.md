# E9 独立审计裁定报告 — 顺天 V2 九引擎验收

> 审计方: Claude (独立第三方, 独立于所有 Bot 自述) | 落盘: 2026-09-09
> 审计包: `docs/audit/E9_AUDIT_PACKAGE.md` | 关联: `docs/audit/E9_AUDIT_FINDINGS.md` (HEAD 83faadf8 时段另一轮裁定)
> 纪律 (V2 §24): 开发 Bot 不拥有最终验收权; 测试通过≠计算验证≠生产准入; Unexpected SKIP>0 不得 BASIC_VALIDATED; 所有 PASS 裁定附本人复现输出。
> 环境: 独立 worktree `D:/shuntian-e9-audit` (每轮检出对应 HEAD), Python 3.11.15 venv (sxtwl 2.0.7/lunar-python 1.4.8/pytest), iztro 2.6.0+lunar-typescript/lunar-lite。

## Round 1 — HEAD 971a0193 (审计包基准)

7 条命令实测: 全量 `pytest` 224F/2137P/1S/106E + 2 模块不可收集 (非 "643+ passed"); path_independency PASS(510, 有盲区); cross_validate 600/600(100%); cross_engine 7引擎 3次稳定; golden_replay 213案例 3次稳定; E8 三项100%; time_boundary 23/23; 引擎级 boundary/negative 0 失败。

发现清单:
- F-01 P0: 基准 commit 全量测试非绿; 2 模块缺 backend/scripts/shuntian_backfill_clusters.py + canonical.root_evaluator
- F-02 P0: ~30 测试文件 `REPO=parents[2]` 越级 → `D:\docs\*.json` 不存在 (m2b/m2a/edition_registry/knowledge_base/mapping_registry/rule_lifecycle/matcher/audit_gates…)
- F-03 P1: ZIWEI 契约漂移 full_chart() 返 dict, Z11–Z14 期望 ZiweiChart → 65F+12E (计算本身经 600/600+E8 独立验证正确)
- F-04 在途: PT-009/010 evidence_refs 悬空 E-DTS-CONGGE/HUAGE (CORPUS-004, 不计引擎缺陷)
- F-05 P2: 审计包数字失实 review_queue 实测 4180(非5678)/verified 37(非74); blind_seg 74/74 属实
- F-06 P1: 缺失资产 docs/k2g, docs/golden_cases/p014, 外部 MingLi-Bench
- F-07 P2: TONGSHU_AUTH_SECRET fixture 未注入 → 39E
- F-08 P1: task_dispatch/ADJUDICATION_* 裁决文档不在仓库; 3 起越界提交属实 (0df0d893/7db31fb0/e32ff4ee)
- F-09 P2: path_independency 工具盲区 (漏 parents[2])
- F-10 可接受: 唯一 SKIP=test_external_benchmarks (外部 repo 未克隆)
**R1 总判定**: REJECTED-as-full-acceptance/CONDITIONAL; 无 PRODUCTION_ADMITTED; ZIWEI PRODUCTION_VALIDATED(附保留); 其余 7 引擎 BASIC 候选(附保留)。

## Round 2 — HEAD f4d9fe46 (+28af726e/008db04a/44524ae1/f4d9fe46)

已修: F-04 证据链闭环 (276 refs 0 missing); F-07 profile_gate 42/42; F-03 半修 (Z11–Z14 五套件转绿)。
**R-01 (P0)**: 28af726e 把 full_chart() dict→ZiweiChart, 使 4 条命令全红: cross_validate 600/600→**19.5%**, E8 100%→**FAIL**(4/20,6/20,4/20), cross_engine/golden_replay ziwei CHANGED; 无 §21 记录/re-snapshot。
**R2 总判定**: REJECTED (ZIWEI PRODUCTION_VALIDATED 撤销); 全量 161F/94E。

## Round 3 — HEAD 14971678 (+83faadf8/f8369dd8/14971678)

R-01 修复确认: cross_validate→**600/600**, E8→**三项100%** PASS; ziwei 7 套件全绿 (phase_a0 45P…)。
**R-02 (P1)**: 44524ae1/f8369dd8 使 compute_stage 以 24h hour 直调 iztro bySolar, 时间政策换算后 hour 可>23 (实测 31), test_profile_gate 25E 复活 (`wrong hour 31`)。
§21 仍未闭合 (baseline 未 re-snapshot, hash 已确定性 a857630b/dfb00ac3)。
**R3 总判定**: 维持 REJECTED (条件收窄 3 项); 全量 145F/2252P/94E。

## Round 4 — HEAD 769cea0d (+8317b3e9/d929d652/eb670b64/b6593d2c/f4052f64/ac2ca9a1/c789b405/769cea0d)

"修复闭环完成" 声明与事实相反, 本轮引入 3 个新回归:

| 命令 | 14971678 | 769cea0d | 判定 |
|---|---|---|---|
| cross_engine_baseline --check | CHANGED | **PASS 3/3** (ziwei re-record 0457c5fd, 实测匹配) | ✅ |
| golden_replay --check | CHANGED | **ziwei 458054ba→0a9abfa4 仍 CHANGED 3/3 FAIL** | ❌ |
| cross_validate --n 50 | **600/600** | **117/600 (19.5%)** | ❌ |
| e8_ziwei_full_replay | **三项100%** | **命宫4/20,五行6/20,主星4/20 FAIL** | ❌ |
| test_time_boundary | **23/23** | **20/23, 3 FAIL** | ❌ |
| path_independency | PASS | PASS (511) | ✅ |
| 全量 pytest | 145F/94E | 117F/2256P/94E/1S | 改善但 94E 仍在 |

**R-03 (P0, ZIWEI 数据对齐)**: d929d652 把 `time_index=(hour+1)//2` **重新加回**, 把上轮 600/600 打回 **19.5%**/E8 FAIL。同一 bug 第三次反复 (44524ae1 加→f8369dd8 撤→d929d652 再加), 根因未交叉证明即反复开关。
**R-04 (P1, BAZI 时柱)**: c789b405 "bazi_engine hour_pillar 改 solar_date.hour" 破坏立春边界, 3 例 年柱/月柱 干支错位 (P2/P3 立春后 1/34 分钟, expected JIACHEN/BING vs actual GUIMAO/YI)。落在审计重点④, 直接否定 BAZI 边界 PASS。
**R-05 (P0 流程, §21)**: ac2ca9a1/c789b405 声明"五步记录 docs/audit/E9_EXPECTED_CHANGE_ZIWEI_BASELINE.md", 但 `git ls-files` 查无、工作区也不存在。golden_replay 基线 ziwei 停在 458054ba (ac2ca9a1 录), 但 c789b405 使实际序列化再到 0a9abfa4 → 两套基线彼此不一致 (cross_engine 已更, golden 未更)。
**部分残留修复确认**: F-01 2 模块已归档 tests/deprecated ✅; p014 fixture 已建 (13/13) ✅; golden/boundary.py 路径已修 ✅; 但 F-02 parents[2] 组 (m2b 23F/m2a 20F/edition_registry 13F/matcher 16E…) 仍全红。

**R4 总判定**: **REJECTED (维持, 回归面比 R3 更宽)** — "E9 修复闭环完成" 不成立: R-03 重新打破已恢复的 E8/cross_validate, R-04 破坏 BAZI 立春边界, R-05 §21 文档未入库+基线不一致。无引擎 PRODUCTION_ADMITTED; ZIWEI/BAZI 的 VALIDATED 候选再次撤销; 其余 7 引擎维持 BASIC 候选(附保留)。

## 十二维度裁定 (基准 769cea0d)

| 维度 | 裁定 | 证据 (本人输出) |
|---|---|---|
| Specification | PASS | V2 手册 §24/§34/§35 已读 |
| Calculation | PASS(引擎级)/FAIL(系统级) | 引擎套件全绿; 全量 117F/94E |
| Evidence | 闭环 | 276 refs 0 missing; 98%+ UNVERIFIED 如实 |
| Golden | FAIL(流程) | 80/80 可执行, 但 ziwei hash 未 re-record (0a9abfa4) |
| Boundary/Negative | FAIL | test_time_boundary 20/23 (R-04 BAZI 边界回归) |
| Regression | FAIL(流程) | golden_replay ziwei CHANGED 无记录/re-snapshot |
| Integration | PASS | profile_gate 42/42 (R-02 已修) |
| Production Trace | FAIL | E8 三项 4/20,6/20,4/20 + cross_validate 19.5% (R-03) |
| Provenance | PARTIAL | 队列 4180, verified 0.9% |
| Isolation | PASS | cross_engine 3/3 稳定 |
| Repo Integrity | FAIL | R-05 五步文档未入库; 3 起越界历史属实 |

SKIP 核对: 全量 1 skipped = test_external_benchmarks (外部 repo 未克隆, 有注释) → **预期 SKIP, 不触发 §24 违规**。8317b3e9 提及的 "32S" 在 769cea0d 已转 167P (ziwei 7 套件 167 passed, 0 skip)。

## 引擎结论 (769cea0d)

- 无引擎 PRODUCTION_ADMITTED。
- ZIWEI: 候选撤销 (R-03 E8/cross_validate 19.5% FAIL)。
- BAZI: BASIC 候选撤销 (R-04 立春边界 20/23)。
- ZIPING/BLIND/HELUO/MEIHUA/YIJING/HUANGLI: 维持 BASIC 候选(附保留: F-02/F-06 + BLIND 值断言/ZIPING 过渡标准 User 裁决)。
- CORPUS: 在途, 不评审; 证据链悬空项已 CLOSED (CONGGE/HUAGE 入库, 但 c789b405 将二者置 QUARANTINE/disputed — 需 User 知悉)。

## 阻塞项 (闭环前按序, 需附复现输出)

1. **R-03 (P0)**: 对 `time_index` 做**不可回退**裁决 — 撤回到 f8369dd8 恒等口径 (600/600 已知达成), 或证明 (hour+1)//2 正确并重跑 cross_validate 回 ≥99%。验收线: `cross_validate 600/600` + `E8 三项≥95%`。禁止第三次反复。
2. **R-04 (P1)**: 修 bazi_engine hour_pillar 回归, 验收线 `test_time_boundary 23/23`。
3. **R-05 (P0 流程)**: 把 §21 五步文档真正 commit 进 `docs/audit/`; 对 golden_replay ziwei (0a9abfa4) 与 cross_engine (0457c5fd) 做**统一** re-snapshot (当前两基线不一致)。
4. **F-02 (P1)**: m2b 23F/m2a 20F/edition_registry 13F/matcher 16E/knowledge_base 7F 等 parents[2] 组仍全红 — 批量修正。
5. **F-06 (P2)**: docs/k2g, MingLi-Bench 资产。

## 待 User 裁决

1. timeIndex 口径锁定 (R-03): 建议锁"cross_validate=100%"为不可回退验收基线。
2. E-DTS-CONGGE/HUAGE QUARANTINE/disputed (c789b405) 是否接受。
3. F 编号: 修复 commit 自称 "F-04/F-07/F-08" 与本报告 F 编号错位, 建议对齐。
4. §七 原裁决项 (BLIND 真值/SEMANTIC_MATCH/越界口径/PRODUCTION_ADMITTED 全量回放) 维持不阻塞。

## 附: 复现命令快查 (769cea0d 实测)

```bash
cd D:/shuntian-e9-audit   # git worktree @769cea0d
# P0 红线:
.venv/Scripts/python scripts/path_independency_audit.py          # PASS 511
# 7 条复现:
ZIWEI_DATASET_ROOT="D:/顺天系统资料/ziwei-doushu-dataset/ziwei-samples-toolkit" .venv/Scripts/python scripts/ziwei_dataset_cross_validate.py --n 50   # 117/600 19.5% R-03
ZIWEI_DATASET_ROOT="..." .venv/Scripts/python scripts/e8_ziwei_full_replay.py --samples 20 --year 1973                          # 4/20 6/20 4/20 FAIL
.venv/Scripts/python scripts/cross_engine_baseline.py --check     # PASS ziwei 0457c5fd
.venv/Scripts/python scripts/golden_replay.py --check             # FAIL ziwei 0a9abfa4 (未 re-record)
.venv/Scripts/python tests/test_time_boundary.py                  # 20/23 R-04
.venv/Scripts/python -m pytest tests/ -q                          # 117F/2256P/94E/1S
```
