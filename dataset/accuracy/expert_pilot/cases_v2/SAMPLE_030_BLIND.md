# SAMPLE_030 — Blind Evaluation (v2)

## 人物基本信息

- **人物ID**: PB-0001
- **性别**: 女
- **出生年**: 1982
- **出生月**: 9
- **出生日**: 27
- **出生时**: 申时

## 系统输入

```json
{
  "birth_info": {
    "year": 1982,
    "month": 9,
    "day": 27,
    "hour": "申",
    "gender": "female"
  }
}
```

## 系统原始输出

### 八字四柱

- 年柱: 壬戌
- 月柱: 己酉
- 日柱: 癸丑
- 时柱: 庚申

### 河洛卦象

- **先天卦**: 天地否（上卦乾，下卦坤）
- **后天卦**: 山天大畜（上卦艮，下卦乾）
- **元堂**: 六三（阴）

### 天地数

- 天数: 40（化简: 5）
- 地数: 36（化简: 6）

### 计算细节

壬戌: 天干6, 地支(5, 10) → 奇数[5], 偶数[6, 10]
己酉: 天干9, 地支(4, 9) → 奇数[9, 9], 偶数[4]
癸丑: 天干2, 地支(5, 10) → 奇数[5], 偶数[2, 10]
庚申: 天干3, 地支(4, 9) → 奇数[3, 9], 偶数[4]

---





### 关系式解释（系统输出）
- 日主：GUI；评估窗口：2017–2037（命主 35–55 岁，聚焦信号最集中的关键年份）

- 【年度焦点】信号叠加最强的年份及具体规则机制：
  · 2017 年（6 个动态信号）：
      - ETP-CRR-102-00 [机会] 流年正印/偏印当值 → 事业助力（依据 E-K2G-DAYUN-002）
      - ETP-CRR-104-01 [变动] 流年偏印当值 → 事业新机会/变动（依据 E-K2G-DAYUN-002）
      - ETP-EDU-101-02 [机会] 流年印星当值 → 学业助力（依据 E-K2G-DAYUN-002）
      - ETP-MAR-202-10 [机会] 女命官星入日支 → 夫星得力（依据 E-K2G-SHIPI-009）
      - ETP-SUY-101-11 [机会] 岁运并临且主气十神为喜用(比印) → 吉信号放大（依据 E-K2G-DAYUN-002）
  · 2029 年（6 个动态信号）：
      - ETP-CRR-102-00 [机会] 流年正印/偏印当值 → 事业助力（依据 E-K2G-DAYUN-002）
      - ETP-CRR-104-01 [变动] 流年偏印当值 → 事业新机会/变动（依据 E-K2G-DAYUN-002）
      - ETP-EDU-101-02 [机会] 流年印星当值 → 学业助力（依据 E-K2G-DAYUN-002）
      - ETP-MAR-202-10 [机会] 女命官星入日支 → 夫星得力（依据 E-K2G-SHIPI-009）
      - ETP-SUY-101-11 [机会] 岁运并临且主气十神为喜用(比印) → 吉信号放大（依据 E-K2G-DAYUN-002）
  · 2027 年（5 个动态信号）：
      - ETP-CRR-101-00 [风险] 流年正官/七杀当值 → 事业变动压力（依据 E-K2G-DAYUN-002）
      - ETP-MAR-202-10 [机会] 女命官星入日支 → 夫星得力（依据 E-K2G-SHIPI-009）
      - ETP-SUY-102-11 [风险] 岁运并临且主气十神为忌神(食伤财官) → 凶信号放大（依据 E-K2G-DAYUN-002）
      - ETP-TF-101-12 [机会] 偏印强于正印出玄学天赋;偏印不可临正官（依据 E-TF-101-001）
      - ETP-WLT-104-13 [风险] 流年支冲日支 → 财运波动（依据 E-K2G-DAYUN-002）
  · 2018 年（4 个动态信号）：
      - ETP-CRR-101-00 [风险] 流年正官/七杀当值 → 事业变动压力（依据 E-K2G-DAYUN-002）
      - ETP-MAR-202-10 [机会] 女命官星入日支 → 夫星得力（依据 E-K2G-SHIPI-009）
      - ETP-SUY-102-11 [风险] 岁运并临且主气十神为忌神(食伤财官) → 凶信号放大（依据 E-K2G-DAYUN-002）
      - ETP-TF-101-12 [机会] 偏印强于正印出玄学天赋;偏印不可临正官（依据 E-TF-101-001）
  · 2021 年（4 个动态信号）：
      - ETP-CRR-101-00 [风险] 流年正官/七杀当值 → 事业变动压力（依据 E-K2G-DAYUN-002）
      - ETP-MAR-202-10 [机会] 女命官星入日支 → 夫星得力（依据 E-K2G-SHIPI-009）
      - ETP-SUY-102-11 [风险] 岁运并临且主气十神为忌神(食伤财官) → 凶信号放大（依据 E-K2G-DAYUN-002）
      - ETP-TF-101-12 [机会] 偏印强于正印出玄学天赋;偏印不可临正官（依据 E-TF-101-001）

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
