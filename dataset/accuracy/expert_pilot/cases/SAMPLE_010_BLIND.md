# SAMPLE_010 — Blind Evaluation

## 人物基本信息

- **人物ID**: PB-0003
- **性别**: 女
- **出生年**: 1962
- **出生月**: 9
- **出生日**: 29
- **出生时**: 寅时

## 系统输入

```json
{
  "birth_info": {
    "year": 1962,
    "month": 9,
    "day": 29,
    "hour": "寅",
    "gender": "female"
  }
}
```

## 系统原始输出

### 八字四柱

- 年柱: 壬寅
- 月柱: 己酉
- 日柱: 庚午
- 时柱: 戊寅

### 河洛卦象

- **先天卦**: 山水蒙
- **后天卦**: 地山谦
- **元堂**: 九二

### 天地数

- 天数: 35 (化简: 1)
- 地数: 28 (化简: 8)

### 解释

先天卦 山水蒙，元堂九二，后天卦 地山谦。

---

## 评分任务

请按照以下 Rubric 对系统输出进行评分：

### 评分维度 (0-2 分)

| Dimension | 2分 (优秀) | 1分 (合格) | 0分 (不合格) |
|-----------|-----------|-----------|-------------|
| STATE | 准确引用卦名、卦象、体用关系 | 基本正确但有遗漏 | 错误或缺失 |
| OPPORTUNITY | 识别具体机会，有经典依据 | 识别但缺乏依据 | 未识别或错误 |
| RISK | 识别具体风险，有经典依据 | 识别但缺乏依据 | 未识别或错误 |
| REMEDIATION | 建议与RISK对应，符合易理 | 建议合理但不具体 | 矛盾或缺失 |
| ACTION | 建议具体可执行 | 建议可操作但关联不强 | 不可操作或矛盾 |
| TEMPORAL | 正确映射时间状态 | 基本正确但有偏差 | 错误或缺失 |
| EVIDENCE | 引用具体经典 | 有引用但不具体 | 无引用或错误 |

### NOT_EVALUABLE

如果某维度无法评估，标记为 NOT_EVALUABLE 并说明原因：
- INSUFFICIENT_EVIDENCE: 系统未提供足够信息
- AMBIGUOUS: 输出模糊无法判断
- NOT_APPLICABLE: 该维度不适用
- MISSING: 维度完全缺失

### 输出格式

请输出 JSON 格式的评分结果：

```json
{
  "case_id": "SAMPLE_010",
  "rater": "GPT",
  "timestamp": "2026-08-22T10:00:00Z",
  "scores": {
    "state": {"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"},
    "opportunity": {"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"},
    "risk": {"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"},
    "remediation": {"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"},
    "action": {"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"},
    "temporal": {"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"},
    "evidence": {"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"}
  },
  "evaluable_dimensions": 7,
  "total_score": 0,
  "normalized_score": 0.0,
  "comments": "..."
}
```

---

## 禁止信息

本文件**不包含**：
- ❌ Ground Truth (历史事件结果)
- ❌ 其他 Rater 评分
- ❌ 系统内部计算链
- ❌ 系统 confidence 值

---

**生成者**: Hermes (Engineering Auditor)
**日期**: 2026-08-22
**版本**: A3.6-A-CaseFormat-v1
