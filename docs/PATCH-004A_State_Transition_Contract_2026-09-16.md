# PATCH-004A State Transition Contract（状态转换契约）

- 日期：2026-09-16
- 状态：FROZEN_DRAFT（不实现任何算法）
- 依据：Human 裁决「PATCH-004 通过；进入 4.4 前先补 PATCH-004A State Transition Contract」
- 契约文件：`governance/patch_004a_state_transition_contract.json`

## 一、目的

PATCH-004 定义了状态变量，PATCH-004A 定义**变量之间允许的关系**：

- `allowed_transition`：原文直接支持的状态产出
- `forbidden_transition`：任何情况下禁止的语义串联
- `requires_context`：可作为分析输入，但必须携带语境/多源

**否则 Agent 后续仍可能自动串联状态**（如得令→strong）。

## 二、核心铁律

1. 状态变量之间不直接产生业务判断；进入 Business Judgment 必须经 Rule 层授权或 Conflict Resolver
2. 未登记转换 FAIL_CLOSED，Agent 不得自行串联
3. 单因子不得决定强弱：`order_state=GET_ORDER` 单独不得输出 strength
4. 禁 `root_state→favorable`、`order_state→strong`、`wang_state→STRONG`、`RULING_SCHEDULE→WEIGHT`
5. 转换必须携带依据（source_ids 或 REQUIRES_RULE）
6. CONFLICT ≠ ERROR，无法判断 UNDETERMINED

## 三、转换表

### 3.1 ALLOWED（状态产出，8 条）

| 转换 | 来源 | 注 |
|---|---|---|
| GET_ORDER → order_state | YHZP-030-001/YHZP-138-001/PZZQ-005-007/SFTK-120-004 | 得令≠强；对象化 |
| GET_TIME → order_state | YHZP-138-001 | 得时≠得令 |
| ROOTED_IN → root_state | YHZP-123-003/PZZQ-007-021/DTS-010-003/QTBJ-011-001/SFTK-020-014 | 对象化根 |
| TREND_TO → trend_state | DTS-008-003/DTS-008-022/SMTH-035-001/SFTK-129-038 | 势≠强弱 |
| PROSPEROUS_AT → wang_state | YHZP-138-001/DTS-016-001/DTS-016-002 | 得时俱为旺论 |
| QIANG_CONDITION → qiang_state | YHZP-138-001/SFTK-120-004 | 遇劫为强 |
| SHUAI_CONDITION → shuai_state | YHZP-138-001/DTS-016-002 | 失令便作衰看 |
| RULING_SCHEDULE → schedule_record | YHZP-056-001/DTS-015-004/DTS-015-006 | SCHEDULE_VARIANT 并存，禁 merge/WEIGHT |

### 3.2 REQUIRES_CONTEXT（分析输入，3 条）

| 转换 | 要求 | 来源 |
|---|---|---|
| order+root+support+qi → strength_analysis | 多源综合，禁单因子；四维齐全 | YHZP-138-001/PZZQ-005-007/SFTK-120-004/DTS-016-001 |
| wang+shuai → wangshuai_analysis | DTS 衰旺真机语境 | DTS-016-001/DTS-016-002 |
| trend → conghua_evaluation | 仅从化域；禁跨域用于强弱 | DTS-008-003/DTS-008-022/SFTK-082-001 |

### 3.3 FORBIDDEN（12 条）

| 转换 | 原因 |
|---|---|
| order_state → strength_state | 得令≠强 |
| order_state → strong | 单因子禁出业务强弱 |
| root_state → strength_state | 有根≠强 |
| root_state → favorable | 根≠喜忌 |
| wang_state → STRONG | 旺≠STRONG |
| trend_state → strength_state | 势≠强弱 |
| RULING_SCHEDULE → WEIGHT | schedule≠weight |
| support_state → strong | 党众≠一定强，禁数量阈值 |
| ANY_STATE → favorable/unfavorable | 喜忌属 Rule Layer |
| DTS_bing → SFTK_bingyao | 禁跨书串联 |
| PZZQ_qingza → DTS_zhuo_state | 禁跨书合并 |
| UNKNOWN → NO/FALSE/ABSENT | UNKNOWN≠否定 |

## 四、转换治理

- 未登记转换 FAIL_CLOSED
- 冲突→Conflict Resolver（登记→经典语境主判→UNDETERMINED）
- REQUIRES_CONTEXT 具体规则由对应域 Rule 授权后执行
- 每个转换记录 from/to/type/source_ids/rule_boundary，可回查

## 五、下一步

004A 冻结后，才进入：
4.4 Boolean/Enum Rule Design → 旺衰状态模型 → 强弱判断模型 →（Rule Construction → Conflict Test → Golden Case → Production Rule）
