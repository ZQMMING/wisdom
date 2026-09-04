# Evidence Status Ladder

**创建时间**: 2026-07-20
**版本**: v1.0
**目的**: 明确区分"来源核验完成"与"生产权威认证"

---

## 状态定义

### Layer 1: Source Verification（来源核验）
```text
source_verification.status = VERIFIED
verification_method = semantic_comparison
```
**含义**: 已完成来源比对，确认 Evidence 与所标来源存在语义对应关系。

**不意味着**: Production Authority

---

### Layer 2: Authority Status（权威状态）
```text
authority_status = SEMANTIC_MATCHED
```
**含义**: Evidence 已通过来源核验，达到语义匹配标准，但尚未获得生产准入。

**使用场景**:
- Engine 可使用进行结构识别
- Signal 生成层可引用
- Assertion 层需额外审核

---

### Layer 3: Production Admissibility（生产准入）
```text
authority_status = PRODUCTION_ADMITTED
verifier = Human Expert
verification_method = verbatim_comparison
```
**含义**: 已通过人类专家签字确认，可产生生产断言。

**要求**:
1. 获取纸质书籍或权威出版物
2. 逐字比对原文与 Evidence
3. Human Expert 签字确认
4. 记录签字人和日期

---

## 完整状态转移图

```text
UNVERIFIED
    ↓
    ↓ semantic_comparison
    ↓
SEMANTIC_MATCHED ←── 当前所有盲派证据的状态
    ↓
    ↓ Human Expert Sign-off
    ↓
PRODUCTION_ADMITTED
    ↓
    ↓ Assertion Layer
    ↓
JUDGMENT
```

---

## 字段语义澄清

### `source_verification.status`
```json
{
  "status": "VERIFIED",
  "reason": "SEMANTIC_MATCH",
  "detail": "Evidence为现代整理版，与原文核心概念语义一致",
  "verification_method": "semantic_comparison"
}
```
**含义**: 来源核验已完成，但仅为语义匹配。

---

### `authority_status`
```json
{
  "authority_status": "SEMANTIC_MATCHED"
}
```
**含义**: 已达到语义匹配标准，但未获得生产准入。

---

### `source_fidelity`
```json
{
  "source_fidelity": "SEMANTIC_MATCH"
}
```
**含义**: 与来源的文本保真度为语义匹配（非逐字）。

---

## 关键规则

### 规则 1: SEMANTIC_MATCHED ≠ PRODUCTION_ADMITTED
```
❌ 禁止: authority_status = SEMANTIC_MATCHED → 直接产生 Judgment
✅ 允许: authority_status = SEMANTIC_MATCHED → 用于 Engine 结构识别
```

### 规则 2: 来源状态标注
```json
{
  "source": {
    "title": "段建业《盲派初级命理学》",
    "status": "CANDIDATE"  // ← 应继续保留，表示"候选权威来源"
  }
}
```

### 规则 3: 验证方法区分
| 方法 | 对应状态 | 要求 |
|------|---------|------|
| `semantic_comparison` | SEMANTIC_MATCHED | 网络检索 + 语义比对 |
| `verbatim_comparison` | PRODUCTION_ADMITTED | 纸质书籍 + 逐字比对 + 人工签字 |

---

## 当前盲派证据状态

```text
SEMANTIC_MATCHED: 74 files ✅
PENDING_REVIEW:   2 files ⏳ (fix-record audit logs)
Total:            76 files
```

**所有证据已到达 Layer 2，尚未到达 Layer 3。**

---

## 生产准入检查清单

在将 `SEMANTIC_MATCHED` 升级为 `PRODUCTION_ADMITTED` 之前，必须满足：

- [ ] 获取纸质书籍或权威出版物
- [ ] 逐字比对原文与 Evidence 的 `source_excerpt`
- [ ] 确认 `source_excerpt` 来自 `normalized_summary` 的真实摘录
- [ ] Human Expert 签字确认
- [ ] 记录签字人、日期、书籍版本

---

**维护者**: Hermes Agent (Agnes) + Human Expert Review Board
**下次更新**: 当第一个 PRODUCTION_ADMITTED 证据产生时
