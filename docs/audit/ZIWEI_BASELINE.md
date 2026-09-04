# ZIWEI BASELINE

> **建立时间**：2026-09-02
> **目的**：记录当前紫微斗数测试基线，供后续重构验证使用

---

## 1. 测试基线数据

### 1.1 现有测试统计

```text
总测试数: 71
通过: 71
失败: 0
子测试: 32
耗时: 32.21s
状态: ✅ ALL PASS
```

### 1.2 紫微相关测试文件

| 文件 | 测试类 | 状态 |
|------|--------|------|
| `tests/test_ziwei_engine.py` | TestZiweiEngineIntegration, TestZiweiStubGuard | ✅ PASS |
| `tests/test_ziwei_pattern.py` | TestZiweiPattern | ✅ PASS |
| `tests/test_ziwei_chart_cross_validate.py` | TestZiweiChartCrossValidation | ✅ PASS |
| `tests/test_ziwei_phase_a0_extended.py` | TestZiweiAdapter, TestGateA_RealZiweiRuntime, TestDecadalBoundary, TestMonthlyMutagen, TestDailyMutagen, TestCrossTemporalValidation, TestCanonicalPalaceSequenceOracle | ✅ PASS |
| `tests/spec/test_vertical_slice_ziwei.py` | TestZiweiVerticalSlice, TestZiweiAssertionGeneration | ✅ PASS |

---

## 2. Golden Cases（用于同盘异法验证）

### 2.1 已验证案例

| 案例ID | 类型 | 阴阳组合 | 状态 |
|--------|------|---------|------|
| ZW-GOLDEN-001 | 阳男 | 甲辰年 | ✅ PASS |
| ZW-GOLDEN-002 | 阳男 | 丙戌年 | ✅ PASS |
| ZW-GOLDEN-003 | 阳女 | 戊子年 | ✅ PASS |
| ZW-GOLDEN-004 | 阳女 | 庚午年 | ✅ PASS |
| ZW-GOLDEN-005 | 阴男 | 乙巳年 | ✅ PASS |
| ZW-GOLDEN-006 | 阴男 | 壬申年 | ✅ PASS |
| ZW-GOLDEN-007 | 阴女 | 丁卯年 | ✅ PASS |
| ZW-GOLDEN-008 | 阴女 | 癸酉年 | ✅ PASS |

> 来源：`data/evidence/ziwei/ziwei_final_report.json` — 8案例100%通过

### 2.2 待补充 Golden Cases

| 类型 | 优先级 | 说明 |
|------|--------|------|
| 空宫命宫 | P0 | 借星场景 |
| 三方四正完整 | P0 | 验证 sanfang_sizheng |
| 生年四化落宫 | P0 | 验证 GAN_SIHUA |
| 大限四化 | P1 | 验证 flow_decadal_mutagen |
| 宫干自化 | P1 | 验证 palace_self_mutagen |
| 来因宫 | P1 | 验证 get_laiyin_gong |
| 立极/转宫 | P2 | 需 Method Profile 完成后 |

---

## 3. 计算一致性验证

### 3.1 已验证项目

| 项目 | 验证状态 | 备注 |
|------|---------|------|
| 命宫定位 | ✅ 一致 | iztro byLunar 正确 |
| 身宫定位 | ✅ 一致 | iztro byLunar 正确 |
| 大限方向（阳男阴女顺） | ✅ 一致 | ShuntianAdapter 修复后 |
| 大限方向（阴男阳女逆） | ✅ 一致 | ShuntianAdapter 修复后 |
| 五行局起运年龄 | ✅ 一致 | 水二木三金四土五火六 |
| 四化表（通行版） | ⚠️ 与明代原版有差异 | 庚干天同 vs 天相 |

### 3.2 待验证项目

| 项目 | 状态 | 阻塞原因 |
|------|------|---------|
| 四化表（中州派特殊版） | ❌ 未验证 | 需 Method Profile |
| 格局识别（37条） | ❌ 未逐条核对 | 需原典对照 |
| 三方四正结果 | ⚠️ 部分验证 | 需 Golden Cases |

---

## 4. 生产路径确认

### 4.1 当前生产路径

```text
API Request
    ↓
ComputeStage.__call__()
    ↓
ZiweiAdapter.compute(ctx, gender)
    ↓
ZiweiEngine._compute_via_iztro()
    ↓
iztro byLunar(solar_date, time_index, gender, is_leap)
    ↓
ZiweiChart (output)
    ↓
ZiweiEngine.extract_baseline_signal(chart)
    ↓
Signal (BASELINE layer)
```

### 4.2 禁止路径（fail-closed）

| 路径 | 禁止原因 |
|------|---------|
| API → LLM → Judgment | 无 Fact/Rule 层 |
| API → score_ziwei → Judgment | Legacy forbidden path |
| Signal → Judgment | 缺少 Rule 匹配 |
| Sanhe Judgment → Feixing Judgment | 跨派依赖 |

---

## 5. 测试命令

### 运行紫微相关测试

```bash
# 仅紫微测试
pytest tests/test_ziwei_engine.py tests/test_ziwei_pattern.py tests/test_ziwei_chart_cross_validate.py tests/test_ziwei_phase_a0_extended.py tests/spec/test_vertical_slice_ziwei.py -v

# 全量测试（含紫微）
pytest -v
```

### 预期结果

```text
71 passed, 32 subtests passed in 32.21s
```

---

## 6. 基线快照哈希

```bash
# 记录当前代码状态
git rev-parse HEAD
# 输出：6b09f0a (P2.1-F+G+H commit)
```

---

*本基线用于后续 Phase A1-A3 重构验证，确保同盘异法不改变 Frozen Chart 计算结果。*
