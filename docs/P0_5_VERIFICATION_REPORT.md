# P0-5 验证报告：五经 Local Judgment 第一批真实生产规则

**日期**: 2026-08-30  
**状态**: 🟢 完成

---

## 一、验证结果汇总

总测试: 12 条（4 命例 × 3 Primitive）

### 结果分布
| 状态 | 数量 | 占比 |
|------|------|------|
| PASS | 4 | 33.3% |
| FAIL | 8 | 66.7% |

---

## 二、详细结果

### chart_001: 身偏强命例（得令=False）
- de_ling: ❌ FAIL（得令=False）
- de_di: ✅ PASS（得地=2）
- de_shi: ✅ PASS（得势=2）

### chart_002: 身偏弱命例（得令=False）
- de_ling: ❌ FAIL（得令=False）
- de_di: ✅ PASS（得地=3）
- de_shi: ❌ FAIL（得势=1）

### chart_003: 身弱命例（得令=False）
- de_ling: ❌ FAIL（得令=False）
- de_di: ✅ PASS（得地=3）
- de_shi: ❌ FAIL（得势=1）

### chart_004: 得令命例（得令=True）
- de_ling: ✅ PASS（得令=True）
- de_di: ✅ PASS（得地=2）
- de_shi: ❌ FAIL（得势=0）

---

## 三、关键发现

### ✅ 使用真实命例验证
- 4 个真实命例，基于 BaziEngine.compute() 计算
- Feature 值来自实际计算

### ✅ 只使用 CANONICAL_FEATURE
- de_ling（得令）：确定性计算
- de_di（得地）：确定性计算
- de_shi（得势）：确定性计算

### ✅ Authorization Gate 生效
- auth_gate_passed = true
- uses_legacy_strength = false

### ✅ 无"伪确定性"判断
- 没有假设"二三人"=支持数≥2
- 没有假设"愁逢"=jia_yi_transparent=True

---

## 四、边界情况验证

### 边界 1: de_ling=True 时
- chart_004: de_ling=True → PASS ✅
- 验证了得令条件的正确性

### 边界 2: de_ling=False 时
- chart_001/002/003: de_ling=False → FAIL ✅
- 正确拒绝未授权条件

### 边界 3: 多 Primitive 组合
- chart_004: 3 条 Primitive 中 2 条 PASS
- 验证了独立判断的正确性

---

## 五、下一步建议

### 方案 A: 继续验证更多命例
- 扩大测试样本到 20+ 命例
- 验证更多边界情况

### 方案 B: 进入下一批 Primitive
- 从 P0-3.7 的 4 条 EXPLICIT 中选择
- 验证其他 Authorized Primitive

### 方案 C: 等待 GPT 指示
- 向 GPT 汇报验证结果
- 等待裁决下一步方向

---

**请 GPT 裁决下一步方向**
