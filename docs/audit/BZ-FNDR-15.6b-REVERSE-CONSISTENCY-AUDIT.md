# ⑮-3 反向一致性审计（Audit Record vs Actual Code）

> **BZ-FNDR-15.6b：对 BZ-FNDR-15.6-15-3 审计记录的逐条代码复核修正**
> **Audit-Only, No Code Change**
>
> 本 commit 是 **Audit Record Commit，不是 Remediation Commit**。
> 不含任何代码修改、Evidence 重挂、Rule ID 变更、算法调整、⑮-0/⑮-1/⑮-2 CLOSED 项回改。
> 本报告**不推翻** ⑮-3 的 A~H 主体结论，而是**逐条对着实际代码复核**，
> 专抓「报告写 PASS、代码实际没做到」的遗漏，并订正 ⑮-3 报告自身的事实错误。

---

## 0. 审计元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.6b |
| 审计类型 | Reverse-Consistency（Audit Record vs Actual Code） |
| 被复核对象 | `BZ-FNDR-15.6-15-3-AUDIT-REPORT.md`（commit `ab7a9574`） |
| 代码取证基线 | `40eeb359`（⑮-0 接入契约）→ `48e66f6c`（⑮-2 审计归档）→ `ab7a9574`（⑮-3 审计归档） |
| 取证方式 | `git show <commit>:<path>`（**只读已提交版本，不读工作区** —— 工作区含未提交 ⑮ 整改代码，会污染取证） |
| 审计窗口 | 2026-09-10 |
| 执行者 | BOT-MASTER（User 授权：逐 commit 对代码，不采信自述/静态推断） |
| **Code Change** | **0（本 commit 仅含本文件）** |
| **Git push** | 待 User 裁决 |

### 复核原则

⑮-3 报告是基于**静态 grep + 单次 H 回放**得出的。本次反向审计补上：
1. **H-3 命题拆分**——把「回放对象来自 factory」与「Bridge 强制 require_factory=True」两个不同命题分开判定；
2. **build_context 输入契约缺口**——逐字段核对 ZiPingCanonical 扩展字段是否进入 Judgment Context；
3. **报告自身事实纠错**——发现 ⑮-3 把 `EVENT_ABSENT` 写成「死值」，实际为活跃值。

---

## 1. 新发现（⑮-3 报告遗漏 / 表述过松）

### N-1 — `require_factory` 契约执行不匹配【P1，User 已定级】

**报告表述（⑮-3 H-3 行）**：

> 「factory provenance = True，⑮-0 契约门通过」

**实际代码（`ab7a9574:src/tongshu/reasoning/ziping_bridge.py` L82-84）**：

```python
# BZ-FNDR-15: 真实生产入口 provenance gate (审计模式).
# require_factory=True 强制: 真实生产路径必须经 from_bazi_chart() 工厂.
from tongshu.models.canonical_bazi import assert_canonical_gate
assert_canonical_gate(chart, require_factory=False)   # ← 注释说 True，实际传 False
```

- **注释/docstring 声明** `require_factory=True`（生产入口必须工厂对象）；
- **实际调用** `require_factory=False`（审计模式，允许直接构造的 chart 通过）。
- 同一不一致**在两处注释里都写着 True**：`ziping_bridge.py` L71（docstring「真实生产路径必须经过 assert_canonical_gate(require_factory=True)」）+ L83（「require_factory=True 强制」）；`compute_stage.py` L154 注释也写「下游通过 assert_canonical_gate(require_factory=True) 校验」。

**关键：这不是文字问题。** `assert_canonical_gate(instance, require_factory)` 在 `False` 时只记录 provenance、**不阻断**（`canonical_bazi.py` L241 语义：`if require_factory and not is_factory_provenance(...): raise`）。也就是说：

> Bridge 层**没有真正强制工厂 provenance**。任何非 factory 构造的 chart（含直接堆 4 柱）都能通过 `run_ziping_judgment` 的 gate。

**H-3 命题必须拆成 User 锁定的 6 行（本报告据实逐项判定）：**

| 命题 | 判定 | 证据 |
|---|---|---|
| 回放使用的对象来自 factory | ✅ | H 回放样本 `ZiPingCanonicalBaziChart.from_bazi_chart()` 构造 |
| `assert_canonical_gate()` 被调用 | ✅ | `ziping_bridge.py` L83 实调 |
| Bridge 强制 `require_factory=True` | ❌ | 实调 `require_factory=False`（L83） |
| 非 factory 对象被生产入口拒绝 | **未证明 / 存在风险** | False 模式下直接构造的 chart 也会被放行 |
| Chain B 生产 Pipeline 有 consumer | ❌ | `pipeline.py` 全文件 0 引用 `run_ziping_judgment/judgment/ZiPing`（取证 1） |
| Chain B → SIR/G1 | ❌ | 0 judgment 字段进 SIR（F-4 实锤，见 N-3） |

**严重级 = P1**（User 裁决）。理由：这是「⑮-0 声明的契约门」在 Bridge 落地的**实现降级**——契约写成 True、代码传 False，属代码—契约不一致；但当前 Chain B 本就 0 生产消费（P0-1），gate 是否强制暂不改变生产行为，故不升 P0。

---

### N-2 — `build_context` 输入契约缺口【P1，User 已定级】

**报告表述（⑮-3 §6）**：

> 「ZiPing 算法/判断层（链 B）内部有效、可测试」

**实际代码（`ab7a9574:src/tongshu/reasoning/ziping_bridge.py` `build_context` L64）**：

```python
def build_context(chart: Any) -> Dict[str, Any]:
    day_master = getattr(chart, "day_master", "") or ""
    pillars = [
        _pillar_dict(getattr(chart, "year_pillar", None), "YEAR"),
        _pillar_dict(getattr(chart, "month_pillar", None), "MONTH"),
        _pillar_dict(getattr(chart, "day_pillar", None), "DAY"),
        _pillar_dict(getattr(chart, "hour_pillar", None), "HOUR"),
    ]
    return {"natal": {"pillars": pillars, "day_master": day_master}}
```

`40eeb359` 给 `ZiPingCanonicalBaziChart` 新增的 **9 个确定性派生字段**：

```
luck_pillars / branch_clash_map / branch_harm_map / branch_he_map /
branch_sanhe_map / branch_sanxing_map / kong_wang / five_element_balance / day_branch_main_ten_god
```

**没有一个进入 Judgment Context。** `build_context` 只组 `{"natal": {pillars: 4柱, day_master}}`。

**更深的取证（`judgment.py` L285-330 `_extract_context`）**：Judgment 各域实际读的是

```
day_master / month_branch / pillars / transparent_stems
```

全部**可由 4 柱 + 日主派生**——即：
- 5 域 judge 逻辑**确实不需要**那 9 个扩展字段就能跑通（所以「算法可独立运行」成立）；
- 但 **⑮-0 契约对象（ZiPingCanonicalBaziChart）携带的扩展确定性事实，在 ⑮-1 消费侧被完全丢弃**。

**订正后的三级定性（替代 ⑮-3「ZiPing 算法内部有效」的笼统说法）：**

```text
Calculation Core              🟢 算法代码可独立运行（5 域 judge 只需 4柱+日主）
ZiPing Contract Consumption   🟠 未证明完整消费 ZiPingCanonical 扩展契约
                              （build_context 只取 4柱+日主，9 扩展字段 0 进入）
Production Integration        🔴 未接入（P0-1）
```

符合 User 一贯要求 **「FROZEN ≠ PROVEN CORRECT」**。

**严重级 = P1**（User 裁决）。理由：⑮-0 契约**已建立对象**（ZiPingCanonicalBaziChart 存在且字段齐全），⑮-1 **消费契约未完成**（消费侧只取 4柱+日主）——这是实现缺口，不是 P0（因为 5 域算法本身可独立验证，扩展字段是否消费属「接入深度」而非「算错」）。

---

### N-3 — 旁路契约对象精确定性【并入 P0-1，非新增 P0】

**报告表述（⑮-3 F-4 / F-5）**：

> 「ComputeResult.canonical_bazi_chart 全仓 0 生产读取」「B-3/C-4/D-3/F-4 = 同一架构断点」

**实际代码（`ab7a9574:src/tongshu/pipeline_stages/compute_stage.py` L161→L176→L265）**：

```python
canonical_bazi_chart = ZiPingCanonicalBaziChart.from_bazi_chart(bazi_chart)  # L161
...
build_result = self.signal_engine.build(
    bazi_chart, ...)   # L176 — 走的是「裸 bazi_chart」，不是 canonical_bazi_chart
...
return ComputeResult(
    ...
    canonical_bazi_chart=canonical_bazi_chart,   # L265 — 只是挂进结果，从未被读
)
```

- `pipeline.py` 全文件 **0 命中** `canonical_bazi_chart / judgment / run_ziping / ZiPing`（取证 1 grep 实锤）。
- 精确定性：**`ZiPingCanonicalBaziChart` 是「被构造的旁路契约对象」，不是生产辨层的实际输入对象。** 它被构造出来 → 挂进 `ComputeResult` → 下游 `signal_engine.build` 继续吃**裸 `bazi_chart`**（链 A），从不读这个旁路对象。

这条比 ⑮-3 F-4「ZiPing 没调用」更精确，应写入 P0-1 的根因描述，**不新增 P0**（仍归 ⑮-3 已去重的 P0-1 单一架构断点）。

---

## 2. ⑮-3 报告自身事实纠错

### C-1 — `EVENT_ABSENT` 不是「死值」【⑮-3 D-2 表述需订正】

**⑮-3 D-2 行原文**：

> 「`EVENT_ABSENT` 枚举残留死值（fail-open 地雷）」

**实际代码（`ab7a9574:src/tongshu/reasoning/judgment.py` L1004）**：

```python
event_signals = [s for s in signals if s.get("event_types")]
if event_signals:
    conclusion = JudgmentConclusion.EVENT_EXIST
else:
    conclusion = JudgmentConclusion.EVENT_ABSENT   # ← L1004，SHIJIAN 域活跃使用
```

`EVENT_ABSENT` 在 **SHIJIAN 域 judge（L993-1011）是活值**：无 event 信号 → `EVENT_ABSENT`。⑮-3 把它写成「残留死值」是**事实错误**。

**⚠️ 但 ⑮-3 的另一条关联结论仍成立（需保留）**：
G-1 异常路径 `run_ziping_judgment` 捕获异常后**只回填 `wangshuai=UNKNOWN` 一个 DomainJudgment**，其余 4 域（geju/yongshen/shishen/shijian）保持 `None`。即异常降级态下 SHIJIAN 不产 `EVENT_ABSENT` 而是 `None`。故「SHISHEN/SHIJIAN None vs UNKNOWN」语义项（⑮-3 Remediation Queue P2 行）依旧 OPEN，不受本纠错影响。

> 订正结论：⑮-3 D-2 应改口——`EVENT_ABSENT` 非死值（SHIJIAN 活跃使用）；真正需要关注的是「异常降级态下 4 域 = None」的语义粒度丢失（已在 ⑮-3 G/Judgment 行与 P2 登记），以及 `has_core_judgment` 误报（P0-2）。

---

### C-2 — 5 域 judge 是否消费 signals【澄清，非纠错】

**取证 7 显示**：5 个 `judge` 方法体里，只有 **SHIJIAN 域实际遍历 `signals`**（`event_signals = [s for s in signals if s.get("event_types")]`）。WANGSHUAI/GEJU/YONGSHEN 三域靠 `_extract_context`（4柱+日主）派生，SHISHEN 靠 context 静态查。

而 `run_ziping_judgment` 传入的 `signals_by_domain = {}`（bridge L88，空 dict）。因此：

> **经 `run_ziping_judgment` 这条 bridge 路径，SHIJIAN 域永远拿不到 event_signals → 恒产 `EVENT_ABSENT`。** 这不是 P0（SHIJIAN 本就 0 生产消费），但坐实 N-2「bridge 路径未真正接通 Feature 层 26 字段」——即使接通生产，若不把 signals_by_domain 喂进去，SHIJIAN 域也退化为常量结论。

**严重级**：并入 N-2（P1）。不新增 P0。

---

## 3. P0 去重维持（不因本次复核改变）

反向审计**不推翻** ⑮-3 的 P0 去重结论，仅在根因描述上补充 N-3 的旁路对象事实：

```text
P0-1 = 单一架构断点（6 观测面 B-3/C-4/D-3/F-4/H-2/H-3，同根因）
       + N-3 旁路契约对象事实（并入，非新增）
P0-2 = has_core_judgment() UNKNOWN 误报（⑮-2 CLOSED 域行为，独立）
```

### P0-2 复核（`judgment.py` L187-192，代码实锤维持 ⑮-3 结论）

```python
@property
def has_core_judgment(self) -> bool:
    """是否完成核心三域（旺衰/格局/用神）判断"""
    return all([
        self.wangshuai is not None,
        self.geju is not None,
        self.yongshen is not None,
    ])
```

判据 = `is not None`（域对象存在），非 `conclusion != UNKNOWN`。全 UNKNOWN 态（含 G-1 异常降级态：三核心域被回填 UNKNOWN 对象）→ 仍报 True。**⑮-3 P0-2 结论成立，维持 OPEN / 需单独裁决（涉 ⑮-2 CLOSED 域）。**

---

## 4. 新增/订正后的 Remediation Queue（仅登记，不执行）

> **User 裁决（2026-09-10）**：N-1、N-2、C-1、C-2 均**不改代码**，并入既有 Queue。
> P0-1 / P0-2 现在**都不动**，进入 **Remediation Architecture Arbitration 架构对比**阶段。
> 任何开发 BOT 不得在本阶段修改代码、Evidence、Rule ID 或 ⑮-0/⑮-1/⑮-2 CLOSED 项。

| 优先级 | 项目 | 来源 | 状态 |
|--------|------|------|------|
| **P0** | ZiPing Chain B → Production Chain A 接通（含 N-3 旁路对象 + N-2 signals 未喂入） | ⑮-3 P0-1 + 15.6b | OPEN / 待架构对比 |
| **P0** | `has_core_judgment()` UNKNOWN 误报（P0-2，涉 ⑮-2 CLOSED 域） | ⑮-3 P0-2 | OPEN / 需单独裁决 |
| P1 | **N-1 `require_factory=False` vs 注释 True（代码—契约不匹配）** | 15.6b 新 | OPEN |
| P1 | **N-2 build_context 仅取 4柱+日主，9 扩展字段 0 进入 Judgment Context** | 15.6b 新 | OPEN |
| P1 | E-7 `atomic_claims` 内部 ID 暴露（泄漏 vs 审计字段，待裁决） | ⑮-3 | OPEN |
| P1 | F-7/G-5/G-7 未接通状态显式标识（ENGINE_NOT_CONNECTED 类输出语义） | ⑮-3 | OPEN |
| P1 | Assertion V2 / Legacy 双轨定轨 + 类型映射 | ⑮-3 | OPEN |
| P1 | ⑮-2-P1-Sub provenance 未闭合项（DTS-106 / ZPZ PARTIAL x5 / 调候 / 病药 8,-7 / 五级顺序 / YHZP-105） | ⑮-3 | EXISTING OPEN |
| P2 | Replay 随机 ID / `created_at`（E8 前置，meta 段剥离） | ⑮-3 | OPEN |
| P2 | `enable_validation=False` 开关语义 | ⑮-3 | OPEN |
| P2 | fallback provenance 契约 | ⑮-3 | OPEN |
| P2 | SHISHEN/SHIJIAN `None` vs `UNKNOWN`（异常态 4 域=None，与 N-2/C-2 关联） | ⑮-3 + 15.6b | OPEN |

---

## 5. 冻结项（本审计生效后维持不变）

```text
Bazi ①–⑭ CLOSED 🔒
Canonical ⑭ FROZEN 🔒
⑮-0 接入契约 CLOSED 🔒
⑮-1 自身方法 CLOSED 🔒
⑮-2 P0 CLOSED 🔒
⑮-2-P1-Sub Audit CLOSED / Provenance OPEN / Admission BLOCKED
⑮-3 Audit COMPLETE / Integration BLOCKED（BZ-FNDR-15.6-15-3）
⑮-3 反向一致性审计 COMPLETE / 报告事实 1 处纠错（C-1）/ 2 处新 P1 登记（N-1/N-2）
Golden expected values 不动
Basis: 415 PASS 基线 + Dual-Track 44/44
```

---

## 6. 反向一致性审计核心结论

> **⑮-3 主体结论（P0-1 单架构断点 + P0-2 误报，Production Integration BLOCKED）经逐 commit 代码复核全部维持成立，无一被推翻。**
>
> **但 ⑮-3 报告存在 1 处事实错误（C-1 `EVENT_ABSENT` 误写为死值，实为 SHIJIAN 活值）+ 2 处表述过松（N-1 `require_factory` 实际 False、N-2 build_context 缺口未量化），本次 15.6b 据代码订正。**
>
> 订正后的精确表述：
> - **Calculation Core = 🟢 可独立运行**（5 域 judge 只需 4柱+日主，代码实证）；
> - **ZiPing Contract Consumption = 🟠 未证明完整消费扩展契约**（9 字段 0 进 Context，N-2）；
> - **Production Integration = 🔴 未接入**（P0-1，N-3 旁路对象坐实）。
>
> **Production Admission 维持 BLOCKED / CONDITIONAL。CODE REMEDIATION = NOT STARTED。**
> 下一步 = Remediation Architecture Arbitration（P0-1 接通方案架构级对比），不在本审计执行。

---

*Generated by BOT-MASTER on 2026-09-10*
*Code change: 0 | Files modified: 1 (this audit report only)*
*取证基线：git show 40eeb359 / 48e66f6c / ab7a9574 已提交版本，非工作区。*
