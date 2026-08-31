# M3 Phase 3.1 滴天髓格局生产 - 第1批（5条）

**时间**: 2026-08-31  
**批次**: 第1批（共4批）  
**断言范围**: DTS-GEJU-001 ~ 005  
**状态**: 🟢 生产中

---

## 用户裁决关键约束（必须遵守）

### 约束1: 禁止大Condition
❌ 不能把"格局判断"工程化成一个大Condition  
✅ 必须拆分为：原典→Evidence→Primitive A/B/C→Condition A/B/C→Local Judgment→Composite

### 约束2: Composite必须有原典授权
❌ 不能工程推断 "A+B+C ⇒ 成格"  
✅ 必须证明原典明确说："若A且B则成格"

### 约束3: 验收标准升级
pytest PASS只是最后一道门，不是命理正确性的证明。  
每条必须同时证明：
- 原典是真的这样说
- Primitive没有扩大语义
- Condition能从Canonical State得出
- Evaluator没有偷偷重新计算命理
- Judgment没有超过原典授权
- 输出可追溯

---

## 第1批断言范围

| ID | 断言主题 | 原典章节 | Primitive拆分 |
|----|---------|---------|--------------|
| DTS-GEJU-001 | 月令透干成格 | 通神论·衰旺 | A:月令主气 B:天干透出 C:生扶关系 |
| DTS-GEJU-002 | 日主有根成格 | 通神论·地支 | A:日支本气 B:通根深浅 C:根气类型 |
| DTS-GEJU-003 | 合化成功条件 | 通神论·合化 | A:天干相合 B:地支引化 C:月令支持 |
| DTS-GEJU-004 | 破格救应机制 | 通神论·救应 | A:格局破损 B:救应存在 C:救应有效 |
| DTS-GEJU-005 | 从格成立条件 | 通神论·从格 | A:日主无根 B:克泄耗势 C:无解救 |

---

## 生产流程（修正版）

```
【STEP 1】原典定位（已完成）
  ↓
  已定位：滴天髓·通神论相关章节
  已提取：6条Evidence（E-DTS-101~107）
  状态：待逐字核验（verification_status=pending_verification）

【STEP 2】Evidence分层（进行中）
  ↓
  原文层 (ORIGINAL_TEXT) - 待核验
  注释层 (ORIGINAL_COMMENTARY) - 任铁樵注
  后世层 (LATER_COMMENTARY) - 现代整理

【STEP 3】Primitive拆分（核心！）
  ↓
  DTS-GEJU-001: Primitive A/B/C
  DTS-GEJU-002: Primitive A/B/C
  DTS-GEJU-003: Primitive A/B/C
  DTS-GEJU-004: Primitive A/B/C
  DTS-GEJU-005: Primitive A/B/C

【STEP 4】Condition拆分（核心！）
  ↓
  每个Primitive对应一个Condition Evaluator
  每个Condition从Canonical State得出

【STEP 5】Local Judgment
  ↓
  单条断言输出
  包含完整trace

【STEP 6】Composite规则（必须有原典授权！）
  ↓
  原典明确说："若A且B则成格"
  不能工程推断！

【STEP 7】Claude审计
  ↓
  独立验证5条断言

【STEP 8】GPT裁决
  ↓
  裁决是否获得Production Authorization

【STEP 9】测试写入
  ↓
  验证用例编写

【STEP 10】Commit记录
  ↓
  完整追溯链
```

---

## 当前进度

- [x] 原典定位（6条Evidence已提取）
- [ ] Evidence逐字核验（pending_verification → CLASSICAL_EXPLICIT）
- [ ] Primitive拆分（5条断言×3个Primitive）
- [ ] Condition构建（15个Condition Evaluator）
- [ ] Local Judgment实现（5个断言输出）
- [ ] Claude审计（待提交）
- [ ] GPT裁决（待请求）
- [ ] 测试写入（待添加）
- [ ] Commit记录（待执行）

---

## 质量门禁

### 必须满足
- ✅ 原典定位：滴天髓通神论具体章节+原文定位
- ✅ Evidence分层：原文层/注释层/后世层独立标注
- ✅ Primitive拆分：至少3个最小信号单元
- ✅ Condition拆分：每个Condition可从Canonical State得出
- ✅ Local Judgment：不超原典授权范围
- ✅ Composite授权：有原典明确授权（非工程推断）
- ✅ Claude审计：独立验证通过
- ✅ GPT裁决：每5条一批，获得授权
- ✅ 测试覆盖：原典定位+Primitive拆分+Condition触发+边界测试
- ✅ 无Legacy调用：verify_legacy_calls.py 0
- ✅ 无XPassed：pytest --tb=short 0 xpassed

---

等待下一步指令。