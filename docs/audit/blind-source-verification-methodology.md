# 盲派辨Evidence来源核验方法论

**创建时间**: 2026-09-02  
**基线Commit**: `53c390c`

---

## 核心问题

经过对13条Evidence的实际核验，发现以下模式：

### 问题1: Evidence多为整理版
```
Evidence original_text
    ↓
后人整理的核心概念
    ↓
与段建业原文"语义一致"
    ↓
但不是"逐字匹配"
```

### 问题2: 无法升VERIFIED
```
VERIFIED标准 = 原文逐字匹配 + 完整定位
                              ↓
Evidence为整理版 ≠ 原文摘录
                              ↓
不能声称 verbatim_comparison
```

---

## 核验流程

### Step 1: 查找候选来源原文
- 使用web_search搜索候选来源
- 优先找：pdfcoffee、算准网、国学资源网
- 记录来源URL和性质（正式出版/内部讲义/网页整理）

### Step 2: 比对原文
```python
# 检查original_text与verified_text的关系
if original_text == verified_text:
    status = "VERIFIED"
    method = "verbatim_comparison"
elif semantic_match(original_text, verified_text):
    status = "PENDING"  # 或 SEMANTIC_MATCHED
    method = "semantic_comparison"
else:
    status = "REJECTED"
    reason = "SOURCE_MISMATCH"
```

### Step 3: 更新Evidence文件
**必须修改Evidence JSON文件本身**，不能只在报告里写文字。

```json
{
  "source_verification": {
    "status": "PENDING",
    "reason": "SEMANTIC_MATCH_ONLY",
    "detail": "Evidence为整理版，与来源原文核心概念一致但表述不同",
    "verification_method": "semantic_comparison"
  },
  "source_fidelity": "PENDING_VERIFICATION"
}
```

### Step 4: 更新Manifest
从Evidence文件实时计算统计，不要手动写数字。

---

## VERIFIED标准（严格版）

要升VERIFIED，必须满足：

1. ✅ 找到候选来源的**完整原文**
2. ✅ Evidence的 `original_text` 与原文**逐字一致**
3. ✅ 有明确的**页码/章节/稳定locator**
4. ✅ `verification_method = verbatim_comparison`
5. ✅ `source_fidelity = VERIFIED`

**如果Evidence是整理版，不能升VERIFIED。**

---

## PENDING状态说明

以下情况应标记为PENDING：

| 情况 | reason |
|------|--------|
| 原文未找到 | SOURCE_UNVERIFIED |
| 原文找到但表述不同 | SEMANTIC_MATCH_ONLY |
| 疑似AI生成/现代总结 | MODERN_SUMMARY |
| 来源不可信 | SOURCE_UNTRUSTED |

---

## REJECTED标准

以下情况应标记为REJECTED：

1. 无法找到任何候选来源
2. Evidence内容与来源原文严重不符
3. 疑似后人伪造或错误归源
4. 原始文本过度现代化（疑似AI生成）

---

## 当前核验进度

| Topic | 总数 | VERIFIED | PENDING | REJECTED |
|-------|------|----------|---------|----------|
| BODY_USE_RELATION | 6 | 0 | 5 | 1 |
| EMPTY_USELESS | 6 | 0 | 6 | 0 |
| A层（夏仲奇遗例） | 2 | 0 | 0 | 2 |
| **其他B层** | 45 | 0 | 45 | 0 |
| **C层案例** | 15 | 0 | 15 | 0 |
| **总计** | **74** | **0** | **72** | **2** |

---

## 待决策问题

### Q1: VERIFIED标准是什么？
- **选项A**: 接受semantic match（语义一致即可）
- **选项B**: 要求verbatim match（逐字匹配）
- **选项C**: 创建新字段区分"原文摘录"与"整理摘要"

### Q2: Evidence Schema是否需要重构？
当前 `original_text` 同时承担"原文摘录"和"整理摘要"两个语义，建议拆分：
- `original_excerpt` — 原文逐字摘录
- `normalized_summary` — 整理版摘要

---

## 参考资源

- 《盲派初级命理学》- 段建业（99页PDF）
  - 来源: https://www.guoxueziyuan.com/1215.html
  - 目录结构已确认
- 《盲派理象学》- 段建业（48页）
  - 来源: https://www.guoxueziyuan.com/1215.html
- 《段氏理象学》- ISBN 9787504474575
  - 出版社: 中国商业出版社，2011年

---

**核验人**: Hermes Agent  
**状态**: 等待用户决策核验标准
