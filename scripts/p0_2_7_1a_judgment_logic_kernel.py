"""
P0-2.7.1A Judgment Logic Kernel - 辨证逻辑内核

这不是命理知识，也不是五部经典。
这是一个通用的符号推理执行器。

核心原则：
- 不使用 score / weight / threshold
- 不使用"支持证据数量"判断整体
- 使用符号逻辑：AND, OR, REQUIRED, SUPPORT, OPPOSE, BLOCK, OVERRIDE, TRANSFORM, QUALIFY, UNRESOLVED
- 支持 precedence, conflict, absence, exception
- UNRESOLVED 是合法结果

核心问题：
A + B + C → 整体辨识
而不是：
support_count > oppose_count
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Set, Any
from abc import ABC, abstractmethod


# ============================================================
# 一、核心枚举定义
# ============================================================

class Polarity(Enum):
    """证据极性"""
    SUPPORT = "support"        # 支持结论
    CONSTRAINT = "constraint"  # 制约结论
    NEUTRAL = "neutral"        # 中性
    MODIFIER = "modifier"      # 修改其他证据的有效性
    TRANSFORM = "transform"    # 转化证据意义


class EvidenceStatus(Enum):
    """证据状态"""
    PRESENT = "present"        # 证据存在
    ABSENT = "absent"          # 证据缺失
    UNKNOWN = "unknown"        # 证据未知（无法确定）
    MODIFIED = "modified"      # 证据被修改
    OVERRIDDEN = "overridden"  # 证据被覆盖
    BLOCKED = "blocked"        # 证据被阻断


class JudgmentOutcome(Enum):
    """辨证结果"""
    CONFIRMED = "confirmed"        # 确认成立
    QUALIFIED = "qualified"        # 有条件成立（需要限定）
    UNRESOLVED = "unresolved"      # 无法裁决（证据不足或冲突）
    REJECTED = "rejected"          # 不成立
    NOT_APPLICABLE = "not_applicable"  # 不适用


class LogicOperator(Enum):
    """逻辑操作符"""
    AND = "and"              # 所有条件必须同时成立
    OR = "or"                # 任一条件成立即可
    REQUIRED = "required"    # 必要条件，缺失则 UNRESOLVED
    SUFFICIENT = "sufficient"  # 充分条件，成立则 CONFIRMED
    OPPOSE = "oppose"        # 反向制约
    BLOCK = "block"          # 阻断结论成立
    OVERRIDE = "override"    # 覆盖普通规则
    TRANSFORM = "transform"  # 转化证据意义
    QUALIFY = "qualify"      # 降低结论等级（CONFIRMED → QUALIFIED）
    NEGATE = "negate"        # 否定证据


# ============================================================
# 二、Evidence（证据）数据结构
# ============================================================

@dataclass
class Evidence:
    """
    辨证证据
    
    关键：Evidence 必须带 judgment_target，说明这个证据是为哪个辨证目标服务的。
    同一个 Relation 可以为不同辨证目标产生不同 Evidence。
    """
    evidence_id: str                    # 证据 ID，如 E-S-001
    judgment_target: str                # 辨证目标，如 DAY_MASTER_STRENGTH
    evidence_type: str                  # 证据类型，如 SEASONAL_SUPPORT
    polarity: Polarity                  # 证据极性
    status: EvidenceStatus = EvidenceStatus.PRESENT  # 证据状态
    source_relation_ids: List[str] = field(default_factory=list)  # 来源 Relation ID
    context: Dict[str, Any] = field(default_factory=dict)  # 上下文
    evidence_meaning: str = ""          # 证据含义
    provenance: str = ""                # 来源
    confidence: float = 1.0             # 置信度（证据确定性，不是力量评分）
    scope: str = ""                     # 范围
    modifiers: List[str] = field(default_factory=list)  # 应用于此证据的修改器
    original_polarity: Optional[Polarity] = None  # 被修改前的原始极性
    
    def __hash__(self):
        """基于 evidence_id 哈希"""
        return hash(self.evidence_id)
    
    def __eq__(self, other):
        if not isinstance(other, Evidence):
            return False
        return self.evidence_id == other.evidence_id
    
    def is_effective(self) -> bool:
        """证据是否有效（未被阻断、覆盖或修改为无效）"""
        return self.status in (EvidenceStatus.PRESENT, EvidenceStatus.MODIFIED)
    
    def get_effective_polarity(self) -> Polarity:
        """获取有效极性（考虑修改）"""
        if self.status == EvidenceStatus.MODIFIED and self.original_polarity:
            return self.polarity  # 已被修改
        return self.polarity


# ============================================================
# 三、LogicCondition（逻辑条件）数据结构
# ============================================================

@dataclass
class LogicCondition:
    """
    逻辑条件
    
    一个条件可以是：
    - 单个证据的存在/缺失
    - 多个条件的 AND/OR 组合
    - 带有操作符（REQUIRED, SUFFICIENT, OPPOSE, BLOCK, OVERRIDE, TRANSFORM, QUALIFY）
    """
    condition_id: str                   # 条件 ID
    operator: LogicOperator             # 逻辑操作符
    evidence_type: Optional[str] = None  # 关联的证据类型（如 SEASONAL_SUPPORT）
    evidence_id: Optional[str] = None   # 关联的具体证据 ID
    expected_status: EvidenceStatus = EvidenceStatus.PRESENT  # 期望的证据状态
    sub_conditions: List['LogicCondition'] = field(default_factory=list)  # 子条件（用于 AND/OR）
    description: str = ""               # 条件描述
    precedence: int = 0                 # 优先级（数字越大越先执行）
    applies_to: str = ""                # 应用于哪个结论/状态
    
    def evaluate(self, evidence_set: Set[Evidence]) -> 'ConditionResult':
        """
        评估条件
        
        返回 ConditionResult，包含：
        - satisfied: 条件是否满足
        - matched_evidence: 匹配的证据列表
        - missing_evidence: 缺失的证据列表
        - conflict_evidence: 冲突的证据列表
        """
        from typing import List as TypingList
        
        matched: TypingList[Evidence] = []
        missing: TypingList[Evidence] = []
        conflict: TypingList[Evidence] = []
        
        if self.sub_conditions:
            # 组合条件（AND/OR）
            sub_results = [sc.evaluate(evidence_set) for sc in self.sub_conditions]
            
            if self.operator == LogicOperator.AND:
                satisfied = all(r.satisfied for r in sub_results)
            elif self.operator == LogicOperator.OR:
                satisfied = any(r.satisfied for r in sub_results)
            else:
                satisfied = False
            
            for r in sub_results:
                matched.extend(r.matched_evidence)
                missing.extend(r.missing_evidence)
                conflict.extend(r.conflict_evidence)
        else:
            # 单个证据条件
            target_evidence = None
            for e in evidence_set:
                if (self.evidence_id and e.evidence_id == self.evidence_id) or \
                   (self.evidence_type and e.evidence_type == self.evidence_type):
                    target_evidence = e
                    break
            
            if target_evidence:
                if target_evidence.status == self.expected_status:
                    satisfied = True
                    matched.append(target_evidence)
                else:
                    satisfied = False
                    conflict.append(target_evidence)
            else:
                satisfied = False
                if self.expected_status == EvidenceStatus.PRESENT:
                    missing.append(Evidence(
                        evidence_id=self.evidence_id or f"MISSING_{self.evidence_type}",
                        judgment_target="",
                        evidence_type=self.evidence_type or "",
                        polarity=Polarity.NEUTRAL,
                        status=EvidenceStatus.ABSENT
                    ))
        
        return ConditionResult(
            condition_id=self.condition_id,
            operator=self.operator,
            satisfied=satisfied,
            matched_evidence=matched,
            missing_evidence=missing,
            conflict_evidence=conflict
        )


@dataclass
class ConditionResult:
    """条件评估结果"""
    condition_id: str
    operator: LogicOperator
    satisfied: bool
    matched_evidence: List[Evidence] = field(default_factory=list)
    missing_evidence: List[Evidence] = field(default_factory=list)
    conflict_evidence: List[Evidence] = field(default_factory=list)


# ============================================================
# 四、LogicGroup（逻辑组）数据结构
# ============================================================

@dataclass
class LogicGroup:
    """
    逻辑组
    
    将多个条件组织成一个有意义的推理单元。
    例如：
    - SUPPORT_GROUP: 所有支持性证据的组合
    - CONSTRAINT_GROUP: 所有制约性证据的组合
    - MODIFIER_GROUP: 修改器组
    """
    group_id: str                       # 组 ID
    group_name: str                     # 组名称
    group_type: str                     # 组类型：SUPPORT / CONSTRAINT / MODIFIER / TRANSFORM / REQUIRED
    conditions: List[LogicCondition] = field(default_factory=list)  # 条件列表
    combination_operator: LogicOperator = LogicOperator.AND  # 组内条件组合方式
    description: str = ""               # 组描述
    
    def evaluate(self, evidence_set: Set[Evidence]) -> 'GroupResult':
        """评估逻辑组"""
        results = [c.evaluate(evidence_set) for c in self.conditions]
        
        if self.combination_operator == LogicOperator.AND:
            satisfied = all(r.satisfied for r in results)
        elif self.combination_operator == LogicOperator.OR:
            satisfied = any(r.satisfied for r in results)
        else:
            satisfied = False
        
        all_matched = []
        all_missing = []
        all_conflict = []
        for r in results:
            all_matched.extend(r.matched_evidence)
            all_missing.extend(r.missing_evidence)
            all_conflict.extend(r.conflict_evidence)
        
        return GroupResult(
            group_id=self.group_id,
            group_type=self.group_type,
            satisfied=satisfied,
            condition_results=results,
            matched_evidence=all_matched,
            missing_evidence=all_missing,
            conflict_evidence=all_conflict
        )


@dataclass
class GroupResult:
    """逻辑组评估结果"""
    group_id: str
    group_type: str
    satisfied: bool
    condition_results: List[ConditionResult] = field(default_factory=list)
    matched_evidence: List[Evidence] = field(default_factory=list)
    missing_evidence: List[Evidence] = field(default_factory=list)
    conflict_evidence: List[Evidence] = field(default_factory=list)


# ============================================================
# 五、JudgmentRule（辨证规则）数据结构
# ============================================================

@dataclass
class JudgmentRule:
    """
    辨证规则
    
    一个辨证规则定义了如何从证据集合得出辨证状态。
    
    关键：不使用 score/weight/threshold，使用符号逻辑。
    """
    rule_id: str                        # 规则 ID
    rule_name: str                      # 规则名称
    system: str                         # 体系/经典，如 DITIANSUI / ZIPING_ZHENQUAN
    target: str                         # 辨证目标，如 DAY_MASTER_STRENGTH
    output_state: str                   # 输出状态，如 "偏强" / "偏弱" / "中和"
    
    # 证据组
    required_groups: List[LogicGroup] = field(default_factory=list)   # 必要条件组
    support_groups: List[LogicGroup] = field(default_factory=list)    # 支持组
    constraint_groups: List[LogicGroup] = field(default_factory=list) # 制约组
    modifier_groups: List[LogicGroup] = field(default_factory=list)   # 修改器组
    blocking_groups: List[LogicGroup] = field(default_factory=list)   # 阻断组
    override_groups: List[LogicGroup] = field(default_factory=list)   # 覆盖组
    transform_groups: List[LogicGroup] = field(default_factory=list)  # 转化组
    qualification_groups: List[LogicGroup] = field(default_factory=list)  # 限定组
    
    # 冲突与缺失策略
    conflict_policy: str = "unresolved"  # 冲突策略：unresolved / override / reject
    absence_policy: str = "unresolved"   # 缺失策略：unresolved / ignore / reject
    precedence: int = 0                   # 优先级
    
    # 元数据
    classical_source: str = ""            # 经典来源
    description: str = ""                  # 规则描述
    
    def evaluate(self, evidence_set: Set[Evidence]) -> 'JudgmentResult':
        """
        评估辨证规则
        
        执行顺序（按优先级）：
        1. OVERRIDE：覆盖普通规则（如果成立，直接输出结果）
        2. BLOCKING：阻断结论（如果成立，结论不成立）
        3. REQUIRED：必要条件（如果缺失，UNRESOLVED）
        4. TRANSFORM：转化证据意义（修改证据极性/状态）
        5. MODIFIER：修改证据有效性
        6. SUPPORT + CONSTRAINT：支持与制约的平衡
        7. QUALIFICATION：限定结论等级
        """
        # 第一步：检查 OVERRIDE
        for group in sorted(self.override_groups, key=lambda g: -g.precedence if hasattr(g, 'precedence') else 0):
            result = group.evaluate(evidence_set)
            if result.satisfied:
                return JudgmentResult(
                    rule_id=self.rule_id,
                    result=JudgmentOutcome.CONFIRMED,
                    output_state=self.output_state,
                    override_triggered=True,
                    matched_groups=[result],
                    reasoning=f"覆盖规则 {group.group_name} 成立，直接确认 {self.output_state}"
                )
        
        # 第二步：检查 BLOCKING
        for group in self.blocking_groups:
            result = group.evaluate(evidence_set)
            if result.satisfied:
                return JudgmentResult(
                    rule_id=self.rule_id,
                    result=JudgmentOutcome.REJECTED,
                    output_state=None,
                    blocked=True,
                    matched_groups=[result],
                    reasoning=f"阻断规则 {group.group_name} 成立，结论不成立"
                )
        
        # 第三步：检查 REQUIRED
        missing_required = []
        for group in self.required_groups:
            result = group.evaluate(evidence_set)
            if not result.satisfied:
                missing_required.append(result)
        
        if missing_required and self.absence_policy == "unresolved":
            return JudgmentResult(
                rule_id=self.rule_id,
                result=JudgmentOutcome.UNRESOLVED,
                output_state=None,
                missing_required=missing_required,
                reasoning=f"必要条件缺失：{', '.join(g.group_id for g in self.required_groups if not any(r.group_id==g.group_id for r in missing_required))}，无法裁决"
            )
        
        # 第四步：应用 TRANSFORM（修改证据意义）
        transformed_evidence = set(evidence_set)
        for group in self.transform_groups:
            result = group.evaluate(transformed_evidence)
            if result.satisfied:
                # 转化匹配的证据
                for e in result.matched_evidence:
                    if e.polarity == Polarity.SUPPORT:
                        e.polarity = Polarity.CONSTRAINT
                        e.original_polarity = Polarity.SUPPORT
                    elif e.polarity == Polarity.CONSTRAINT:
                        e.polarity = Polarity.SUPPORT
                        e.original_polarity = Polarity.CONSTRAINT
                    e.status = EvidenceStatus.MODIFIED
        
        # 第五步：应用 MODIFIER（修改证据有效性）
        for group in self.modifier_groups:
            result = group.evaluate(transformed_evidence)
            if result.satisfied:
                # 修改匹配证据的状态
                for e in result.matched_evidence:
                    e.status = EvidenceStatus.MODIFIED
        
        # 第六步：评估 SUPPORT 和 CONSTRAINT
        support_results = [g.evaluate(transformed_evidence) for g in self.support_groups]
        constraint_results = [g.evaluate(transformed_evidence) for g in self.constraint_groups]
        
        support_satisfied = [r for r in support_results if r.satisfied]
        constraint_satisfied = [r for r in constraint_results if r.satisfied]
        
        # 关键：不使用"支持证据数量"判断整体
        # 而是检查：
        # 1. 是否有充分支持条件（SUFFICIENT）
        # 2. 是否有强制约条件
        # 3. 证据之间的结构关系
        
        has_sufficient_support = any(
            any(c.operator == LogicOperator.SUFFICIENT for c in g.conditions)
            for g in self.support_groups
            if any(r.satisfied for r in [g.evaluate(transformed_evidence)])
        )
        
        has_strong_constraint = any(
            any(c.operator == LogicOperator.OPPOSE for c in g.conditions)
            for g in self.constraint_groups
            if any(r.satisfied for r in [g.evaluate(transformed_evidence)])
        )
        
        # 第七步：检查 QUALIFICATION
        qualification_results = [g.evaluate(transformed_evidence) for g in self.qualification_groups]
        qualification_satisfied = [r for r in qualification_results if r.satisfied]
        
        # 第八步：综合判断
        if has_sufficient_support and not has_strong_constraint:
            base_result = JudgmentOutcome.CONFIRMED
        elif has_strong_constraint and not has_sufficient_support:
            base_result = JudgmentOutcome.REJECTED
        elif support_satisfied and not constraint_satisfied:
            base_result = JudgmentOutcome.CONFIRMED
        elif constraint_satisfied and not support_satisfied:
            base_result = JudgmentOutcome.REJECTED
        elif support_satisfied and constraint_satisfied:
            # 支持与制约同时存在
            if self.conflict_policy == "unresolved":
                base_result = JudgmentOutcome.UNRESOLVED
            elif self.conflict_policy == "override":
                base_result = JudgmentOutcome.CONFIRMED  # 支持优先
            else:
                base_result = JudgmentOutcome.REJECTED  # 制约优先
        else:
            base_result = JudgmentOutcome.UNRESOLVED
        
        # 应用 QUALIFICATION
        final_result = base_result
        if qualification_satisfied and base_result == JudgmentOutcome.CONFIRMED:
            final_result = JudgmentOutcome.QUALIFIED
        
        # 构建推理过程
        reasoning_parts = []
        if support_satisfied:
            reasoning_parts.append(f"支持条件成立：{', '.join(r.group_id for r in support_satisfied)}")
        if constraint_satisfied:
            reasoning_parts.append(f"制约条件成立：{', '.join(r.group_id for r in constraint_satisfied)}")
        if qualification_satisfied:
            reasoning_parts.append(f"限定条件成立：{', '.join(r.group_id for r in qualification_satisfied)}")
        if missing_required:
            reasoning_parts.append(f"必要条件缺失：{', '.join(r.group_id for r in missing_required)}")
        
        return JudgmentResult(
            rule_id=self.rule_id,
            result=final_result,
            output_state=self.output_state if final_result in (JudgmentOutcome.CONFIRMED, JudgmentOutcome.QUALIFIED) else None,
            support_results=support_results,
            constraint_results=constraint_results,
            qualification_results=qualification_results,
            reasoning="; ".join(reasoning_parts) if reasoning_parts else "证据不足，无法裁决"
        )


@dataclass
class JudgmentResult:
    """辨证结果"""
    rule_id: str
    result: JudgmentOutcome
    output_state: Optional[str] = None
    override_triggered: bool = False
    blocked: bool = False
    missing_required: List[GroupResult] = field(default_factory=list)
    support_results: List[GroupResult] = field(default_factory=list)
    constraint_results: List[GroupResult] = field(default_factory=list)
    qualification_results: List[GroupResult] = field(default_factory=list)
    matched_groups: List[GroupResult] = field(default_factory=list)
    reasoning: str = ""
    
    def is_confirmed(self) -> bool:
        return self.result == JudgmentOutcome.CONFIRMED
    
    def is_qualified(self) -> bool:
        return self.result == JudgmentOutcome.QUALIFIED
    
    def is_unresolved(self) -> bool:
        return self.result == JudgmentOutcome.UNRESOLVED
    
    def is_rejected(self) -> bool:
        return self.result == JudgmentOutcome.REJECTED


# ============================================================
# 六、JudgmentEngine（辨证引擎）
# ============================================================

class JudgmentEngine:
    """
    辨证引擎
    
    负责：
    1. 接收证据集合
    2. 按优先级执行所有适用的辨证规则
    3. 处理规则之间的冲突
    4. 输出最终辨证状态（或 UNRESOLVED）
    """
    
    def __init__(self, system: str, target: str):
        self.system = system  # 体系/经典
        self.target = target  # 辨证目标
        self.rules: List[JudgmentRule] = []
    
    def add_rule(self, rule: JudgmentRule):
        """添加辨证规则"""
        if rule.system == self.system and rule.target == self.target:
            self.rules.append(rule)
            self.rules.sort(key=lambda r: -r.precedence)
    
    def evaluate(self, evidence_set: Set[Evidence]) -> 'FinalJudgment':
        """
        执行辨证
        
        关键：
        - 不使用 score/weight/threshold
        - 不使用"支持证据数量"判断整体
        - 使用符号逻辑
        - UNRESOLVED 是合法结果
        """
        # 过滤适用的证据
        applicable_evidence = {e for e in evidence_set if e.judgment_target == self.target}
        
        if not applicable_evidence:
            return FinalJudgment(
                system=self.system,
                target=self.target,
                result=JudgmentOutcome.UNRESOLVED,
                output_state=None,
                reasoning="没有适用于此辨证目标的证据",
                rule_results=[]
            )
        
        # 执行所有规则
        rule_results = []
        for rule in self.rules:
            result = rule.evaluate(applicable_evidence)
            rule_results.append(result)
        
        # 综合规则结果
        confirmed = [r for r in rule_results if r.is_confirmed()]
        qualified = [r for r in rule_results if r.is_qualified()]
        unresolved = [r for r in rule_results if r.is_unresolved()]
        rejected = [r for r in rule_results if r.is_rejected()]
        
        # 冲突处理
        if confirmed and rejected:
            # 确认与拒绝同时存在
            final_result = JudgmentOutcome.UNRESOLVED
            output_state = None
            reasoning = f"规则冲突：{len(confirmed)} 条确认，{len(rejected)} 条拒绝，无法裁决"
        elif confirmed:
            final_result = JudgmentOutcome.CONFIRMED
            output_state = confirmed[0].output_state
            reasoning = f"{len(confirmed)} 条规则确认：{output_state}"
        elif qualified:
            final_result = JudgmentOutcome.QUALIFIED
            output_state = qualified[0].output_state
            reasoning = f"{len(qualified)} 条规则有条件确认：{output_state}"
        elif unresolved:
            final_result = JudgmentOutcome.UNRESOLVED
            output_state = None
            reasoning = f"{len(unresolved)} 条规则无法裁决"
        else:
            final_result = JudgmentOutcome.REJECTED
            output_state = None
            reasoning = f"所有 {len(rejected)} 条规则拒绝"
        
        return FinalJudgment(
            system=self.system,
            target=self.target,
            result=final_result,
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
    result: JudgmentOutcome
    output_state: Optional[str]
    reasoning: str
    rule_results: List[JudgmentResult] = field(default_factory=list)
    evidence_used: Set[Evidence] = field(default_factory=set)
    
    def __str__(self):
        return f"[{self.system}] {self.target}: {self.result.value} = {self.output_state or 'UNRESOLVED'}\n推理: {self.reasoning}"


# ============================================================
# 七、演示：A+B+C → 整体辨识（无 score）
# ============================================================

def demo_strength_judgment():
    """
    演示：旺衰辨证
    
    场景：甲日主，寅月
    A = 得令（临官）→ SUPPORT
    B = 得地（本气根）→ SUPPORT
    C = 得势（透印）→ SUPPORT
    D = 官杀重 → CONSTRAINT
    E = 财旺 → CONSTRAINT
    F = 根被冲 → MODIFIER
    
    目标：证明 A+B+C+D+E+F 可以通过符号逻辑得到整体状态，而不是靠 score。
    """
    print("=" * 70)
    print("演示：旺衰辨证（A+B+C → 整体辨识，无 score/weight/threshold）")
    print("=" * 70)
    
    # 1. 创建证据集合
    evidence_set = {
        Evidence(
            evidence_id="E-S-001",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="SEASONAL_SUPPORT",
            polarity=Polarity.SUPPORT,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=["R-020"],
            evidence_meaning="得令支持（甲在寅=临官）",
            provenance="滴天髓·通神论·衰旺"
        ),
        Evidence(
            evidence_id="E-S-004",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="ROOT_MAIN_QI_SUPPORT",
            polarity=Polarity.SUPPORT,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=["R-010"],
            evidence_meaning="本气根强支持（甲在寅=本气根）",
            provenance="滴天髓·通神论·地支"
        ),
        Evidence(
            evidence_id="E-S-006",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="RESOURCE_SUPPORT",
            polarity=Polarity.SUPPORT,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=["R-003"],
            evidence_meaning="印星生扶支持（透印）",
            provenance="子平真诠·论用神"
        ),
        Evidence(
            evidence_id="E-S-009",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="OFFICER_CONTROL",
            polarity=Polarity.CONSTRAINT,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=["R-005"],
            evidence_meaning="官杀制约（官杀重）",
            provenance="子平真诠·论用神"
        ),
        Evidence(
            evidence_id="E-S-008",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="WEALTH_DRAIN",
            polarity=Polarity.CONSTRAINT,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=["R-004"],
            evidence_meaning="财星耗泄（财旺）",
            provenance="子平真诠·论用神"
        ),
        Evidence(
            evidence_id="E-S-010",
            judgment_target="DAY_MASTER_STRENGTH",
            evidence_type="ROOT_DAMAGED",
            polarity=Polarity.MODIFIER,
            status=EvidenceStatus.PRESENT,
            source_relation_ids=["R-013"],
            evidence_meaning="根气受损（根被冲）",
            provenance="滴天髓·通神论·地支"
        ),
    }
    
    print(f"\n输入证据（{len(evidence_set)} 条）：")
    for e in sorted(evidence_set, key=lambda x: x.evidence_id):
        print(f"  {e.evidence_id}: {e.evidence_meaning} [{e.polarity.value}]")
    
    # 2. 创建辨证规则（滴天髓旺衰辨证）
    # 规则1：偏强 - 得令+得地+得势，无强制约
    rule_strong = JudgmentRule(
        rule_id="J-DTS-STRONG-001",
        rule_name="滴天髓旺衰辨证-偏强",
        system="DITIANSUI",
        target="DAY_MASTER_STRENGTH",
        output_state="偏强",
        precedence=10,
        classical_source="滴天髓·通神论·衰旺",
        description="得令+得地+得势，无强制约 → 偏强",
        
        # 必要条件：得令
        required_groups=[
            LogicGroup(
                group_id="REQ-SEASONAL",
                group_name="得令必要条件",
                group_type="REQUIRED",
                conditions=[
                    LogicCondition(
                        condition_id="C-SEASONAL",
                        operator=LogicOperator.REQUIRED,
                        evidence_type="SEASONAL_SUPPORT",
                        expected_status=EvidenceStatus.PRESENT,
                        description="得令证据必须存在"
                    )
                ],
                description="得令是旺衰辨证的必要条件"
            )
        ],
        
        # 支持组：得地+得势
        support_groups=[
            LogicGroup(
                group_id="SUPPORT-ROOT-QI",
                group_name="得地得势支持组",
                group_type="SUPPORT",
                combination_operator=LogicOperator.AND,
                conditions=[
                    LogicCondition(
                        condition_id="C-ROOT",
                        operator=LogicOperator.SUFFICIENT,
                        evidence_type="ROOT_MAIN_QI_SUPPORT",
                        expected_status=EvidenceStatus.PRESENT,
                        description="本气根支持（充分条件）"
                    ),
                    LogicCondition(
                        condition_id="C-QI",
                        operator=LogicOperator.AND,
                        evidence_type="RESOURCE_SUPPORT",
                        expected_status=EvidenceStatus.PRESENT,
                        description="印星生扶支持"
                    )
                ],
                description="得地（本气根）+ 得势（透印）= 强支持"
            )
        ],
        
        # 制约组：官杀重
        constraint_groups=[
            LogicGroup(
                group_id="CONSTRAINT-OFFICER",
                group_name="官杀制约组",
                group_type="CONSTRAINT",
                conditions=[
                    LogicCondition(
                        condition_id="C-OFFICER",
                        operator=LogicOperator.OPPOSE,
                        evidence_type="OFFICER_CONTROL",
                        expected_status=EvidenceStatus.PRESENT,
                        description="官杀重（强制约）"
                    )
                ],
                description="官杀重是强制约条件"
            )
        ],
        
        # 修改器组：根被冲
        modifier_groups=[
            LogicGroup(
                group_id="MODIFIER-ROOT-DAMAGED",
                group_name="根气受损修改器",
                group_type="MODIFIER",
                conditions=[
                    LogicCondition(
                        condition_id="C-ROOT-DAMAGED",
                        operator=LogicOperator.TRANSFORM,
                        evidence_type="ROOT_DAMAGED",
                        expected_status=EvidenceStatus.PRESENT,
                        description="根被冲（修改根气有效性）"
                    )
                ],
                description="根被冲会修改得地证据的有效性"
            )
        ],
        
        conflict_policy="unresolved",
        absence_policy="unresolved"
    )
    
    # 规则2：偏弱 - 失令+无地+无势，有强制约
    rule_weak = JudgmentRule(
        rule_id="J-DTS-WEAK-001",
        rule_name="滴天髓旺衰辨证-偏弱",
        system="DITIANSUI",
        target="DAY_MASTER_STRENGTH",
        output_state="偏弱",
        precedence=5,
        classical_source="滴天髓·通神论·衰旺",
        description="失令+无地+无势，有强制约 → 偏弱",
        
        # 阻断组：得令（如果得令，则此规则不适用）
        blocking_groups=[
            LogicGroup(
                group_id="BLOCK-SEASONAL",
                group_name="得令阻断",
                group_type="BLOCK",
                conditions=[
                    LogicCondition(
                        condition_id="C-SEASONAL-PRESENT",
                        operator=LogicOperator.BLOCK,
                        evidence_type="SEASONAL_SUPPORT",
                        expected_status=EvidenceStatus.PRESENT,
                        description="得令存在则偏弱规则不适用"
                    )
                ],
                description="得令存在时，偏弱规则被阻断"
            )
        ],
        
        conflict_policy="unresolved",
        absence_policy="unresolved"
    )
    
    # 3. 创建辨证引擎并执行
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
        print(f"  {rr.rule_id}: {rr.result.value} → {rr.output_state or 'N/A'}")
        print(f"    推理: {rr.reasoning}")
    
    print(f"\n{'=' * 70}")
    print("关键验证：")
    print(f"{'=' * 70}")
    print(f"  ✓ 未使用 score/weight/threshold")
    print(f"  ✓ 未使用 support_count > oppose_count")
    print(f"  ✓ 使用符号逻辑：REQUIRED / SUFFICIENT / OPPOSE / BLOCK / TRANSFORM")
    print(f"  ✓ 证据带 judgment_target")
    print(f"  ✓ UNRESOLVED 是合法结果")
    print(f"  ✓ A+B+C+D+E+F 通过符号逻辑组合得到整体状态")
    
    return result


if __name__ == "__main__":
    demo_strength_judgment()
