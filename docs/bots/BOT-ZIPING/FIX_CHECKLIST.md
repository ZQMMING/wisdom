# ZIPING P0 修复执行清单

**任务 ID**: T-ENGINE-BAZI-002 Phase 4 Fix
**执行者**: @bot-ziping
**日期**: 2026-09-07
**依据**: BOT-MASTER 裁决表

---

## 执行原则

1. **按顺序修复** — 不得跳步
2. **修复一项，测试一项** — 不得批量修复
3. **禁止修改 BAZI** — 仅修复 ZIPING
4. **禁止补 YG 规则** — 先稳定基础链路
5. **每步提交前确认测试通过**

---

## Fix-001: 删除 ContextAssembler 中的重复排盘调用

### 目标
删除 `context_assembler.py:532` 的 `bazi_engine.compute()` 调用，改为消费传入的 chart 参数。

### 当前代码
```python
# src/tongshu/reasoning/context_assembler.py:527-532
def assemble(self, case_id: str, birth_year: int, birth_month: int,
             birth_day: int, birth_hour: int, gender: str,
             target_year: int) -> TemporalContext:
    """完整组装TemporalContext."""
    # 0. 只调用一次BaziEngine
    chart = self.bazi_engine.compute((birth_year, birth_month, birth_day, birth_hour), gender)
```

### 修复方案
```python
def assemble(self, case_id: str, chart, gender: str,
             target_year: int) -> TemporalContext:
    """完整组装TemporalContext.
    
    Args:
        chart: 已计算的 BaziChart（由 ComputeStage 提供）
    """
    # 0. 直接使用传入的 chart，不再重新排盘
```

### 测试要求
1. `__main__` 测试块需先调用 BaziEngine.compute()，再传入 assemble()
2. 确认输出与修复前一致

### 验收标准
- [ ] 第532行的 compute() 调用已删除
- [ ] assemble() 方法签名已更新
- [ ] `__main__` 测试块已适配
- [ ] 测试通过: `python -m pytest tests/test_phase3_p0.py -v`

---

## Fix-002: 修复硬编码路径

### 目标
将生产代码中的硬编码绝对路径改为相对路径。

### 涉及文件
1. `src/tongshu/phase_b1_evidence_connection.py` (3处)
2. `src/tongshu/phase_b2_1_remediation.py` (2处)
3. `src/tongshu/phase_b2_rule_authorization.py` (3处)

### 修复模式
```python
# 修复前
loader = EvidenceLoader(Path("D:/shuntian/data/evidence"))

# 修复后
_REPO_ROOT = Path(__file__).resolve().parents[2]  # D:/shuntian
loader = EvidenceLoader(_REPO_ROOT / "data" / "evidence")
```

### 验收标准
- [ ] 所有生产代码中的硬编码路径已替换
- [ ] 脚本目录中的硬编码路径保持不变（可接受）
- [ ] 测试通过

---

## Fix-003: 决策 Gap 3（等待 BOT-MASTER 裁决）

### 选项 A: 集成 Registry
- 将 EvidenceRegistry 和 RuleRegistry 集成到生产路径
- 启用 Rule Lifecycle 状态机
- 强制执行 Authorization Gate

### 选项 B: 移除 Registry
- 删除 phase_b1_evidence_connection.py 中的 Registry 类
- 保留 EvidenceLoader 作为证据加载器
- Phase B-2.1 的 RemediationEngine 作为参考

### 验收标准
- [ ] 根据裁决执行对应选项
- [ ] 代码清洁，无孤立类

---

## Fix-004: 添加 Signal.domain 字段

### 目标
在 Signal 数据类中添加 domain 字段，区分五大辨证域。

### 当前代码
```python
# src/tongshu/reasoning/signal_engine.py:117-131
@dataclass(frozen=True)
class Signal:
    signal_id: str
    ontology_type: str
    direction: str
    polarity: str
    strength: str
    layer: str
    rule_refs: list
    evidence_refs: list
```

### 修复方案
```python
@dataclass(frozen=True)
class Signal:
    signal_id: str
    ontology_type: str
    direction: str
    polarity: str
    strength: str
    layer: str
    domain: str  # 新增: 辨证域（wangshuai/pattern/yongshen/ten_god/event）
    rule_refs: list
    evidence_refs: list
```

### 验收标准
- [ ] Signal 类已添加 domain 字段
- [ ] 所有创建 Signal 的地方已更新
- [ ] 测试通过

---

## Fix-005: 建立 Domain Judgment 层

### 目标
建立五大辨证域各自的 Judgment 产出机制。

### 新增文件
- `src/tongshu/reasoning/domain_judgment.py`

### 设计要点
```python
@dataclass(frozen=True)
class DomainJudgment:
    domain: str  # wangshuai / pattern / yongshen / ten_god / event
    judgment_id: str
    signals: List[Signal]
    conclusion: str
    confidence: str  # HIGH / MEDIUM / LOW / UNRESOLVED
    evidence_refs: List[str]
    rule_refs: List[str]
```

### 验收标准
- [ ] DomainJudgment 类已定义
- [ ] 五大域各自的 Judgment 逻辑已实现
- [ ] 每个域能独立消费本域 Signal，产出 Judgment

---

## Fix-006: 建立 Judgment Synthesis 机制

### 目标
汇总各域 Judgment 为最终语义信号。

### 新增文件
- `src/tongshu/reasoning/synthesis.py`

### 设计要点
```python
class JudgmentSynthesis:
    def synthesize(self, judgments: Dict[str, DomainJudgment]) -> SemanticSignal:
        """汇总各域 Judgment，处理冲突，产出最终语义信号"""
        ...
```

### 验收标准
- [ ] Synthesis 机制已实现
- [ ] 能处理域间冲突
- [ ] 产出最终的 SemanticSignal

---

## Fix-007: 补充缺失的 Schema 文件

### 目标
创建 rule.schema.json 和 evidence.schema.json。

### 新增文件
- `docs/rule.schema.json`
- `docs/evidence.schema.json`

### 验收标准
- [ ] Schema 文件已创建
- [ ] 现有规则/证据能通过 Schema 验证
- [ ] test_rule_lifecycle.py 测试通过

---

## Fix-008: 端到端测试验证

### 目标
确认所有修复后，端到端链路正常。

### 测试清单
- [ ] `tests/test_rule_engine.py` — 12/12 PASS
- [ ] `tests/test_phase3_p0.py` — 3/3 PASS
- [ ] `tests/test_rule_lifecycle.py` — 9/9 PASS（Fix-007 后）
- [ ] 端到端回归测试

---

## 执行检查表

### Fix-001 完成后
- [ ] git diff 确认仅修改 context_assembler.py
- [ ] 测试通过
- [ ] 无其他文件受影响

### Fix-002 完成后
- [ ] git diff 确认仅修改 phase_b*.py 文件
- [ ] 测试通过
- [ ] 脚本目录中的硬编码路径保持不变

### Fix-004 完成后
- [ ] git diff 确认修改了 signal_engine.py
- [ ] 测试通过
- [ ] 无破坏性变更

### Fix-005/006 完成后
- [ ] 新增文件已创建
- [ ] 测试通过
- [ ] 五大域 Judgment 能独立产出

### Fix-007 完成后
- [ ] Schema 文件已创建
- [ ] test_rule_lifecycle.py 9/9 PASS

### Fix-008 完成后
- [ ] 所有测试通过
- [ ] 端到端链路正常
- [ ] 准备冻结申请

---

**执行者**: @bot-ziping  
**状态**: 等待开始执行 Fix-001
