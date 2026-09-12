# 顺天 V2 规范对齐：引擎必要件齐全度审计与细节完善方案

> 文档性质：**只读审计 + 完善方案（讨论/拍板稿，不改动任何计算）**
> 对齐基线：`docs/v2/V2新架构和引擎规范.md`（下称《架构》）、`docs/v2/验收和生产准入规范.md`（下称《验收》）
> 审计日期：2026-09-11 ｜ 审计方式：逐文件/逐目录客观扫描（脚本 `.tmp_cases/scan_v2_required.py`，可重跑）
> 审计范围：BAZI FOUNDATION + 子平/盲派/紫微/河洛/梅花/易经/黄历 共 8 个对象
> 重要口径：**"零吉凶"只约束前端 Expression；后端 Fact 层输出全事实（干支/十神/五行阴阳/藏干/作用关系/时间轴等所有确定性 Fact），吉凶断语归 Judgment。本方案不删任何后端事实。**

---

## 0. 一句话结论（信心 9/10）

项目**计算骨架与准入机制已具雏形且总体诚实（无一引擎虚标 PRODUCTION_ADMITTED）**，但对照两份 V2 规范，"每个引擎的必要件"存在 **4 类系统性缺口**：

1. **契约枚举只覆盖 5 引擎，漏梅花、黄历**（架构 §06 要求 7 引擎）；
2. **Engine Output Contract（架构 §14）没有统一落地对象**，编排层证据桶硬编码只接 `ZI_PING/ZI_WEI`；
3. **Golden 用了 4 套不同 schema、字段普遍不齐（验收 §14 九字段），河洛无独立 Golden 文件**；
4. **每引擎目录资产（验收 §06 七文档 + tests 标准十层目录）未建立，tests 为历史平铺**。

下面逐件给出现状、证据、一次到位的补法与执行批次。**所有 P2 补齐动作均为"加结构/加字段/加文档"，不改任何已冻结计算结果。**

---

## 1. 规范要求的"必要件"总清单（验收标尺）

### 1.1 每个 Engine 必备九件套（架构 §07）

`Calculation / Evidence / Signal / Rule / Judgment / Golden / Regression / Provenance / Production Admission`

### 1.2 Engine Output Contract 十段（架构 §14）

```
engine, engine_version, calculation_version, input_reference,
calculation, signals, evidence, rules, judgments, provenance
```

### 1.3 EngineEvidence 字段（架构 §15）

```
id, case_id, engine, engine_version, feature, value, source, rule_id,
classical_reference, calculation_reference, temporal_scope, provenance
```

### 1.4 Golden Case 九字段（验收 §14 / 架构 §32）

```
case_id, input, canonical_state, expected_calculation, expected_evidence,
expected_rule, expected_judgment, human_verified_result, source
（必要时 + calculation_version / engine_version / dataset_version / provenance）
```

### 1.5 E0–E10 验收层 + 三生命周期（验收 §07、§29-31、§60）

E0 Contract → E1 Unit → E2 Algorithm → E3 Boundary → E4 Negative → E5 Golden →
E6 Regression → E7 Integration → E8 Production Trace → E9 Independent Audit → E10 Acceptance；
状态仅 `BASIC_VALIDATED / PRODUCTION_VALIDATED / PRODUCTION_ADMITTED`，E10 判定 `PASS/CONDITIONAL/FAIL/BLOCKED`。

### 1.6 每引擎目录最低资产（验收 §06）

```
ENGINE/ ├─ SOUL.md AGENTS.md SPECIFICATION.md ARCHITECTURE.md TESTING.md AUDIT.md ACCEPTANCE.md
        ├─ implementation/  tests/(contract|unit|algorithm|boundary|negative|golden|regression|integration|production|audit)/
        ├─ golden/(canonical|expected_calculation|expected_evidence|expected_rule|expected_diagnosis)/
        └─ provenance/
```

---

## 2. 总体现状矩阵（客观扫描，数字可重跑复核）

### 2.1 九件套代码层命中文件数（该引擎归属代码中出现对应构造的 .py 文件数）

| 对象 | py文件 | Evidence | Signal | Rule | Judgment | Provenance | 版本字段 | Golden(n) | 测试文件 | 验收文档 | ADMITTED |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|:--:|:--:|
| BAZI FOUNDATION | 26 | 5 | 3 | 2 | 0* | 3 | 1 | 18（schema另套） | 34 | 有 | 否 |
| ZIPING 子平 | 19 | 12 | 10 | 15 | 2 | 4 | 2 | 25 | 6 | 有（过渡PASS） | 否 |
| BLIND 盲派 | 11 | 5 | 2 | 7 | 2 | **0** | **0** | 40 | 5 | 有 | 否 |
| ZIWEI 紫微 | 11 | 7 | 1 | 7 | 0* | **0** | 3 | 80（最全） | 9 | 有 | 否 |
| HELUO 河洛 | 26 | 11 | 4 | 7 | 3 | **0** | 3 | **0（无文件）** | 12 | 有 | 否 |
| MEIHUA 梅花 | 2 | **0** | **0** | **0** | **0** | **0** | **0** | 30（schema另套） | 5 | 有 | 否 |
| YIJING 易经 | 16 | 1 | **0** | 1 | 1 | **0** | 1 | 20 | 7 | 有 | 否 |
| HUANGLI 黄历 | 1 | **0** | 1 | 1 | **0** | **0** | **0** | 38（schema另套） | 4 | 有 | 否 |

> \* 底座/紫微 Judgment=0 不必然是错：底座只产 Fact 不产判断（合理）；紫微判断走派法 profile，需在文档中显式说明归属，不能留空。
> 统一契约枚举 `EngineName`（`spec/canonical/engine_evidence.py`、`assertion_v2/contract.py`）实测：**MEIHUA=False、HUANGLI=False**，两处都只枚举 5 引擎。

### 2.2 Golden 字段齐全度（对照 §1.4 九字段，列出缺失项）

| Golden 文件 | n | 缺失字段 |
|---|---:|---|
| ziwei_golden_set.json | 80 | 仅缺 `expected_rule`（最接近规范，另含 expected_signal/engine_version/provenance） |
| ziping_golden_set.json | 25 | canonical_state, expected_evidence, expected_rule, expected_judgment |
| yijing_golden_set.json | 20 | 同上四项 |
| blind_golden_set(_v2).json | 20+20 | 同上四项 |
| meihua_golden_set.json | 30 | 用 `expected/calculation` 另一套；缺 canonical_state 及四个 expected_*、human_verified_result |
| huangli_golden_set.json | 38 | 同梅花（另一套字段名） |
| bazi_garden_cases.json | 18 | 用 `id/expected/verified/name` 第三套；九字段几乎全缺 |
| golden_cases.json（总） | 50 | 用 birth_date/events/source_type 第四套 |
| **heluo** | **0** | **cases/golden 下无独立河洛 Golden 文件** |
| calc_golden_dataset_001.json | — | 八字底座数据集，CALC-GOLDEN-001 期望值已知有误，受 AGENTS.md 保护，未改 |

**结论：8 套 Golden 存在 4 种字段风格，无一套完全齐九字段；河洛缺文件。**

### 2.3 已具备、应保留的扎实件（避免重复造轮子）

- 时间/真太阳时/换日/节气底座：`engines/time/*`（resolver/eot/longitude/day_boundary…）+ 34 个底座测试，FROZEN。
- 准入权威：`assertion/admission_registry.py`（v7 不可伪造 Authority + 身份绑定），对应架构 §21 Gate / Production Admission，实质健全。
- Rule 状态门：`data/rules`(140)、`backend/data/rules`(136) + `.admission/`（DTS/SMTH…）+ `verification_status`（unverified→scope），有状态门实质（命名需与 §21 的 DRAFT/REVIEW/ACTIVE/REJECTED/DEPRECATED 建立映射表）。
- 跨引擎污染基线：`scripts/cross_engine_baseline.py`（5 引擎 hash 快照 + --check），对应验收 §34。
- Provenance 解析器：`governance/provenance_resolver.py`、`RUNTIME_AUTHORITY_LEDGER.yaml`（但多数引擎未接线，见下）。
- 验收文档：`docs/acceptance/*_ACCEPTANCE.md` 9 份 + `V2_ACCEPTANCE_OVERVIEW.md`（全部诚实标 CONDITIONAL/过渡，无虚标 ADMITTED）。

---

## 3. 缺口分级台账（P0 架构级 / P1 契约级 / P2 齐套级）

> 判级原则：违反"一入口/独立引擎/Fail-Closed/不可变计算"为 P0；契约字段/链路缺失为 P1；文档、目录、字段补全且不改计算为 P2。

### P0 — 架构契约级（必须先定，不然后面全返工）

| # | 缺口 | 规范条款 | 证据（文件） | 一次到位补法 | 改计算? |
|---|---|---|---|---|---|
| P0-1 | 统一引擎枚举只有 5 个，**梅花/黄历不在 EngineName** | 架构§06 七引擎 | `spec/canonical/engine_evidence.py:23`、`assertion_v2/contract.py:17` | 两处枚举同步增 `MEI_HUA="MEI_HUA"`、`HUANG_LI="HUANG_LI"`，并补各自 JudgmentType 枚举（梅花：起卦/本卦/动爻/互卦/变卦/体用；黄历：干支/节气/宜忌/方位，**黄历为公共时间层，不产个人吉凶 Judgment**） | 否 |
| P0-2 | **无统一 EngineResult 输出对象**，§14 十段靠各处手拼 | 架构§14 | 全仓无 EngineResult/EngineOutput 类；`pipeline_stages/compute_stage.py:382` 证据桶硬编码 `{"ZI_PING":[],"ZI_WEI":[]}` | 新增 `spec/canonical/engine_result.py`：冻结 dataclass `EngineResult`（十段），各引擎 evidence_producer 统一返回它；compute_stage 改为按 7 引擎枚举初始化证据桶 | 否 |
| P0-3 | **梅花引擎零 Evidence/Signal/Rule/Judgment/Provenance**，未进入辨层 | 架构§07/§10、§14 | `meihua.py`、`meihua_engine.py` 关键字 0 命中；MEIHUA_ACCEPTANCE E7=FAIL | 建 `engines/meihua/evidence_producer.py`，把本卦/动爻/变卦/互卦/体用全部转成**事实型** EngineEvidence/Signal（不含吉凶），补齐 input_mode/calculation_method/provenance（架构§10.3 双模式） | 否（只加事实层） |
| P0-4 | 黄历仅 1 文件、近零契约件，且公共层有越界成个人判断风险 | 架构§13、验收 E8=FAIL | `huangli_engine.py`（evidence 0/judgment 0） | 建 `engines/huangli/evidence_producer.py`，只输出公共时间事实（干支/节气/宜忌/方位），**显式禁止个人命理 Judgment**，补 E8 生产路径 trace | 否 |

### P1 — 契约/链路级

| # | 缺口 | 规范条款 | 证据 | 补法 | 改计算? |
|---|---|---|---|---|---|
| P1-1 | EngineEvidence 字段与 §15 不一致：缺 case_id/feature/source/classical_reference/calculation_reference/provenance | 架构§15 | `spec/canonical/engine_evidence.py:43-85`（现仅 evidence_id/engine/rule_id/value/temporal_scope/attributes/source_rule_ref/source_field/版本） | **向后兼容扩字段**（新增带默认值字段，不动旧字段），加 `feature/source/classical_reference/calculation_reference/case_id/provenance`，to_dict 补出 | 否 |
| P1-2 | 盲派/紫微/河洛/易经/黄历/梅花 **Provenance 文件命中 0**，判断/证据不可全链回溯 | 架构§16、验收§38 | 见表 2.1 | 每引擎 evidence_producer 强制带 provenance（source_id/source_version/rule_id/engine_version/calculation_version/dataset_version），接 `governance/provenance_resolver.py` | 否 |
| P1-3 | **河洛无独立 Golden 文件**（n=0） | 验收§14/§57 | cases/golden 无 heluo_*；测试 12 个但 Golden 内联/散在 data | 抽 `cases/golden/heluo_golden_set.json`（本命/元堂/后天/时间结构/卦气，对齐 §57），统一九字段 | 否 |
| P1-4 | Golden schema 四套不统一、普遍缺 canonical_state/expected_evidence/expected_rule/expected_judgment | 验收§14 | 见表 2.2 | 定一份 Golden 标准 schema + 迁移映射（见 §4），**只补结构不改期望值**；值断言缺失项显式标 `"human_verified_result": null, "verify_status":"PENDING"`，不许编 | 否 |
| P1-5 | 编排层只聚合子平/紫微证据，其余引擎证据/Signal 进不了 Cross-System | 架构§22/§24 | `compute_stage.py:382/469` | 证据桶按 EngineName 七枚举初始化；signal 缺的引擎（梅花/黄历/易经）补 P0-3/P0-4 后自然汇入 | 否 |
| P1-6 | 易经 Signal 文件命中 0、Evidence 仅 1 | 架构§07/§12 | 见表 2.1 | `engines/yi/evidence_producer.py` 补齐卦/爻/象/辞事实型 Signal，卦结构来自梅花时只读不改（架构§11） | 否 |
| P1-7 | Rule 状态词与 §21 五态未建显式映射 | 架构§21 | verification_status vs DRAFT/REVIEW/ACTIVE/… | 建映射表 + Runtime Status Gate：仅 ACTIVE 进生产，DRAFT/REVIEW 拒绝（fail-closed） | 否 |

### P2 — 齐套/文档/目录级（不改计算，纯补齐）

| # | 缺口 | 规范条款 | 补法 |
|---|---|---|---|
| P2-1 | 无每引擎七文档（SOUL/AGENTS/SPECIFICATION/ARCHITECTURE/TESTING/AUDIT/ACCEPTANCE） | 验收§06 | 现有 docs/acceptance、docs/bots/BOT-* 内容**归并**成每引擎目录七文档，不新写结论、只搬运+标注缺口 |
| P2-2 | tests 无标准十层目录（contract/unit/algorithm/boundary/negative/golden/regression/integration/production/audit） | 验收§06 | 不移动文件（避免 import 断裂），用 `tests/INDEX.md` 把现有平铺测试**映射**到 E0-E10/十层，缺层列空；后续新增测试按层归位 |
| P2-3 | golden 无子目录（canonical/expected_calculation/expected_evidence/expected_rule/expected_diagnosis） | 验收§06 | 同上，先在 INDEX/元数据里逻辑分层，物理迁移放最后批次 |
| P2-4 | 每引擎缺 provenance/ 目录 | 验收§06、架构§16 | 建 `provenance/SOURCES.md`（列该引擎经典来源与版本），与 P1-2 字段对应 |
| P2-5 | 缺 BAZI Foundation 专项七件套命名（BAZI-TIME/CALENDAR/JIEQI/BOUNDARY/FOUR-PILLAR/DA-YUN/REPLAY） | 验收§52 | 在 BAZI 的 TESTING/ACCEPTANCE 里把 34 个现有测试映射到这 7 个专项编号，缺项（REPLAY）列入待办 |
| P2-6 | 子平专项矩阵缺"流年"事实层验收（§56 要求四柱/五行/十神/月令/旺衰/格局/用神/干支关系/大运/流年） | 验收§56 | 与 Fact API 一并补：流年/流月/流日 Fact 的 Golden 与边界（立春/节气切换），见 §6 |
| P2-7 | 紫微缺 Chart Hash 稳定断言、ZW-004 证据不足（overview 已记 P1） | 验收§19/§54 | 补同 Canonical→同 Chart hash 测试到 ZIWEI-CHART-HASH；ZW-004 走证据补全不硬判 |
| P2-8 | 梅花缺 BOT-MEIHUA 目录、双模式（Birth/Event）Contract 未文件化 | 架构§10.3、验收§04/§53 | 建 docs/bots/BOT-MEIHUA；SPECIFICATION 写死 Mode A/Mode B 入口与 input_mode/calculation_method/provenance |

---

## 4. Golden 标准 Schema 与四套现状迁移映射（一次定死，避免反复改）

### 4.1 目标标准（对齐验收 §14，所有引擎统一）

```json
{
  "case_id": "ZP-WANG-001",
  "engine": "ZI_PING",
  "input": { "birth_date": "1980-06-22", "birth_hour": 10, "gender": "male",
             "location": "广州", "time_basis": "true_solar", "input_mode": "birth" },
  "canonical_state": { "four_pillars": ["庚申","壬午","丙寅","癸巳"], "day_master": "丙" },
  "expected_calculation": { },
  "expected_evidence": [ ],
  "expected_rule": [ ],
  "expected_judgment": [ ],
  "human_verified_result": null,
  "source": { "work": "子平真诠", "chapter": "", "verify_status": "PENDING" },
  "calculation_version": "2026.09",
  "engine_version": "",
  "dataset_version": "1.0.0",
  "provenance": { }
}
```

> 铁律：**迁移只做"字段重命名 + 补空槽"，绝不改既有期望值**；暂时没有真值的，写 `null + verify_status:PENDING`，禁止编造（验收 §15、§47）。

### 4.2 现状字段 → 标准字段映射

| 现集合 | 现状键 | 映射到标准键 | 处理 |
|---|---|---|---|
| ziping/yijing/blind | expected_calculation ✅ | expected_calculation | 保留；补其余空槽 |
| meihua/huangli | `expected` + `calculation` | expected_calculation | 改名合并；`human_verified`→human_verified_result |
| bazi_garden | `id/name/expected/verified` | case_id/（description）/expected_calculation/human_verified_result | 改名；补 canonical_state（可由底座确定性回填） |
| golden_cases(50) | birth_date/birth_hour/gender/events/source_type | input.*/（events→expected）/source | 拆分重组；events 非标准，单列保留不丢 |
| ziwei | 已近齐 | — | 仅补 expected_rule 空槽 |
| heluo | 不存在 | — | 新建（P1-3） |

---

## 5. 统一 EngineResult / EngineEvidence 目标骨架（Copy-Paste Ready）

### 5.1 EngineResult（新增 `spec/canonical/engine_result.py`，架构 §14）

```python
@dataclass(frozen=True)
class EngineResult:
    engine: str                       # EngineName.value
    engine_version: str
    calculation_version: str
    input_reference: str              # Canonical State 的 resource_id（非文件路径，架构§17）
    calculation: dict                 # 纯事实计算结果（后端全事实，不含吉凶断语）
    signals: list = field(default_factory=list)      # 事实语义 Signal（架构§18）
    evidence: list = field(default_factory=list)     # EngineEvidence 列表
    rules: list = field(default_factory=list)        # 命中的 ACTIVE rule_id
    judgments: list = field(default_factory=list)    # NativeJudgment；黄历=[]
    provenance: dict = field(default_factory=dict)
    def to_dict(self): ...
```

### 5.2 EngineEvidence 向后兼容扩字段（架构 §15；旧字段不删）

在现有 dataclass 上**新增带默认值**字段：`case_id=None、feature=None、source=None、
classical_reference=None、calculation_reference=None、provenance=None`，并同步 to_dict。

### 5.3 编排层修正（compute_stage）

```python
# 现状（硬编码两引擎）：
engine_evidences: dict[str, list] = {"ZI_PING": [], "ZI_WEI": []}
# 目标（七枚举，缺则空桶，由各引擎 evidence_producer 填）：
engine_evidences = {e.value: [] for e in EngineName}   # 含 MEI_HUA/HUANG_LI
```

---

## 6. 与"后端全事实 / ZIPING Fact API"口径的衔接（用户已裁决）

- **零吉凶只约束前端**；后端 Calculation/Signal 必须把确定性事实备齐，不产出吉凶断语（断语归 Judgment）。
- 子平 Fact 层 14 项已盘点的缺口，按"Fact（进 Calculation/Evidence）"与"Judgment（进 judgments）"二分补齐：
  - **Fact 补齐（P2，纯计算事实，不算吉凶）**：完整藏干（本/中/余气）、四支藏干十神、天干/地支阴阳字段、十二长生、天干五合（现 `STEM_HE` 是死代码，接线）、六破、纳音、神煞体系、胎元/命宫/身宫/胎息、大运起止、**流年/流月/流日时间轴 Fact**。
  - **流年/流月/流日 Fact 契约**（沿用已写 ADR `docs/bots/BOT-BAZI/ZIPING_FACT_API_BOUNDARY_20260911.md`，并按"后端全事实"修正其"零吉凶"措辞）：
    - 流年 `{type,year,pillar,gan,zhi,start(立春),end(次年立春前)}`
    - 流月 `{type,year,month_index(寅=1),pillar,gan,zhi,start(节),end(下一节约)}`
    - 流日 `{type,date,pillar,gan,zhi}`
  - **不可复用河洛 timeline_yun/time_sequence**：其流月按公历月而非节气月、耦合 gender/六爻、只吐单字符串无 gan/zhi/start/end，口径不同（已核实）。八字口径用 sxtwl 在子平内独立封装。
  - 已知坑（避免返工）：`bazi_l1_facts.py` 喂拼音键查中文表导致藏干/长生全空，接线前先做键归一；`STEM_HE` 定义后零调用；己土十二长生表现标 UNRESOLVED/PARTIAL，不得擅改。

---

## 7. 建议执行批次（零计算改动优先，逐级解锁，杜绝返工）

> 顺序铁律：**先定契约（P0），再补链路（P1），最后齐套文档/目录（P2）**；每批结束跑全量 pytest + cross_engine_baseline --check，确保已冻结计算 hash 不变。

- **批次 A｜契约定型（P0-1、P0-2、P1-1、P1-7）**：七引擎枚举、EngineResult、EngineEvidence 扩字段、Rule 五态映射门。纯加类型/枚举/默认字段，不改算法。→ 解锁所有下游。
- **批次 B｜事实层接线（P0-3、P0-4、P1-5、P1-6、P1-2）**：梅花/黄历/易经 evidence_producer、七引擎证据桶、全引擎 provenance 接线。只加事实，不产吉凶。
- **批次 C｜Golden 统一（P1-3、P1-4）**：定标准 schema → 写一次性迁移脚本（只改名/补空，不改值）→ 新建河洛 Golden → 校验 LOAD/EXECUTE=100%、UNEXPECTED_SKIP=0。
- **批次 D｜子平 Fact 补齐（§6）**：藏干/阴阳/长生/作用关系/神煞/胎命身/流年流月流日 Fact + 对应 Golden 与边界；同步修正 Fact API ADR 口径。
- **批次 E｜齐套与可审计（P2 全部）**：每引擎七文档归并、tests/golden/provenance 的 INDEX 逻辑分层、专项矩阵编号映射、E8 生产 trace、E9 独立审计材料。**本批结束才具备申请 BASIC_VALIDATED 复评的条件；是否升状态由 User/独立审计裁决，Agent 不自行宣布（架构§43）。**

每批验收门槛（对照验收 §32 矩阵）：P0=0、P1=0、Golden 100% 执行、Unexpected Skip=0、Determinism 同输入同结果、跨引擎其余 6 个 hash 不变。

---

## 8. 明确不做（边界，防止"乱来"）

1. 不改任何已 FROZEN 计算（BAZI 底座、已验证四柱/大运），不改 Golden 既有期望值；CALC-GOLDEN-001 已知错误值受 AGENTS.md 保护，须正式变更+User 批准。
2. 不把河洛/紫微结果拿来替代或修改子平（架构§23/§24，互补不比较）。
3. 不自行把任何引擎升为 PRODUCTION_VALIDATED/ADMITTED，不把 DRAFT Rule 放进生产（架构§21/§43）。
4. 不在后端删事实以迎合"零吉凶"；零吉凶只在前端 Expression 落地。
5. 不 `git add .`、不顺手改其他引擎；跨引擎问题走 CHANGE REQUEST（验收§43）。

---

## 9. 待 User 拍板项

1. 是否按"批次 A→E"顺序推进？是否先只做**批次 A（契约定型，零计算风险）**？
2. Golden 迁移是否授权"补空槽用 null+PENDING、绝不编真值"（盲派真值缺失三选一仍挂起，见 V2_ACCEPTANCE_OVERVIEW §四）？
3. 引擎物理目录是否需要在批次 E 重排为 §06 标准结构，还是长期用 INDEX 逻辑映射（后者零 import 风险，建议先用）？
4. 子平 Fact 层（批次 D）是否与契约批次并行，还是严格排在 C 之后？

---

*本审计全部数字由 `.tmp_cases/scan_v2_required.py` 对当前工作区客观扫描得到，可随时重跑复核；本文不含任何 LLM 猜测的命理结论。*
