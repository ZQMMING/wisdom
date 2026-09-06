# ZIPING Rule Engine Implementation Plan

**任务 ID**: T-ENGINE-BAZI-002 Phase 2 Architecture  
**执行者**: @bot-ziping  
**日期**: 2026-09-06

---

## 执行摘要

基于 BOT-MASTER 裁决，制定 ZIPING Rule Engine 分阶段实现计划。
**关键原则**: 先建立 Rule Authority 体系，再实现具体规则。

---

## Phase A: Architecture Design (1-2 小时)

### A.1 Rule Schema 定义

```python
# src/tongshu/reasoning/rule_engine/rule_schema.py

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Callable, Any

class RuleAuthorityLevel(str, Enum):
    EXPLICIT = "EXPLICIT"              # 原典明确
    IMPLICIT = "IMPLICIT"              # 原典隐含
    HYPOTHESIS = "HYPOTHESIS"          # 合理假说
    ENGINEERING = "ENGINEERING"        # 工程推导
    UNVERIFIED = "UNVERIFIED"          # 未核验
    NOT_AUTHORIZED = "NOT_AUTHORIZED"  # 未授权

class RuleDomain(str, Enum):
    WANGSHUAI = "wangshuai"            # 旺衰
    PATTERN = "pattern"                # 格局
    YONGSHEN = "yongshen"              # 用神
    TEN_GOD_SEMANTICS = "ten_god_semantics"  # 十神语义
    EVENT = "event"                    # 事件判断

@dataclass(frozen=True)
class RuleCondition:
    """规则触发条件"""
    # 月令条件
    monthly_command: Optional[str] = None  # "得令"/"失令"
    
    # 通根条件
    root_present: Optional[bool] = None    # 是否有根
    root_type: Optional[str] = None        # "main_qi"/"middle_qi"/"residual_qi"
    
    # 天干条件
    stem_count: Optional[int] = None       # 特定十神数量
    stem_positions: Optional[List[str]] = None  # 特定位置的天干
    
    # 综合条件
    weight_threshold: Optional[float] = None  # 权重阈值（谨慎使用）
    
    def evaluate(self, state: 'CanonicalState') -> bool:
        """评估条件是否满足"""
        raise NotImplementedError

@dataclass(frozen=True)
class EvidenceProvenance:
    """证据溯源"""
    evidence_ids: List[str]                # 来源证据ID列表
    extraction_method: str                 # 提取方法
    confidence: float                      # 置信度 0-1
    
@dataclass(frozen=True)
class Rule:
    """子平规则定义"""
    rule_id: str                           # ZIPING-RULE-WS-001
    name: str                              # 规则名称
    domain: RuleDomain                     # 所属域
    description: str                       # 规则描述
    
    # 溯源
    provenance: EvidenceProvenance         # 证据溯源
    
    # 条件
    condition: RuleCondition               # 触发条件
    
    # 输出
    output_value: str                      # 输出值
    output_domain: Optional[str] = None    # 输出域
    
    # 优先级
    priority: int                          # 优先级（数字越小越高）
    authority_level: RuleAuthorityLevel    # 权威等级
    
    # 元数据
    classic_reference: str                 # 经典出处
    notes: str = ""
    
    def evaluate(self, state: 'CanonicalState') -> bool:
        """评估规则是否触发"""
        return self.condition.evaluate(state)
    
    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "domain": self.domain.value,
            "description": self.description,
            "priority": self.priority,
            "authority_level": self.authority_level.value,
            "classic_reference": self.classic_reference,
        }
```

### A.2 Evidence → Rule Provenance Contract

```python
# src/tongshu/reasoning/rule_engine/provenance.py

@dataclass(frozen=True)
class EvidenceRuleLink:
    """证据→规则链接"""
    evidence_id: str                       # E-YHZP-001-001
    evidence_text: str                     # 原文内容
    rule_id: str                           # ZIPING-RULE-WS-001
    extraction_method: str                 # 如何提取
    extraction_notes: str = ""
    
    def validate(self) -> List[str]:
        errors = []
        if not self.evidence_id:
            errors.append("evidence_id is required")
        if not self.evidence_text:
            errors.append("evidence_text is required")
        if not self.rule_id:
            errors.append("rule_id is required")
        if not self.extraction_method:
            errors.append("extraction_method is required")
        return errors

@dataclass(frozen=True)
class RuleChain:
    """规则链（用于追溯）"""
    rule_id: str
    evidence_ids: List[str]
    derivation_steps: List[str]            # 推导步骤
    final_judgment: str                    # 最终判断
```

### A.3 Rule Authority 体系

```python
# src/tongshu/reasoning/rule_engine/authority.py

CLASSIC_AUTHORITY = {
    "ziping_zhenquan": 1,    # 格局权威（最高）
    "yuan_hai_zi_ping": 2,   # 基础权威
    "di_tian_sui": 3,        # 旺衰权威
    "qiong_tong_bao_jian": 4, # 调候权威
    "san_ming_tong_hui": 5,  # 杂项权威（最低）
}

def get_classic_authority(classic_id: str) -> int:
    """获取经典权威等级"""
    return CLASSIC_AUTHORITY.get(classic_id, 99)

def resolve_rule_conflict(rules: List[Rule]) -> Rule:
    """解决规则冲突"""
    if len(rules) == 1:
        return rules[0]
    
    # 按权威等级排序
    sorted_rules = sorted(
        rules,
        key=lambda r: get_classic_authority(r.provenance.evidence_ids[0].split('-')[1])
    )
    
    # 返回高权威经典的规则
    return sorted_rules[0]
```

---

## Phase B: Evidence Connection (2-3 小时)

### B.1 实现 EvidenceLoader

```python
# src/tongshu/reasoning/evidence_loader.py

import json
from pathlib import Path
from typing import Dict, List, Optional

class EvidenceLoader:
    """证据加载器"""
    
    def __init__(self, evidence_dir: Path):
        self.evidence_dir = evidence_dir
        self._cache: Dict[str, List[dict]] = {}
    
    def load_evidence(self, classic_id: str) -> List[dict]:
        """加载指定经典的证据"""
        if classic_id in self._cache:
            return self._cache[classic_id]
        
        classic_dir = self.evidence_dir / classic_id
        if not classic_dir.exists():
            return []
        
        entries = []
        for json_file in classic_dir.glob("*.json"):
            if json_file.name.startswith('_'):
                continue
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                entries.append(data)
        
        self._cache[classic_id] = entries
        return entries
    
    def get_evidence_by_id(self, evidence_id: str) -> Optional[dict]:
        """按ID获取证据"""
        for classic_id in ['yuan_hai_zi_ping', 'ziping_zhenquan', 
                          'di_tian_sui', 'qiong_tong_bao_jian', 
                          'san_ming_tong_hui']:
            entries = self.load_evidence(classic_id)
            for entry in entries:
                if entry.get('evidence_id') == evidence_id:
                    return entry
        return None
    
    def search_by_keyword(self, keywords: List[str], classic_id: Optional[str] = None) -> List[dict]:
        """关键词搜索"""
        results = []
        classic_ids = [classic_id] if classic_id else list(self._cache.keys())
        
        for cid in classic_ids:
            entries = self.load_evidence(cid)
            for entry in entries:
                text = entry.get('original_text', '')
                if any(kw in text for kw in keywords):
                    results.append(entry)
        
        return results
```

### B.2 实现 Bian Agent 连接

```python
# src/tongshu/bian/base.py (修改)

class BianAgent:
    def __init__(self, classics_data_dir: Path, evidence_output_dir: Path):
        self.classics_data_dir = classics_data_dir
        self.evidence_output_dir = evidence_output_dir
        self.evidence_loader = EvidenceLoader(classics_data_dir / "evidence")
        self._entries: List[Dict] = []
        self._build_passage_index()
    
    def _load_classic_entries(self) -> List[Dict]:
        """加载经典原文数据 - 连接证据数据库"""
        # 实现具体加载逻辑
        return self.evidence_loader.load_evidence(self.CLASSIC_ID)
```

---

## Phase C: Rule Engine Implementation (3-4 小时)

### C.1 RuleEngine 核心类

```python
# src/tongshu/reasoning/rule_engine/engine.py

from typing import List, Dict, Optional
from .rule_schema import Rule, RuleCondition, RuleDomain
from .authority import resolve_rule_conflict

class RuleEngine:
    """子平规则引擎"""
    
    def __init__(self):
        self._rules: Dict[str, Rule] = {}
        self._domain_rules: Dict[RuleDomain, List[Rule]] = {
            domain: [] for domain in RuleDomain
        }
    
    def register_rule(self, rule: Rule):
        """注册规则"""
        self._rules[rule.rule_id] = rule
        self._domain_rules[rule.domain].append(rule)
    
    def evaluate_rule(self, rule: Rule, state: 'CanonicalState') -> bool:
        """评估单条规则"""
        return rule.evaluate(state)
    
    def evaluate_domain(self, domain: RuleDomain, state: 'CanonicalState') -> List[Rule]:
        """评估某域所有规则"""
        triggered = []
        for rule in self._domain_rules.get(domain, []):
            if self.evaluate_rule(rule, state):
                triggered.append(rule)
        return triggered
    
    def apply_priority(self, rules: List[Rule]) -> Rule:
        """应用优先级"""
        if not rules:
            return None
        sorted_rules = sorted(rules, key=lambda r: r.priority)
        return sorted_rules[0]
    
    def detect_conflicts(self, rules: List[Rule]) -> List[Dict]:
        """检测规则冲突"""
        conflicts = []
        for i, r1 in enumerate(rules):
            for r2 in rules[i+1:]:
                if r1.output_value != r2.output_value:
                    conflicts.append({
                        "rule_1": r1.rule_id,
                        "rule_2": r2.rule_id,
                        "conflict": f"{r1.output_value} vs {r2.output_value}"
                    })
        return conflicts
    
    def judge(self, domain: RuleDomain, state: 'CanonicalState') -> Optional[str]:
        """执行辨证判断"""
        triggered = self.evaluate_domain(domain, state)
        
        if not triggered:
            return None
        
        # 检测冲突
        conflicts = self.detect_conflicts(triggered)
        if conflicts:
            # 应用冲突解决策略
            resolved = resolve_rule_conflict(triggered)
            return resolved.output_value
        
        # 应用优先级
        return self.apply_priority(triggered).output_value
```

---

## Phase D: Domain Implementation (每个域 2-3 小时)

### D.1 旺衰引擎

```python
# src/tongshu/reasoning/rule_engine/wangshuai.py

from .engine import RuleEngine, Rule, RuleCondition, RuleDomain
from .rule_schema import RuleAuthorityLevel, EvidenceProvenance

class WangShuaiEngine:
    """旺衰辨证引擎"""
    
    def __init__(self, rule_engine: RuleEngine):
        self.engine = rule_engine
        self._register_rules()
    
    def _register_rules(self):
        """注册旺衰规则"""
        
        # 得令规则
        self.engine.register_rule(Rule(
            rule_id="ZIPING-RULE-WS-001",
            name="得令判定",
            domain=RuleDomain.WANGSHUAI,
            description="月支五行生助或同于日主",
            provenance=EvidenceProvenance(
                evidence_ids=["E-DTS-144-001"],
                extraction_method="direct_quote",
                confidence=0.95
            ),
            condition=RuleCondition(monthly_command="得令"),
            output_value="SUPPORT",
            priority=1,
            authority_level=RuleAuthorityLevel.EXPLICIT,
            classic_reference="滴天髓·通神论·衰旺",
        ))
        
        # 通根规则
        self.engine.register_rule(Rule(
            rule_id="ZIPING-RULE-WS-003",
            name="通根判定",
            domain=RuleDomain.WANGSHUAI,
            description="四柱地支藏干含日主",
            provenance=EvidenceProvenance(
                evidence_ids=["E-YHZP-003-001"],
                extraction_method="direct_quote",
                confidence=0.9
            ),
            condition=RuleCondition(root_present=True),
            output_value="SUPPORT",
            priority=2,
            authority_level=RuleAuthorityLevel.EXPLICIT,
            classic_reference="渊海子平·论根气",
        ))
        
        # ... 更多规则
        
    def judge(self, state: 'CanonicalState') -> str:
        """判断旺衰"""
        return self.engine.judge(RuleDomain.WANGSHUAI, state)
```

### D.2 格局引擎

```python
# src/tongshu/reasoning/rule_engine/pattern.py

class PatternEngine:
    """格局辨证引擎"""
    
    def __init__(self, rule_engine: RuleEngine):
        self.engine = rule_engine
        self._register_rules()
    
    def _register_rules(self):
        """注册格局规则"""
        
        # 从格（最高优先级）
        self.engine.register_rule(Rule(
            rule_id="ZIPING-RULE-PT-009",
            name="从格判定",
            domain=RuleDomain.PATTERN,
            description="日主无根无帮扶，顺势而为",
            provenance=EvidenceProvenance(
                evidence_ids=["E-PZZQ-009-001"],
                extraction_method="synthesis",
                confidence=0.85
            ),
            condition=RuleCondition(root_present=False, peer_support=0, resource_support=0),
            output_value="CONGRUENT_PATTERN",
            priority=0,  # 最高优先级
            authority_level=RuleAuthorityLevel.IMPLICIT,
            classic_reference="子平真诠·论从格",
        ))
        
        # 正官格
        self.engine.register_rule(Rule(
            rule_id="ZIPING-RULE-PT-001",
            name="正官格",
            domain=RuleDomain.PATTERN,
            description="月令正官透干",
            provenance=EvidenceProvenance(
                evidence_ids=["E-PZZQ-001-001"],
                extraction_method="direct_quote",
                confidence=0.95
            ),
            condition=RuleCondition(stem_count=1, stem_positions=["month"]),
            output_value="ZHENGGUAN_PATTERN",
            priority=4,
            authority_level=RuleAuthorityLevel.EXPLICIT,
            classic_reference="子平真诠·论正官",
        ))
        
        # ... 更多规则
    
    def judge(self, state: 'CanonicalState') -> str:
        """判断格局"""
        return self.engine.judge(RuleDomain.PATTERN, state)
```

### D.3 用神引擎

```python
# src/tongshu/reasoning/rule_engine/yongshen.py

class YongShenEngine:
    """用神辨证引擎"""
    
    def __init__(self, rule_engine: RuleEngine):
        self.engine = rule_engine
        self._register_rules()
    
    def _register_rules(self):
        """注册用神规则"""
        
        # 格局用神（最高优先级）
        self.engine.register_rule(Rule(
            rule_id="ZIPING-RULE-YG-001",
            name="格局用神",
            domain=RuleDomain.YONGSHEN,
            description="根据格局类型确定用神",
            provenance=EvidenceProvenance(
                evidence_ids=["E-PZZQ-001-001", "E-PZZQ-002-001"],
                extraction_method="synthesis",
                confidence=0.9
            ),
            condition=RuleCondition(),
            output_value="PATTERN_YONGSHEN",
            priority=1,
            authority_level=RuleAuthorityLevel.EXPLICIT,
            classic_reference="子平真诠·论用神",
        ))
        
        # 调候用神
        self.engine.register_rule(Rule(
            rule_id="ZIPING-RULE-YG-002",
            name="调候用神",
            domain=RuleDomain.YONGSHEN,
            description="根据日主和月令确定调候用神",
            provenance=EvidenceProvenance(
                evidence_ids=["E-QTBJ-001-001"],
                extraction_method="lookup",
                confidence=0.95
            ),
            condition=RuleCondition(),
            output_value="CLIMATE_YONGSHEN",
            priority=2,
            authority_level=RuleAuthorityLevel.EXPLICIT,
            classic_reference="穷通宝鉴",
        ))
        
        # ... 更多规则
    
    def judge(self, state: 'CanonicalState') -> str:
        """判断用神"""
        return self.engine.judge(RuleDomain.YONGSHEN, state)
```

---

## Phase E: Validation (2-3 小时)

### E.1 Golden Cases 验证

```python
# tests/test_rule_engine_validation.py

def test_wangshuai_golden_cases():
    """旺衰 Golden Cases 验证"""
    engine = WangShuaiEngine(RuleEngine())
    
    # 案例1: 甲日主生于寅月（得令）
    case1 = create_canonical_state(day_master="JIA", month_branch="YIN")
    result1 = engine.judge(case1)
    assert result1 == "STRONG", f"Expected STRONG, got {result1}"
    
    # 案例2: 甲日主生于酉月（失令）
    case2 = create_canonical_state(day_master="JIA", month_branch="YOU")
    result2 = engine.judge(case2)
    assert result2 == "WEAK", f"Expected WEAK, got {result2}"

def test_pattern_golden_cases():
    """格局 Golden Cases 验证"""
    engine = PatternEngine(RuleEngine())
    
    # 案例: 正官格
    case = create_canonical_state(
        day_master="JIA",
        month_branch="YOU",  # 酉为正官
        month_stem="GENG"   # 透干
    )
    result = engine.judge(case)
    assert result == "ZHENGGUAN_PATTERN", f"Expected ZHENGGUAN_PATTERN, got {result}"
```

### E.2 Rule Provenance 追溯测试

```python
def test_rule_provenance():
    """测试规则溯源"""
    rule = Rule(
        rule_id="ZIPING-RULE-WS-001",
        name="得令判定",
        provenance=EvidenceProvenance(
            evidence_ids=["E-DTS-144-001"],
            extraction_method="direct_quote",
            confidence=0.95
        ),
        # ...
    )
    
    # 验证溯源链
    assert len(rule.provenance.evidence_ids) > 0
    assert rule.provenance.confidence > 0.5
    assert rule.classic_reference != ""
```

---

## 时间估算

| Phase | 预估时间 | 关键交付物 |
|-------|----------|------------|
| A: Architecture Design | 1-2h | Rule Schema, Provenance Contract |
| B: Evidence Connection | 2-3h | EvidenceLoader, Agent连接 |
| C: Rule Engine | 3-4h | RuleEngine核心类 |
| D: Domain Implementation | 10-15h | 五大辨证域引擎 |
| E: Validation | 2-3h | Golden Cases验证 |
| **总计** | **18-27h** | 完整Rule Engine |

---

## 风险控制

### 禁止事项

1. ❌ 不修改 BAZI Canonical Chart
2. ❌ 不使用 LLM 自由判断
3. ❌ 不使用评分模型（strength_score）
4. ❌ 不自行发明未经证据支持 Rule
5. ❌ 不忽略经典冲突

### 必须事项

1. ✅ 每条 Rule 必须有 Evidence Provenance
2. ✅ 冲突必须记录并裁决
3. ✅ 未授权 Rule 标记为 INSUFFICIENT_SOURCE
4. ✅ 验证 Golden Cases 准确率

---

**计划制定**: @bot-ziping  
**状态**: 📋 READY FOR APPROVAL
