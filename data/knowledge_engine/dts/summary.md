# DTS（滴天髓）SourceRegistry + RuleRegistry 候选 · 摘要

## 数量
- Sources：604（ORIGINAL 136 / ANNOTATION 275 / LATER_COMMENTARY 192 / UNVERIFIED 1）
- Rules：66（CAND-DTS-001 起连续编号）
- Unformalizable：86（韵文宇宙论铺垫，无干净 IF-THEN）

## 章节覆盖
65 章全量录入（天道…贞元）。

## text_layer 分布
见上。Rule 仅来自 ORIGINAL。

## Rule 类型侧重
按 DTS 特性，以 resolution（格局/从象/化象取舍）与 effectiveness（旺衰/根气/气势对结论的影响）为主，辅以 definition/diagnosis/medicine。

## 抽样 Rule（3 条，原文对照）
### CAND-DTS-001（源 DTS-009-001，definition）
```json
{"rule_id": "CAND-DTS-001", "engine": "DI_TIAN_SUI", "source_id": "DTS-009-001", "rule_type": "definition", "scope": "natal", "subject": "stem", "predicate": "is", "preconditions": {"type": "conjunction", "conditions": [{"field": "stem", "operator": "equals", "value": "丙"}]}, "operation": "emit", "outputs": [{"field": "stem_yinyang", "value": "阳至极"}], "evidence_requirement": "A", "status": "CANDIDATE", "notes": "五阳皆阳丙为最"}
```
原文：天干第九页《滴天髓阐微》上篇第07章天干五阳皆阳丙为最，五阴皆阴癸为至。

### CAND-DTS-034（源 DTS-027-001，effectiveness）
```json
{"rule_id": "CAND-DTS-034", "engine": "DI_TIAN_SUI", "source_id": "DTS-027-001", "rule_type": "effectiveness", "scope": "natal", "subject": "zhen_shen", "predicate": "result", "preconditions": {"type": "conjunction", "conditions": [{"field": "zhen_shen", "operator": "equals", "value": "得用"}]}, "operation": "emit", "outputs": [{"field": "result", "value": "生平贵"}], "evidence_requirement": "B", "status": "CANDIDATE", "notes": "真神得用生平贵"}
```
原文：真神第二十七页《滴天髓阐微》上篇第25章真神令上寻其聚得真，假神休要乱真神，真神得用生平贵，用若无为碌碌人。

### CAND-DTS-043（源 DTS-041-010，diagnosis）
```json
{"rule_id": "CAND-DTS-043", "engine": "DI_TIAN_SUI", "source_id": "DTS-041-010", "rule_type": "diagnosis", "scope": "natal", "subject": "guan", "predicate": "sign", "preconditions": {"type": "conjunction", "conditions": [{"field": "guan", "operator": "equals", "value": "不见"}]}, "operation": "emit", "outputs": [{"field": "sign", "value": "贱"}], "evidence_requirement": "A", "status": "CANDIDATE", "notes": "何知其人贱官星还不见"}
```
原文：何知其人贱？官星还不见。


## 说明
- 只落盘未 commit；未动 `D:\shuntian\data\classics\original\`。
- 未改原著一字、未评分、未跨经典优先级、未统一用神。
