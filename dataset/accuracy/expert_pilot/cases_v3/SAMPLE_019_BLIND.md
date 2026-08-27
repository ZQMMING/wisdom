# SAMPLE_019 — Blind Evaluation (v3)

## 人物基本信息

- **人物ID**: PB-800903
- **性别**: 男
- **出生年**: 1980
- **出生月**: 9
- **出生日**: 3
- **出生时**: 寅

## 系统输入

```json
{
  "birth_info": {
    "year": 1980,
    "month": 9,
    "day": 3,
    "hour": "寅",
    "gender": "male"
  }
}
```

## 系统原始输出

### 八字四柱

- 年柱: Pillar(heavenly_stem='GENG', earthly_branch='SHEN')
- 月柱: Pillar(heavenly_stem='JIA', earthly_branch='SHEN')
- 日柱: Pillar(heavenly_stem='JI', earthly_branch='MAO')
- 时柱: Pillar(heavenly_stem='YI', earthly_branch='CHOU')

### 河洛卦象

- **先天卦**: 雷风恒（上卦震, 下卦巽）
- **后天卦**: 水雷屯（上卦坎, 下卦震）
- **元堂**: 九三
- 天数: 38（化简: 3）
- 地数: 34（化简: 4）

### 天地数

- 天数: 38（化简: 3）
- 地数: 34（化简: 4）

### 计算细节

庚申: 天干3, 地支(4, 9) → 奇数[3, 9], 偶数[4]
甲申: 天干6, 地支(4, 9) → 奇数[9], 偶数[6, 4]
己卯: 天干9, 地支(3, 8) → 奇数[9, 3], 偶数[8]
乙丑: 天干2, 地支(5, 10) → 奇数[5], 偶数[2, 10]

---

### 易经解释
- **状态**: 卦象：水雷屯卦；上坎☵(水)下震☳(木)；体用关系：体生用（泄）；元堂：九三；爻辞原文：'即鹿无虞，惟入于林中，君子几不如舍，往吝。'；爻义：即鹿无虞，惟入于林中，君子几不如舍，往吝，盲目追逐必失利；大象：云雷屯，君子以经纶。。
- **机会**: 体用内生外，需主动付出，宜注重长期回报；爻辞启示：即鹿无虞，惟入于林中，君子几不如舍，往吝，盲目追逐必失利；有利方向：没有向导/资源就贸然追猎，等于自投罗网。如果缺少必要的前提条件（资金、人脉、信息），立即放弃这个目标。及时止损是智慧；相关领域：起步、艰难、破局。
- **风险**: 体泄于用，注意精力过度消耗；爻位分析：三爻阴居阳位，不当位。六三居下卦之极，上临四阴，下承二阴。无应（与上六皆阴），又失位，往则入林无所获；注意领域：放弃错误投资、及时止损、避免盲目冒险。
- **建议**: 策略建议：没有向导/资源就贸然追猎，等于自投罗网。如果缺少必要的前提条件（资金、人脉、信息），立即放弃这个目标。及时止损是智慧；五行态势：下卦木，上卦水；建议借助WATER性人事物调和，平衡内外局势。
- **行动**: 参考周易·屯卦·六三：'即鹿无虞，惟入于林中，君子几不如舍，往吝。'。没有向导/资源就贸然追猎，等于自投罗网。如果缺少必要的前提条件（资金、人脉、信息），立即放弃这个目标。及时止损是智慧。；土性主信，宜稳重扎实，积累信誉与人脉。
- **方向**: CHANGE
- **来源**: 周易·水雷屯·卦辞, 周易·屯卦·六三, 错卦:火风鼎, 综卦:雷水解
- **置信度**: 0.8

---


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
  "strengths": [...],
  "weaknesses": [...],
  "contradictions": [...],
  "unsupported_claims": [...],
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
