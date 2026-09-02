# 盲派辨Evidence来源核验报告 (第七轮)

**核验时间**: 2026-09-02  
**基线Commit**: `8ff3555`  
**核验范围**: B层EMPTY_USELESS系列 + 核验方法论

---

## 执行摘要

### 当前状态
```
总证据:       74条
Active:       72条
├─ VERIFIED:    0条
├─ PENDING:    72条
└─ REJECTED:    2条 (A层)
```

### 本次核验
- EMPTY_USELESS系列: 6条已分析，全部标记PENDING
- 原因: Evidence为整理版，与原文概念一致但表述不同

---

## 已获取原文资源

### 《盲派初级命理学》- 段建业
- **来源**: https://www.guoxueziyuan.com/1215.html
- **性质**: 内部培训讲义，99页，0.6MB
- **目录结构**:
  - 第一章 盲派命理体系介绍
    - 第二节 盲师派命理体系的特点
      - 一、宾主的概念 (p.1)
      - 二、"体用"的概念 (p.2)
      - 三、功神、废神概念 (p.9)
      - 四、能量与效率概念
      - 五、贼神捕神的概念
      - 六、象

---

## EMPTY_USELESS系列核验详情

### E-BLIND-EMPTY_USELESS-001
- **主题**: EMPTY_USELESS
- **原文**: "虚是指天干没有根气，实是指天干有根气。虚神无用，实神有用..."
- **核验结果**: ⚠️ 疑似整理版总结，非原始文献
- **状态**: PENDING
- **说明**: 概念与原文一致，但原文表述为"功神/废神"，此条使用"虚神/实神"术语，需进一步确认

### E-BLIND-EMPTY_USELESS-002
- **主题**: EMPTY_USELESS
- **原文**: "虚是指无用之神，实是指有用之神。虚神虽然存在但不起作用..."
- **核验结果**: ⚠️ 疑似整理版总结
- **状态**: PENDING
- **说明**: 语义与原文一致，但表述为现代总结风格

### E-BLIND-EMPTY_USELESS-003 ~ 006
- **主题**: EMPTY_USELESS
- **状态**: 全部PENDING
- **说明**: 均为段落式总结，非原始文献直接引用

---

## 核验方法论总结

### 问题发现
经过对BODY_USE_RELATION和EMPTY_USELESS系列的核验，发现以下模式：

1. **Evidence多为整理版**: 74条Evidence中，绝大多数是后人整理的核心概念，非原始文献逐字摘录
2. **无法逐字匹配**: Evidence原文与段建业原文只是"语义一致"，不是"逐字相同"
3. **术语差异**: 部分Evidence使用整理后的术语（如"虚神/实神"），原文使用原始术语（如"功神/废神"）

### 核心矛盾
```text
E evidence original_text
    ↓
整理版（现代人总结）

≠

来源原文
    ↓
原始文献（段建业著作）
```

---

## 等待用户决策

### 选项A: 调整VERIFIED标准
- 接受"语义一致"作为VERIFIED条件
- 创建`source_excerpt`字段存放原文摘录
- Evidence的`original_text`保持整理版

### 选项B: 保持严格标准
- 要求Evidence的`original_text`必须与来源原文逐字匹配
- 如果无法匹配，标记为PENDING或REJECTED
- 继续寻找原始文献摘录

### 选项C: 重构Evidence Schema
- 创建新的字段区分"原文摘录"与"整理摘要"
- 例如: `original_excerp`（原文摘录）+ `normalized_summary`（整理摘要）
- 允许同一Evidence有多个版本

---

## 建议

基于当前核验结果，建议：

1. **暂停批量升级VERIFIED**: 在Schema未明确前，不升任何Evidence为VERIFIED
2. **用户决策**: 等待用户对核验标准做出明确指示
3. **继续核验**: 对剩余59条Evidence进行抽样核验，记录核验结果

---

**核验人**: Hermes Agent  
**状态**: EMPTY_USELESS核验完成，等待用户决策
