# 🔴 P0 紧急审计：子平引擎证据系统断裂

**审计时间**: 2026-09-06 17:30  
**审计人**: Hermes (顺天总调度Agent)  
**严重级别**: 🔴 P0-CRITICAL - 系统不可用

---

## 核心发现：证据系统断裂

### 问题描述

`D:/shuntian/src/tongshu/engines/bazi_engine.py` 引用了 **9个证据ID**，但这些证据文件**根本不存在**。

```python
# 代码中的引用（第56-153行）
STEM_HE_evidence_id = "E-DTS-144-001"      # ❌ 不存在
BRANCH_CLASH_evidence_id = "E-YHZP-002-001" # ❌ 不存在
BRANCH_HARM_evidence_id = "E-YHZP-003-001"  # ❌ 不存在
PEACH_BLOSSOM_evidence_id = "E-YHZP-004-001"# ❌ 不存在
BRANCH_HE_evidence_id = "E-YHZP-005-001"    # ❌ 不存在
BRANCH_SANHE_evidence_id = "E-YHZP-006-001" # ❌ 不存在
BRANCH_SANHUI_evidence_id = "E-DTS-145-001" # ❌ 不存在
BRANCH_SANXING_evidence_id = "E-YHZP-007-001"# ❌ 不存在
KONG_WANG_evidence_id = "E-YHZP-008-001"    # ❌ 不存在
```

### 证据库现状

```
✅ 存在的证据文件: 86个
❌ 缺失的证据文件: 9个（全部是代码引用的基础规则）
```

**缺失文件列表**:
```
E-DTS-144-001  # 十干之合（滴天髓）
E-DTS-145-001  # 三会局方位五行（滴天髓）
E-YHZP-002-001 # 十二地支相冲（渊海子平）
E-YHZP-003-001 # 十二地支相穿（渊海子平）
E-YHZP-004-001 # 桃花咸池查法（渊海子平）
E-YHZP-005-001 # 地支六合（渊海子平）
E-YHZP-006-001 # 地支三合（渊海子平）
E-YHZP-007-001 # 地支三刑（渊海子平）
E-YHZP-008-001 # 空亡旬表（渊海子平）
```

### 影响评估

1. **证据链断裂**: 所有基础规则（冲、害、合、刑、空亡）都无法通过证据系统验证
2. **权威性问题**: 虽然算法正确，但无法证明其经典出处
3. **系统风险**: 如果审计系统检查证据完整性，整个引擎会被标记为"未验证"

---

## 代码对比分析

### D:/shuntian（当前主仓库）

**优点**:
- ✅ 修复了日支冲/害的位置过滤bug（按位置排除而非按值过滤）
- ✅ 支持分钟/秒级时间精度
- ✅ 精确处理节气边界（立春、月柱切换）
- ✅ 使用真太阳时
- ✅ FAIL-CLOSED机制（sxtwl不可用时直接报错）
- ✅ 计算10个大运
- ✅ 有证据ID标记（但文件缺失）

**缺点**:
- ❌ 证据文件缺失（9个核心文件）
- ❌ 证据系统是空壳（有ID无内容）

### D:/shuntian-NEW（已停用）

**优点**:
- ✅ 代码简洁
- ✅ 有fallback机制（不报错）

**缺点**:
- ❌ 丢失分钟/秒级精度
- ❌ 丢失节气边界精确处理
- ❌ 只计算3个大运（错误）
- ❌ 日支冲/害按值过滤（会漏判）
- ❌ 完全无证据系统
- ❌ 静默返回错误数据

---

## 紧急修复方案

### 方案A：补全证据文件（推荐）

创建9个缺失的证据文件：

```json
// E-YHZP-002-001.json
{
  "evidence_id": "E-YHZP-002-001",
  "rule_refs": ["YHZP-002"],
  "citation": {
    "original_text": "(待校,paraphrase)十二地支相冲：子午冲、丑未冲、寅申冲、卯酉冲、辰戌冲、巳亥冲。渊海子平·卷一·论地支相冲。",
    "language": "vernacular_chinese",
    "verification_status": "pending_verification"
  },
  "modern_paraphrase": "《渊海子平》六冲定式：子午、丑未、寅申、卯酉、辰戌、巳亥。六组对冲关系。",
  "evidence_strength": "primary",
  "source_locator": {
    "work": "渊海子平",
    "edition": "通行本",
    "chapter": "卷一·论地支"
  }
}
```

需要创建的文件：
1. E-DTS-144-001.json（十干之合）
2. E-DTS-145-001.json（三会局）
3. E-YHZP-002-001.json（六冲）
4. E-YHZP-003-001.json（六害）
5. E-YHZP-004-001.json（桃花）
6. E-YHZP-005-001.json（六合）
7. E-YHZP-006-001.json（三合）
8. E-YHZP-007-001.json（三刑）
9. E-YHZP-008-001.json（空亡）

### 方案B：移除证据ID标记

如果暂时无法补全证据文件，可以：
```python
# 移除这些标记，直到证据文件就绪
# STEM_HE_evidence_id = "E-DTS-144-001"  # 注释掉
```

但这只是权宜之计，不符合顺天项目的证据优先原则。

---

## 建议行动

### 立即执行（P0）

1. **验证证据加载逻辑**
   ```bash
   python -c "from tongshu.audit.evidence_loader import EvidenceLoader; print(EvidenceLoader.load_all())"
   ```
   确认是否会有报错或警告。

2. **运行测试套件**
   ```bash
   cd D:/shuntian && python -m pytest tests/ -v
   ```

3. **创建缺失的9个证据文件**（按方案A的模板）

### 架构决策

**我的建议**: 采用**方案A**（补全证据文件），因为：
1. 符合顺天项目的"证据优先"原则
2. D:/shuntian的代码质量优于D:/shuntian-NEW
3. 证据文件补全是机械性工作，风险可控

---

## 等待用户裁决

1. 是否需要我立即创建9个缺失的证据文件？
2. 是否需要我先验证证据加载逻辑是否会报错？
3. 是否确认以D:/shuntian为主，放弃D:/shuntian-NEW？

---

**审计人**: Hermes Agent  
**日期**: 2026-09-06  
**状态**: 🔴 等待用户决策 - 证据系统断裂需立即修复
