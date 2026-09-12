# E9 独立审计 — BLIND 盲派引擎（外部独立审计 + 验收修改）

> **审计角色**: 外部独立审计（独立于 BOT-MASTER 自述）；User 指派：BLIND 审计 + 验收修改
> **审计日期**: 2026-09-09
> **审计基线**: `main @ e5ba6e0d`（**脏工作区**：`bazi_engine.py`/`bazi_facts.py` 等未提交改动；`engines/blind/` 包与 `tests/test_blind_rules` 本身干净）
> **规范依据**: 顺天 V2 §3/§22/§24/§44/§46/§47/§48/§51/§55/§59/§60 + AGENTS.md 红线
> **纪律**: 不采信 Bot 自述；所有 PASS 附本人复现；审计角色不改被审引擎算法语义；修改仅限验收补全（测试卫生/夹具），逐项标注于 §6。

---

## 0. 被审对象界定（BLIND = 两个代码体）

| 代码体 | 内容 | 测试 | 生产可达 |
|---|---|---|---|
| **BLIND-A** `engines/blind_bazi_engine.py` + `engines/blind_yingqi.py` | 宾主/体用/做功（12 类）/信号 + 应期三法 | test_blind_golden(21)、test_blind_yingqi(10)、test_blind_signal_regression(5+3sub) | ❌ 无 |
| **BLIND-B** `engines/blind/`（palace.py 宫位 / workgraph.py / workchain.py / evidence_producer.py + palace_rules.json 审核资产） | 宫位计算层（语义从审核资产加载，禁硬编码） | tests/test_blind_rules/（86 例） | ❌ 无 |

§55 盲派专项六项映射：宫位✅（BLIND-B palace）· 宾主✅（main/guest_branches）· 体用✅（ti/yong）· 做功✅（12 类 + workgraph/workchain）· 取象⚠️（仅信号→事件映射，无专门取象模块）· 应期✅（yingqi 三法：大限/禄原身/遁藏透干 + 运年引动冲穿刑合墓库）。

---

## 1. 逐层取证（E0–E10，附本人复现）

### E0 契约 — **PASS**
- `compute_blind_bazi(birth,gender) → BlindBaziResult`；`analyze_yingqi(birth,gender,target_age/year)`；`PalaceFeatureCalculator.compute(chart) → PalaceState`。
- 信号为 `CanonicalSignal`（`source_engine=SourceEngine.BLIND`，带 `evidence_refs`（E-BLIND-*）+ `rule_refs`（BLIND-CAI-001 等）+ 确定性 strength（0.3–0.8））。
- 出生事实**不自造**：两代码体均调 `canonical_bazi_engine.compute`（P0 Gate 正确模式，无 §3 架构违规）。

### E1 单元 — **PASS**
```
pytest tests/test_blind_golden.py tests/test_blind_yingqi.py tests/test_blind_signal_regression.py tests/test_blind_rules -q
→ 122 passed, 3 subtests, 0 failed
```
（数字说明：内部审计"test_blind_golden 36 PASS"实为 4 个文件合计 21+10+5=36，单文件 golden=21——文档数字错位，P2-3。）

### E2 算法 — **PASS（附 P2 观察）**
- 确定性 ✅：`compute_blind_bazi((1990,5,12,10))` 与 `analyze_yingqi(...,40)` 各跑两次，序列化 md5 一致。
- **P2-2 观察（过触发风险）**：样本 1990-05-12 一命局触发 **13 种做功**（比劫制财+穿制七杀+穿制偏财+食伤生财+官杀制比劫+食伤制杀+穿制正财+财制印+印化官杀+墓库收物+暗合+包局+禄神受穿）。V2.2 声称"距离≤2 才作用"后仍近全触发；golden 阈值 `zuo_gong_methods_min: 3` 极低，抓不到此质量退化。**不影响正确性判定，但建议在 Golden 升级时加 `max` 上界或逐例真值。**

### E3 边界 — **PASS（继承 BAZI 基础）**
- BLIND 不自解释出生时间/节气/时区（P0 Gate 合规）；边界 = BAZI 基础边界（时柱 23/23 已复测全绿）。

### E4 负向 — **PASS（验收修改 M-03 已做）**
- 初始取证发现 `analyze_yingqi` 对 `target_age=-5/150`、`target_year=1800/3000`（负年龄/越界年）**静默返回结果**，不 fail-closed → 违反 §55/E4。
- **M-03 修改**：`blind_yingqi.py::analyze` 加设计范围守卫（`0 <= age < 150`，越界 `raise ValueError(...fail-closed)`）；新增 `tests/test_blind_negative.py`（7 例：负年龄/超 150/出生前年/超远年 均断言 `ValueError`；边界 149/0 断言合法；便捷入口继承守卫）。
- 复现：`pytest tests/test_blind_negative.py tests/test_blind_yingqi.py -q → 17 passed`；golden/cross hash 不变（守卫只拒越界输入，合法结果不变）。
- BLIND-A（blind_bazi_engine）入口为定长 birth tuple，负向面在 BAZI 基础（fail-closed 已继承 P0 Gate）。

### E5 Golden — **PARTIAL（真值断言未过，User 裁决项）**
```
python scripts/golden_replay.py --engine blind --check
→ blind: LOAD 20, EXECUTE 20/20 [OK]  hash=29dd863ee7168aa4（与基线一致）
```
- 执行面 ✅（LOAD/EXECUTE 100%、Unexpected SKIP=0）。
- **但 20 例 `blind_golden_set_v2.json` 全部是存在/结构断言**（`has_signals / min_signal_count / strength_range / has_zuo_gong / zuo_gong_methods_min:3`），**无一值断言**；而 `verification_status` 全标 **`VERIFIED`**（20/20）——**验证状态过度声称**（E9 保留项"BLIND 值断言"）。
- schema 缺 §22 必需 `canonical_state / expected_evidence / expected_rule / expected_judgment / provenance`。
- `source` 字段部分循环论证：如 `"《盲派初级命理学》第五章 + 引擎实测"`——**"引擎实测"不是独立真值来源**（拿引擎输出当自己的老师）。
- 结论：案例验收**未过**（与子平同型；执行 100% ≠ 真值 100%）。

### E6 回归 — **PASS**
- replay hash 与基线一致；无"结果不同所以新版对"（§21）。

### E7 集成 — **PASS**
```
python scripts/cross_engine_baseline.py --check
→ ziwei fd3a4cb4 / meihua bcaa91c3 / huangli 103d2022 / blind 8f6ed3a4 / heluo 750a1ee2 / yi cf5b7413 / ziping 63f6ae0a 全部 OK，无引擎被污染
```

### E8 生产 Trace — **FAIL（P0，User 范围裁决项）**
- 三重取证：
  1. 调用图：`BlindBaziEngine / compute_blind_bazi / BlindYingqiEngine / analyze_yingqi / PalaceFeatureCalculator / workgraph` 全仓引用仅自身 + `tests/` + `scripts/golden_replay.py` + `feature_registry/__init__.py`（仅 export）。
  2. 生产入口链：`ComputeStage.run` 只接 bazi/ziwei/huangli/heluo/yi/meihua + signal/cross/temporal；`ADAPTER_REGISTRY`（signal/adapters）只有 `BAZI/HELUO/ZIWEI/HUANGLI/KNOWLEDGE`——**`BlindAdapter` 未注册**；`SignalEngine` 不调 BLIND；`api/`、`services/` 零 "blind" 引用。
  3. 测试对象核对：122 例全测独立入口（`compute_blind_bazi` 等），**非生产实体**。
- 0908 总览"BLIND E8 ProductionTrace ✅（7 引擎接线）"**不成立**（7 引擎指计算层接入，盲派未接线）。
- 结论：BLIND 两代码体均**无生产入口链**，E8 = FAIL。

### E9 独立审计 — **完成（本报告）**

### E10 裁决 — **FAIL（生产准入拒绝）**
- E8=FAIL + E5 案例验收未过 → 不得 PRODUCTION_ADMITTED（§59/§60）。

---

## 2. P0/P1/P2 发现清单

### P0 1 项
- **P0-1 E8 生产入口缺失**（BLIND 两代码体）：同子平辨层型。需 User 定范围：**A 接线生产（注册 BlindAdapter 进 ADAPTER_REGISTRY + ComputeStage 消费）/ B 收口为离线研究能力（OUT-OF-SCOPE）/ C 维持现状（正式记录未达生产）**。

### P1 4 项
- **P1-1 Golden 真值断言未过**：20 例全结构断言却 20/20 标 `VERIFIED`；缺 canonical_state/provenance；部分 source 循环（"引擎实测"）。需 User 裁决真值来源（0908 总览三选一：A 段书真实命例 / B 引擎快照+人工抽检过渡 / C 挂起）。
- **P1-2 死适配器 `BlindSchoolFeatureAdapter`**：field_map 期望 `body/use/guest/host/doing_work/palace_data/ten_god_palace/grave/timing` 九字段，与 BLIND-A（main/ti/yong/zuo_gong…）及 BLIND-B（PalaceState 序列化）**都不匹配** → 恒 0 resolved。属 §56 溯源链路断点（不阻塞计算，阻塞特征层接入）。
- **P1-3 审计基线非干净 commit**（脏树，同子平 P1-3）：结论须落干净 commit 复核。
- **P1-4 缺 BLIND 专属负向/边界测试（✅ M-03 已修）**：已补 `tests/test_blind_negative.py`（7 例）+ `blind_yingqi.analyze` 越界 fail-closed 守卫。E4 由 PARTIAL → PASS。

### P2 3 项
- **P2-1 §55 取象**无专门模块（信号事件映射部分覆盖）。
- **P2-2 做功过触发**（样本 13 类全触发；golden 无 max 上界）。
- **P2-3 内部文档数字错位**："test_blind_golden 36 PASS"=4 文件合计，单文件实为 21。

### 测试卫生（✅ 已修改，见 §6）
- **P1-5→已修**：`test_mingli_bench_blind.py` 3 例 **unexpected FAIL**（CWD 相对路径 + 数据集缺失无守卫）→ 改为期望 SKIP + 路径锚定仓库根（未动断言）。修后全量 4 skipped 均为期望型（外部数据集未克隆），**Unexpected SKIP=0**。

---

## 3. 与内部文档的对照

`docs/audit/BLIND_ENGINE_AUDIT_20260909.md`（BOT-MASTER）称：
> "36 + 3 subtests PASS；Golden Replay PASS；Cross-engine OK；**BLIND = ENGINE_CALCULATION_VALIDATED 候选**"

本审计核对：
- 36+3sub、replay、cross-engine 数字**属实且复现** ✅
- 但内部审计**未报 E8（生产入口）**、**未报 golden 结构断言=VERIFIED 的过度声称**、未报 P1-2/P1-4——即其"计算层闭环"结论回避了案例验收与生产 Trace 两关。
- E9 报告（User 已采信）裁定 BLIND="BASIC 候选（附保留：BLIND 值断言）"，与本审计一致；**"ENGINE_CALCULATION_VALIDATED 候选"（内部自述状态名）不在 V2 三态生命周期内，属非规范状态名**（P2，文档规范问题）。

---

## 4. §46 十八问应答

1. 验收哪个 Engine？ **BLIND（盲派，BLIND-A 算/信号/应期 + BLIND-B 宫位/做功图 两代码体）**
2. Engine Version？ **无显式版本**（无 engine_version 声明）
3. Calculation Version？ **未声明**
4. 使用哪个 Canonical State？ **BaziEngine.compute → BaziChart（canonical_bazi_engine）**；Golden 未记录 canonical_state（P1-1）
5. Golden Case 多少？ **20（blind_golden_set_v2.json，replay 加载集）**
6. 是否 100% Execute？ **是（20/20）**
7. Unexpected Skip 是否 0？ **是（0；全量 4 skipped 均为外部数据集期望 SKIP）**
8. Boundary 是否通过？ **通过（继承 BAZI 基础；BLIND 不自解释出生）**
9. Negative 是否通过？ **通过（M-03 已补 BLIND 专属负向测试 + fail-closed 守卫；越界 target 抛 ValueError，边界 149/0 合法）**
10. Regression 是否通过？ **通过（replay/cross_engine hash 稳定）**
11. Integration 是否通过？ **通过（无跨引擎污染）**
12. Production Replay 是否完成？ **否（E8：两代码体无生产入口链，P0-1 待 User 范围裁决）**
13. Provenance 是否完整？ **不完整（缺 calculation_version；golden 缺 provenance/canonical_state；feature 适配器死链 P1-2）**
14. Isolation 是否通过？ **通过（§55：不 import 子平判断/紫微；仅依赖 BAZI facts 层 ten_god/藏干/禄刃表——共享基础事实合规，无隐式 ZiPing Judgment）**
15. Independent Audit 是否完成？ **完成（本报告）**
16. P0 数量？ **1**
17. P1 数量？ **4（P1-1..P1-4）；其中 P1-4（负向）与 P1-5（mingli_bench）已由 M-03/M-01 修好；剩余未决 P1 = P1-1（golden 真值）/ P1-2（死适配器）/ P1-3（脏树）**
18. 最终状态？ **E10 = FAIL；生命周期：至多 BASIC 候选（附保留），案例验收（P1-1）未过则不达 BASIC_VALIDATED；生产准入拒绝，待 User 裁决 P0-1 范围**

---

## 5. 生命周期裁决（§60）

```
BASIC_VALIDATED      → 未达（E5 案例验收未过：结构断言全标 VERIFIED + 无值断言/真值）
PRODUCTION_VALIDATED → 不可达（E8 FAIL + E5 未过）
PRODUCTION_ADMITTED  → 拒绝
```
与 E9 裁定（"BLIND 维持 BASIC 候选（附保留）"）一致；按子平行先例（User 裁定"案例验收未通过"），BLIND 同型未过 → **NOT BASIC_VALIDATED**，除非 P1-1 真值升级经 User 裁决通过。

---

## 6. 修改清单（验收修改，本次已做 / 建议待做）

**已做（2 项，未 commit，交 User/提交链处置）：**
| # | 文件 | 内容 | 红线核对 |
|---|---|---|---|
| M-01 | `tests/test_mingli_bench_blind.py` | 数据集路径 `./MingLi-Bench`（CWD 相对）→ 锚定仓库根 `_REPO_ROOT`；加 `@unittest.skipUnless(_DATASET.exists(), ...)` 整类期望 SKIP；删除冗余 CWD sys.path 行 | 未改任何断言强度；未碰 Golden；`open(..., encoding="utf-8")` 保留；未 git add/commit |
| M-03 | `src/tongshu/engines/blind_yingqi.py` + 新增 `tests/test_blind_negative.py` | `analyze` 加设计范围守卫（`0<=age<150`，越界 `raise ValueError(...fail-closed)`）；新增 7 例负向/边界测试（越界 target_age/target_year 断言抛错，边界 149/0 断言合法） | 只拒越界输入，**不改任何合法结果/算法语义**（golden/cross hash 实测不变）；未降级断言；未 git add/commit |

**待做（需 User 裁决后执行，均为"加强"非"削弱"）：**
- **M-02（P1-1）**：User 定真值来源后，为 20 例补 `canonical_state + expected_evidence + expected_rule + expected_judgment + provenance`；`verification_status` 改为与真值核验一致（未核验的不得标 VERIFIED）；加 1–2 例**值断言**（如某例 `zuo_gong_methods` 必含/必为指定集合）。
- ~~**M-03（P1-4）**~~ ✅ **已完成**：补 `tests/test_blind_negative.py`（7 例负向/边界）+ `blind_yingqi.analyze` 越界 fail-closed 守卫。E4 → PASS。
- **M-04（P1-2）**：`BlindSchoolFeatureAdapter` 字段 map 对齐真实输出（BLIND-A `to_dict` 或 BLIND-B `PalaceState`），或标注 DEPRECATED。
- **M-05（P0-1 若选 A）**：`BlindAdapter` 注册进 `ADAPTER_REGISTRY` + `ComputeStage` 消费 + E8 生产 Trace 测试（断言 SourceEngine.BLIND 信号在场）。
- **M-06（P1-3）**：脏树处置（提交/stash）后在干净 commit 复测全部本报告数字。

---

## 7. 复现命令快查

```bash
cd D:/shuntian
git status --porcelain        # P1-3: 应为空
# E1 单元(122+3sub):
PYTHONPATH=src .venv/Scripts/python -m pytest tests/test_blind_golden.py tests/test_blind_yingqi.py tests/test_blind_signal_regression.py tests/test_blind_rules -q
# mingli_bench(期望 SKIP 3):
PYTHONPATH=src .venv/Scripts/python -m pytest tests/test_mingli_bench_blind.py -q -rs
# E5/E6 Golden + 回归:
.venv/Scripts/python scripts/golden_replay.py --engine blind --check
.venv/Scripts/python scripts/cross_engine_baseline.py --check
# E8 生产入口验证(应 0 命中):
git grep -n "BlindBaziEngine\|compute_blind_bazi\|BlindYingqiEngine\|PalaceFeatureCalculator" -- src/tongshu/api src/tongshu/services src/tongshu/pipeline_stages src/tongshu/reasoning
# 确定性:
PYTHONPATH=src .venv/Scripts/python -c "from tongshu.engines.blind_bazi_engine import compute_blind_bazi; import json,hashlib; f=lambda x: hashlib.md5(json.dumps(x,sort_keys=True).encode()).hexdigest(); a=f(compute_blind_bazi((1990,5,12,10),'male').to_dict()); b=f(compute_blind_bazi((1990,5,12,10),'male').to_dict()); print(a==b)"
```

---

## 8. 待 User 裁决

1. **P0-1 BLIND 生产范围**：A 接线生产（M-05）/ B 离线 OUT-OF-SCOPE / C 维持现状记录。
2. **P1-1 Golden 真值来源**（0908 总览三选一）：A 段建业书真实命例 / B 引擎快照+人工抽检（过渡，明示"快照基线≠真值"）/ C 挂起（E5 保持未过）。
3. **M-01 修改采纳**：`test_mingli_bench_blind.py` skip 守卫 + 路径锚定（已改未 commit）。

**签核**: 外部独立审计 | 2026-09-09 | 依据 V2 §44/§46/§55/§59/§60
> 本报告只记录与取证 + 1 项测试卫生修改（M-01）；**未改**被审引擎算法、**未改** Golden 期望值、**未** git add/commit。
