# Schema v2.0 迁移验证报告

**验证时间**: 2026-09-02  
**基线Commit**: `edc14a3`

---

## 验证结果

### ✅ PASSED - Schema v2.0迁移完成

```
总Evidence:      74条
已迁移:          74条 (100%)
迁移错误:        0条

状态统计:
  VERIFIED:       0条
  PENDING:       72条
  REJECTED:       2条 (A层)
```

---

## Schema v2.0 结构

```json
{
  "source_excerpt": "",           // 原文逐字摘录 (EMPTY until VERIFIED)
  "normalized_summary": "...",    // 整理摘要 (原original_text)
  "source_verification": {
    "status": "PENDING",
    "comparison_result": null,
    "locator": null
  }
}
```

---

## 迁移规则

| 旧字段 | 新字段 | 说明 |
|--------|--------|------|
| `original_text` | `normalized_summary` | 现代整理版摘要 |
| (新增) | `source_excerpt` | 原文逐字摘录（空） |

---

## VERIFIED 标准

```
source_fidelity = VERIFIED 当且仅当:
  1. source_excerpt ≠ ""
  2. comparison_result = "VERBATIM_MATCH"
  3. locator 完整（页码/章节）
  4. source_url 指向可复核的原文
```

---

## 下一步

继续72条Active Evidence的逐条Source Verification。
