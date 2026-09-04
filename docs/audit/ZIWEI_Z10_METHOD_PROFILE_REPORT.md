# Z10 执行报告：ZiweiMethodProfile 方法论契约

> **执行时间**：2026-09-04  
> **状态**：✅ 完成

---

## 一、交付物

### 新增文件

| 文件 | 大小 | 内容 |
|------|------|------|
| `src/tongshu/engines/ziwei_method_profile.py` | 14KB | 方法论契约定义 |
| `tests/test_ziwei_method_profile.py` | 8KB | 契约测试（14项） |

---

## 二、核心设计

### 2.1 数据结构

```
MethodId          # 流派枚举 (sanhe/zhongzhou/feixing/qintian)
RuleType          # 规则类型 (pattern/sihua/palace/interaction/cycle)
ConfidenceLevel   # 置信度 (high/medium/low/unknown)

EvidenceRef       # 证据引用
├── source_type: str
├── source_name: str
├── section: str
├── quote: str
└── verified: bool

RuleSpec          # 规则规格
├── rule_id: str
├── rule_type: RuleType
├── method_ids: Tuple[MethodId, ...]
├── condition: Callable
├── effect: Callable
├── evidence: List[EvidenceRef]
└── confidence: ConfidenceLevel

SiHuaTable        # 四化表
├── name: str
├── description: str
├── data: Dict[str, Tuple]
└── sources: List[EvidenceRef]
```

### 2.2 流派契约

| 流派 | 四化表 | 自化 | 立极宫 | 流昌流曲 | 小限 | 空宫策略 |
|------|--------|------|--------|----------|------|----------|
| 三合派 | classic | ✗ | ✗ | ✗ | ✓ | partial |
| 中州派 | zhongzhou | ✗ | ✗ | ✓ | ✓ | **full** |
| 飞星派 | classic | ✓ | ✗ | ✗ | ✗ | partial |
| 钦天门 | classic | ✓ | ✓ | ✗ | partial | partial |

### 2.3 关键差异

**四化表差异**：
- 戊干：中州派 `太阳化科`，其他派 `右弼化科`
- 庚干：中州派 `天府化科`，通行版 `太阴化科`
- 壬干：中州派 `天府化科`，通行版 `左辅化科`

---

## 三、测试结果

```
================== 120 passed, 32 subtests passed ==================
```

| 测试文件 | 通过数 |
|---------|--------|
| test_ziwei_engine.py | 11 |
| test_ziwei_pattern.py | 11 |
| test_ziwei_sanhe.py | 7 |
| test_ziwei_zhongzhou.py | 6 |
| test_ziwei_feixing.py | 7 |
| test_ziwei_qintian.py | 8 |
| test_ziwei_pipeline.py | 7 |
| **test_ziwei_method_profile.py** | **14** |
| test_ziwei_chart_cross_validate.py | 3 |
| test_ziwei_phase_a0_extended.py | 32 subtests |
| **总计** | **120 passed** |

---

## 四、完整架构

```
src/tongshu/engines/
├── ziwei_method_profile.py  ← Z10 (方法论契约)
├── ziwei_profile.py         ← Z1 (配置)
├── ziwei_fact_layer.py      ← Z2 (事实层)
├── ziwei_rule_graph.py      ← Z3 (规则图)
├── ziwei_sanhe.py           ← Z4 (三合派)
├── ziwei_zhongzhou.py       ← Z5 (中州派)
├── ziwei_feixing.py         ← Z6 (飞星派)
├── ziwei_qintian.py         ← Z7 (钦天门)
└── ziwei_pipeline.py        ← Z8 (API)

docs/audit/
├── ZIWEI_Z1_EXECUTION_REPORT.md
├── ZIWEI_Z2_EXECUTION_REPORT.md
├── ZIWEI_Z3_EXECUTION_REPORT.md
├── ZIWEI_Z4_Z5_EXECUTION_REPORT.md
├── ZIWEI_Z6_Z8_EXECUTION_REPORT.md
├── ZIWEI_Z9_VALIDATION_REPORT.md
└── ZIWEI_Z10_METHOD_PROFILE_REPORT.md (本报告)

scripts/
├── validate_ziwei_dataset.py      (20 samples, 100% pass)
└── validate_ziwei_dataset_large.py (100 samples, 100% pass)
```

---

## 五、下一步建议

1. **集成 bySolar** — 将验证脚本的 bySolar 逻辑集成到 `ziwei_engine.py`
2. **扩展验证** — 运行全量 518,400 样本验证
3. **实证研究** — 对比四派断事准确率
