# P0-8.10 Assertion一致性审计报告

**Commit**: 234fa9c（HOLD）  
**审计日期**: 2026-08-31  
**审计目标**: 逐条核对原典Evidence vs Assertion主体/条件/结论

---

## 审计方法

对每条COMPLETE Assertion进行：
1. 确认原典书名
2. 确认原典章节
3. 提取Evidence Span原文
4. 核对Assertion主体（十神名称）
5. 核对Assertion条件
6. 核对Assertion结论（格局名称）
7. 判断是否一致

---

## 审计结果

### PZZQ成格条件（11条）

#### 1. PZZQ-GEJU-004-A
```
Assertion: 伤官生财 → 伤官格成

Evidence Span (PZZQ 论食神格):
"食神生财，或食带煞而无财...食格成也"

主体核对:
- Evidence: 食神生财
- Assertion: 伤官生财
- ❌ 主体不一致！食神 ≠ 伤官

条件核对:
- Evidence: 食神生财
- Assertion: 伤官生财
- ❌ 条件不一致！

结论核对:
- Evidence: 食格成也
- Assertion: 伤官格成
- ❌ 结论不一致！食神格 ≠ 伤官格

裁决: REJECT（主体错位：食神→伤官）
```

---

#### 2. PZZQ-GEJU-004-B
```
Assertion: 伤官佩印且伤官旺、印有根 → 伤官格成

Evidence Span (PZZQ 论食神格):
"食神带煞而无财，弃食就煞而透印，食格成也。伤官生财，或伤官佩印而伤官旺，印有根，或伤官旺、身主弱而透煞印，或伤官带煞而无财，伤官格成也。"

主体核对:
- Evidence: 伤官佩印而伤官旺，印有根 → 伤官格成也
- Assertion: 伤官佩印且伤官旺、印有根 → 伤官格成
- ✅ 主体一致！

结论核对:
- Evidence: 伤官格成也
- Assertion: 伤官格成
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 3. PZZQ-GEJU-005-A
```
Assertion: 印轻逢煞 → 印格成

Evidence Span (PZZQ 论印绶格):
"印轻逢煞，或官印双全，或身印两旺而用食伤泄气...印格成也"

主体核对:
- Evidence: 印轻逢煞
- Assertion: 印轻逢煞
- ✅ 主体一致！

结论核对:
- Evidence: 印格成也
- Assertion: 印格成
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 4. PZZQ-GEJU-005-B
```
Assertion: 官印双全 → 印格成

Evidence Span (PZZQ 论印绶格):
"印轻逢煞，或官印双全...印格成也"

主体核对:
- Evidence: 官印双全
- Assertion: 官印双全
- ✅ 主体一致！

结论核对:
- Evidence: 印格成也
- Assertion: 印格成
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 5. PZZQ-GEJU-005-C
```
Assertion: 身印两旺而用食伤泄气 → 印格成

Evidence Span (PZZQ 论印绶格):
"印轻逢煞，或官印双全，或身印两旺而用食伤泄气...印格成也"

主体核对:
- Evidence: 身印两旺而用食伤泄气
- Assertion: 身印两旺而用食伤泄气
- ✅ 主体一致！

结论核对:
- Evidence: 印格成也
- Assertion: 印格成
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 6. PZZQ-GEJU-006-A
```
Assertion: 财生官旺 → 财格成

Evidence Span (PZZQ 论财格):
"财生官旺，或财逢食生而身强带比...财格成也"

主体核对:
- Evidence: 财生官旺
- Assertion: 财生官旺
- ✅ 主体一致！

结论核对:
- Evidence: 财格成也
- Assertion: 财格成
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 7. PZZQ-GEJU-006-B
```
Assertion: 财逢食生而身强带比 → 财格成

Evidence Span (PZZQ 论财格):
"财生官旺，或财逢食生而身强带比...财格成也"

主体核对:
- Evidence: 财逢食生而身强带比
- Assertion: 财逢食生而身强带比
- ✅ 主体一致！

结论核对:
- Evidence: 财格成也
- Assertion: 财格成
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 8. PZZQ-GEJU-007
```
Assertion: 阳刃透官煞而露财印，不见伤官 → 阳刃格成

Evidence Span (PZZQ 论阳刃格):
"阳刃透官煞而露财印，不见伤官，阳刃格成也"

主体核对:
- Evidence: 阳刃透官煞而露财印，不见伤官
- Assertion: 阳刃透官煞而露财印，不见伤官
- ✅ 主体一致！

结论核对:
- Evidence: 阳刃格成也
- Assertion: 阳刃格成
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 9. PZZQ-GEJU-008-A
```
Assertion: 透官而逢财印 → 建禄月劫格成

Evidence Span (PZZQ 论建禄月劫格):
"建禄月劫，透官而逢财印，透财而逢食伤，透煞而遇制伏，建禄月劫之格成也"

主体核对:
- Evidence: 透官而逢财印
- Assertion: 透官而逢财印
- ✅ 主体一致！

结论核对:
- Evidence: 建禄月劫之格成也
- Assertion: 建禄月劫格成
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 10. PZZQ-GEJU-008-B
```
Assertion: 透财而逢食伤 → 建禄月劫格成

Evidence Span (PZZQ 论建禄月劫格):
"建禄月劫，透官而逢财印，透财而逢食伤，透煞而遇制伏，建禄月劫之格成也"

主体核对:
- Evidence: 透财而逢食伤
- Assertion: 透财而逢食伤
- ✅ 主体一致！

结论核对:
- Evidence: 建禄月劫之格成也
- Assertion: 建禄月劫格成
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 11. PZZQ-GEJU-008-C
```
Assertion: 透煞而遇制伏 → 建禄月劫格成

Evidence Span (PZZQ 论建禄月劫格):
"建禄月劫，透官而逢财印，透财而逢食伤，透煞而遇制伏，建禄月劫之格成也"

主体核对:
- Evidence: 透煞而遇制伏
- Assertion: 透煞而遇制伏
- ✅ 主体一致！

结论核对:
- Evidence: 建禄月劫之格成也
- Assertion: 建禄月劫格成
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

### YHZP岁君关系（5条）

#### 12. YHZP-SUIJUN-002-A
```
Assertion: 日犯岁君 → 灾殃必重

Evidence Span (YHZP 论岁君):
"日犯岁君，灾殃必重；五行有救，其年反必招财"

主体核对:
- Evidence: 日犯岁君
- Assertion: 日犯岁君
- ✅ 主体一致！

结论核对:
- Evidence: 灾殃必重
- Assertion: 灾殃必重
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 13. YHZP-SUIJUN-002-B
```
Assertion: 日犯岁君 + 五行有救 → 其年反必为财

Evidence Span (YHZP 论岁君):
"日犯岁君，灾殃必重；五行有救，其年反必招财"

主体核对:
- Evidence: 日犯岁君 + 五行有救
- Assertion: 日犯岁君 + 五行有救
- ✅ 主体一致！

结论核对:
- Evidence: 其年反必招财
- Assertion: 其年反必为财
- ✅ 结论一致！（"招财"≈"为财"）

裁决: COMPLETE ✅
```

---

#### 14. YHZP-SUIJUN-003-A
```
Assertion: 犯岁君者 → 其年必主凶丧

Evidence Span (YHZP 论岁君):
"犯岁君者，其年必主凶丧、剋妻妾及破财是非、犯上之悔"

主体核对:
- Evidence: 犯岁君者
- Assertion: 犯岁君者
- ✅ 主体一致！

结论核对:
- Evidence: 其年必主凶丧
- Assertion: 其年必主凶丧
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 15. YHZP-SUIJUN-003-B
```
Assertion: 犯岁君者 → 剋妻妾

Evidence Span (YHZP 论岁君):
"犯岁君者，其年必主凶丧、剋妻妾及破财是非、犯上之悔"

主体核对:
- Evidence: 犯岁君者
- Assertion: 犯岁君者
- ✅ 主体一致！

结论核对:
- Evidence: 剋妻妾
- Assertion: 剋妻妾
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

#### 16. YHZP-SUIJUN-003-C
```
Assertion: 犯岁君者 → 破财是非

Evidence Span (YHZP 论岁君):
"犯岁君者，其年必主凶丧、剋妻妾及破财是非、犯上之悔"

主体核对:
- Evidence: 犯岁君者
- Assertion: 犯岁君者
- ✅ 主体一致！

结论核对:
- Evidence: 破财是非
- Assertion: 破财是非
- ✅ 结论一致！

裁决: COMPLETE ✅
```

---

## 审计统计

### REJECT（主体错位）
```
PZZQ-GEJU-004-A: REJECT
原因: 主体错位（食神→伤官）
证据: "食神生财，食格成也"
Assertion: "伤官生财 → 伤官格成"
```

### COMPLETE（主体一致）
```
PZZQ-GEJU-004-B: COMPLETE ✅
PZZQ-GEJU-005-A: COMPLETE ✅
PZZQ-GEJU-005-B: COMPLETE ✅
PZZQ-GEJU-005-C: COMPLETE ✅
PZZQ-GEJU-006-A: COMPLETE ✅
PZZQ-GEJU-006-B: COMPLETE ✅
PZZQ-GEJU-007: COMPLETE ✅
PZZQ-GEJU-008-A: COMPLETE ✅
PZZQ-GEJU-008-B: COMPLETE ✅
PZZQ-GEJU-008-C: COMPLETE ✅
YHZP-SUIJUN-002-A: COMPLETE ✅
YHZP-SUIJUN-002-B: COMPLETE ✅
YHZP-SUIJUN-003-A: COMPLETE ✅
YHZP-SUIJUN-003-B: COMPLETE ✅
YHZP-SUIJUN-003-C: COMPLETE ✅
```

### 统计
- 总裁决: 16条
- COMPLETE: 15条（93.75%）
- REJECT: 1条（6.25%）

---

## 关键发现

### 问题根源
PZZQ-GEJU-004-A的Evidence来自"论食神格"，原典写的是"食神生财，食格成也"，但Assertion写成了"伤官生财 → 伤官格成"。

这是典型的：
- 证据来源错误（食神格→伤官格）
- 主体替换（食神→伤官）
- 结论替换（食格→伤官格）

### 教训
1. 必须严格核对原典章节名
2. 必须核对Evidence Span中的十神名称
3. 不能假设"食神"和"伤官"可以互换
4. 原典证据必须与Assertion主体完全一致

---

## 资产库更新

### 最终COMPLETE资产（15条）
```
PZZQ-GEJU-004-B, PZZQ-GEJU-005-A/B/C, 
PZZQ-GEJU-006-A/B, PZZQ-GEJU-007,
PZZQ-GEJU-008-A/B/C,
YHZP-SUIJUN-002-A/B,
YHZP-SUIJUN-003-A/B/C
```

### 移出资产（1条）
```
PZZQ-GEJU-004-A: REJECT（主体错位：食神→伤官）
```

---

## 下一步

1. 修正M2_VERIFICATION_REPORT.md，标记PZZQ-GEJU-004-A为REJECT
2. 建立主体核对检查点，防止后续再出现类似问题
3. 等待GPT对审计报告和修正后资产的裁决

---

**状态**: 一致性审计完成，15条COMPLETE + 1条REJECT
