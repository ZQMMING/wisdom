# SAMPLE_037 — Blind Evaluation (v3)

## 人物基本信息

- **人物ID**: PB-640508
- **性别**: 男
- **出生年**: 1964
- **出生月**: 5
- **出生日**: 8
- **出生时**: 申

## 系统输入

```json
{
  "birth_info": {
    "year": 1964,
    "month": 5,
    "day": 8,
    "hour": "申",
    "gender": "male"
  }
}
```

## 系统原始输出

### 八字四柱

- 年柱: Pillar(heavenly_stem='JIA', earthly_branch='CHEN')
- 月柱: Pillar(heavenly_stem='JI', earthly_branch='SI')
- 日柱: Pillar(heavenly_stem='DING', earthly_branch='SI')
- 时柱: Pillar(heavenly_stem='JIA', earthly_branch='CHEN')

### 河洛卦象

- **先天卦**: 山天大畜（上卦艮, 下卦乾）
- **后天卦**: 风山渐（上卦巽, 下卦艮）
- **元堂**: 初九
- 天数: 40（化简: 5）
- 地数: 36（化简: 6）

### 天地数

- 天数: 40（化简: 5）
- 地数: 36（化简: 6）

### 计算细节

甲辰: 天干6, 地支(5, 10) → 奇数[5], 偶数[6, 10]
己巳: 天干9, 地支(2, 7) → 奇数[9, 7], 偶数[2]
丁巳: 天干7, 地支(2, 7) → 奇数[7, 7], 偶数[2]
甲辰: 天干6, 地支(5, 10) → 奇数[5], 偶数[6, 10]

---

### 易经解释
- **状态**: 卦象：风山渐卦；上巽☴(木)下艮☶(土)；体用关系：体克用（耗）；元堂：初九；爻辞原文：'鸿渐于干，小子厉，有言无咎。'；大象：山上有木，渐。君子以居贤德善俗。。
- **机会**: 体用内克外，内在能力可制衡外部，宜适度主动；局面研判：暂无显著障碍，可平稳行动；相关领域：渐进、积累、循序渐进。
- **风险**: 体虽克用，但主动出击亦需谨慎；审慎提示：形势严峻，不可大意。
- **建议**: 五行态势：下卦土，上卦木；建议借助METAL性人事物调和，平衡内外局势。
- **行动**: 参考周易·渐卦·初6：'鸿渐于干，小子厉，有言无咎。'，结合当前情境判断。；火性主礼，宜主动表达，把握时机展现能力。
- **方向**: CHANGE
- **来源**: 周易·风山渐·卦辞, 周易·渐卦·初6, 错卦:雷泽归妹, 综卦:山风蛊
- **置信度**: 0.7

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
