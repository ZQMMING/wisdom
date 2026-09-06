# BOT-ZIPING 生产准入审计任务单 (Revised)

## 总裁决摘要

**核心结论**: 八字排盘核心暂时可以维持，不需要重写。但需要完成 Production Admission 审计。

**原报告P0 → 降级为P2**
**原报告P2-6 → 升级为P1**

---

## 重新分级后的优先级

| 原ID | 新级别 | 处理 |
|------|--------|------|
| P0-1 Optional | P2 | 顺手修 |
| P1-1 sys.exit() | P1 | 立即修 |
| P1-2 K2G路径 | P1 | 修测试基础设施 |
| P1-3 recompute_month | P1 | 全仓追踪后决定 |
| P1-4 solar_date契约 | P1/P2边界 | 明确Contract+fail-closed |
| P2-1 simple月柱 | P2 | 检查fallback策略 |
| P2-2 evidence_id | P2 | 证据分类治理 |
| P2-3 1412/1509 | P2 | 核对证据分类 |
| P2-4 branch_root_idx | P2 | 清理注释 |
| P2-5 heuristic | P2 | 保持NOT_AUTHORIZED |
| P2-6 测试覆盖 | P1 | 第一入口数据契约 |

---

## 执行顺序 (B0-B12)

### Phase 1: 核心计算入口审计
- [ ] B0: 计算入口审计 - 确认BaziEngine只算不改
- [ ] B1: Frozen Bazi State 审计 - 确认计算结果不可被下游修改
- [ ] B2: solar_date Contract - 明确输入契约+fail-closed校验
- [ ] B3: 节气/月柱路径追踪 - 确认production path
- [ ] B4: sxtwl dependency/fallback policy - 确定fail-closed策略

### Phase 2: 调用图与边界
- [ ] B5: 全仓调用图 - 扫描所有bazi_engine引用
- [ ] B6: Adapter boundary - 确认bazi_adapter.py不越权重算
- [ ] B7: 下游是否重复计算 - 确认ZiPing/Blind/Ziwei不重排
- [ ] B8: P2 fields semantic contract - 补充9个字段测试

### Phase 3: 测试与证据
- [ ] B9: 测试基础设施修复 - 修sys.exit(), K2G路径
- [ ] B10: Golden / Boundary replay - 验证129/129可pytest运行
- [ ] B11: Evidence integrity - 分类1509文件，核对1412差异
- [ ] B12: Production Admission - 综合判定

---

## 验收标准

```
BAZI CALCULATION PRODUCTION ADMISSION

Calculation Integrity: PASS/FAIL
Canonical Input Contract: PASS/FAIL
Solar Term Boundary: PASS/FAIL
Zi Hour Boundary: PASS/FAIL
Frozen State Contract: PASS/FAIL
Adapter Boundary: PASS/FAIL
No Duplicate Calculation: PASS/FAIL
Fallback Policy: PASS/FAIL
Evidence Integrity: PASS/FAIL
Replay Determinism: PASS/FAIL

PRODUCTION_ADMITTED: YES/NO
```

---

## 重要约束

1. **FROZEN ≠ PROVEN CORRECT**
2. **死代码 ≠ 立即删除** — 必须先追踪再决定
3. **Silent Wrong Calculation 比直接报错更危险**
4. **第一入口必须有完整数据契约证明**

---

*任务单创建时间: 2026-09-06*
*基于User总裁决修订*
