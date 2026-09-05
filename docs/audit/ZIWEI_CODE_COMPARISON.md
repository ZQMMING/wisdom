# 紫微斗数引擎代码对比分析

> **对比日期**：2026-09-04  
> **对比对象**：本地引擎 vs GitHub 开源项目

---

## 一、本地引擎架构

### 文件结构
```
src/tongshu/engines/ziwei_*.py
├── ziwei_method_profile.py  (10.7KB) ← Z10 方法论契约
├── ziwei_engine.py          (36KB)   ← 主引擎
├── ziwei_adapter.py         (5.6KB)  ← bySolar适配
├── ziwei_profile.py         (8.3KB)  ← Z1 配置层
├── ziwei_fact_layer.py      (9.6KB)  ← Z2 事实层
├── ziwei_rule_graph.py      (18KB)   ← Z3 规则图
├── ziwei_sanhe.py           (10KB)   ← Z4 三合派
├── ziwei_zhongzhou.py       (5.9KB)  ← Z5 中州派
├── ziwei_feixing.py         (8.4KB)  ← Z6 飞星派
├── ziwei_qintian.py         (9.9KB)  ← Z7 钦天门
├── ziwei_pipeline.py        (5.5KB)  ← Z8 API流水线
└── ziwei_pattern.py         (6.4KB)  ← 格局识别
```

### 核心能力矩阵

| 能力 | 本地引擎 | cdestiny | FateCat |
|------|---------|----------|---------|
| 四派隔离 | ✅ Z1-Z7 | ❌ 单一流派 | ✅ 多引擎 |
| 方法论契约 | ✅ Z10 | ❌ | ❌ |
| 事实层隔离 | ✅ Z2 | ❌ | ❌ |
| 规则图系统 | ✅ Z3 | ❌ | ❌ |
| 证据追溯 | ✅ | ❌ | ✅ |
| 流派四化差异 | ✅ 戊干/庚干/壬干 | ⚠️ 仅通行版 | ⚠️ 需扩展 |
| 空宫策略差异 | ✅ partial/full | ❌ | ❌ |
| 流昌流曲 | ✅ 中州派 | ❌ | ❌ |
| 自化系统 | ✅ 飞星/钦天 | ❌ | ❌ |
| 立极宫 | ✅ 钦天门 | ❌ | ❌ |

---

## 二、四化表对比

### cdestiny 四化表（通行版）
```python
SIHUA = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},  # 右弼化科
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "太阴", "忌": "天同"},  # 太阴化科
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "左辅", "忌": "武曲"},  # 左辅化科
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}
```

### 中州派四化表（本地引擎）
```python
"戊": {"禄": "贪狼", "权": "太阴", "科": "太阳", "忌": "天机"},  # 太阳化科 ✅
"庚": {"禄": "太阳", "权": "武曲", "科": "天府", "忌": "天同"},  # 天府化科 ✅
"壬": {"禄": "天梁", "权": "紫微", "科": "天府", "忌": "武曲"},  # 天府化科 ✅
```

### 关键差异
| 天干 | 通行版 | 中州派 | 影响 |
|------|--------|--------|------|
| 戊 | 右弼化科 | **太阳化科** | 命宫/官禄宫判断不同 |
| 庚 | 太阴化科 | **天府化科** | 财帛/田宅判断不同 |
| 壬 | 左辅化科 | **天府化科** | 迁移/交友判断不同 |

---

## 三、算法实现对比

### 3.1 命宫计算

**cdestiny** (`zwds.py:60`):
```python
def place_ming_shen_gong(lm, hz):
    si = (iz("寅") + lm - 1) % 12
    hi = iz(hz)
    return DIZHI[(si - hi) % 12], DIZHI[(si + hi) % 12]
```

**本地引擎** (`ziwei_engine.py`):
```python
# 调用 bySolar 计算
result = bySolar(solar_year, solar_month, solar_day, hour, gender, is_leap, locale)
ming_gong = result.earthlyBranchOfSoulPalace
shen_gong = result.earthlyBranchOfBodyPalace
```

### 3.2 安星法

**cdestiny** (`zwds.py:74-82`):
```python
ZIWEI_START = {2: "丑", 3: "辰", 4: "亥", 5: "午", 6: "酉"}

def place_ziwei(ld, jn):
    start_zhi = ZIWEI_START[jn]
    half = jn // 2
    g = (ld - 1) // jn
    p = ld - g * jn
    if p <= half:
        inner = -half * (p - 1)
    else:
        inner = -half * (jn - p)
    return DIZHI[(si + g + inner) % 12]
```

**本地引擎**: 依赖 `iztro` 库的 `bySolar` 函数，实现已验证对齐倪海厦数据集。

---

## 四、特征能力差距分析

### 4.1 本地引擎独有特性

| 特性 | 描述 | cdestiny状态 |
|------|------|-------------|
| **MethodProfile** | 流派方法论契约定义 | ❌ 不存在 |
| **Fact Layer** | 独立于分析方法的事实层 | ❌ 不存在 |
| **Rule Graph** | 规则图系统，支持多规则验证 | ❌ 不存在 |
| **四派隔离** | 三合/中州/飞星/钦天独立实现 | ❌ 单一实现 |
| **空宫策略** | partial vs full 可配置 | ❌ 固定策略 |
| **流昌流曲** | 中州派特有 | ❌ 未实现 |
| **自化系统** | 飞星派/钦天门特有 | ❌ 未实现 |
| **立极宫** | 钦天门特有 | ❌ 未实现 |

### 4.2 cdestiny 独有特性

| 特性 | 描述 | 本地引擎状态 |
|------|------|-------------|
| **True Solar Time** | 真太阳时校正 | ⚠️ 有时间模块 |
| **纯Python实现** | 无外部依赖（仅lunardate） | ❌ 依赖iztro |
| **BaZi集成** | 八字紫微一体化 | ⚠️ 有独立八字模块 |
| **MIT License** | 宽松许可证 | ⚠️ 需确认 |

---

## 五、测试覆盖率对比

### 本地引擎
```
总计: 129 passed, 32 subtests passed
- 测试文件: 9个
- 核心测试: test_ziwei_method_profile.py (23项)
- 数据验证: validate_ziwei_dataset.py (100%通过率)
```

### cdestiny
```
测试文件: test_known_charts.py
验证方式: 公开案例交叉验证
```

---

## 六、结论与建议

### 6.1 本地引擎优势

1. **方法论完整性** — Z1-Z10 完整架构，四派隔离明确
2. **证据追溯** — 每条规则带 source_ref
3. **流派差异** — 正确实现中州派特殊四化
4. **数据验证** — 通过倪海厦518,400样本验证

### 6.2 可借鉴点

1. **真太阳时** — cdestiny 的实现可参考
2. **纯Python** — 降低部署依赖
3. **API简洁** — `zwds_chart(year, month, day, hour, gender)` 更易用

### 6.3 建议行动

- [ ] 考虑将 `bySolar` 替换为本地纯Python实现（可选）
- [ ] 集成真太阳时校正（优先级中）
- [ ] 保持当前架构（方法论契约+Fact Layer+Rule Graph 为核心竞争力）
