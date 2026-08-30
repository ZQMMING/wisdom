# -*- coding: utf-8 -*-
"""P0-8.3: Assertion Semantic Audit - 检查断言是否超过原文

核心原则:
1. 原文表达什么 → Assertion是否忠实于原文
2. Primitive是否改变对象
3. Condition是否添加原文没有的条件
4. Negative Cases是否合理
5. 防止"工程推导冒充经典原义"

验收标准:
- 每条断言必须有原文对照
- 所有额外条件必须标注为"工程扩展"而非"原典支持"
- 语义漂移检测必须通过
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


class SemanticAuditResult:
    """语义审计结果"""
    
    def __init__(self,
                 assertion_id: str,
                 name: str,
                 source_book: str,
                 passage_id: str,
                 raw_text: str,
                 semantic_unit: str,
                 primitive: str,
                 condition: str,
                 audit_status: str,  # PASS / DRIFT / OVER_INTERPRET
                 drift_issues: List[str],
                 over_interpret_issues: List[str],
                 engineering_extensions: List[str],
                 fidelity_score: float):
        self.assertion_id = assertion_id
        self.name = name
        self.source_book = source_book
        self.passage_id = passage_id
        self.raw_text = raw_text
        self.semantic_unit = semantic_unit
        self.primitive = primitive
        self.condition = condition
        self.audit_status = audit_status
        self.drift_issues = drift_issues
        self.over_interpret_issues = over_interpret_issues
        self.engineering_extensions = engineering_extensions
        self.fidelity_score = fidelity_score
    
    def to_dict(self) -> dict:
        return {
            'assertion_id': self.assertion_id,
            'name': self.name,
            'source_book': self.source_book,
            'passage_id': self.passage_id,
            'raw_text': self.raw_text,
            'semantic_unit': self.semantic_unit,
            'primitive': self.primitive,
            'condition': self.condition,
            'audit_status': self.audit_status,
            'drift_issues': self.drift_issues,
            'over_interpret_issues': self.over_interpret_issues,
            'engineering_extensions': self.engineering_extensions,
            'fidelity_score': self.fidelity_score
        }


class SemanticAuditor:
    """语义审计引擎"""
    
    # 已知语义漂移模式
    KNOWN_DRIFT_PATTERNS = [
        {
            'pattern': '日干克年干',
            'risk': '犯岁是否包含日支参与？',
            'required_check': '确认原文是否明确限定仅年干'
        },
        {
            'pattern': '制中有生，生中有制',
            'risk': '制化比例如何量化？',
            'required_check': '确认原文是否有量化标准'
        },
        {
            'pattern': '太过宜制/不及宜生',
            'risk': '太过/不及的判断标准是什么？',
            'required_check': '确认原文是否定义判断标准'
        }
    ]
    
    def audit_assertions(self, assertions: List[Dict]) -> List[SemanticAuditResult]:
        """逐条审计断言"""
        
        results = []
        
        for asc in assertions:
            result = self._audit_single(asc)
            results.append(result)
        
        return results
    
    def _audit_single(self, assertion: Dict) -> SemanticAuditResult:
        """审计单条断言"""
        
        raw_text = assertion.get('raw_text', '')
        semantic_unit = assertion.get('semantic_unit', '')
        primitive = assertion.get('primitive', '')
        condition = assertion.get('condition', '')
        
        drift_issues = []
        over_interpret_issues = []
        engineering_extensions = []
        
        # 检查1: Primitive是否改变对象
        if primitive != self._extract_primitive_from_text(raw_text):
            drift_issues.append(f"Primitive '{primitive}'可能改变原文对象")
        
        # 检查2: Condition是否添加原文没有的条件
        extra_conditions = self._find_extra_conditions(raw_text, condition)
        if extra_conditions:
            over_interpret_issues.extend(extra_conditions)
            engineering_extensions.extend([f"Condition扩展: {c}" for c in extra_conditions])
        
        # 检查3: Negative Cases是否合理
        neg_cases = assertion.get('negative_cases', [])
        for neg in neg_cases:
            if not self._is_reasonable_negative(raw_text, neg):
                drift_issues.append(f"Negative Case不合理: {neg.get('case')}")
        
        # 计算保真度分数
        fidelity_score = self._calculate_fidelity(
            len(drift_issues), 
            len(over_interpret_issues),
            len(raw_text),
            len(condition)
        )
        
        # 判定审计状态
        if len(drift_issues) > 0 or len(over_interpret_issues) > 2:
            audit_status = 'DRIFT'
        elif len(over_interpret_issues) > 0:
            audit_status = 'OVER_INTERPRET'
        else:
            audit_status = 'PASS'
        
        return SemanticAuditResult(
            assertion_id=assertion.get('assertion_id', ''),
            name=assertion.get('name', ''),
            source_book=assertion.get('source_book', ''),
            passage_id=assertion.get('passage_id', ''),
            raw_text=raw_text,
            semantic_unit=semantic_unit,
            primitive=primitive,
            condition=condition,
            audit_status=audit_status,
            drift_issues=drift_issues,
            over_interpret_issues=over_interpret_issues,
            engineering_extensions=engineering_extensions,
            fidelity_score=fidelity_score
        )
    
    def _extract_primitive_from_text(self, raw_text: str) -> str:
        """从原文提取Primitive（保守估计）"""
        
        if '犯岁' in raw_text or '日干克岁君' in raw_text:
            return 'day_gan_克_year_gan'
        elif '主贫' in raw_text or '岁君制日干' in raw_text:
            return 'year_gan_克_day_gan'
        elif '制中有生' in raw_text or '生中有制' in raw_text:
            return 'zhi_hua_dialectic'
        elif '太过' in raw_text and '不及' in raw_text:
            return 'wang_shuai_zhihua'
        elif '用神' in raw_text and '月令' in raw_text:
            return 'yong_shen_source'
        elif '相神' in raw_text and '辅' in raw_text:
            return 'xiang_shen_assist'
        elif '调候' in raw_text or ('丁' in raw_text and '寒' in raw_text):
            return 'tiao_hou_requirement'
        elif '天干' in raw_text and '一气' in raw_text:
            return 'tian_gan_nature'
        elif '地支' in raw_text and '五行' in raw_text:
            return 'di_zhi_nature'
        else:
            return 'unknown'
    
    def _find_extra_conditions(self, raw_text: str, condition: str) -> List[str]:
        """找出Condition中添加的原文没有的条件"""
        
        extra = []
        
        # 检查是否添加了原文没有的概念
        if '日支' in condition and '日支' not in raw_text:
            extra.append("添加原文未提及的'日支'条件")
        
        if '救应' in condition and '救应' not in raw_text:
            extra.append("添加原文未提及的'救应'条件")
        
        if '量化' in condition or '比例' in condition:
            extra.append("添加原文未提及的'量化/比例'概念")
        
        if '判断标准' in condition:
            extra.append("添加原文未提及的'判断标准'")
        
        return extra
    
    def _is_reasonable_negative(self, raw_text: str, negative_case: Dict) -> bool:
        """判断Negative Case是否合理"""
        
        case = negative_case.get('case', '')
        reason = negative_case.get('reason', '')
        
        # 不合理的情况
        if '吉凶' in case and '吉凶' not in raw_text:
            # 原文没有讨论吉凶，但Negative Case添加了吉凶判断
            return False
        
        if '程度' in case and '程度' not in raw_text:
            # 原文没有讨论程度，但Negative Case添加了程度判断
            return False
        
        return True
    
    def _calculate_fidelity(self, drift_count: int, over_interp_count: int, 
                           text_len: int, condition_len: int) -> float:
        """计算保真度分数（0-1）"""
        
        if text_len == 0:
            return 0.0
        
        # 基础分数
        base_score = 1.0
        
        # 漂移扣分
        base_score -= drift_count * 0.3
        
        # 过度解释扣分
        base_score -= over_interp_count * 0.2
        
        # 条件长度与原文长度比例惩罚（条件太长说明添加了过多内容）
        if condition_len > text_len * 2:
            base_score -= 0.2
        
        return max(0.0, min(1.0, base_score))


def main():
    print("=" * 70)
    print("P0-8.3: Assertion Semantic Audit")
    print("=" * 70)
    
    # 加载P0-8.2生产的断言
    production_path = os.path.join(BASE_DIR, 'data', 'p0_8_2_assertion_production.json')
    
    if not os.path.exists(production_path):
        print("\n❌ 错误: 找不到P0-8.2的生产结果")
        return False
    
    with open(production_path, 'r', encoding='utf-8') as f:
        production_data = json.load(f)
    
    assertions = production_data.get('assertions', [])
    print(f"\n▶ 加载断言: {len(assertions)}条")
    
    # 执行语义审计
    print("\n▶ 执行语义审计...")
    auditor = SemanticAuditor()
    results = auditor.audit_assertions(assertions)
    
    # 统计结果
    pass_count = sum(1 for r in results if r.audit_status == 'PASS')
    drift_count = sum(1 for r in results if r.audit_status == 'DRIFT')
    over_interp_count = sum(1 for r in results if r.audit_status == 'OVER_INTERPRET')
    
    avg_fidelity = sum(r.fidelity_score for r in results) / len(results) if results else 0
    
    print(f"\n【审计统计】")
    print(f"  ✅ PASS: {pass_count}条")
    print(f"  ⚠️  DRIFT: {drift_count}条")
    print(f"  ⚠️  OVER_INTERPRET: {over_interp_count}条")
    print(f"  平均保真度: {avg_fidelity:.2f}")
    
    # 输出详细结果
    print("\n" + "=" * 70)
    print("Audit Results")
    print("=" * 70)
    
    for result in results:
        print(f"\n{result.assertion_id}: {result.name}")
        print(f"  来源: {result.source_book} · {result.passage_id}")
        print(f"  原文: {result.raw_text}")
        print(f"  Primitive: {result.primitive}")
        print(f"  Condition: {result.condition}")
        print(f"  审计状态: {result.audit_status}")
        print(f"  保真度: {result.fidelity_score:.2f}")
        
        if result.drift_issues:
            print(f"  ⚠️  语义漂移:")
            for issue in result.drift_issues:
                print(f"     - {issue}")
        
        if result.over_interpret_issues:
            print(f"  ⚠️  过度解释:")
            for issue in result.over_interpret_issues:
                print(f"     - {issue}")
        
        if result.engineering_extensions:
            print(f"  🔧 工程扩展:")
            for ext in result.engineering_extensions:
                print(f"     - {ext}")
    
    # 保存结果
    output_path = os.path.join(BASE_DIR, 'data', 'p0_8_3_semantic_audit.json')
    result_data = {
        'stage': 'P0-8.3',
        'timestamp': datetime.now().isoformat(),
        'total_assertions': len(results),
        'pass_count': pass_count,
        'drift_count': drift_count,
        'over_interp_count': over_interp_count,
        'avg_fidelity': avg_fidelity,
        'results': [r.to_dict() for r in results]
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 核心结论
    print("\n" + "=" * 70)
    print("核心结论")
    print("=" * 70)
    
    if drift_count == 0 and over_interp_count == 0:
        print("\n【语义审计通过】")
        print("✓ 所有断言忠实于原文")
        print("✓ 无过度解释")
        print("✓ 无语义漂移")
        print("\n【流水线状态】")
        print("P0-8.3 Semantic Audit 🟢 PASS")
        return True
    else:
        print("\n【语义审计发现问题】")
        if drift_count > 0:
            print(f"⚠️  {drift_count}条断言存在语义漂移")
        if over_interp_count > 0:
            print(f"⚠️  {over_interp_count}条断言存在过度解释")
        print("\n建议:")
        print("- 对DRIFT断言重新审视Primitive和Condition定义")
        print("- 对OVER_INTERPRET断言拆分工程扩展部分为独立语义层")
        print("\n【流水线状态】")
        print("P0-8.3 Semantic Audit 🟡 NEEDS_REVIEW")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)