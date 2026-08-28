# 顺天/EXIS Canonical Semantic Authorization Pipeline - 上下文保存

**保存时间**: 2026-08-28
**当前阶段**: 七层语义授权链修正版已建立，待用户核查后可FROZEN

---

## 一、项目背景

用户正在构建一个命理系统（子平/盲派/紫微/河洛/易经），核心问题是：
> Engine算出了一个数，不代表这个数已经获得了原典概念的语义授权。

经过多轮审计，从最初的"Resolver能不能匹配"深入到"Canonical Condition怎样从原典获得语义授权"。

---

## 二、已完成的关键工作

### 2.1 Birth Chart Evidence Lock
- 原始输入：农历1983年9月29日，午时，男
- 正确公历：1983-11-03
- 正确八字：癸亥年 / 壬戌月 / 乙未日 / 壬午时
- 日主：乙木
- Evidence Hash: 66d485306b5d5a7b
- 发现并纠正了之前的Fixture错误（错误地使用了1983-06-15甲戌日甲木）

### 2.2 Phase 3 Rerun（正确八字下）
- PAT-001 正财格：SELECTED ✓
- TUN-001 乙木戌月调候：SELECTED ✓
- STR-001 身弱（WOOD<0.15）：SELECTED ⚠
- PAT-010 用神正财：SELECTED ⚠ HOLD
- STR-004 五行偏枯：SELECTED ⚠ HOLD

### 2.3 HOLD-001 PAT-010 审计
- 问题：Canonical Statement"用神正财"在子平真诠体系中不标准
- 原典依据：《子平真诠》第33章论财 + 第8章论用神
- 关键发现："用神专求月令"，正财格用神=月令正财（已被PAT-001覆盖）
- 徐注明确："格局之中，单用财者甚少"（财旺生官用神在官/食神生财用在食神/财格佩印用神在印）
- 当前Condition"存在正财"过宽：有正财≠正财为用神
- 状态：RETIRED_PENDING_REPLACEMENT（保留provenance，reuse: FORBIDDEN）

### 2.4 HOLD-002 STR-004 审计
- 问题：Engine的five_element_imbalance≠Canonical"五行偏枯"
- 原典依据：《渊海子平·五行元理消息赋》"五行不可太甚，八字须得中和""遐龄得于中和，夭折丧于偏枯"
- Engine算法：4天干+4地支本气简单计数，max>0.40或min<0.05
- 原典"偏枯"需要：太甚/不及 + 有无克制 + 有无生扶 + 五行接续 + 月令旺衰
- Engine只覆盖了"太甚/不及"的简单计数部分
- 状态：HOLD（继续Source Mapping，不定义"真正偏枯"的算法）

### 2.5 STR-001 Canonical Fidelity Audit
- 两个semantic jump：
  - Jump 1: WOOD<0.15 → 身弱 = INVALID（原典身弱需要月令+根气+生克对比多维度）
  - Jump 2: 身弱 → 喜印比 = CONDITIONAL（原典依据存在，但前提身弱未被证明）
- 循环自证风险：HIGH（不能用Engine的WOOD<0.15反过来定义"身弱"）
- Feature Sufficiency: INSUFFICIENT
- 拆分：STR-001A（日主身弱）+ STR-001B（身弱喜印比，前提依赖STR-001A）

### 2.6 七层语义授权链（修正版v2）
- L1 ENGINE FACT - 确定性计算事实
- L2 SEMANTIC MAPPING - Feature → Observable Meaning → Canonical Concept
- L3 CANONICAL EVIDENCE - 原典认可的证据（带evidence_role）
- L4 CANONICAL PROPOSITION - Evidence Aggregation后的命题判定
- L5 CONDITION AUTHORIZATION - 经过授权的条件
- L6 CANONICAL JUDGMENT - 格局/身弱/调候
- L7 CANONICAL ASSERTION - 正式断言（FROZEN）

---

## 三、关键架构原则（已确立）

1. **Feature Equivalence ≠ Judgment Equivalence**
2. **ENGINEERING_STATISTICAL_METRIC ≠ CANONICAL_CONCEPT**
3. **不能用工程阈值定义命理概念（防止循环自证）**
4. **Partial Evidence SHALL NOT be aggregated by count/score/vote（GOV-11禁止证据投票）**
5. **Source Scope必须明确（system/school/sources），防止不同体系被强行统一**
6. **Evidence Role必须标注（PRIMARY/SUPPORTING/CONTEXTUAL/EXCLUSION/NON_CANONICAL）**
7. **L2必须区分Observable Meaning和Canonical Concept**
8. **L3→L4必须经过Evidence Aggregation，且聚合方法必须由Canonical Contract授权**
9. **Assertion继续冻结，不进入Interpretation/Polarity/Cross-Engine**
10. **互补，不比较；不是投票**

---

## 四、15条治理规则（GOV-01到GOV-15）

- GOV-01: 不能从原典文本描述→人工归纳→直接变成机器必要条件
- GOV-02: Feature Semantic Mapping需要独立验证（L2）
- GOV-03: Canonical Evidence需要独立验证（L3）
- GOV-04: 每层都有自己的Fidelity，不能合并
- GOV-05: 下层UNPROVEN/INSUFFICIENT时，上层只能是PENDING
- GOV-06: Feature Equivalence ≠ Judgment Equivalence
- GOV-07: ENGINEERING_STATISTICAL_METRIC ≠ CANONICAL_CONCEPT
- GOV-08: 不能用工程阈值定义命理概念（防止循环自证）
- GOV-09: Canonical Condition必须基于AUTHORIZED的层
- GOV-10: Assertion继续冻结（L7）
- **GOV-11: Partial Evidence SHALL NOT be aggregated by count/score/vote/confidence，除非Canonical Contract明确定义aggregation relation**
- GOV-12: Source Scope必须明确
- GOV-13: Evidence Role必须标注，NON_CANONICAL不能直接用于Canonical授权
- GOV-14: L2必须区分Observable Meaning和Canonical Concept
- GOV-15: L3→L4必须经过Evidence Aggregation，且聚合方法必须由Canonical Contract授权

---

## 五、当前资产状态

| Judgment | Selection | Canonical Fidelity | 当前状态 |
|----------|-----------|-------------------|----------|
| PAT-001 正财格 | ✓ | ✓ | VALID |
| TUN-001 乙木戌月调候 | ✓ | ✓ | VALID |
| STR-001A 日主身弱 | ✓ | ❌ L2/L3未通过 | HOLD |
| STR-001B 身弱喜印比 | ✓ | ❌ 前提不成立 | HOLD（依赖STR-001A） |
| PAT-010 用神正财 | ✓ | ❌ 有正财≠用神 | RETIRED_PENDING_REPLACEMENT |
| STR-004 五行偏枯 | ✓ | ❌ imbalance≠偏枯 | HOLD |

**Production-valid = 2 | HOLD = 3 | RETIRED_PENDING_REPLACEMENT = 1**

---

## 六、STR-001A 七层贯通案例验证结果

- L1: wood_ratio=0.125 COMPUTED, evidence_role=NON_CANONICAL
- L2: Observable Meaning准确，但到Canonical Concept映射UNPROVEN
- L3: "木气偏少"只能作为SUPPORTING_EVIDENCE，缺失6个维度（月令/根气/生扶/克泄耗/坐旺衰/全局生克），INSUFFICIENT
- L4-L7: NOT CREATED
- Chain Validation: BLOCKED at L2+L3+L4+L5
- GOV-11检查: PASS

---

## 七、文件清单

| 文件 | 说明 |
|------|------|
| scripts/canonical_semantic_authorization_pipeline_v2.py | 七层语义授权链修正版（最新） |
| scripts/canonical_semantic_mapping_contract.py | 旧版三层架构（已被v2取代） |
| scripts/str001_canonical_fidelity_audit.py | STR-001 Canonical Fidelity Audit |
| scripts/canonical_source_audit_hold_001_002.py | HOLD-001/002 Canonical Source Audit |
| scripts/p3_rerun_audit_hold.py | HOLD审计（问题确认） |
| scripts/p6c3c4_phase3_rerun_correct_bazi.py | Phase 3 Rerun（正确八字） |
| scripts/birth_chart_evidence_lock_1983.py | Birth Chart Evidence Lock |
| scripts/birth_chart_reconciliation_1983.py | 日柱错误发现与比对 |

---

## 八、待决策项（下一步）

1. **七层Contract批准**: 用户核查后可FROZEN
2. **STR-001A下一步**: 基于七层架构，建立身弱的Canonical Source Mapping
   - 定义PRIMARY/SUPPORTING/CONTEXTUAL维度
   - 建立经过授权的Evidence Aggregation方法
   - 然后才能创建L4 Canonical Proposition
3. **PAT-010**: 正式执行RETIRED_PENDING_REPLACEMENT流程
4. **STR-004**: 继续HOLD，先完成Canonical Source Mapping
5. **不做**: 不继续Phase 3-4盲派做功，不开发"身弱算法"，不进入ContextResolver/Assertion

---

## 九、用户偏好和约束（从对话中提取）

- 极度严谨，要求逐项核查，不接受"看起来合理"的结论
- 要求区分Selection / Canonical Fidelity / Assertion三层
- 禁止证据投票、加权投票
- 禁止用工程阈值定义命理概念（循环自证）
- 要求原典出处，不接受"传统命理常识"
- 要求Source Scope明确，不同体系不强行统一
- 要求保留provenance，不删除历史资产ID
- Assertion/Interpretation/Polarity继续冻结
- 偏好粤语沟通（但当前对话用中文）
- 要求输出格式支持直接复制粘贴（Markdown代码块）

---

## 十、关键引用（原典）

### 《渊海子平·玄机赋》
- "得时俱为旺论，失令便作衰看。"
- "四柱无根，得时为旺；日干无气，遇劫为强。"
- "身弱喜印，主旺宜官。"
- "身弱者忌见财官。"
- "身衰则喜扶喜助。"
- "财多身弱，畏入财乡。"
- "身坐休囚，平生未济。"

### 《渊海子平·五行元理消息赋》
- "五行不可太甚，八字须得中和。"
- "遐龄得于中和。夭折丧于偏枯。"

### 《子平真诠》第8章 论用神
- "八字用神，专求月令，以日干配月令地支，而生克不同，格局分焉。"

### 《子平真诠》第33章 论财
- "财为我克，使用之物也，以能生官，所以为美。"
- 徐注："财为我克，必须身强，万能克制。若身弱，虽有财不能任，则财反为祸矣。……格局之中，单用财者甚少……皆非单用财也。"

---

**上下文保存完成。下一步等待用户核查七层Contract后，基于七层架构建立身弱的Canonical Source Mapping。**
