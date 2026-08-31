# P1.3 — Cross-Domain Evidence Integration Design

> **设计时间**：2026-09-01
> **状态**：DRAFT — 待 User 裁决后实施
> **基线**：P1.2 冻结（commit 28133c0）

---

## 一、目标

验证：**两个不同体系（子平 + 紫微）进入同一事件上下文时，系统能否保持"互补不比较"**。

不是：
```text
子平 vs 紫微
  ↓
谁更强？谁冲突？
```

而是：
```text
子平 Evidence ──┐
紫微 Evidence ──┼→ EvidenceCoverage（结构性组织）
                │
                └→ 各自独立 Assertion
```

---

## 二、当前架构支持情况

### 2.1 已具备的跨域机制

| 组件 | 当前状态 | P1.3 用途 |
|------|---------|----------|
| `EvidenceCoverage.source_engines` | ✅ 支持多引擎列表 | 记录哪些引擎提供了证据 |
| `EvidenceCoverage.assertion_ids` | ✅ 支持多 Assertion 聚合 | 记录覆盖范围内所有 Assertion |
| `JudgmentRule.MULTI_SOURCE` | ✅ 检查 source_engines 包含关系 | 触发跨体系 Judgment |
| `EvidenceCoverage.evidence_count` | ✅ 仅统计，不参与 Judgment | 记录证据数量（非投票） |

### 2.2 缺失的组件

| 组件 | 说明 | 优先级 |
|------|------|--------|
| `CrossDomainOrchestrator` | 接收多引擎 Evidence，构建 EvidenceCoverage | 🔴 HIGH |
| `cross_domain_assertion_builder` | 合并多个引擎的 Assertion，不做方向比较 | 🔴 HIGH |
| P1.3 集成测试 | 验证 Bazi + Ziwei 共享上下文 | 🔴 HIGH |

---

## 三、核心 Contract 变更

### 3.1 EvidenceCoverage 扩展（可选）

当前 `EvidenceCoverage` 已满足基本需求。可能需要新增：

```python
@dataclass(frozen=True)
class CrossDomainContext:
    """跨体系共享上下文。

    不包含方向比较，仅记录各体系独立产出的事实。
    """
    case_id: str
    temporal_scope: str  # birth / year / month / ...
    bazi_evidence_ids: List[str]      # 子平证据 ID 列表
    ziwei_evidence_ids: List[str]     # 紫微证据 ID 列表
    # 未来可扩展：blind_evidence_ids, heluo_evidence_ids, yi_evidence_ids
```

### 3.2 新增：CrossDomainOrchestrator

```python
class CrossDomainOrchestrator:
    """跨体系证据编排器。

    职责：
    1. 接收多个引擎的 Evidence
    2. 构建 EvidenceCoverage（结构性组织，不比较方向）
    3. 查找并应用 Authorization Rule（JudgmentRule）
    4. 产出多体系独立 Assertion + 可选 Judgment

    严禁：
    - 比较不同引擎的 direction
    - 计算 confidence / weight / score
    - 产生 CONFLICTED / ALIGNED / PARTIAL
    - 投票 / 多数决
    """

    def __init__(
        self,
        bazi_producer: BaziEvidenceProducer,
        ziwei_producer: ZiweiEvidenceProducer,
        assertion_library: AssertionRuleLibrary,
        judgment_library: JudgmentRuleLibrary,
    ):
        self._bazi = bazi_producer
        self._ziwei = ziwei_producer
        self._assertion_lib = assertion_library
        self._judgment_lib = judgment_library

    def orchestrate(
        self,
        case_id: str,
        bazi_chart: BaziChart,
        ziwei_chart: ZiweiChart,
    ) -> CrossDomainResult:
        """编排跨体系证据。

        返回 CrossDomainResult：
        - bazi_assertions: List[CanonicalAssertion]
        - ziwei_assertions: List[CanonicalAssertion]
        - coverage: EvidenceCoverage（合并后的覆盖）
        - judgments: List[Judgment]（授权判断，如有）
        - no_assertion_count: int（未授权数量）
        """
        ...
```

### 3.3 新增：CrossDomainResult

```python
@dataclass(frozen=True)
class CrossDomainResult:
    """跨体系编排结果。"""
    case_id: str
    bazi_assertions: List[CanonicalAssertion]
    ziwei_assertions: List[CanonicalAssertion]
    coverage: EvidenceCoverage
    judgments: List[Judgment]
    no_assertion_count: int  # 未授权数量（用于审计）

    def verify_no_cross_comparison(self) -> List[str]:
        """验证：没有任何跨体系方向比较逻辑被调用。"""
        errors = []
        # 检查 assertions 中没有来自其他引擎的 direction 依赖
        for a in self.bazi_assertions:
            if a.source_engine != "ZI_PING":
                errors.append(f"Bazi assertion has wrong engine: {a.source_engine}")
        for a in self.ziwei_assertions:
            if a.source_engine != "ZI_WEI":
                errors.append(f"Ziwei assertion has wrong engine: {a.source_engine}")
        # 检查 coverage 中没有隐藏的比较逻辑
        if hasattr(self.coverage, 'direction_alignment'):
            errors.append("Coverage should not have direction_alignment")
        return errors
```

---

## 四、P1.3 测试计划

### 4.1 测试文件

```
tests/spec/test_cross_domain_integration.py
```

### 4.2 测试用例（预计 15-20 个）

#### Stage 1: Evidence 独立生产

| 用例 | 验证 |
|------|------|
| T1 | Bazi Evidence 无 direction/strength/confidence |
| T2 | Ziwei Evidence 无 direction/strength/confidence |
| T3 | 两套 Evidence 结构独立，互不影响 |

#### Stage 2: Assertion 独立生成

| 用例 | 验证 |
|------|------|
| T4 | Bazi Assertion direction 来自 Bazi 授权规则 |
| T5 | Ziwei Assertion direction 来自 Ziwei 授权规则 |
| T6 | Bazi Assertion 不引用 Ziwei Evidence |
| T7 | Ziwei Assertion 不引用 Bazi Evidence |
| T8 | 两套 Assertion 的 assertion_id 格式正确 |

#### Stage 3: EvidenceCoverage 合并

| 用例 | 验证 |
|------|------|
| T9 | EvidenceCoverage.source_engines 包含 ZI_PING + ZI_WEI |
| T10 | EvidenceCoverage.evidence_count = 各体系证据数之和 |
| T11 | EvidenceCoverage.assertion_ids 包含所有 Assertion |
| T12 | EvidenceCoverage 无 direction 字段 |
| T13 | EvidenceCoverage 无 vote/score/weight 字段 |

#### Stage 4: 禁止行为验证

| 用例 | 验证 |
|------|------|
| T14 | 无 CrossAnalyzer 调用 |
| T15 | 无 ConvergenceArbiter 调用 |
| T16 | 无 evidence_count 阈值触发 Judgment |
| T17 | 无 NEUTRAL fallback |
| T18 | 追溯链完整：Assertion → Rule → Evidence → Engine |

#### Stage 5: 真实命例验证

| 用例 | 验证 |
|------|------|
| T19 | 纪晓岚命例：Bazi + Ziwei 同时跑通 |
| T20 | 两套 Assertion 可独立追溯到各自 Engine |

---

## 五、验收红线（严格禁止）

```text
❌ 任何跨引擎 direction 比较
❌ 任何 vote / score / weight / confidence 聚合
❌ 任何 CONFLICTED / ALIGNED / PARTIAL 状态
❌ 任何 evidence_count >= N 触发 Judgment
❌ 任何 NEUTRAL 作为默认 fallback
❌ 任何旧 Signal / CrossAnalyzer / Convergence 调用
❌ 任何强度/置信度数值计算
❌ 任何"哪个体系更准"的推断
```

---

## 六、实施步骤

### Phase 1: Design（当前）
- [x] 本设计文档
- [ ] User 裁决

### Phase 2: Contract Extension
- [ ] 新增 `CrossDomainContext` / `CrossDomainResult`（如需要）
- [ ] 扩展现有 `EvidenceCoverage`（如需要）

### Phase 3: Orchestrator Implementation
- [ ] 实现 `CrossDomainOrchestrator`
- [ ] 实现 `cross_domain_assertion_builder`

### Phase 4: Tests
- [ ] 编写 `test_cross_domain_integration.py`
- [ ] 所有红线测试 PASS

### Phase 5: Audit
- [ ] 独立审计（Claude 只读）
- [ ] 输出 `docs/audit/p1_3_cross_domain_audit.md`

---

## 七、与 P1.2 的关系

| 维度 | P1.2 | P1.3 |
|------|------|------|
| 范围 | 单引擎垂直切片 | 多引擎横向编排 |
| Contract | 建立 Evidence/Atom/Assertion | 复用，不修改 |
| 验证 | 单引擎全链路 | 跨引擎共存验证 |
| 禁止行为 | 方向泄漏/投票 | 同左 + 跨引擎比较 |
| 冻结 | ✅ FROZEN | 待裁决 |

**关键原则**：P1.3 不得修改 P1.2 已冻结的 Contract。如果 P1.3 需要新的 Contract，必须经过独立审计 + User 裁决。

---

*本文档为 P1.3 设计草案，待 User 裁决后进入实施阶段。*
