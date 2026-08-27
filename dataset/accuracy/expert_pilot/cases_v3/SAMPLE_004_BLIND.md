# SAMPLE_004 — Blind Evaluation (v3)

## 人物基本信息

- **人物ID**: PB-900108
- **性别**: 女
- **出生年**: 1990
- **出生月**: 1
- **出生日**: 8
- **出生时**: 辰

## 系统输入

```json
{
  "birth_info": {
    "year": 1990,
    "month": 1,
    "day": 8,
    "hour": "辰",
    "gender": "female"
  }
}
```

## 系统原始输出

### 八字四柱

- 年柱: Pillar(heavenly_stem='JI', earthly_branch='SI')
- 月柱: Pillar(heavenly_stem='DING', earthly_branch='CHOU')
- 日柱: Pillar(heavenly_stem='GUI', earthly_branch='YOU')
- 时柱: Pillar(heavenly_stem='JIA', earthly_branch='YIN')

### 河洛卦象

- **先天卦**: 山地剥（上卦艮, 下卦坤）
- **后天卦**: 坤为地（上卦坤, 下卦坤）
- **元堂**: 上九
- 天数: 40（化简: 5）
- 地数: 32（化简: 2）

### 天地数

- 天数: 40（化简: 5）
- 地数: 32（化简: 2）

### 计算细节

己巳: 天干9, 地支(2, 7) → 奇数[9, 7], 偶数[2]
丁丑: 天干7, 地支(5, 10) → 奇数[7, 5], 偶数[10]
癸酉: 天干2, 地支(4, 9) → 奇数[9], 偶数[2, 4]
甲寅: 天干6, 地支(3, 8) → 奇数[3], 偶数[6, 8]

---

### 易经解释
- **状态**: 卦象：坤为地卦；上坤☷(土)下坤☷(土)；体用关系：比和（平）；元堂：上六；爻辞原文：'龙战于野，其血玄黄。'；爻义：龙战于野，其血玄黄，阴阳相争两败俱伤；大象：地势坤，君子以厚德载物。。
- **机会**: 体用内外一致，能量协调，宜稳步推进；爻辞启示：龙战于野，其血玄黄，阴阳相争两败俱伤；有利方向：阴柔之势发展到极端，不得不与阳刚对抗。但这不是好局面，双方都会受伤。优先寻求和解方案，避免正面冲突。若已开战，做好止损准备；相关领域：包容、承载、稳定。
- **风险**: 爻位分析：上爻阴居阳位，不当位。上六处坤卦之极，阴极而阳生，龙战之象。坤道穷极，不得不与乾争，两败俱伤；注意领域：冲突爆发、两败局面、止损收尾。
- **建议**: 策略建议：阴柔之势发展到极端，不得不与阳刚对抗。但这不是好局面，双方都会受伤。优先寻求和解方案，避免正面冲突。若已开战，做好止损准备；五行态势：下卦土，上卦土；同气相应，宜顺势而为，不宜强行改变方向。
- **行动**: 参考周易·坤卦·上六：'龙战于野，其血玄黄。'。阴柔之势发展到极端，不得不与阳刚对抗。但这不是好局面，双方都会受伤。优先寻求和解方案，避免正面冲突。若已开战，做好止损准备。；水性主智，宜灵活变通，善用策略与时机。
- **方向**: NEUTRAL
- **来源**: 周易·坤为地·卦辞, 周易·坤卦·上六, 错卦:乾为天, 综卦:坤为地
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
