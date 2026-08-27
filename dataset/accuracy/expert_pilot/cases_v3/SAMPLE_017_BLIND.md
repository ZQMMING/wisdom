# SAMPLE_017 — Blind Evaluation (v3)

## 人物基本信息

- **人物ID**: PB-730628
- **性别**: 男
- **出生年**: 1973
- **出生月**: 6
- **出生日**: 28
- **出生时**: 申

## 系统输入

```json
{
  "birth_info": {
    "year": 1973,
    "month": 6,
    "day": 28,
    "hour": "申",
    "gender": "male"
  }
}
```

## 系统原始输出

### 八字四柱

- 年柱: Pillar(heavenly_stem='GUI', earthly_branch='CHOU')
- 月柱: Pillar(heavenly_stem='WU', earthly_branch='WU')
- 日柱: Pillar(heavenly_stem='YI', earthly_branch='WEI')
- 时柱: Pillar(heavenly_stem='GENG', earthly_branch='CHEN')

### 河洛卦象

- **先天卦**: 天水讼（上卦乾, 下卦坎）
- **后天卦**: 地天泰（上卦坤, 下卦乾）
- **元堂**: 九二
- 天数: 26（化简: 1）
- 地数: 36（化简: 6）

### 天地数

- 天数: 26（化简: 1）
- 地数: 36（化简: 6）

### 计算细节

癸丑: 天干2, 地支(5, 10) → 奇数[5], 偶数[2, 10]
戊午: 天干1, 地支(2, 7) → 奇数[1, 7], 偶数[2]
乙未: 天干2, 地支(5, 10) → 奇数[5], 偶数[2, 10]
庚辰: 天干3, 地支(5, 10) → 奇数[3, 5], 偶数[10]

---

### 易经解释
- **状态**: 卦象：地天泰卦；上坤☷(土)下乾☰(金)；体用关系：体生用（泄）；元堂：六二；爻辞原文：'包荒，用冯河，不遐遗，朋亡，得尚于中行。'；爻义：包荒，用冯河，不遐遗，朋亡，得尚于中行，胸怀宽广中正行事；大象：天地交，泰。后以财成天地之道，辅相天地之宜，以左右民。。
- **机会**: 体用内生外，需主动付出，宜注重长期回报；爻辞启示：包荒，用冯河，不遐遗，朋亡，得尚于中行，胸怀宽广中正行事；有利方向：要有包容一切的胸襟，既能深入险境（冯河），又不遗忘远方的人（不遐遗），还能放下小圈子（朋亡）。做决策时保持中立公正；相关领域：通达、和谐、交流。
- **风险**: 体泄于用，注意精力过度消耗；爻位分析：二爻阳居阳位，当位且得中。九二居下卦之中，刚健中正。包荒用冯河，中正之道，得尚于中行；注意领域：领导力、包容管理、公正决策。
- **建议**: 策略建议：要有包容一切的胸襟，既能深入险境（冯河），又不遗忘远方的人（不遐遗），还能放下小圈子（朋亡）。做决策时保持中立公正；五行态势：下卦金，上卦土；建议借助EARTH性人事物调和，平衡内外局势。
- **行动**: 参考周易·泰卦·九二：'包荒，用冯河，不遐遗，朋亡，得尚于中行。'。要有包容一切的胸襟，既能深入险境（冯河），又不遗忘远方的人（不遐遗），还能放下小圈子（朋亡）。做决策时保持中立公正。；木性主仁，宜温和推进，善借人脉与成长机会。
- **方向**: CHANGE
- **来源**: 周易·地天泰·卦辞, 周易·泰卦·九二, 错卦:天地否, 综卦:天地否
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
