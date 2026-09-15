# -*- coding: utf-8 -*-
"""PATCH-004A-R1：四条治理补丁（RULE-14~17）+ execution_mode 字段"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\governance\patch_004a_state_transition_contract.json'
d = json.load(io.open(P, encoding='utf-8'))

# 1. 新增治理规则（RULE-14~17）
d['governance_rules'] = [
    {
        "id": "RULE-14",
        "text": "ALLOWED_TRANSITION ≠ AUTOMATIC_RULE_EXECUTION：状态产出可登记，但进入业务判断必须经 Rule 授权",
        "execution_mode_enum": ["DIRECT_OUTPUT", "CONTEXT_ONLY", "RULE_REQUIRED", "REFERENCE_ONLY"]
    },
    {
        "id": "RULE-15",
        "text": "strength_factor_assessment 仅产生 evidence/factor 集合，不得直接生成 strength_state；最终强弱状态必须进入 Rule Layer",
        "renamed_from": "strength_analysis"
    },
    {
        "id": "RULE-16",
        "text": "factor_count / score / percentage 禁止生成旺衰强弱状态（六经典无三项累计评分依据）",
        "forbidden": "FORBIDDEN-13: factor_count → strength_state"
    },
    {
        "id": "RULE-17",
        "text": "SOURCE_PRIORITY 必须服从 CLASSICAL_SCOPE_MATCH（DOMAIN_MATCH_PRIORITY > BOOK_PRIORITY）；不得按经典等级排序（SOURCE_PRIORITY ≠ CLASSIC_PRIORITY）"
    }
]

# 2. ALLOWED 转换补 execution_mode
for t in d['transitions']['state_production_allowed']:
    if t['to'] == 'schedule_record':
        t['execution_mode'] = 'REFERENCE_ONLY'
    elif t['to'] in ('order_state', 'root_state', 'trend_state', 'wang_state', 'qiang_state', 'shuai_state'):
        t['execution_mode'] = 'DIRECT_OUTPUT'
    else:
        t['execution_mode'] = 'CONTEXT_ONLY'

# 3. REQUIRES_CONTEXT：strength_analysis 改名 strength_factor_assessment + 补 execution_mode
for t in d['transitions']['analysis_inputs_requires_context']:
    if t['to'] == 'strength_analysis':
        t['to'] = 'strength_factor_assessment'
        t['note'] = '仅产生证据/因子集合（令根扶制泄耗），不产出强弱结论；最终 strength_state 必须经 Rule Layer（RULE-15）'
        t['execution_mode'] = 'CONTEXT_ONLY'
    elif t['to'] == 'wangshuai_analysis':
        t['to'] = 'wangshuai_factor_assessment'
        t['note'] = 'DTS 衰旺真机语境；仅证据集合，不产出强弱结论（RULE-15）'
        t['execution_mode'] = 'CONTEXT_ONLY'
    elif t['to'] == 'conghua_evaluation':
        t['execution_mode'] = 'RULE_REQUIRED'

# 4. FORBIDDEN 增加 FORBIDDEN-13（RULE-16）
d['transitions']['forbidden'].append({
    "from": "factor_count/score/percentage",
    "to": "strength_state",
    "reason": "六经典无三项累计评分/百分比权重依据；禁现代旺衰评分模型（RULE-16）",
    "rule_boundary": "PATCH-004A RULE-16"
})

# 5. 4.5/冲突处理补 DOMAIN_MATCH_PRIORITY > BOOK_PRIORITY（RULE-17）
d['transition_governance']['domain_match_priority'] = (
    "DOMAIN_MATCH_PRIORITY > BOOK_PRIORITY：主判选择按问题域匹配（如调候→QTBJ 优先，寒暖燥湿→DTS 次之，其余按域），"
    "不是按经典等级排序；SOURCE_PRIORITY ≠ CLASSIC_PRIORITY（RULE-17）"
)

json.dump(d, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('PATCH-004A-R1 补丁完成：')
print('  RULE-14~17 已写入 governance_rules')
print('  ALLOWED 8 条 execution_mode 已补（DIRECT_OUTPUT/REFERENCE_ONLY）')
print('  REQUIRES_CONTEXT 改名：strength_factor_assessment / wangshuai_factor_assessment')
print('  FORBIDDEN-13 已加：factor_count/score/percentage → strength_state')
print('  冲突治理补：DOMAIN_MATCH_PRIORITY > BOOK_PRIORITY')
