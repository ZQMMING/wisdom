# SAMPLE_015 — Blind Evaluation (v2)

## 人物基本信息

- **人物ID**: PB-0002
- **性别**: 男
- **出生年**: 1960
- **出生月**: 12
- **出生日**: 10
- **出生时**: 巳时

## 系统输入

```json
{
  "birth_info": {
    "year": 1960,
    "month": 12,
    "day": 10,
    "hour": "巳",
    "gender": "male"
  }
}
```

## 系统原始输出

### 八字四柱

- 年柱: 庚子
- 月柱: 戊子
- 日柱: 壬申
- 时柱: 乙巳

### 河洛卦象

- **先天卦**: 地天泰（上卦坤，下卦乾）
- **后天卦**: 泽地萃（上卦兑，下卦坤）
- **元堂**: 九三（阳）

### 天地数

- 天数: 22（化简: 2）
- 地数: 26（化简: 6）

### 计算细节

庚子: 天干3, 地支(1, 6) → 奇数[3, 1], 偶数[6]
戊子: 天干1, 地支(1, 6) → 奇数[1, 1], 偶数[6]
壬申: 天干6, 地支(4, 9) → 奇数[9], 偶数[6, 4]
乙巳: 天干2, 地支(2, 7) → 奇数[7], 偶数[2, 2]

---





### 关系式解释（系统输出）
- 日主：REN；评估窗口：1995–2015（命主 35–55 岁，聚焦信号最集中的关键年份）

- 【年度焦点】信号叠加最强的年份及具体规则机制：
  · 2004 年（5 个动态信号）：
      - ETP-CRR-102-00 [机会] 流年正印/偏印当值 → 事业助力（依据 E-K2G-DAYUN-002）
      - ETP-CRR-104-01 [变动] 流年偏印当值 → 事业新机会/变动（依据 E-K2G-DAYUN-002）
      - ETP-EDU-101-02 [机会] 流年印星当值 → 学业助力（依据 E-K2G-DAYUN-002）
      - ETP-MAR-105-08 [变动] 男命财星弱/无根 → 妻星不显 → 婚姻迟滞（依据 E-K2G-SHIPI-009）
      - ETP-SUY-101-09 [机会] 岁运并临且主气十神为喜用(比印) → 吉信号放大（依据 E-K2G-DAYUN-002）
  · 1998 年（4 个动态信号）：
      - ETP-EDU-102-00 [变动] 流年食神当值 → 学业表现活跃（依据 E-K2G-DAYUN-002）
      - ETP-MAR-105-06 [变动] 男命财星弱/无根 → 妻星不显 → 婚姻迟滞（依据 E-K2G-SHIPI-009）
      - ETP-SUY-102-07 [风险] 岁运并临且主气十神为忌神(食伤财官) → 凶信号放大（依据 E-K2G-DAYUN-002）
      - ETP-WLT-104-10 [风险] 流年支冲日支 → 财运波动（依据 E-K2G-DAYUN-002）
  · 2005 年（4 个动态信号）：
      - ETP-CRR-102-00 [机会] 流年正印/偏印当值 → 事业助力（依据 E-K2G-DAYUN-002）
      - ETP-EDU-101-01 [机会] 流年印星当值 → 学业助力（依据 E-K2G-DAYUN-002）
      - ETP-MAR-105-07 [变动] 男命财星弱/无根 → 妻星不显 → 婚姻迟滞（依据 E-K2G-SHIPI-009）
      - ETP-SUY-101-08 [机会] 岁运并临且主气十神为喜用(比印) → 吉信号放大（依据 E-K2G-DAYUN-002）
  · 2010 年（4 个动态信号）：
      - ETP-EDU-102-00 [变动] 流年食神当值 → 学业表现活跃（依据 E-K2G-DAYUN-002）
      - ETP-MAR-105-06 [变动] 男命财星弱/无根 → 妻星不显 → 婚姻迟滞（依据 E-K2G-SHIPI-009）
      - ETP-SUY-102-07 [风险] 岁运并临且主气十神为忌神(食伤财官) → 凶信号放大（依据 E-K2G-DAYUN-002）
      - ETP-WLT-104-10 [风险] 流年支冲日支 → 财运波动（依据 E-K2G-DAYUN-002）
  · 1997 年（3 个动态信号）：
      - ETP-CRR-101-00 [风险] 流年正官/七杀当值 → 事业变动压力（依据 E-K2G-DAYUN-002）
      - ETP-MAR-105-07 [变动] 男命财星弱/无根 → 妻星不显 → 婚姻迟滞（依据 E-K2G-SHIPI-009）
      - ETP-SUY-102-08 [风险] 岁运并临且主气十神为忌神(食伤财官) → 凶信号放大（依据 E-K2G-DAYUN-002）

- 【方向】各关键年份由具体规则机制驱动（流年正印/偏印当值、比劫夺财、岁运并临、流年支冲日支等），机会与风险信号并存且方向明确。
- 【证据】每条信号标注古籍依据（E-K2G 证据链）。
- 【置信度】LIKELY（单体系 EVENT_TOPIC，未跨体系收敛）。

## 评分任务

你是「顺天 V1.3 Accuracy Validation」项目的独立专家评价员。

你的唯一任务是：在严格的盲评条件下，根据预先冻结的评价标准，对「顺天系统生成的关系式解释」进行专家级质量评价。

### 最重要的原则

1. 评价系统，不重新计算系统 — 不得自行重新计算八字/河洛/紫微
2. 评价关系，不评价语言漂亮程度
3. 历史事实不能自动证明预测正确
4. 禁止事后合理化 — 宽泛语言适配大量事件不得视为高质量
5. 证据不足时必须使用 NOT_EVALUABLE

### 评分维度 (0-3 分)

| 维度 | 3 (STRONG) | 2 (ACCEPTABLE) | 1 (WEAK) | 0 (FAIL) |
|------|-----------|---------------|---------|---------|
| Temporal Alignment | 时间关系清晰，集中于目标窗口 | 基本对应，时间边界较宽 | 时间对应较弱，明显泛化 | 无法建立时间对应 |
| Event Correspondence | 对事件类型及性质有明确对应 | 存在合理对应，不够具体 | 只能通过宽泛解释勉强对应 | 无合理对应 |
| Relational Coherence | 关系结构高度一致 | 基本一致，轻微缺口 | 关系链存在明显断裂 | 自相矛盾或无法成立 |
| Evidence Support | 核心判断均有明确证据支持 | 大部分判断有证据支持 | 证据薄弱或存在明显跳跃 | 核心结论基本没有证据支持 |
| Directionality | 方向明确且证据充分 | 基本合理 | 方向模糊或存在明显冲突 | 方向与证据明显相反 |
| Specificity | 高度具体，具有明显约束力 | 有一定具体性 | 高度泛化 | 几乎完全属于通用套话 |
| Overall Interpretability | 整体解释成熟、连贯、可审计 | 基本成立，存在明显不足 | 解释零散或逻辑薄弱 | 无法形成有效解释 |

### 输出格式

必须严格输出 JSON，不得输出 Markdown 或额外解释：

```json
{
  "case_id": "...",
  "evaluable": true,
  "dimensions": {
    "temporal_alignment": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "event_correspondence": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "relational_coherence": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "evidence_support": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "directionality": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "specificity": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "overall_interpretability": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."}
  },
  "strengths": ["..."],
  "weaknesses": ["..."],
  "contradictions": ["..."],
  "unsupported_claims": ["..."],
  "overall_assessment": "...",
  "confidence": "HIGH|MEDIUM|LOW"
}
```

### 禁止行为

- 不得因为相信/不相信命理而评分
- 不得因为系统使用传统术语而加分
- 不得因为语言优美/冗长而加分
- 不得因为"看起来很准"而直接加分
- 不得使用事后已知信息反向修改评分标准
- 不得为系统寻找合理化解释或制造缺失证据
- 不得自己重新计算系统结果并将其作为 Ground Truth


---

**禁止信息**: 本文件不包含 Ground Truth、其他 Rater 评分、系统内部计算链、系统 confidence 值。
