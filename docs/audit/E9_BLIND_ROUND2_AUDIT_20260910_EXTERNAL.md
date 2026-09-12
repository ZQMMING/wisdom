# E9 独立审计（第二轮）— BLIND 盲派引擎

> **审计角色**: 外部独立审计（User 指派；独立于 BOT-MASTER 自述）
> **审计日期**: 2026-09-10
> **审计基线**: `main @ 0803f059`（BZ-FNDR-15.15；较第一轮 `e5ba6e0d` 推进 24 提交；工作区仍脏：`judgment.py`/`compute_stage.py`/`context_assembler.py`/`blind_yingqi.py` 等 9 个 M 文件）
> **前置**: `docs/audit/E9_BLIND_INDEPENDENT_AUDIT_20260909_EXTERNAL.md`（第一轮，e5ba6e0d）
> **纪律**: 只读审计——本轮**未改**任何被审代码/夹具；第一轮 M-01/M-03 修改仍在工作区未 commit，本轮仅验证其在新树上有效。

---

## 1. 增量影响面分析（e5ba6e0d → 0803f059，24 提交）

| 维度 | 结论 | 证据 |
|---|---|---|
| **BLIND 文件变更** | **0 处**（engines/blind*、tests/test_blind*、blind golden 集全部未触碰） | `git log e5ba6e0d..HEAD --name-only` 过滤 BLIND 路径 → 空 |
| **上游 BAZI 变更** | `bazi_engine.py` +213 行、`bazi_facts.py` +117、`canonical_bazi.py` +189（BZ-FNDR-10/15：Pillar.stem_ten_god、ZiPingCanonicalBaziChart、provenance gate） | `git diff --stat e5ba6e0d..HEAD` |
| **BLIND 上游兼容性** | ✅ **保持**——BLIND-A 的 `from ..engines.bazi_engine import ...`（含 `_branch_element`/`STEM_ELEMENT`/`canonical_bazi_engine`）在新 BAZI 上全绿；golden hash 与第一轮**完全一致**（`29dd863e`）→ 24 次上游重构未改变盲派任何计算结果 | 本轮 §2 实跑 |
| **治理事实新增** | BZ-FNDR-15.12 三门封口：① 严格 FAIL-CLOSED + 独立方法审计 + **①-f BLIND event_type 禁用为 ZiPing Oracle**；ZIP-INT-01~08 未授权；G0-1/G0-2（Evidence Index + Provenance Resolver）已实施（15/15 PASS） | `docs/audit/BZ-FNDR-15.12-THREE-GATES-SEALED.md` |

---

## 2. 逐层复核（本轮实跑输出）

| 层 | 裁定 | 证据（0803f059 实跑） |
|---|---|---|
| E0 契约 | **PASS**（不变） | `compute_blind_bazi/analyze_yingqi/PalaceFeatureCalculator` 入口不变；CanonicalSignal 带 evidence/rule refs |
| E1 单元 | **PASS** | `pytest <6 个 BLIND 套件> → 129 passed, 3 skipped(期望), 3 subtests, 0 failed`（含 M-03 负向 7 例） |
| E2 算法 | **PASS** | bazi/yingqi 序列化 md5 两次一致（deterministic=True）；P2-2 做功过触发观察仍有效 |
| E3 边界 | **PASS** | BAZI 时柱边界 `test_time_boundary.py → 23/23`（新树复测）；BLIND 不自解释出生 |
| E4 负向 | **PASS** | M-03 fail-closed 守卫在新树有效（`test_blind_negative` 7/7） |
| E5 Golden | **未过（P1-1，不变）** | replay `LOAD 20/20 EXECUTE 20/20 hash=29dd863e=基线`；但 20 例仍全结构断言、`verification_status` 仍 20/20 `VERIFIED`（无值断言、缺 canonical_state/provenance，source 部分"引擎实测"循环）——golden 文件 24 提交内零改动，缺陷原样保留 |
| E6 回归 | **PASS（BLIND 面）** | golden hash 两轮一致；**注意**：`cross_engine_baseline --check` 整体 FAIL = **ziping 基线过期**（`63f6ae0a→7ed21571` CHANGED，BZ-FNDR-15 改了 ziping 序列化未 re-record，§21 系统级缺口，**非 BLIND 缺陷**） |
| E7 集成/隔离 | **PASS** | 7 引擎中 6 个 OK、**blind 8f6ed3a4 稳定=未被污染**；①-f 反向渗漏核查：子平新接口（canonical_bazi/judgment/ziping_bridge/context_assembler/governance）**零 BLIND 引用**，双向隔离成立 |
| E8 生产 Trace | **FAIL（P0-1，不变）** | 0 生产调用方（`BlindBaziEngine/analyze_yingqi/PalaceFeatureCalculator` 仅引擎自身+feature_registry export） |
| E9 独立审计 | **完成（本报告）** | — |
| E10 裁决 | **FAIL** | E5 未过 + E8 FAIL → 不得 PRODUCTION_ADMITTED |

---

## 3. 第一轮发现的状态更新

| 项 | 第一轮 | 第二轮 | 变化 |
|---|---|---|---|
| P0-1 E8 生产入口缺失 | 待 User 范围裁决（A/B/C） | **不变**，仍 0 调用方；①-f（BLIND 禁作 ZiPing Oracle）+ 子平辨层离线定案 → **选 B（离线 OUT-OF-SCOPE）是当前治理体系下唯一自洽项**（接线生产既无需求方也违反 ①-f 隔离精神） | 倾向明确，待 User 正式定案 |
| P1-1 Golden 真值断言未过 | 待 User 定真值来源（A 段书命例/B 快照+抽检/C 挂起） | **不变**（golden 文件零改动） | — |
| P1-2 死适配器 BlindSchoolFeatureAdapter | 9 字段与输出不匹配 | **不变** | — |
| P1-3 脏树基线 | e5ba6e0d 脏 | 0803f059 仍脏（且新增 4 个 BZ-FNDR-15 脏文件）→ 结论可复核性仍未解决 | 恶化 |
| P1-4 负向测试 | M-03 已修 | 新树有效（7/7） | ✅ 维持 |
| P1-5 mingli_bench 3 unexpected FAIL | M-01 已修 | 新树有效（3 期望 SKIP，Unexpected SKIP 仍=0） | ✅ 维持 |
| P2-1 取象无专门模块 | 未决 | 不变 | — |
| P2-2 做功过触发（13 类） | 未决 | 不变 | — |
| P2-3 内部文档数字错位 | 未决 | 不变 | — |
| **（新）§21 ziping 基线过期** | — | cross-engine 整体 FAIL 由 ziping CHANGED 导致；需 BZ-FNDR-15 owner re-record（子平/系统侧，非 BLIND） | 新增系统级阻塞 |

---

## 4. 生命周期裁定（第二轮）

```
BASIC_VALIDATED      → 未达（E5 案例验收未过，P1-1 待 User 真值裁决；同第一轮，无变化）
PRODUCTION_VALIDATED → 不可达
PRODUCTION_ADMITTED  → 拒绝
```

**E10 = FAIL。生命周期建议维持第一轮结论：NOT BASIC_VALIDATED（案例验收未过），生产准入拒绝。**
本轮 24 次上游重构**未恶化亦未改善** BLIND 的任何验收状态——盲派计算层在 BAZI 大重构下哈希级稳定（golden/cross 双 hash 不变），这是 BZ-FNDR 系列"单源化重构不改结果"纪律的正向证据。

---

## 5. 待 User 裁决（与第一轮相同 + 1 新增）

1. **P0-1 BLIND 生产范围**：B（离线 OUT-OF-SCOPE，推荐，与 ①-f/子平辨层离线定案自洽）/ A（接线生产——当前无需求方且违反隔离精神）/ C（维持现状记录）。
2. **P1-1 Golden 真值来源**：A 段建业书真实命例 / B 引擎快照+人工抽检（过渡）/ C 挂起（E5 保持未过）。
3. **M-01/M-03 两个未 commit 修改**：采纳进入提交链，或回滚（本轮审计按"在树"状态取证）。
4. **（新增）P1-3 脏树处置**：9 个 M 文件 + 2 个审计修改未 commit，所有"可复核"要求悬空；建议按 BZ-FNDR 系列既有流程提交后在干净 commit 复核本轮数字。

---

## 6. 复现命令快查（0803f059）

```bash
cd D:/shuntian
git status --porcelain                 # P1-3: 当前 9 个 M + 若干 ??
# E1+E4 (129+3sub, 含 M-03):
PYTHONPATH=src .venv/Scripts/python -m pytest tests/test_blind_golden.py tests/test_blind_yingqi.py tests/test_blind_signal_regression.py tests/test_blind_rules tests/test_blind_negative.py tests/test_mingli_bench_blind.py -q -rs
# E3:
PYTHONPATH=src .venv/Scripts/python tests/test_time_boundary.py   # 23/23
# E5/E6/E7:
.venv/Scripts/python scripts/golden_replay.py --engine blind --check   # 20/20, hash=29dd863e
.venv/Scripts/python scripts/cross_engine_baseline.py --check          # blind OK; ziping CHANGED(§21)
# E8 生产调用方(应 0):
git grep -l "BlindBaziEngine\|compute_blind_bazi\|BlindYingqiEngine\|analyze_yingqi\|PalaceFeatureCalculator" -- src
# ①-f 反向渗漏(应无):
git grep -niE "blind" -- src/tongshu/models/canonical_bazi.py src/tongshu/reasoning/judgment.py src/tongshu/reasoning/ziping_bridge.py src/tongshu/reasoning/context_assembler.py
```

---

**签核**: 外部独立审计（第二轮）| 2026-09-10 | 依据 V2 §21/§44/§46/§48/§55/§59/§60
> 本轮纯只读：未改被审代码、未改 Golden、未 commit。M-01/M-03 为第一轮遗留的未提交修改，本轮仅验证其有效性。
