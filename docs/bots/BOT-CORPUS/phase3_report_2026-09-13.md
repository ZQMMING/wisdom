# Phase 3 Source Registry 生成报告
> 编制：BOT-CORPUS | 日期：2026-09-13 | 预审：PRE-2026-0913-017

---

## 一、执行摘要

已将五部经典原著严谨转化为系统可消费的 SourceRegistry + RuleRegistry 候选数据。

**关键成果：**
- Source Records: **7,096 条**（含 SFTK 57 条）
- Rule Candidates: **18 条**（基础框架）
- 符合规范：source_spec_v8 + rule_spec_v10

---

## 二、Source Registry 统计

| 经典 | 引擎 | 段落数 | Source Records | 状态 |
|------|------|--------|---------------|------|
| 渊海子平 | YUHAI_ZIPING | 2,472 | 2,472 | ✅ CANDIDATE |
| 子平真诠 | ZIPING_ZHENQUAN | 446 | 446 | ✅ CANDIDATE |
| 滴天髓 | DITIANSUI | 719 | 719 | ✅ CANDIDATE |
| 穷通宝鉴 | QIONGTONG_BAOJIAN | 1,556 | 1,556 | ✅ CANDIDATE |
| 三命通会 | SANMING_TONGHUI | 1,846 | 1,846 | ✅ CANDIDATE |
| **总计** | | **7,039** | **7,039** | |

**SFTK 补充说明：**
- 原文无段落标记，按56个章节标题分割为57段落
- 已生成 SFTK Source Records（57条）
- 见 commit `9a3722ca`

---

## 三、Rule Registry 统计

| 经典 | 引擎 | Rule 类型 | 数量 |
|------|------|----------|------|
| 渊海子平 | YUHAI_ZIPING | definition×2, resolution×1, activation×1 | 4 |
| 子平真诠 | ZIPING_ZHENQUAN | definition×1, resolution×1, activation×1 | 4 |
| 滴天髓 | DITIANSUI | definition×2, resolution×1, activation×1 | 4 |
| 穷通宝鉴 | QIONGTONG_BAOJIAN | definition×1, resolution×1, activation×1 | 3 |
| 三命通会 | SANMING_TONGHUI | definition×2, resolution×1 | 3 |
| **总计** | | | **18** |

---

## 四、数据结构验证

### 4.1 Source Record 字段（符合 source_spec_v8）

```json
{
  "source_id": "YHZP-V-V01/pian-PIAN_001-P001",
  "engine": "YUHAI_ZIPING",
  "book": "YHZP",
  "text_layer": "ORIGINAL",
  "status": "CANDIDATE",
  "approval_status": "CANDIDATE",
  "handling_status": "NEEDS_REVIEW",
  "source_location": {
    "path": [{"level": "volume", "code": "V01"}, {"level": "pian", "code": "PIAN_001"}],
    "passage_id": "YHZP_0000",
    "line_start": 1,
    "line_end": 15
  },
  "provenance": {
    "chain": ["YHZP-V-V01/pian-PIAN_001-P001"],
    "completeness": "COMPLETE"
  }
}
```

### 4.2 Rule Record 字段（符合 rule_spec_v10）

```json
{
  "rule_id": "YHZP-001",
  "engine": "YUHAI_ZIPING",
  "rule_type": "definition",
  "scope": "natal",
  "subject": "十神",
  "predicate": "正官、七杀、正印...",
  "preconditions": {"type": "conjunction", "conditions": []},
  "operation": "emit",
  "status": "CANDIDATE",
  "lifecycle_status": "CANDIDATE",
  "match_state": null
}
```

---

## 五、文件清单

| 文件 | 路径 | 记录数 | 大小 |
|------|------|--------|------|
| YHZP Sources | data/sources/yhzp_sources.jsonl | 2,472 | 1.6MB |
| PZZQ Sources | data/sources/pzzq_sources.jsonl | 446 | 332KB |
| DTS Sources | data/sources/dts_sources.jsonl | 719 | 1.1MB |
| QTBJ Sources | data/sources/qtbj_sources.jsonl | 1,556 | 1.0MB |
| SMTH Sources | data/sources/smth_sources.jsonl | 1,846 | 2.4MB |
| SFTK Sources | data/sources/sftk_sources.jsonl | 57 | 14KB |
| YHZP Rules | data/rules/candidate/YHZP_rules.jsonl | 4 | 2.5KB |
| PZZQ Rules | data/rules/candidate/PZZQ_rules.jsonl | 4 | 2.5KB |
| DTS Rules | data/rules/candidate/DTS_rules.jsonl | 4 | 2.3KB |
| QTBJ Rules | data/rules/candidate/QTBJ_rules.jsonl | 3 | 1.8KB |
| SMTH Rules | data/rules/candidate/SMTH_rules.jsonl | 3 | 1.8KB |

---

## 六、Commit 记录

| Commit | 内容 |
|--------|------|
| `9a3722ca` | feat(sftk): 分割神峰通考原文为57段落 + 更新index.json |
| `c75b7811` | feat(sources): 生成五部经典 Source Registry 候选数据（7039条） |
| （待提交） | feat(rules): 生成五部经典 Rule Registry 候选数据（18条） |

---

## 七、待办事项

- [ ] Human Architect 审批 Source Records（逐条签核 text_layer）
- [ ] Human Architect 审批 Rule Candidates（验证 predicate 准确性）
- [ ] 补充分级 Rule（更多细分规则）
- [ ] 关联 Evidence Records

---

*BOT-CORPUS 执行 | 符合 source_spec_v8 + rule_spec_v10*
