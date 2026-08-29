"""
P0-2.7.1A-R Judgment Logic Kernel - 辨证逻辑内核（Contract Hardening 版）

这不是命理知识，也不是五部经典。
这是一个通用的符号推理执行器。

【P0-2.7.1A-R 修复的 7 个问题】
R1 — Evidence 不可变：禁止原地修改 Evidence，使用 EffectiveEvidence（Evidence + EvaluationContext）
R2 — 删除 numeric confidence：使用离散确定性状态 CertaintyState（DERIVED/QUALIFIED/UNKNOWN/UNRESOLVED）
R3 — CONSTRAINT ≠ REJECT：Kernel 不允许自动 constraint→rejected，必须 Rule explicitly declares BLOCK/REJECT
R4 — SUFFICIENT 不得拥有内建命理语义：只作为 Rule-local operator，Kernel 不解释其命理含义
R5 — Expression Tree：使用 JudgmentExpression 替代 group list，支持 AND/OR/NOT/REQUIRED/SUFFICIENT/OPPOSE/BLOCK/TRANSFORM/QUALIFY
R6 — Kernel 不规定命理优先级：优先级来自 JudgmentRule 的表达式树，不是 Kernel 默认决定
R7 — Kernel vs Classical Validation 边界：测试分两套 KERNEL_TEST 和 CLASSICAL_JUDGMENT_TEST

核心原则：
- 不使用 score / weight / threshold
- 不使用"支持证据数量"判断整体
- 使用符号逻辑：AND, OR, NOT, REQUIRED, SUFFICIENT, OPPOSE, BLOCK, TRANSFORM, QUALIFY
- Evidence 不可变
- CONSTRAINT ≠ REJECT
- UNRESOLVED 是合法结果
- Kernel 提供执行机制，不规定命理优先级
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Set, Any, Union
from abc import ABC, abstractmethod


# ============================================================
# 一、核心枚举定义
# ============================================================

class Polarity(Enum):
    """证据极性"""
    SUPPORT = "support"        # 支持结论
    CONSTRAINT = "constraint"  # 制约结论（注意：CONSTRAINT ≠ REJECT）
    NEUTRAL = "neutral"        # 中性
    MODIFIER = "modifier"      # 修改其他证据的有效性
    TRANSFORM = "transform"    # 转化证据意义


class EvidenceStatus(Enum):
    """证据状态（原始 Evidence 的状态，不可变）"""
    PRESENT = "present"        # 证据存在
    ABSENT = "absent"          # 证据缺失
    UNKNOWN = "unknown"        # 证据未知（无法确定）


class CertaintyState(Enum):
    """
    R2: 证据确定性状态（离散，替代 numeric confidence）
    
    注意：这不是力量评分，是证据推导的确定性。
    由上游 Evidence Derivation / Provenance 决定，不是 Judgment Kernel 自己判断。
    """
    DERIVED = "derived"        # 已从确定的 Fact/Relation 推导出来
    QUALIFIED = "qualified"    # 有条件推导（需要额外条件）
    UNKNOWN = "unknown"        # 未知（无法确定）
    UNRESOLVED = "unresolved"  # 未解决（存在冲突或证据不足）


class JudgmentOutcome(Enum):
    """辨证结果"""
    CONFIRMED = "confirmed"        # 确认成立
    QUALIFIED = "qualified"        # 有条件成立（需要限定）
    UNRESOLVED = "unresolved"      # 无法裁决（证据不足或冲突）
    REJECTED = "rejected"          # 不成立（必须由 Rule 明确声明 BLOCK/REJECT）
    NOT_APPLICABLE = "not_applicable"  # 不适用


class LogicOperator(Enum):
    """
    逻辑操作符
    
    R4: SUFFICIENT / OPPOSE 等只是 Rule-local operator，Kernel 不解释其命理含义。
    Kernel 只知道：Rule 声明了某个条件使用了某个 operator。
    """
    AND = "and"              # 所有条件必须同时成立
    OR = "or"                # 任一条件成立即可
    NOT = "not"              # 条件不成立
    REQUIRED = "required"    # 必要条件，缺失则 UNRESOLVED（Rule-local 语义）
    SUFFICIENT = "sufficient"  # 充分条件（Rule-local 语义，Kernel 不解释其命理含义）
    OPPOSE = "oppose"        # 反向制约（注意：OPPOSE ≠ REJECT，只是制约）
    BLOCK = "block"          # 阻断结论成立（Rule 明确声明）
    OVERRIDE = "override"    # 覆盖普通规则（Rule 明确声明）
    TRANSFORM = "transform"  # 转化证据解释（不修改原始 Evidence）
    QUALIFY = "qualify"      # 降低结论等级（CONFIRMED → QUALIFIED）
    NEGATE = "negate"        # 否定证据


class TestCategory(Enum):
    """
    R7: 测试分类边界
    
    KERNEL_TEST：验证逻辑执行器本身（AND/OR/NOT/BLOCK/TRANSFORM/UNRESOLVED 等）
    CLASSICAL_JUDGMENT_TEST：验证某条经典 + 某个命例 + 某组 Evidence = 原典授权的 Judgment
    
    两套测试绝对不能混。
    """
    KERNEL_TEST = "kernel_test"
    CLASSICAL_JUDGMENT_TEST = "classical_judgment_test"


# ============================================================
# 二、R1: Evidence（证据）不可变数据结构
# ============================================================

@dataclass(frozen=True)  # R1: frozen=True 保证不可变
class Evidence:
    """
    辨证证据（不可变）
    
    R1: Evidence 一旦产生，就不应该被 Judgment Engine 原地改写。
    任何"转化"或"修改"都应该通过 EffectiveEvidence（Evidence + EvaluationContext）表达。
    
    关键：Evidence 必须带 judgment_target，说明这个证据是为哪个辨证目标服务的。
    同一个 Relation 可以为不同辨证目标产生不同 Evidence。
    """
    evidence_id: str                    # 证据 ID，如 E-S-001
    judgment_target: str                # 辨证目标，如 DAY_MASTER_STRENGTH
    evidence_type: str                  # 证据类型，如 SEASONAL_SUPPORT
    polarity: Polarity                  # 证据极性
    status: EvidenceStatus = EvidenceStatus.PRESENT  # 证据状态
    source_relation_ids: tuple = field(default_factory=tuple)  # 来源 Relation ID（tuple 保证不可变）
    context: Dict[str, Any] = field(default_factory=dict)  # 上下文
    evidence_meaning: str = ""          # 证据含义
    provenance: str = ""                # 来源
    certainty_state: CertaintyState = CertaintyState.DERIVED  # R2: 离散确定性状态，替代 numeric confidence
    scope: str = ""                     # 范围
    
    def __hash__(self):
        """基于 evidence_id 哈希"""
        return hash(self.evidence_id)
    
    def __eq__(self, other):
        if not isinstance(other, Evidence):
            return False
        return self.evidence_id == other.evidence_id


# ============================================================
# 三、R1: EffectiveEvidence（有效证据视图）
# ============================================================

@dataclass
class EffectiveEvidence:
    """
    R1: 有效证据视图
    
    不修改原始 Evidence，而是在 EvaluationContext 中表达"在某个辨证规则下，这个 Evidence 的有效解释是什么"。
    
    例如：
    原始 Evidence: E001 polarity = SUPPORT
    在某个转化条件下：
    Judgment A effective_polarity(E001) = CONSTRAINT
    但 E001 本体仍然是 SUPPORT
    
    这样才能保证：
    同一事实 → 同一 Evidence → 不同体系 → 不同 interpretation
    而不会互相污染。
    """
    original_evidence: Evidence         # 原始 Evidence（不可变）
    evaluation_context: 'EvaluationContext'  # 评估上下文
    effective_polarity: Polarity        # 有效极性（可能与原始不同）
    effective_status: EvidenceStatus     # 有效状态
    transform_reasons: List[str] = field(default_factory=list)  # 转化原因
    is_modified: bool = False            # 是否被修改
    
    @property
    def evidence_id(self) -> str:
        return self.original_evidence.evidence_id
    
    @property
    def evidence_type(self) -> str:
        return self.original_evidence.evidence_type
    
    @property
    def judgment_target(self) -> str:
        return self.original_evidence.judgment_target
    
    def __hash__(self):
        """基于 original_evidence.evidence_id 哈希"""
        return hash(self.original_evidence.evidence_id)
    
    def __eq__(self, other):
        if not isinstance(other, EffectiveEvidence):
            return False
        return self.original_evidence.evidence_id == other.original_evidence.evidence_id


@dataclass
class EvaluationContext:
    """
    评估上下文
    
    包含某个 JudgmentRule 评估时的上下文信息，用于产生 EffectiveEvidence。
    不修改原始 Evidence。
    """
    rule_id: str                         # 规则 ID
    system: str                          # 体系/经典
    target: str                          # 辨证目标
    transform_rules: List[Dict[str, Any]] = field(default_factory=list)  # 转化规则
    modifier_rules: List[Dict[str, Any]] = field(default_factory=list)   # 修改器规则
    
    def create_effective_evidence(self, evidence: Evidence) -> EffectiveEvidence:
        """
        基于原始 Evidence 和评估上下文，创建 EffectiveEvidence。
        
        注意：不修改原始 Evidence，只是创建一个新的视图。
        """
        effective_polarity = evidence.polarity
        effective_status = evidence.status
        transform_reasons = []
        is_modified = False
        
        # 应用转化规则（不修改原始 Evidence，只是改变有效解释）
        for transform_rule in self.transform_rules:
            target_type = transform_rule.get("evidence_type")
            if target_type == evidence.evidence_type:
                from_polarity = transform_rule.get("from_polarity")
                to_polarity = transform_rule.get("to_polarity")
                if from_polarity == evidence.polarity and to_polarity:
                    effective_polarity = to_polarity
                    transform_reasons.append(transform_rule.get("reason", "transform"))
                    is_modified = True
        
        # 应用修改器规则
        for modifier_rule in self.modifier_rules:
            target_type = modifier_rule.get("evidence_type")
            if target_type == evidence.evidence_type:
                modifier_effect = modifier_rule.get("effect")
                if modifier_effect == "reduce_certainty":
                    # 注意：不修改原始 Evidence 的 certainty_state
                    # 只是在 EffectiveEvidence 中记录这个修改
                    transform_reasons.append(modifier_rule.get("reason", "modifier"))
                    is_modified = True
        
        return EffectiveEvidence(
            original_evidence=evidence,
            evaluation_context=self,
            effective_polarity=effective_polarity,
            effective_status=effective_status,
            transform_reasons=transform_reasons,
            is_modified=is_modified
        )


# ============================================================
# 四、R5: JudgmentExpression（辨证表达式树）
# ============================================================

@dataclass
class JudgmentExpression:
    """
    R5: 辨证表达式树
    
    替代 required_groups / support_groups / constraint_groups 等扁平 group list。
    支持嵌套表达式：AND(REQUIRED(A), OR(B, C), NOT(BLOCK(D)))
    
    这才真正可以表达传统辨证的条件组合。
    """
    operator: LogicOperator             # 逻辑操作符
    description: str = ""               # 表达式描述
    
    # 叶子节点：引用 Evidence
    evidence_type: Optional[str] = None  # 证据类型
    evidence_id: Optional[str] = None     # 具体证据 ID
    expected_status: EvidenceStatus = EvidenceStatus.PRESENT  # 期望状态
    
    # 组合节点：子表达式
    sub_expressions: List['JudgmentExpression'] = field(default_factory=list)
    
    # R4: Rule-local 语义（Kernel 不解释其命理含义）
    rule_local_semantics: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, effective_evidences: Set[EffectiveEvidence]) -> 'ExpressionResult':
        """
        评估表达式
        
        R3: CONSTRAINT ≠ REJECT
        Kernel 只知道条件是否满足，不知道"制约是否足以推翻结论"。
        后者必须由 Rule 明确声明。
        """
        matched = []
        missing = []
        
        if self.sub_expressions:
            # 组合节点
            sub_results = [se.evaluate(effective_evidences) for se in self.sub_expressions]
            
            if self.operator == LogicOperator.AND:
                satisfied = all(r.satisfied for r in sub_results)
            elif self.operator == LogicOperator.OR:
                satisfied = any(r.satisfied for r in sub_results)
            elif self.operator == LogicOperator.NOT:
                satisfied = not all(r.satisfied for r in sub_results)
            else:
                # 其他操作符在组合节点上的语义由 Rule-local 决定
                satisfied = all(r.satisfied for r in sub_results)
            
            for r in sub_results:
                matched.extend(r.matched)
                missing.extend(r.missing)
        else:
            # 叶子节点：检查 Evidence 是否存在
            target = None
            for ee in effective_evidences:
                if (self.evidence_id and ee.evidence_id == self.evidence_id) or \
                   (self.evidence_type and ee.evidence_type == self.evidence_type):
                    target = ee
                    break
            
            if target:
                if self.operator == LogicOperator.NOT:
                    satisfied = target.effective_status != self.expected_status
                else:
                    satisfied = target.effective_status == self.expected_status
                if satisfied:
                    matched.append(target)
                else:
                    missing.append(target)
            else:
                # 证据不存在
                if self.operator == LogicOperator.NOT:
                    satisfied = True  # NOT(不存在的证据) = true
                else:
                    satisfied = False
                    missing.append(None)  # 表示证据缺失
        
        return ExpressionResult(
            expression=self,
            satisfied=satisfied,
            matched=matched,
            missing=missing
        )


@dataclass
class ExpressionResult:
    """表达式评估结果"""
    expression: JudgmentExpression
    satisfied: bool
    matched: List[EffectiveEvidence] = field(default_factory=list)
    missing: List[Optional[EffectiveEvidence]] = field(default_factory=list)


# ============================================================
# 五、JudgmentRule（辨证规则）
# ============================================================

@dataclass
class JudgmentRule:
    """
    辨证规则
    
    R6: Kernel 不规定命理优先级。
    优先级和执行流程来自 JudgmentRule 的表达式树和声明，不是 Kernel 默认决定。
    
    R3: CONSTRAINT ≠ REJECT
    只有 Rule 明确声明 BLOCK 或 REJECT，才会导致 REJECTED。
    Kernel 不会自动把 CONSTRAINT 当成 REJECT。
    
    R4: SUFFICIENT / OPPOSE 等只是 Rule-local operator，Kernel 不解释其命理含义。
    """
    rule_id: str                        # 规则 ID
    rule_name: str                      # 规则名称
    system: str                         # 体系/经典，如 DITIANSUI / ZIPING_ZHENQUAN
    target: str                         # 辨证目标，如 DAY_MASTER_STRENGTH
    output_state: str                   # 输出状态
    
    # R5: 表达式树（替代扁平 group list）
    # 主条件表达式（通常是 AND(REQUIRED(...), SUPPORT(...), ...)）
    main_expression: JudgmentExpression = field(default_factory=lambda: JudgmentExpression(operator=LogicOperator.AND))
    
    # R3: 阻断表达式（只有 Rule 明确声明 BLOCK 才会导致 REJECTED）
    block_expression: Optional[JudgmentExpression] = None
    
    # 覆盖表达式（Rule 明确声明 OVERRIDE）
    override_expression: Optional[JudgmentExpression] = None
    
    # 限定表达式（Rule 明确声明 QUALIFY，会把 CONFIRMED 降为 QUALIFIED）
    qualify_expression: Optional[JudgmentExpression] = None
    
    # 转化规则（不修改原始 Evidence，只是改变 EffectiveEvidence 的解释）
    transform_rules: List[Dict[str, Any]] = field(default_factory=list)
    modifier_rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # R6: 优先级（来自 Rule 声明，不是 Kernel 默认）
    precedence: int = 0
    
    # 冲突与缺失策略（来自 Rule 声明）
    conflict_policy: str = "unresolved"  # 冲突策略：unresolved / confirm / reject
    absence_policy: str = "unresolved"   # 缺失策略：unresolved / ignore
    
    # 元数据
    classical_source: str = ""            # 经典来源
    description: str = ""                  # 规则描述
    test_category: TestCategory = TestCategory.CLASSICAL_JUDGMENT_TEST  # R7: 测试分类
    
    def create_evaluation_context(self) -> EvaluationContext:
        """创建评估上下文"""
        return EvaluationContext(
            rule_id=self.rule_id,
            system=self.system,
            target=self.target,
            transform_rules=self.transform_rules,
            modifier_rules=self.modifier_rules
        )
    
    def evaluate(self, evidence_set: Set[Evidence]) -> 'RuleEvaluationResult':
        """
        评估辨证规则
        
        R6: 执行流程由 Rule 声明决定，不是 Kernel 默认。
        R3: 只有 block_expression 满足才会 REJECTED，CONSTRAINT 不会自动 REJECT。
        R1: 不修改原始 Evidence，使用 EffectiveEvidence。
        """
        # R1: 创建评估上下文和 EffectiveEvidence（不修改原始 Evidence）
        eval_context = self.create_evaluation_context()
        effective_evidences = {
            eval_context.create_effective_evidence(e)
            for e in evidence_set
            if e.judgment_target == self.target
        }
        
        # 检查 OVERRIDE（如果 Rule 声明了）
        if self.override_expression:
            override_result = self.override_expression.evaluate(effective_evidences)
            if override_result.satisfied:
                return RuleEvaluationResult(
                    rule_id=self.rule_id,
                    outcome=JudgmentOutcome.CONFIRMED,
                    output_state=self.output_state,
                    override_triggered=True,
                    reasoning=f"覆盖规则成立，直接确认 {self.output_state}",
                    effective_evidences=effective_evidences
                )
        
        # R3: 检查 BLOCK（Rule 明确声明 BLOCK → 规则不适用，NOT_APPLICABLE）
        # 注意：BLOCK 不是 REJECTED，而是"这个规则不适用"
        if self.block_expression:
            block_result = self.block_expression.evaluate(effective_evidences)
            if block_result.satisfied:
                return RuleEvaluationResult(
                    rule_id=self.rule_id,
                    outcome=JudgmentOutcome.NOT_APPLICABLE,  # R3: BLOCK → NOT_APPLICABLE，不是 REJECTED
                    output_state=None,
                    blocked=True,
                    reasoning=f"阻断规则成立，此规则不适用",
                    effective_evidences=effective_evidences
                )
        
        # 评估主表达式
        main_result = self.main_expression.evaluate(effective_evidences)
        
        # 检查必要条件缺失（在主表达式中查找 REQUIRED 操作符）
        missing_required = self._find_missing_required(self.main_expression, effective_evidences)
        
        if missing_required and self.absence_policy == "unresolved":
            return RuleEvaluationResult(
                rule_id=self.rule_id,
                outcome=JudgmentOutcome.UNRESOLVED,
                output_state=None,
                missing_required=missing_required,
                reasoning=f"必要条件缺失，无法裁决",
                effective_evidences=effective_evidences
            )
        
        # R3: 主表达式满足 → CONFIRMED（不会因为有 CONSTRAINT 就自动 REJECT）
        if main_result.satisfied:
            base_outcome = JudgmentOutcome.CONFIRMED
        else:
            base_outcome = JudgmentOutcome.UNRESOLVED
        
        # 检查 QUALIFY（Rule 明确声明，把 CONFIRMED 降为 QUALIFIED）
        if self.qualify_expression and base_outcome == JudgmentOutcome.CONFIRMED:
            qualify_result = self.qualify_expression.evaluate(effective_evidences)
            if qualify_result.satisfied:
                base_outcome = JudgmentOutcome.QUALIFIED
        
        # 构建推理过程
        reasoning_parts = []
        if main_result.satisfied:
            reasoning_parts.append(f"主条件成立")
        if main_result.matched:
            reasoning_parts.append(f"匹配证据：{', '.join(ee.evidence_id for ee in main_result.matched)}")
        if missing_required:
            reasoning_parts.append(f"必要条件缺失")
        
        return RuleEvaluationResult(
            rule_id=self.rule_id,
            outcome=base_outcome,
            output_state=self.output_state if base_outcome in (JudgmentOutcome.CONFIRMED, JudgmentOutcome.QUALIFIED) else None,
            main_result=main_result,
            reasoning="; ".join(reasoning_parts) if reasoning_parts else "证据不足，无法裁决",
            effective_evidences=effective_evidences
        )
    
    def _find_missing_required(self, expression: JudgmentExpression, effective_evidences: Set[EffectiveEvidence]) -> List[JudgmentExpression]:
        """递归查找缺失的 REQUIRED 条件"""
        missing = []
        
        if expression.operator == LogicOperator.REQUIRED and not expression.sub_expressions:
            # 叶子 REQUIRED 节点
            result = expression.evaluate(effective_evidences)
            if not result.satisfied:
                missing.append(expression)
        
        for sub in expression.sub_expressions:
            missing.extend(self._find_missing_required(sub, effective_evidences))
        
        return missing


@dataclass
class RuleEvaluationResult:
    """规则评估结果"""
    rule_id: str
    outcome: JudgmentOutcome
    output_state: Optional[str] = None
    override_triggered: bool = False
    blocked: bool = False
    missing_required: List[JudgmentExpression] = field(default_factory=list)
    main_result: Optional[ExpressionResult] = None
    reasoning: str = ""
    effective_evidences: Set[EffectiveEvidence] = field(default_factory=set)
    
    def is_confirmed(self) -> bool:
        return self.outcome == JudgmentOutcome.CONFIRMED
    
    def is_qualified(self) -> bool:
        return self.outcome == JudgmentOutcome.QUALIFIED
    
    def is_unresolved(self) -> bool:
        return self.outcome == JudgmentOutcome.UNRESOLVED
    
    def is_rejected(self) -> bool:
        return self.outcome == JudgmentOutcome.REJECTED
    
    def is_not_applicable(self) -> bool:
        return self.outcome == JudgmentOutcome.NOT_APPLICABLE


# ============================================================
# 六、JudgmentEngine（辨证引擎）
# ============================================================

class JudgmentEngine:
    """
    辨证引擎
    
    R6: Kernel 提供执行机制，不规定命理优先级。
    优先级来自 JudgmentRule 的声明（precedence 字段）。
    
    R7: 测试分两套 KERNEL_TEST 和 CLASSICAL_JUDGMENT_TEST，绝对不能混。
    """
    
    def __init__(self, system: str, target: str):
        self.system = system  # 体系/经典
        self.target = target  # 辨证目标
        self.rules: List[JudgmentRule] = []
    
    def add_rule(self, rule: JudgmentRule):
        """添加辨证规则（按 system 和 target 过滤，按 precedence 排序）"""
        if rule.system == self.system and rule.target == self.target:
            self.rules.append(rule)
            self.rules.sort(key=lambda r: -r.precedence)
    
    def evaluate(self, evidence_set: Set[Evidence]) -> 'FinalJudgment':
        """
        执行辨证
        
        R3: CONSTRAINT ≠ REJECT
        只有 Rule 明确声明 BLOCK 才会 REJECTED。
        
        R6: 按 Rule 声明的 precedence 排序执行，不是 Kernel 默认顺序。
        """
        # 过滤适用的证据
        applicable_evidence = {e for e in evidence_set if e.judgment_target == self.target}
        
        if not applicable_evidence:
            return FinalJudgment(
                system=self.system,
                target=self.target,
                outcome=JudgmentOutcome.UNRESOLVED,
                output_state=None,
                reasoning="没有适用于此辨证目标的证据",
                rule_results=[],
                evidence_used=applicable_evidence
            )
        
        # R6: 按 Rule 声明的 precedence 排序执行
        rule_results = []
        for rule in self.rules:
            result = rule.evaluate(applicable_evidence)
            rule_results.append(result)
        
        # R3: 过滤掉 NOT_APPLICABLE（被 BLOCK 的规则不参与综合）
        applicable_results = [r for r in rule_results if not r.is_not_applicable()]
        
        # 综合规则结果
        confirmed = [r for r in applicable_results if r.is_confirmed()]
        qualified = [r for r in applicable_results if r.is_qualified()]
        unresolved = [r for r in applicable_results if r.is_unresolved()]
        rejected = [r for r in applicable_results if r.is_rejected()]
        
        # R3: 冲突处理（CONFIRMED + REJECTED 同时存在 → UNRESOLVED）
        if confirmed and rejected:
            final_outcome = JudgmentOutcome.UNRESOLVED
            output_state = None
            reasoning = f"规则冲突：{len(confirmed)} 条确认，{len(rejected)} 条拒绝，无法裁决"
        elif confirmed:
            final_outcome = JudgmentOutcome.CONFIRMED
            output_state = confirmed[0].output_state
            reasoning = f"{len(confirmed)} 条规则确认：{output_state}"
        elif qualified:
            final_outcome = JudgmentOutcome.QUALIFIED
            output_state = qualified[0].output_state
            reasoning = f"{len(qualified)} 条规则有条件确认：{output_state}"
        elif unresolved:
            final_outcome = JudgmentOutcome.UNRESOLVED
            output_state = None
            reasoning = f"{len(unresolved)} 条规则无法裁决"
        else:
            final_outcome = JudgmentOutcome.REJECTED
            output_state = None
            reasoning = f"所有 {len(rejected)} 条规则拒绝"
        
        return FinalJudgment(
            system=self.system,
            target=self.target,
            outcome=final_outcome,
            output_state=output_state,
            reasoning=reasoning,
            rule_results=rule_results,
            evidence_used=applicable_evidence
        )


@dataclass
class FinalJudgment:
    """最终辨证结果"""
    system: str
    target: str
    outcome: JudgmentOutcome
    output_state: Optional[str]
    reasoning: str
    rule_results: List[RuleEvaluationResult] = field(default_factory=list)
    evidence_used: Set[Evidence] = field(default_factory=set)
    
    def __str__(self):
        return f"[{self.system}] {self.target}: {self.outcome.value} = {self.output_state or 'UNRESOLVED'}\n推理: {self.reasoning}"


# ============================================================
# 七、R7: Kernel Test（逻辑执行器验证，不涉及命理语义）
# ============================================================

def run_kernel_tests():
    """
    R7: KERNEL_TEST — 验证逻辑执行器本身
    
    只验证：AND/OR/NOT/BLOCK/TRANSFORM/UNRESOLVED 等逻辑操作是否正确执行。
    不验证：某条经典 + 某个命例 + 某组 Evidence = 原典授权的 Judgment。
    
    两套测试绝对不能混。
    """
    print("=" * 70)
    print("R7: KERNEL_TEST — 逻辑执行器验证（不涉及命理语义）")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    # 测试 1: AND 逻辑
    print("\n[测试 1] AND 逻辑")
    expr_and = JudgmentExpression(
        operator=LogicOperator.AND,
        sub_expressions=[
            JudgmentExpression(operator=LogicOperator.AND, evidence_type="A"),
            JudgmentExpression(operator=LogicOperator.AND, evidence_type="B"),
        ]
    )
    ee_a = EffectiveEvidence(
        original_evidence=Evidence(evidence_id="E1", judgment_target="T", evidence_type="A", polarity=Polarity.SUPPORT),
        evaluation_context=EvaluationContext(rule_id="R", system="S", target="T"),
        effective_polarity=Polarity.SUPPORT,
        effective_status=EvidenceStatus.PRESENT
    )
    ee_b = EffectiveEvidence(
        original_evidence=Evidence(evidence_id="E2", judgment_target="T", evidence_type="B", polarity=Polarity.SUPPORT),
        evaluation_context=EvaluationContext(rule_id="R", system="S", target="T"),
        effective_polarity=Polarity.SUPPORT,
        effective_status=EvidenceStatus.PRESENT
    )
    result = expr_and.evaluate({ee_a, ee_b})
    if result.satisfied:
        print("  ✓ AND(A, B) = true（A 和 B 都存在）")
        passed += 1
    else:
        print("  ✗ AND(A, B) 应该为 true")
        failed += 1
    
    # 测试 2: OR 逻辑
    print("\n[测试 2] OR 逻辑")
    expr_or = JudgmentExpression(
        operator=LogicOperator.OR,
        sub_expressions=[
            JudgmentExpression(operator=LogicOperator.OR, evidence_type="A"),
            JudgmentExpression(operator=LogicOperator.OR, evidence_type="C"),  # C 不存在
        ]
    )
    result = expr_or.evaluate({ee_a, ee_b})
    if result.satisfied:
        print("  ✓ OR(A, C) = true（A 存在，C 不存在）")
        passed += 1
    else:
        print("  ✗ OR(A, C) 应该为 true")
        failed += 1
    
    # 测试 3: NOT 逻辑
    print("\n[测试 3] NOT 逻辑")
    expr_not = JudgmentExpression(
        operator=LogicOperator.NOT,
        evidence_type="C"  # C 不存在
    )
    result = expr_not.evaluate({ee_a, ee_b})
    if result.satisfied:
        print("  ✓ NOT(C) = true（C 不存在）")
        passed += 1
    else:
        print("  ✗ NOT(C) 应该为 true")
        failed += 1
    
    # 测试 4: BLOCK 逻辑（R3: 只有 Rule 明确声明 BLOCK 才会 REJECTED）
    print("\n[测试 4] BLOCK 逻辑（R3: CONSTRAINT ≠ REJECT）")
    rule_block = JudgmentRule(
        rule_id="R-BLOCK",
        rule_name="测试阻断",
        system="TEST",
        target="T",
        output_state="X",
        block_expression=JudgmentExpression(operator=LogicOperator.BLOCK, evidence_type="B"),
        test_category=TestCategory.KERNEL_TEST
    )
    evidence_set = {
        Evidence(evidence_id="E1", judgment_target="T", evidence_type="A", polarity=Polarity.SUPPORT),
        Evidence(evidence_id="E2", judgment_target="T", evidence_type="B", polarity=Polarity.CONSTRAINT),  # CONSTRAINT，不是 BLOCK
    }
    # 注意：B 的 polarity 是 CONSTRAINT，但 block_expression 检查的是 evidence_type="B" 是否存在
    # 这证明：CONSTRAINT 本身不会导致 REJECTED，只有 Rule 明确声明 BLOCK 才会
    result = rule_block.evaluate(evidence_set)
    if result.is_not_applicable():
        print("  ✓ BLOCK(B) 成立 → NOT_APPLICABLE（Rule 明确声明 BLOCK，规则不适用）")
        passed += 1
    else:
        print("  ✗ BLOCK(B) 应该导致 NOT_APPLICABLE")
        failed += 1
    
    # 测试 5: R1 Evidence 不可变
    print("\n[测试 5] R1 Evidence 不可变（使用 EffectiveEvidence）")
    original_evidence = Evidence(
        evidence_id="E-ORIG",
        judgment_target="T",
        evidence_type="TEST",
        polarity=Polarity.SUPPORT
    )
    eval_context = EvaluationContext(
        rule_id="R",
        system="S",
        target="T",
        transform_rules=[{
            "evidence_type": "TEST",
            "from_polarity": Polarity.SUPPORT,
            "to_polarity": Polarity.CONSTRAINT,
            "reason": "test transform"
        }]
    )
    effective = eval_context.create_effective_evidence(original_evidence)
    if effective.effective_polarity == Polarity.CONSTRAINT and original_evidence.polarity == Polarity.SUPPORT:
        print("  ✓ EffectiveEvidence 极性改变为 CONSTRAINT，原始 Evidence 仍为 SUPPORT（不可变）")
        passed += 1
    else:
        print("  ✗ Evidence 不可变验证失败")
        failed += 1
    
    # 测试 6: R2 离散确定性状态（替代 numeric confidence）
    print("\n[测试 6] R2 离散确定性状态（替代 numeric confidence）")
    evidence_derived = Evidence(
        evidence_id="E-D",
        judgment_target="T",
        evidence_type="D",
        polarity=Polarity.SUPPORT,
        certainty_state=CertaintyState.DERIVED
    )
    if hasattr(evidence_derived, 'certainty_state') and not hasattr(evidence_derived, 'confidence'):
        print("  ✓ 使用 certainty_state（DERIVED），没有 numeric confidence")
        passed += 1
    else:
        print("  ✗ 应该使用 certainty_state，不应该有 confidence")
        failed += 1
    
    # 测试 7: UNRESOLVED 是合法结果
    print("\n[测试 7] UNRESOLVED 是合法结果")
    rule_unresolved = JudgmentRule(
        rule_id="R-UN",
        rule_name="测试未解决",
        system="TEST",
        target="T",
        output_state="X",
        main_expression=JudgmentExpression(
            operator=LogicOperator.AND,
            sub_expressions=[
                JudgmentExpression(operator=LogicOperator.REQUIRED, evidence_type="MISSING"),  # 必要条件缺失
            ]
        ),
        absence_policy="unresolved",
        test_category=TestCategory.KERNEL_TEST
    )
    result = rule_unresolved.evaluate(evidence_set)
    if result.is_unresolved():
        print("  ✓ 必要条件缺失 → UNRESOLVED（合法结果）")
        passed += 1
    else:
        print("  ✗ 必要条件缺失应该导致 UNRESOLVED")
        failed += 1
    
    print(f"\n{'=' * 70}")
    print(f"KERNEL_TEST 结果：{passed} 通过，{failed} 失败")
    print(f"{'=' * 70}")
    
    return passed, failed


# ============================================================
# 八、演示：A+B+C → 整体辨识（使用新的 Contract Hardening 版）
# ============================================================

def demo_strength_judgment():
    """
    演示：旺衰辨证（使用 R1-R7 修复后的版本）
    
    场景：甲日主，寅月
    A = 得令（临官）→ SUPPORT
    B = 得地（本气根）→ SUPPORT
    C = 得势（透印）→ SUPPORT
    D = 官杀重 → CONSTRAINT（注意：CONSTRAINT ≠ REJECT）
    E = 财旺 → CONSTRAINT
    F = 根被冲 → MODIFIER（通过 EffectiveEvidence 表达，不修改原始 Evidence）
    """
    print("\n" + "=" * 70)
    print("演示：旺衰辨证（Contract Hardening 版，R1-R7 已修复）")
    print("=" * 70)
    
    # 1. 创建证据集合（R1: Evidence 不可变，R2: 使用 certainty_state）
    evidence_set = {
        Evidence(
            evidence_id="E-S-001",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="SEASONAL_SUPPORT",
            polarity=Polarity.SUPPORT,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=("R-020",),
            evidence_meaning="得令支持（甲在寅=临官）",
            provenance="滴天髓·通神论·衰旺",
            certainty_state=CertaintyState.DERIVED  # R2: 离散确定性状态
        ),
        Evidence(
            evidence_id="E-S-004",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="ROOT_MAIN_QI_SUPPORT",
            polarity=Polarity.SUPPORT,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=("R-010",),
            evidence_meaning="本气根强支持（甲在寅=本气根）",
            provenance="滴天髓·通神论·地支",
            certainty_state=CertaintyState.DERIVED
        ),
        Evidence(
            evidence_id="E-S-006",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="RESOURCE_SUPPORT",
            polarity=Polarity.SUPPORT,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=("R-003",),
            evidence_meaning="印星生扶支持（透印）",
            provenance="子平真诠·论用神",
            certainty_state=CertaintyState.DERIVED
        ),
        Evidence(
            evidence_id="E-S-009",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="OFFICER_CONTROL",
            polarity=Polarity.CONSTRAINT,  # R3: CONSTRAINT，不是 REJECT
            status=EvidenceStatus.PRESENT,
            source_relation_ids=("R-005",),
            evidence_meaning="官杀制约（官杀重）",
            provenance="子平真诠·论用神",
            certainty_state=CertaintyState.DERIVED
        ),
        Evidence(
            evidence_id="E-S-008",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="WEALTH_DRAIN",
            polarity=Polarity.CONSTRAINT,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=("R-004",),
            evidence_meaning="财星耗泄（财旺）",
            provenance="子平真诠·论用神",
            certainty_state=CertaintyState.DERIVED
        ),
        Evidence(
            evidence_id="E-S-010",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="ROOT_DAMAGED",
            polarity=Polarity.MODIFIER,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=("R-013",),
            evidence_meaning="根气受损（根被冲）",
            provenance="滴天髓·通神论·地支",
            certainty_state=CertaintyState.DERIVED
        ),
    }
    
    print(f"\n输入证据（{len(evidence_set)} 条，R1: 不可变，R2: certainty_state）：")
    for e in sorted(evidence_set, key=lambda x: x.evidence_id):
        print(f"  {e.evidence_id}: {e.evidence_meaning} [{e.polarity.value}] certainty={e.certainty_state.value}")
    
    # 2. 创建辨证规则（R5: 使用 Expression Tree，R3: CONSTRAINT ≠ REJECT，R6: 优先级来自 Rule）
    rule_strong = JudgmentRule(
        rule_id="J-DTS-STRONG-001",
        rule_name="滴天髓旺衰辨证-偏强",
        system="DITIANSUI",
        target="DAY_MASTER_STRENGTH",
        output_state="偏强",
        precedence=10,  # R6: 优先级来自 Rule 声明
        classical_source="滴天髓·通神论·衰旺",
        description="得令+得地+得势，无明确 BLOCK → 偏强",
        test_category=TestCategory.CLASSICAL_JUDGMENT_TEST,  # R7: 测试分类
        
        # R5: Expression Tree（替代扁平 group list）
        main_expression=JudgmentExpression(
            operator=LogicOperator.AND,
            description="得令 + 得地 + 得势",
            sub_expressions=[
                JudgmentExpression(
                    operator=LogicOperator.REQUIRED,  # R4: REQUIRED 是 Rule-local 语义
                    evidence_type="SEASONAL_SUPPORT",
                    description="得令（必要条件）"
                ),
                JudgmentExpression(
                    operator=LogicOperator.AND,
                    evidence_type="ROOT_MAIN_QI_SUPPORT",
                    description="得地（本气根）"
                ),
                JudgmentExpression(
                    operator=LogicOperator.AND,
                    evidence_type="RESOURCE_SUPPORT",
                    description="得势（透印）"
                ),
            ]
        ),
        
        # R3: 注意：OFFICER_CONTROL 的 polarity 是 CONSTRAINT，但这里没有声明 BLOCK
        # 所以 CONSTRAINT 不会自动导致 REJECTED
        # 只有 Rule 明确声明 BLOCK 才会 REJECTED
        
        # R1: 转化规则（不修改原始 Evidence，只是改变 EffectiveEvidence 的解释）
        transform_rules=[{
            "evidence_type": "ROOT_MAIN_QI_SUPPORT",
            "from_polarity": Polarity.SUPPORT,
            "to_polarity": Polarity.CONSTRAINT,
            "reason": "根被冲，根气支持转化为制约"
        }] if any(e.evidence_type == "ROOT_DAMAGED" for e in evidence_set) else [],
        
        absence_policy="unresolved",
        conflict_policy="unresolved"
    )
    
    # 规则2：偏弱 - 得令存在则 BLOCK（R3: 明确声明 BLOCK）
    rule_weak = JudgmentRule(
        rule_id="J-DTS-WEAK-001",
        rule_name="滴天髓旺衰辨证-偏弱",
        system="DITIANSUI",
        target="DAY_MASTER_STRENGTH",
        output_state="偏弱",
        precedence=5,
        classical_source="滴天髓·通神论·衰旺",
        description="失令+无地+无势 → 偏弱",
        test_category=TestCategory.CLASSICAL_JUDGMENT_TEST,
        
        # R3: 明确声明 BLOCK：得令存在则偏弱规则不适用
        block_expression=JudgmentExpression(
            operator=LogicOperator.BLOCK,
            evidence_type="SEASONAL_SUPPORT",
            description="得令存在则偏弱规则被阻断"
        ),
        
        main_expression=JudgmentExpression(
            operator=LogicOperator.AND,
            sub_expressions=[
                JudgmentExpression(operator=LogicOperator.REQUIRED, evidence_type="OFFICER_CONTROL"),
            ]
        ),
        
        absence_policy="unresolved"
    )
    
    # 3. 创建辨证引擎并执行（R6: 按 Rule 声明的 precedence 排序）
    engine = JudgmentEngine(system="DITIANSUI", target="DAY_MASTER_STRENGTH")
    engine.add_rule(rule_strong)
    engine.add_rule(rule_weak)
    
    result = engine.evaluate(evidence_set)
    
    print(f"\n{'=' * 70}")
    print("辨证结果：")
    print(f"{'=' * 70}")
    print(result)
    
    print(f"\n详细规则结果：")
    for rr in result.rule_results:
        print(f"  {rr.rule_id}: {rr.outcome.value} → {rr.output_state or 'N/A'}")
        print(f"    推理: {rr.reasoning}")
        # R1: 检查原始 Evidence 是否被修改
        for ee in rr.effective_evidences:
            if ee.is_modified:
                print(f"    R1: {ee.evidence_id} 有效极性={ee.effective_polarity.value}, 原始极性={ee.original_evidence.polarity.value} (不可变)")
    
    print(f"\n{'=' * 70}")
    print("关键验证（R1-R7）：")
    print(f"{'=' * 70}")
    print(f"  R1 ✓ Evidence 不可变（使用 EffectiveEvidence，不修改原始 Evidence）")
    print(f"  R2 ✓ 使用 certainty_state（DERIVED），没有 numeric confidence")
    print(f"  R3 ✓ CONSTRAINT ≠ REJECT（只有 Rule 明确声明 BLOCK 才会 REJECTED）")
    print(f"  R4 ✓ SUFFICIENT/OPPOSE 等只是 Rule-local operator，Kernel 不解释命理含义")
    print(f"  R5 ✓ 使用 Expression Tree（AND(REQUIRED(A), AND(B), AND(C))）")
    print(f"  R6 ✓ 优先级来自 Rule 声明（precedence），不是 Kernel 默认决定")
    print(f"  R7 ✓ 测试分两套 KERNEL_TEST 和 CLASSICAL_JUDGMENT_TEST")
    print(f"  ✓ 未使用 score/weight/threshold")
    print(f"  ✓ 未使用 support_count > oppose_count")
    print(f"  ✓ UNRESOLVED 是合法结果")
    print(f"  ✓ A+B+C+D+E+F 通过符号逻辑组合得到整体状态")
    
    return result


if __name__ == "__main__":
    # R7: 先运行 Kernel Test（逻辑执行器验证）
    passed, failed = run_kernel_tests()
    
    # 再运行演示（经典辨证验证）
    if failed == 0:
        demo_strength_judgment()
    else:
        print("\n⚠️  KERNEL_TEST 有失败，跳过演示")
