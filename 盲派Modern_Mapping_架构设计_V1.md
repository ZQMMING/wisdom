# 盲派 Modern Semantic Mapping 层架构设计 V1

封板日期: 2026-09-17
状态: 架构设计封板，未开工

---

## 核心边界

系统严格分两个世界：

```
【经典语义域】                          【现代表达域】
八字排盘 Fact
     ↓
Blind Rule Evidence
     ↓
Blind Rule Registry
     ↓
Assertion Engine
     ↓
Judgment Engine V1.2
     ↓
───────────── Classical Boundary ─────────────
     ↓
Modern Semantic Mapping
     ↓
User Expression
```

**铁律**：
- 经典语义域：按书直说，不做现代化稀释
- Modern Mapping层：唯一负责现代语义转义
- Modern Mapping **禁止反向修改** 经典层任何内容

---

## 层职责

### 经典语义域（已封板）

| 层 | 职责 | 语言 |
|---|---|---|
| 八字排盘 | 原始确定事实 | 干支/十神/宫位等原始事实 |
| Blind Rule Evidence | 原书原义取证 | 原典原文+章节定位 |
| Blind Rule Registry | 按书执行规则 | 布尔条件规则 |
| Assertion Engine | 事实断言 | 结构枚举（如PRISON_STRUCTURE） |
| Judgment Engine | 经典判断 | 经典断语结构（如"主牢狱"） |

**原则**：古籍怎么说，后端就怎么保存。不做安全措辞稀释。

### Modern Mapping层（待开工）

| 层 | 职责 | 语言 |
|---|---|---|
| MappingRule | 经典→现代映射规则 | 结构化映射表 |
| ModernSemantic | 现代语义结果 | 安全/温和/非宿命论 |
| UserExpression | 用户表达 | 大白话/前端渲染 |

**原则**：
- 绝对化语言 → 倾向/风险/可能性
- 吉凶表达 → 中性描述
- 现代医学误读 → 风险信号不是确诊
- 现代法律事件误读 → 结构象不是事件坐实
- 宿命论 → 时间窗口不是必然
- 确定性事件语言 → 信号/方向

---

## 数据流

### 输入：ClassicalAssertion / JudgmentResult

```python
{
    "judgment_id": "J-DISASTER-004",
    "domain": "J7",
    "judgment_result": "PRISON_STRUCTURE",  # 经典语义
    "triggered_clauses": ("A",),
    "matched_assertions": ("A-DISASTER-PRISON",),
    "classical_meaning": "主牢狱",  # 原典原文含义
    "provenance": "J-DISASTER-004 → ... → 第12章",
}
```

### 中间：MappingRule

```python
{
    "classical_result": "PRISON_STRUCTURE",
    "modern_semantic": "传统命理将该结构解释为与受限制、约束、失去行动自由等情境有关",
    "cautious_notes": [
        "这是结构象，不是事件坐实",
        "不代表一定会发生牢狱事件",
        "需结合岁运引动和现实条件综合判断"
    ],
    "avoid_phrases": [
        "你会坐牢",
        "必然入狱",
        "肯定有牢狱之灾"
    ]
}
```

### 输出：ModernSemantic / UserExpression

```python
{
    "summary": "传统命理中，该结构与「受限制、约束、失去行动自由」的意象相关",
    "risk_level": "结构风险信号",
    "notes": [
        "这是传统命理的结构判断，不是事件预测",
        "是否应事取决于岁运引动和现实条件",
        "建议理性看待，不必过度焦虑"
    ]
}
```

---

## MappingRule 设计原则

### 1. 一条ClassicalAssertion对应一条MappingRule

不做"AI综合理解"。每条JudgmentResult有独立的现代语义映射。

### 2. MappingRule是静态配置，不是AI生成

所有映射规则必须预先人工审核后写死，不允许LLM动态生成。

### 3. 保留两层语义

输出必须同时保留：
- **经典语义**（classical_meaning）：原典原文含义
- **现代语义**（modern_semantic）：安全温和的现代表达

用户可以选择看经典版还是现代版。

### 4. 禁止反向污染

Mapping层的任何输出，禁止反写回经典层。经典层永远按书直说。

---

## 46条Judgment Mapping覆盖清单

| Judgment_ID | 经典Result | 经典语义（原典） | 现代Mapping方向 |
|---|---|---|---|
| J-WEALTH-003 | WEALTH_OWNERSHIP | 财主宾定位 | 财富来源方向 |
| J-WEALTH-005 | WEALTH_AUSPICIOUS_BREAK | 财星反局主大凶 | 财富结构风险 |
| J-OFFICIAL-002 | OFFICIAL_OWNERSHIP | 官主宾定位 | 事业平台方向 |
| J-OFFICIAL-003 | OFFICIAL_DISASTER_RISK | 官星高透克身=当官有灾 | 事业风险信号 |
| J-CAREER-001 | CAREER_DIRECTION_BANK | 财原神=银行/辰拱水=化工 | 职业方向候选 |
| J-SPECIAL-001 | FANJU_LAYERED_JUDGMENT | 反局三层应凶 | 结构层次判断 |
| J-TIMING-002 | LUCK_DYNAMIC_STATIC | 大运体用动静 | 岁运动静判断 |
| J-DISASTER-002 | PRISON_RISK | 反局+辰=牢狱风险 | 受限制风险信号 |
| J-HEALTH-002 | HEALTH_RISK_BLADDER_RECTUM | 时柱被穿=膀胱直肠风险 | 健康风险信号 |
| J-DISASTER-003 | CRIME_STRUCTURE_YIN | 丑酉阴中阴=犯罪结构 | 结构风险信号 |
| J-CAREER-003 | CAREER_ACADEMIC_DIRECTION | 文理分科 | 学科方向候选 |
| J-CAREER-004 | CAREER_INDUSTRY_DIRECTION | 干支→行业 | 行业方向候选 |
| J-HEALTH-003 | HEALTH_RISK_HAIR_FACE | 甲丁=头发/面损 | 健康风险信号 |
| J-WEALTH-006 | WEALTH_EASE_OR_HARD | 禄印相随=享受/辛苦 | 财富辛苦程度 |
| J-OFFICIAL-004 | ORTHODOX_UNORTHODOX_DIRECTION | 羊刃正/偏业 | 事业性质方向 |
| J-CAREER-002 | INSTITUTION_DIRECTION | 墓库→机构 | 机构方向候选 |
| J-TIMING-003 | YIMA_DYNAMIC_OR_STATIONARY | 驿马走动/停留 | 岁运动静信号 |
| J-KIN-002 | KIN_KONGWANG_RELATION | 空亡分宫六亲 | 六亲缘薄倾向 |
| J-MARRIAGE-002 | TAOHUA_MARITAL_RISK | 禄绊桃花=感情风险 | 感情风险信号 |
| J-WEALTH-007 | CAR_PROPERTY_SIGNAL | 时支=车 | 车辆相关信号 |
| J-HEALTH-005 | HEALTH_RISK_LEG_FOOT | 年支被破=腿足残疾 | 健康风险信号 |
| J-KIN-003 | MOTHER_IN_LAW_RELATION | 丈母娘在年 | 亲属关系象 |
| J-MARRIAGE-003 | SPOUSE_SOURCE_DIRECTION | 夫妻象在月=同学 | 配偶来源方向 |
| J-WEALTH-008 | WEALTH_CAREER_CONFLICT | 财多心乱=早辍学 | 学业事业冲突倾向 |
| J-WEALTH-009 | WEALTH_TALENT_DIRECTION | 财虚透=才华 | 才华方向 |
| J-CHILD-001 | CHILD_GENDER_TENDENCY | 子女性别倾向 | 子女性别倾向 |
| J-KIN-004 | MOTHER_HEALTH_RISK | 食神被穿=母早死风险 | 母亲健康风险 |
| J-WEALTH-010 | CAR_THEFT_RISK | 穿门口=车被盗风险 | 车辆财物风险 |
| J-OFFICIAL-005 | POLICE_DEPARTMENT_DIRECTION | 阳制阴=公安 | 部门方向候选 |
| J-WEALTH-011 | WEALTH_NATURE_DIRECTION | 带象四法 | 财富性质方向 |
| J-OFFICIAL-006 | MILITARY_DIRECTION | 杀入羊刃墓=军队 | 行业方向候选 |
| J-CAREER-005 | CHEMICAL_PHARMA_DIRECTION | 辰子=化工制药 | 行业方向候选 |
| J-WEALTH-012 | CAPITAL_OPERATION_DIRECTION | 丑未冲=资本运营 | 财富运作方向 |
| J-WEALTH-013 | LU_WEALTH_STRUCTURE | 禄神当财 | 财富结构判断 |
| J-WEALTH-014 | SHANGSHI_WEALTH_STRUCTURE | 伤食当财 | 财富结构判断 |
| J-WEALTH-015 | GUAN_WEALTH_STRUCTURE | 官杀当财 | 财富结构判断 |
| J-CAREER-006 | BUSINESS_MANAGER_DIRECTION | 内食神=企业 | 职业方向候选 |
| J-WEALTH-016 | REMOTE_TRADE_DIRECTION | 财在年=远方贸易 | 贸易方向候选 |
| J-MARRIAGE-004 | GOOD_MARRIAGE_STRUCTURE | 好婚姻结构 | 婚姻质量方向 |
| J-MARRIAGE-005 | BAD_MARRIAGE_STRUCTURE | 差婚姻结构 | 婚姻质量方向 |
| J-MARRIAGE-006 | MARRIAGE_TIMING_WINDOW | 结婚应期窗口 | 婚姻时间窗口 |
| J-MARRIAGE-007 | HUSBAND_COMPETE_RISK | 比劫争夫 | 感情竞争风险 |
| J-DISASTER-004 | PRISON_STRUCTURE | 牢狱五结构 | 受限制风险信号 |
| J-DISASTER-005 | RELEASE_TIMING_WINDOW | 出狱应期窗口 | 时间窗口 |
| J-WEALTH-017 | THIEF_STRUCTURE | 劫财官在主=小偷 | 结构风险信号 |
| J-DISASTER-006 | FREEDOM_LOSS_STRUCTURE | 食伤入墓=失自由 | 受限制风险信号 |

---

## 禁止事项

1. ❌ Mapping层反向修改Rule/Assertion/Judgment
2. ❌ Mapping层引入评分/概率/权重
3. ❌ Mapping层LLM动态生成语义
4. ❌ Mapping层输出Event（"你会坐牢"/"你会离婚"）
5. ❌ Mapping层输出WEALTH_LEVEL/财富金额
6. ❌ Mapping层修改经典语义本身

---

## 下一步

1. 逐条建立46条MappingRule（静态配置表）
2. 人工审核每条MappingRule的现代语义是否准确
3. 建立Modern Semantic Engine
4. 做Mapping层Semantic Gate
5. 解锁Frontend渲染
