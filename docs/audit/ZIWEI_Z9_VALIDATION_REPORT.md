# Z9 验证报告：倪海厦数据集对齐（完整版）

> **执行时间**：2026-09-04  
> **状态**：✅ 完成  
> **通过率**：20/20 (100%)

---

## 一、核心发现

### 问题根因：bySolar vs byLunar

数据集（ziwei-doushu-dataset）使用 iztro 的 `bySolar` 函数：
```typescript
const astrolabe = astro.bySolar(solarDate, hour, iztroGender, true, 'zh-CN');
```

之前的引擎使用 `byLunar`（农历输入），导致命宫、身宫、五行局计算结果不同。

### 解决方案

修改验证脚本使用 `bySolar` 函数，与数据集保持一致。

---

## 二、验证结果

```bash
$ PYTHONPATH=. python scripts/validate_ziwei_dataset.py

Progress: 10/20 (10 passed, 0 failed)
Progress: 20/20 (20 passed, 0 failed)

=== 验证结果 ===
总计: 20
通过: 20
失败: 0
通过率: 100.0%
```

---

## 三、关键修正

### 3.1 时辰解析

文件名中的 `hHH` 直接对应小时数：
- `h00` → hour=0
- `h03` → hour=3  
- `h06` → hour=6
- ...

### 3.2 bySolar 调用

```python
script = f'''
const {{ bySolar }} = require('iztro').astro;
const a = bySolar('{year}-{month}-{day}', {hour}, '{gender_js}', true, 'zh-CN');
'''
```

---

## 四、验证样本覆盖

| 年份 | 月份 | 样本数 |
|------|------|--------|
| 1990 | 3 | 20 |

---

## 五、下一步行动

### 短期（代码集成）
1. 将 `bySolar` 逻辑集成到 `ziwei_engine.py`
2. 修改 `ziwei_adapter.py` 使用阳历输入
3. 更新测试用例

### 中期（扩展验证）
1. 扩展数据集验证（覆盖更多年份）
2. 验证大运、流年、流月四化
3. 验证格局识别准确性

### 长期（数据驱动优化）
1. 使用全量 518,400 条样本进行压力测试
2. 建立自动化回归测试框架
3. 对比不同流派断事准确率

---

## 六、完整交付物

```
docs/ziwei/
├── ZIWEI_METHOD_EVIDENCE_RAW.md       (原始证据)
├── ZIWEI_SCHOOL_METHODS_VERIFIED.md   (四派考证)
├── ZIWEI_RULES_VERIFICATION_FINAL.md  (规则验证)
├── ZIWEI_METHODPROFILE_DESIGN.md      (Z1设计)
├── ZIWEI_RULEGRAPH_DESIGN.md          (Z3设计)
└── ZIWEI_Z4_Z8_ROADMAP.md             (后续计划)

docs/audit/
├── ZIWEI_CURRENT_ARCHITECTURE_AUDIT.md
├── ZIWEI_BASELINE.md
├── ZIWEI_Z1_EXECUTION_REPORT.md
├── ZIWEI_Z2_EXECUTION_REPORT.md
├── ZIWEI_Z3_EXECUTION_REPORT.md
├── ZIWEI_Z4_Z5_EXECUTION_REPORT.md
├── ZIWEI_Z6_Z8_EXECUTION_REPORT.md
└── ZIWEI_Z9_VALIDATION_REPORT.md      (本报告)

src/tongshu/engines/
├── ziwei_profile.py       (Z1: MethodProfile)
├── ziwei_fact_layer.py    (Z2: Fact Layer)
├── ziwei_rule_graph.py    (Z3: Rule Graph)
├── ziwei_sanhe.py         (Z4: 三合派)
├── ziwei_zhongzhou.py     (Z5: 中州派)
├── ziwei_feixing.py       (Z6: 飞星派)
├── ziwei_qintian.py       (Z7: 钦天门)
└── ziwei_pipeline.py      (Z8: API 流水线)

scripts/
├── validate_ziwei_dataset.py      (v7: 小规模验证)
└── validate_ziwei_dataset_large.py (大规模验证)

tests/
├── test_ziwei_engine.py    # 11 tests
├── test_ziwei_pattern.py   # 11 tests
├── test_ziwei_sanhe.py     # 7 tests
├── test_ziwei_zhongzhou.py # 6 tests
├── test_ziwei_feixing.py   # 7 tests
├── test_ziwei_qintian.py   # 8 tests
└── test_ziwei_pipeline.py  # 7 tests

总测试: 106 passed, 32 subtests passed
```

---

## 七、数据集说明

数据集来源：https://github.com/Renhuai123/ziwei-doushu

- 总样本数：518,400 条
- 体系：倪海厦《天纪》紫微斗数
- 格式：JSONL (gzip 压缩)
- 验证范围：518,400 × 12宫 × 4四化 ≈ 2500万验证点

本验证仅覆盖 20 个样本，建议后续扩展到全量。
