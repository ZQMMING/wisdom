# ZIPING Phase 4 P0 深挖阶段报告

**任务 ID**: T-ENGINE-BAZI-002 Phase 4 P0 Deep Dive
**执行者**: @bot-ziping
**日期**: 2026-09-07
**状态**: 证据追踪完成，禁止修改代码

---

## 汇总

| 级别 | 数量 |
|------|------|
| P0 | 400 |
| P1 | 5 |
| INFO | 7 |

---

## 详细发现

### 🔴 [P0-1-A] ContextAssembler 第 532 行调用 bazi_engine.compute()

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `chart = self.bazi_engine.compute((birth_year, birth_month, birth_day, birth_hour), gender)`
- **Git 历史**: cb25806a9 (ming 2026-08-28 16:05:00 +0800 532)         chart = self.bazi_engine.compute((birth_year, birth_month, birth_day, birth_hour), gender)
- **影响**: 可能重新计算四柱，违反 BAZI Frozen State 原则
- **建议**: 删除或重构此调用，改为消费已计算的 chart

### 🔴 [P0-1-B] ContextAssembler 被 1 处引用

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/reasoning/context_assembler.py:570:    assembler = ContextAssembler()`
- **影响**: 需要确认是否进入生产路径
- **建议**: 检查每个调用点是否必要

### 🔴 [P0-1-C-engine\.co-D:\shuntian\src/tongshu/api/ap] 发现可能的重复排盘调用: engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/api/app.py:398:        chart = pipeline.bazi_engine.compute((ad.year, ad.month, ad.day, 12), gender="male")`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-engine\.co-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/bazi_adapter.py:51:        return self._engine.compute(`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-engine\.co-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/blind_bazi_engine.py:149:        chart = self.bazi_engine.compute(birth, gender=gender)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-engine\.co-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/blind_bazi_engine.py:618:    return engine.compute(birth, gender=gender)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-engine\.co-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/blind_yingqi.py:144:        chart = self.bazi_engine.compute(birth, gender=gender)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-engine\.co-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/heluo/interpretation.py:475:    return engine.compute()`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-engine\.co-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/ziwei_engine.py:768:            bazi = canonical_bazi_engine.compute(`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-engine\.co-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/ziwei_engine.py:774:            bazi = canonical_bazi_engine.compute((1990, 5, 15, hour), gender=gender)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-engine\.co-D:\shuntian\src/tongshu/judgme] 发现可能的重复排盘调用: engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/judgment_architecture/judgment_index_foundation.py:324:    chart = engine.compute((1983, 11, 3, 12), "male")`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-bazi_engin-D:\shuntian\src/tongshu/api/ap] 发现可能的重复排盘调用: bazi_engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/api/app.py:398:        chart = pipeline.bazi_engine.compute((ad.year, ad.month, ad.day, 12), gender="male")`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-bazi_engin-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: bazi_engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/blind_bazi_engine.py:149:        chart = self.bazi_engine.compute(birth, gender=gender)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-bazi_engin-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: bazi_engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/blind_yingqi.py:144:        chart = self.bazi_engine.compute(birth, gender=gender)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-bazi_engin-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: bazi_engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/ziwei_engine.py:768:            bazi = canonical_bazi_engine.compute(`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-bazi_engin-D:\shuntian\src/tongshu/engine] 发现可能的重复排盘调用: bazi_engine\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/engines/ziwei_engine.py:774:            bazi = canonical_bazi_engine.compute((1990, 5, 15, hour), gender=gender)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-BaziEngine-D:\shuntian\src/tongshu/v_vali] 发现可能的重复排盘调用: BaziEngine\(\)\.compute\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/v_validation/end_to_end.py:66:    bazi = BaziEngine().compute(SEED_CASE.birth_date_tuple, gender=SEED_CASE.gender)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-resolver\.-D:\shuntian\src/tongshu/api/ap] 发现可能的重复排盘调用: resolver\.resolve\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/api/app.py:492:        resolved = time_resolver.resolve(`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-resolver\.-D:\shuntian\src/tongshu/judgme] 发现可能的重复排盘调用: resolver\.resolve\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/judgment_architecture/judgment_asset_v2.py:734:    smth_results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-resolver\.-D:\shuntian\src/tongshu/judgme] 发现可能的重复排盘调用: resolver\.resolve\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/judgment_architecture/judgment_asset_v2.py:742:    qtbj_results = resolver.resolve("ZI_PING", "QIONG_TONG_BAO_JIAN", features)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-resolver\.-D:\shuntian\src/tongshu/judgme] 发现可能的重复排盘调用: resolver\.resolve\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/judgment_architecture/judgment_asset_v2.py:750:    neg_results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features_neg)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-resolver\.-D:\shuntian\src/tongshu/judgme] 发现可能的重复排盘调用: resolver\.resolve\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/judgment_architecture/judgment_index_foundation.py:111:        return self.resolver.resolve(self.system, self.school, features)`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-TimeResolv-D:\shuntian\src/tongshu/api/ap] 发现可能的重复排盘调用: TimeResolver\(\)

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/api/app.py:226:    time_resolver = TimeResolver()`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-TimeResolv-D:\shuntian\src/tongshu/golden] 发现可能的重复排盘调用: TimeResolver\(\)

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/golden/boundary.py:63:    r = TimeResolver()`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔴 [P0-1-C-TimeResolv-D:\shuntian\src/tongshu/pipeli] 发现可能的重复排盘调用: TimeResolver\(\)

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `D:\shuntian\src/tongshu/pipeline.py:95:        self.time_resolver = TimeResolver()`
- **影响**: 需要人工核查是否为合法调用
- **建议**: 检查调用点是否在 ZIPING 域内

### 🔵 [P0-1-D] ContextAssembler git 历史记录

- **类别**: GIT_HISTORY
- **严重级别**: INFO
- **证据**: `共 2 次提交`
- **Git 历史**: 2026-09-06 6a0bf855 docs: 添加迁移完整性验证报告
2026-08-28 cb25806a P6-C-3B完成: Context Assembly - 513 events 100% completeness GATE PASS
- **建议**: 检查是否有主动删除的 commit

### 🔴 [P0-2-PY-gen_hetu.py-24] 可能的路径依赖: gen_hetu.py:24

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `with open('D:/shuntian/hetu.svg','w',encoding='utf-8') as f:f.write('\n'.join(L))`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-_run_golden.py-3] 可能的路径依赖: _run_golden.py:3

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `os.chdir("D:/today/backend")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-_run_golden2.py-3] 可能的路径依赖: _run_golden2.py:3

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `os.chdir("D:/today/backend")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-_run_golden3.py-3] 可能的路径依赖: _run_golden3.py:3

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `os.chdir("D:/today/backend")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-_run_golden_stub.py-4] 可能的路径依赖: _run_golden_stub.py:4

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `os.chdir("D:/today/backend")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-_run_snapshots.py-4] 可能的路径依赖: _run_snapshots.py:4

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `os.chdir("D:/today/backend")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-gen_hetu.py-24] 可能的路径依赖: gen_hetu.py:24

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `with open('D:/shuntian/hetu.svg','w',encoding='utf-8') as f:f.write('\n'.join(L))`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-_run_golden.py-3] 可能的路径依赖: _run_golden.py:3

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `os.chdir("D:/today/backend")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-_run_golden2.py-3] 可能的路径依赖: _run_golden2.py:3

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `os.chdir("D:/today/backend")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-_run_golden3.py-3] 可能的路径依赖: _run_golden3.py:3

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `os.chdir("D:/today/backend")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-_run_golden_stub.py-4] 可能的路径依赖: _run_golden_stub.py:4

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `os.chdir("D:/today/backend")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-_run_snapshots.py-4] 可能的路径依赖: _run_snapshots.py:4

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `os.chdir("D:/today/backend")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-blind_architecture_audit.py-7] 可能的路径依赖: blind_architecture_audit.py:7

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence/blind_seg')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-blind_final_verification.py-10] 可能的路径依赖: blind_final_verification.py:10

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `project_dir = Path('C:/Users/wisdom/wisdom')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-blind_reclassification.py-9] 可能的路径依赖: blind_reclassification.py:9

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `project_dir = Path('C:/Users/wisdom/wisdom')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-blind_topic_corrections.py-7] 可能的路径依赖: blind_topic_corrections.py:7

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence/blind_seg')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-complete_evidence_fields_v2.py-303] 可能的路径依赖: complete_evidence_fields_v2.py:303

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `base_dir = Path('C:/Users/wisdom/wisdom')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-complete_evidence_semantics.py-9] 可能的路径依赖: complete_evidence_semantics.py:9

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `BASE = r"C:/Users/wisdom/wisdom/data"`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-complete_semantic_fields.py-12] 可能的路径依赖: complete_semantic_fields.py:12

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `BASE = Path("C:/Users/wisdom/wisdom/data/evidence")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-depth_conflict_analysis.py-15] 可能的路径依赖: depth_conflict_analysis.py:15

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-feature_signal_mapping.py-13] 可能的路径依赖: feature_signal_mapping.py:13

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-feature_signal_mapping.py-14] 可能的路径依赖: feature_signal_mapping.py:14

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `canonical_dir = Path('C:/Users/wisdom/wisdom/data/canonical')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-integrity_check.py-13] 可能的路径依赖: integrity_check.py:13

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-merge_passages.py-133] 可能的路径依赖: merge_passages.py:133

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `base_dir = Path('C:/Users/wisdom/wisdom')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-optimize_conditions.py-145] 可能的路径依赖: optimize_conditions.py:145

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase3b_signal_mapping_fix.py-74] 可能的路径依赖: phase3b_signal_mapping_fix.py:74

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase3b_signal_mapping_fix.py-146] 可能的路径依赖: phase3b_signal_mapping_fix.py:146

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `mapping_path = Path('C:/Users/wisdom/wisdom/data/feature_signal_mapping.json')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase3b_signal_mapping_fix.py-191] 可能的路径依赖: phase3b_signal_mapping_fix.py:191

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase3c_enhanced_verification.py-13] 可能的路径依赖: phase3c_enhanced_verification.py:13

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase3c_enhanced_verification.py-14] 可能的路径依赖: phase3c_enhanced_verification.py:14

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `canonical_dir = Path('C:/Users/wisdom/wisdom/data/canonical')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase3c_verification.py-13] 可能的路径依赖: phase3c_verification.py:13

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase3c_verification.py-14] 可能的路径依赖: phase3c_verification.py:14

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `canonical_dir = Path('C:/Users/wisdom/wisdom/data/canonical')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-281] 可能的路径依赖: phase4_p0_deep_dive.py:281

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r'/home/',             # Linux 用户目录`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-282] 可能的路径依赖: phase4_p0_deep_dive.py:282

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r'C:\\',               # Windows 转义路径`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-283] 可能的路径依赖: phase4_p0_deep_dive.py:283

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r'D:\\',`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-284] 可能的路径依赖: phase4_p0_deep_dive.py:284

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r'C:/Users/',`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-285] 可能的路径依赖: phase4_p0_deep_dive.py:285

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r'/c/Users/',`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-286] 可能的路径依赖: phase4_p0_deep_dive.py:286

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r'/d/shuntian/',       # 硬编码项目路径`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-287] 可能的路径依赖: phase4_p0_deep_dive.py:287

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r'D:/shuntian',`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-288] 可能的路径依赖: phase4_p0_deep_dive.py:288

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r'D:/today',`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-290] 可能的路径依赖: phase4_p0_deep_dive.py:290

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r'"D:"',`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-291] 可能的路径依赖: phase4_p0_deep_dive.py:291

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r"'D:'",`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_p0_deep_dive.py-376] 可能的路径依赖: phase4_p0_deep_dive.py:376

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `if re.search(r'[A-Z]:/|/home/|/c/Users/', content):`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_reaudit.py-628] 可能的路径依赖: phase4_reaudit.py:628

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `repo_root = script_dir.parent  # D:\shuntian`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_verification.py-12] 可能的路径依赖: phase4_verification.py:12

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `WORKSPACE = Path("D:/shuntian")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_verification.py-16] 可能的路径依赖: phase4_verification.py:16

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `OUTPUT_DIR = Path("C:/Users/ming/wisdom/docs/bots/BOT-CORPUS")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_verification_v2.py-11] 可能的路径依赖: phase4_verification_v2.py:11

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `WORKSPACE = Path("D:/shuntian")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_verification_v2.py-14] 可能的路径依赖: phase4_verification_v2.py:14

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `OUTPUT_DIR = Path("C:/Users/ming/wisdom/docs/bots/BOT-CORPUS")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase4_verification_v2.py-192] 可能的路径依赖: phase4_verification_v2.py:192

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `> Workspace: D:/shuntian`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase5_crossbot_verification.py-11] 可能的路径依赖: phase5_crossbot_verification.py:11

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `WORKSPACE = Path("D:/shuntian")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase5_crossbot_verification.py-14] 可能的路径依赖: phase5_crossbot_verification.py:14

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `OUTPUT_DIR = Path("C:/Users/ming/wisdom/docs/bots/BOT-MASTER")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase_b0_1_gap_closure.py-550] 可能的路径依赖: phase_b0_1_gap_closure.py:550

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `loader = EvidenceLoader(Path("D:/shuntian/data/evidence"))`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase_b0_1_gap_closure.py-596] 可能的路径依赖: phase_b0_1_gap_closure.py:596

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `output_dir = Path("D:/shuntian/docs/bots/BOT-ZIPING")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-pre_task_check.py-35] 可能的路径依赖: pre_task_check.py:35

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `return False, f"❌ 违规: 当前路径 {cwd} 不在 D:/shuntian/ 下"`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-semantic_normalization.py-416] 可能的路径依赖: semantic_normalization.py:416

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `output_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-semantic_normalization.py-494] 可能的路径依赖: semantic_normalization.py:494

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-semantic_normalization_final.py-41] 可能的路径依赖: semantic_normalization_final.py:41

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-semantic_normalization_v3.py-41] 可能的路径依赖: semantic_normalization_v3.py:41

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-semantic_normalization_v4.py-80] 可能的路径依赖: semantic_normalization_v4.py:80

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-semantic_normalization_v5.py-79] 可能的路径依赖: semantic_normalization_v5.py:79

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-semantic_normalization_v6.py-76] 可能的路径依赖: semantic_normalization_v6.py:76

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-update_evidence_context.py-166] 可能的路径依赖: update_evidence_context.py:166

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `base_dir = Path('C:/Users/wisdom/wisdom')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-validate_provenance.py-144] 可能的路径依赖: validate_provenance.py:144

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence/blind_seg')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-verify_blind_corpus.py-6] 可能的路径依赖: verify_blind_corpus.py:6

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence/blind_seg')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-verify_semantic_artifacts.py-13] 可能的路径依赖: verify_semantic_artifacts.py:13

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-ziwei_production_trace.py-16] 可能的路径依赖: ziwei_production_trace.py:16

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `for p in ['C:/Users/wisdom/wisdom/src', 'D:/today/backend/src']:`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase_b1_evidence_connection.py-724] 可能的路径依赖: phase_b1_evidence_connection.py:724

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `loader = EvidenceLoader(Path("D:/shuntian/data/evidence"))`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase_b1_evidence_connection.py-803] 可能的路径依赖: phase_b1_evidence_connection.py:803

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `analysis_data = json.loads(Path("D:/shuntian/docs/bots/BOT-ZIPING/phase_b0_1_analysis.json").read_te`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase_b1_evidence_connection.py-853] 可能的路径依赖: phase_b1_evidence_connection.py:853

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `output_path = Path("D:/shuntian/docs/bots/BOT-ZIPING/PHASE_B1_EVIDENCE_CONNECTION_AUDIT.md")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase_b2_1_remediation.py-667] 可能的路径依赖: phase_b2_1_remediation.py:667

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `output_path = Path("D:/shuntian/docs/bots/BOT-ZIPING/PHASE_B2_1_REMEDIATION_AUDIT.md")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase_b2_1_remediation.py-671] 可能的路径依赖: phase_b2_1_remediation.py:671

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `results_path = Path("D:/shuntian/docs/bots/BOT-ZIPING/phase_b2_1_results.json")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase_b2_rule_authorization.py-519] 可能的路径依赖: phase_b2_rule_authorization.py:519

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `loader = EvidenceLoader(Path("D:/shuntian/data/evidence"))`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase_b2_rule_authorization.py-560] 可能的路径依赖: phase_b2_rule_authorization.py:560

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `output_path = Path("D:/shuntian/docs/bots/BOT-ZIPING/PHASE_B2_RULE_AUTHORIZATION_AUDIT.md")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-phase_b2_rule_authorization.py-564] 可能的路径依赖: phase_b2_rule_authorization.py:564

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `results_path = Path("D:/shuntian/docs/bots/BOT-ZIPING/phase_b2_audit_results.json")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-fupeirong_loader.py-99] 可能的路径依赖: fupeirong_loader.py:99

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `dimension: 维度(fortune/wealth/home/career/marriage/health/lawsuit/travel)`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-registry_loader.py-15] 可能的路径依赖: registry_loader.py:15

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `r'D:\today\docs\k2g',`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-fix_paths.py-3] 可能的路径依赖: fix_paths.py:3

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `修复 D:/shuntian 测试文件中的错误仓库路径`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-fix_paths.py-23] 可能的路径依赖: fix_paths.py:23

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `content = re.sub(r'D:\\\\today', '.', content)`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-fix_paths.py-70] 可能的路径依赖: fix_paths.py:70

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `if '.' in content or 'D:\\today' in content:`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-extract_4dim_validation.py-24] 可能的路径依赖: extract_4dim_validation.py:24

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `doc_path = r"D:\today\chinese-fortune\references\64hex-full.md"`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-extract_4dim_validation.py-75] 可能的路径依赖: extract_4dim_validation.py:75

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `corpus_path = r"D:\today\nihai-tianji-corpus\docs\09-六十四卦.md"`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-extract_4dim_validation.py-125] 可能的路径依赖: extract_4dim_validation.py:125

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `out_path = r"D:\TODAY\backend\data\research\64gua_4dim_validation.json"`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-extract_nihai_64gua.py-7] 可能的路径依赖: extract_nihai_64gua.py:7

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `DOC = Path(r"D:\today\nihai-tianji-corpus\docs\09-六十四卦.md")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-extract_nihai_64gua.py-77] 可能的路径依赖: extract_nihai_64gua.py:77

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `out = Path(r"D:\TODAY\backend\data\research\nihai_64gua_extract.json")`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-PY-generate_assertion_table.py-5] 可能的路径依赖: generate_assertion_table.py:5

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `data = json.load(open(r"D:\TODAY\backend\data\research\64gua_4dim_validation.json", encoding="utf-8"`
- **影响**: 项目移动后索引可能失效
- **建议**: 改为相对路径或 Path(__file__) 解析

### 🔴 [P0-2-ABS-34] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `archive/heluo_legacy/heluo_yi_flow.py:34:SHENG = {WOOD: FIRE, FIRE: EARTH, EARTH: METAL, METAL: WATE`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-35] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `archive/heluo_legacy/heluo_yi_flow.py:35:KE = {WOOD: EARTH, EARTH: WATER, WATER: FIRE, FIRE: METAL, `
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-130] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `archive/signal/convergence.py:130:            if outcome.outcome == ConvergenceOutcome.ALIGNED:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-149] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `archive/signal/convergence.py:149:        if overall_outcome == ConvergenceOutcome.ALIGNED:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-151] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `archive/signal/convergence.py:151:        elif overall_outcome == ConvergenceOutcome.CONFLICTED:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-24] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `backend/data/docs/architecture/gen_hetu.py:24:with open('D:/shuntian/hetu.svg','w',encoding='utf-8')`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-3] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `backend/data/docs/audit/step6_interim_baseline/_run_golden.py:3:os.chdir("D:/today/backend")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-3] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `backend/data/docs/audit/step6_interim_baseline/_run_golden2.py:3:os.chdir("D:/today/backend")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-3] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `backend/data/docs/audit/step6_interim_baseline/_run_golden3.py:3:os.chdir("D:/today/backend")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-4] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `backend/data/docs/audit/step6_interim_baseline/_run_golden_stub.py:4:os.chdir("D:/today/backend")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-4] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `backend/data/docs/audit/step6_interim_baseline/_run_snapshots.py:4:os.chdir("D:/today/backend")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `cases/scripts/validate_cases.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-12] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `dataset/golden_v1/create_full.py:12:sys.path.insert(0, str(Path("D:/today/backend/src")))`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-9] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `dataset/golden_v1/create_full_v2.py:9:sys.path.insert(0, str(Path("D:/today/backend/src")))`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-6] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `dataset/golden_v1/create_full_v3.py:6:sys.path.insert(0, str(Path("D:/today/backend/src")))`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-12] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `dataset/golden_v1/expand.py:12:sys.path.insert(0, str(Path("D:/today/backend/src")))`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-9] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `dataset/golden_v1/expand_to_500.py:9:sys.path.insert(0, str(Path("D:/today/backend/src")))`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-19] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `dataset/golden_v1/generate.py:19:sys.path.insert(0, str(Path("D:/today/backend/src")))`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-11] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `dataset/golden_v1/generate_golden.py:11:sys.path.insert(0, str(Path("D:/today/backend/src")))`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-24] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `docs/architecture/gen_hetu.py:24:with open('D:/shuntian/hetu.svg','w',encoding='utf-8') as f:f.write`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-3] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `docs/audit/step6_interim_baseline/_run_golden.py:3:os.chdir("D:/today/backend")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-3] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `docs/audit/step6_interim_baseline/_run_golden2.py:3:os.chdir("D:/today/backend")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-3] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `docs/audit/step6_interim_baseline/_run_golden3.py:3:os.chdir("D:/today/backend")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-4] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `docs/audit/step6_interim_baseline/_run_golden_stub.py:4:os.chdir("D:/today/backend")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-4] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `docs/audit/step6_interim_baseline/_run_snapshots.py:4:os.chdir("D:/today/backend")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/analyze_sxtwl_jd.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-70] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/analyze_sxtwl_jd.py:70:    print(f"  JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-112] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/analyze_sxtwl_jd.py:112:    print(f"  实际JD: {actual_jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/analyze_xinhua_vs_sxtwl.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-38] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/analyze_xinhua_vs_sxtwl.py:38:print(f"  JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-92] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/analyze_xinhua_vs_sxtwl.py:92:print(f"  JD: {jd_2023}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/authority_verification_report.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-73] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/authority_verification_report.py:73:        print(f"sxtwl JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/blind_architecture_audit.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/blind_final_verification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-39] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/blind_final_verification.py:39:print(f"   VERIFIED: {len(verified)}条")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-193] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/blind_final_verification.py:193:print(f"   VERIFIED: {final_verified}条")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/blind_reclassification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/blind_source_verification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/blind_topic_corrections.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/bot-workspace-check.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-9] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/bot-workspace-check.py:9:WORKSPACE_ROOT = Path("D:/shuntian").resolve()`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-12] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/bot-workspace-check.py:12:    Path("D:/today").resolve(),`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-13] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/bot-workspace-check.py:13:    Path("D:/d/today").resolve(),`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-14] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/bot-workspace-check.py:14:    Path("D:/shuntian-NEW").resolve(),`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/complete_evidence_fields.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/complete_evidence_fields_v2.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-9] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/complete_evidence_semantics.py:9:BASE = r"C:/Users/wisdom/wisdom/data"`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/complete_semantic_fields.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-12] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/complete_semantic_fields.py:12:BASE = Path("C:/Users/wisdom/wisdom/data/evidence")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/debug_iztro_decadal_bug.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-127] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/debug_iztro_decadal_bug.py:127:        print("CONFIRMED: iztro decadal direction bug affects`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/debug_jd_conversion.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-19] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/debug_jd_conversion.py:19:    print(f"sxtwl JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-60] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/debug_jd_conversion.py:60:    print(f"sxtwl JD:                      {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/deep_jd_analysis.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-34] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/deep_jd_analysis.py:34:        print(f"sxtwl JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/depth_conflict_analysis.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/feature_signal_mapping.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/final_authority_check.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-102] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/final_authority_check.py:102:    print(f"  JD: {jd_val}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/final_jd_verification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-31] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/final_jd_verification.py:31:print(f"sxtwl JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/final_jpl_verification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-47] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/final_jpl_verification.py:47:    print(f"  sxtwl JD:                {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/final_sxtwl_verification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-42] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/final_sxtwl_verification.py:42:        print(f"  JD:            {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/final_xinhua_analysis.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-90] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/final_xinhua_analysis.py:90:        print(f"  sxtwl JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/fix_p0_daymaster_strength.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/generate_provenance_matrix.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/integrity_check.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/merge_passages.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/migrate_blind_evidence_schema.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-76] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/migrate_blind_evidence_schema.py:76:print(f"  VERIFIED: {verified}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-78] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/migrate_blind_evidence_schema.py:78:print(f"  REJECTED: {rejected}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-85] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/migrate_blind_evidence_schema.py:85:    print("PASSED: Schema v2.0 迁移完成")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/optimize_conditions.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase0_complete_verification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase0_complete_verification_v2.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase3b_signal_mapping_fix.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase3c_enhanced_verification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-161] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase3c_enhanced_verification.py:161:        print("   TEN_GOD: Canonical Derived ✅")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-216] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase3c_enhanced_verification.py:216:        print("❌ Verification FAILED:")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-227] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase3c_enhanced_verification.py:227:        print(f"  - TEN_GOD: Canonical Derived ✅")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase3c_verification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-136] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase3c_verification.py:136:        print(f"  - TEN_GOD: Canonical Derived ✓")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_p0_deep_dive.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-281] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_p0_deep_dive.py:281:        r'/home/',             # Linux 用户目录`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-283] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_p0_deep_dive.py:283:        r'D:\\',`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-287] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_p0_deep_dive.py:287:        r'D:/shuntian',`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-288] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_p0_deep_dive.py:288:        r'D:/today',`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-290] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_p0_deep_dive.py:290:        r'"D:"',`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-291] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_p0_deep_dive.py:291:        r"'D:'",`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-376] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_p0_deep_dive.py:376:                if re.search(r'[A-Z]:/|/home/|/c/Users/', content`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-391] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_p0_deep_dive.py:391:             '-E', r'/(home|usr|var|etc)/|"D:|"C:|\'D:|\'C:',`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_reaudit.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-628] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_reaudit.py:628:    repo_root = script_dir.parent  # D:\shuntian`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_verification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-12] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_verification.py:12:WORKSPACE = Path("D:/shuntian")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-16] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_verification.py:16:OUTPUT_DIR = Path("C:/Users/ming/wisdom/docs/bots/BOT-CORPUS")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_verification_v2.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-11] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_verification_v2.py:11:WORKSPACE = Path("D:/shuntian")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-14] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_verification_v2.py:14:OUTPUT_DIR = Path("C:/Users/ming/wisdom/docs/bots/BOT-CORPUS")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-192] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase4_verification_v2.py:192:> Workspace: D:/shuntian`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase5_crossbot_verification.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-11] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase5_crossbot_verification.py:11:WORKSPACE = Path("D:/shuntian")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-14] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase5_crossbot_verification.py:14:OUTPUT_DIR = Path("C:/Users/ming/wisdom/docs/bots/BOT-MAS`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase_b0_1_gap_closure.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-550] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase_b0_1_gap_closure.py:550:    loader = EvidenceLoader(Path("D:/shuntian/data/evidence"))`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-596] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/phase_b0_1_gap_closure.py:596:    output_dir = Path("D:/shuntian/docs/bots/BOT-ZIPING")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-15] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/pre_task_check.py:15:    Path("D:/today").resolve(),`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-16] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/pre_task_check.py:16:    Path("D:/d/today").resolve(),`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-17] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/pre_task_check.py:17:    Path("D:/shuntian-NEW").resolve(),`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-29] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/pre_task_check.py:29:    shuntian_root = Path("D:/shuntian").resolve()`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-35] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/pre_task_check.py:35:        return False, f"❌ 违规: 当前路径 {cwd} 不在 D:/shuntian/ 下"`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/semantic_normalization.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/semantic_normalization_final.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/semantic_normalization_v3.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/semantic_normalization_v4.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/semantic_normalization_v5.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/semantic_normalization_v6.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/sxtwl_internal_check.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-46] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/sxtwl_internal_check.py:46:            print(f"  反推JD: {back_jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-58] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/sxtwl_internal_check.py:58:    print(f"JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/update_evidence_context.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/validate_provenance.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_blind_corpus.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_corpus_phase4.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_jd_converter_fix.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-77] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_jd_converter_fix.py:77:        print(f"  JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_jd_correct.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-43] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_jd_correct.py:43:        print(f"sxtwl JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_jieqi_time.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-55] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_jieqi_time.py:55:        print(f"sxtwl JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_mixed_hypothesis.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-50] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_mixed_hypothesis.py:50:    print(f"  JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_mixed_jd.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-59] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_mixed_jd.py:59:    print(f"sxtwl JD: {jd}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_p1_fix.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_semantic_artifacts.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-81] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/verify_semantic_artifacts.py:81:        print("❌ VERIFICATION FAILED:")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/ziwei_production_trace.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-16] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/ziwei_production_trace.py:16:for p in ['C:/Users/wisdom/wisdom/src', 'D:/today/backend/src']`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/ziwei_runtime_output_audit.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/ziwei_runtime_output_audit_v5.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `scripts/ziwei_runtime_output_audit_v6.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-43] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/api/errors.py:43:    ErrorCode.AUDIT_BLOCKED: 423,`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-44] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/api/errors.py:44:    ErrorCode.EVIDENCE_INVALID: 424,`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-45] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/api/errors.py:45:    ErrorCode.MAPPING_INVALID: 425,`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-46] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/api/errors.py:46:    ErrorCode.RATE_LIMITED: 429,`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-114] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/api/profile.py:114:      - VALID: 所有 §1.2 必填字段提交且校验通过 → 计算就绪`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-97] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/assertion/admission_registry.py:97:    if _AUTHORITY_LOCKED:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-118] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/assertion/admission_registry.py:118:    if _AUTHORITY_LOCKED:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-274] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/assertion/admission_registry.py:274:        if required_scope == AdmissionScope.PRODUCTI`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-129] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/assertion/judgment_rule_library.py:129:            elif cond_type == JudgmentCondition.S`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-25] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/audit_validation/validators/layer2_similarity.py:25:THRESHOLD: float = 0.20`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-205] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/bian/base.py:205:    CLASSIC_ID: str = ""`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-74] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/canonical/day_year_evaluator.py:74:                - UNRESOLVED: 数据不足，无法判断`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-45] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/canonical/negation_evaluator.py:45:            - UNRESOLVED: 数据缺失，无法判断`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-58] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/canonical/root_evaluator_v2.py:58:                - UNRESOLVED: 数据不足或映射失败`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-47] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/classic_evidence/base.py:47:    - AUTHORIZED: 已授权（仅验证层可授予）`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-69] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/classic_evidence/base.py:69:    - FOUND: 有完整 provenance 的证据`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-70] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/classic_evidence/base.py:70:    - NOT_FOUND: 找不到原文，不是 Evidence，而是搜索结果`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-204] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/classic_evidence/base.py:204:        if self.production_status == ProductionStatus.APPRO`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-207] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/classic_evidence/base.py:207:        if self.authorization_level == AuthorizationLevel.A`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-234] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/classic_evidence/base.py:234:    CLASSIC_ID: str = ""`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-296] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/classic_evidence/base.py:296:        if authorization_level == AuthorizationLevel.AUTHOR`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-421] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/corpus/validation.py:421:        if best_coverage >= self.PARTIAL_THRESHOLD:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-14] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/bazi_adapter.py:14:P2.7-D: 传递 true_solar_datetime 给引擎，确保节气判断使用真太阳时。`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1005] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/bazi_engine.py:1005:        """FAIL-CLOSED: sxtwl is required for correct bazi c`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-83] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/heluo/canonical.py:83:                best[lm] = (gap, f"{t.Y:04d}-{t.M:02d}-{t.`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-3] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/heluo/relationship/engine.py:3:Phase 5-D: Relationship State Engine 核心算法`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-14] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/snapshot/manager.py:14:    async def save_snapshot(self, snapshot: CalculationSn`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-14] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/snapshot/repository.py:14:    async def save(self, snapshot: CalculationSnapshot`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-25] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/snapshot/repository.py:25:    async def save(self, snapshot: CalculationSnapshot`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-99] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/yi/fupeirong_loader.py:99:        dimension: 维度(fortune/wealth/home/career/marri`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-77] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/ziwei/rules/method_graphs.py:77:        SCAFFOLD: 骨架实现，逻辑来自父类/共享实现，待完善`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-376] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/ziwei/rules/method_graphs.py:376:        # SCAFFOLD: 暂时共享 Sanhe 的格局规则（戊干四化表不同）`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-360] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/ziwei_dependency_adapter.py:360:            if corrected_direction == Direction.`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-361] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/ziwei_dependency_adapter.py:361:                # FORWARD: 命宫→父母→福德... (顺时针, +i)`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-135] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/engines/ziwei_method_profile.py:135:    METHOD_ID: MethodId = MethodId.SANHE`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-4] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/evaluation/l2_direction.py:4:输入: D:/TODAY/MingLi-Bench/data/data.json (200 题, 41 命主)`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-12] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/evaluation/l2_direction.py:12:  cd D:/TODAY/backend`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-22] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/evaluation/l2_direction.py:22:REPO = Path("D:/TODAY")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-173] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/forward_validation/engine.py:173:            if ev.status == ForwardValidationStatus.PAS`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-175] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/forward_validation/engine.py:175:            elif ev.status == ForwardValidationStatus.F`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-39] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:39:    SourceStatus.DISCOVERED: [So`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-40] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:40:    SourceStatus.LOCATED: [Sourc`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-41] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:41:    SourceStatus.EXTRACTED: [Sou`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-42] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:42:    SourceStatus.VERIFIED: [Sour`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-43] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:43:    SourceStatus.STRUCTURED: [So`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-44] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:44:    SourceStatus.MAPPED: [Source`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-45] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:45:    SourceStatus.VALIDATED: [Sou`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-505] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:505:        if j.status != SourceSt`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-584] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:584:    print(f"  Source ID: {sourc`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-595] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:595:    print(f"  Statement ID: {st`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-616] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/canonical_asset_acquisition.py:616:    print(f"  Judgment ID: {jud`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-399] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/source_verification.py:399:            return {"complete": False, `
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-513] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/source_verification.py:513:            if verifications and verifi`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-559] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/source_verification.py:559:    print(f"  Edition ID: {edition.edit`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-571] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/source_verification.py:571:    print(f"  Verification ID: {verific`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-596] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/judgment_architecture/source_verification.py:596:    print(f"  Variant ID: {variant.vari`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/k2g/concepts/generate_concepts.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-15] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/k2g/registry_loader.py:15:    r'D:\today\docs\k2g',`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-495] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b1_evidence_connection.py:495:        RuleStatus.EVIDENCE_VERIFIED: {RuleStatus.AD`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-496] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b1_evidence_connection.py:496:        RuleStatus.ADJUDICATED: {RuleStatus.AUTHORIZ`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-497] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b1_evidence_connection.py:497:        RuleStatus.AUTHORIZED: {RuleStatus.PRODUCTIO`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-499] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b1_evidence_connection.py:499:        RuleStatus.REJECTED: {RuleStatus.DRAFT},`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-724] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b1_evidence_connection.py:724:    loader = EvidenceLoader(Path("D:/shuntian/data/e`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-803] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b1_evidence_connection.py:803:    analysis_data = json.loads(Path("D:/shuntian/doc`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-853] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b1_evidence_connection.py:853:    output_path = Path("D:/shuntian/docs/bots/BOT-ZI`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-147] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:147:        if self.lifecycle_status == RuleLifecycleStatus.RE`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-154] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:154:        if self.lifecycle_status == RuleLifecycleStatus.EV`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-175] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:175:        RuleLifecycleStatus.EVIDENCE_VERIFIED: {`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-179] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:179:        RuleLifecycleStatus.ADJUDICATED: {`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-183] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:183:        RuleLifecycleStatus.AUTHORIZED: {`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-188] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:188:        RuleLifecycleStatus.REJECTED: {`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-378] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:378:        if status == RuleLifecycleStatus.EVIDENCE_VERIFIED`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-575] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:575:    # EVIDENCE_VERIFIED: 18条（修复 YG-003 为 EVIDENCE_VERIFIED`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-588] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:588:    # REJECTED: 8条`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-615] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:615:    print(f"     - EVIDENCE_VERIFIED: {len(evidence_verifi`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-616] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:616:    print(f"     - REJECTED: {len(rejected)}")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-667] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:667:    output_path = Path("D:/shuntian/docs/bots/BOT-ZIPING/P`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-671] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_1_remediation.py:671:    results_path = Path("D:/shuntian/docs/bots/BOT-ZIPING/`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_rule_authorization.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-345] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_rule_authorization.py:345:        if result.current_status == RuleStatus.EVIDEN`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-393] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_rule_authorization.py:393:            if result.current_status == RuleStatus.EV`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-395] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_rule_authorization.py:395:            elif result.current_status == RuleStatus.`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-519] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_rule_authorization.py:519:    loader = EvidenceLoader(Path("D:/shuntian/data/ev`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-560] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_rule_authorization.py:560:    output_path = Path("D:/shuntian/docs/bots/BOT-ZIP`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-564] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/phase_b2_rule_authorization.py:564:    results_path = Path("D:/shuntian/docs/bots/BOT-ZI`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-210] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/pipeline.py:210:        if _AUTHORITY_LOCKED:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-101] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/reasoning/signal_engine.py:101:            if ratio > _WUXING_OVER_THRESHOLD:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-103] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/reasoning/signal_engine.py:103:            elif ratio < _WUXING_UNDER_THRESHOLD:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-2] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/services/analytics_engine.py:2:Phase 8-D: Analytics Layer 模块`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-191] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/signal/canonical_signal.py:191:        if signal.event_type in EVENT_TYPE_BY_ID:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-107] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/spec/event_ontology_v1.py:107:EVENT_TYPE_BY_ID: Dict[str, EventDefinition] = {e.id: e fo`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-108] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/spec/event_ontology_v1.py:108:DOMAIN_BY_ID: Dict[str, Domain] = {e.id: e.domain for e in`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-109] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/spec/event_ontology_v1.py:109:DIRECTION_BY_ID: Dict[str, EventDirection] = {e.id: e.dire`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-133] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/spec/validation_dimensions.py:133:DIMENSION_BY_ID: Dict[str, ValidationDimension] = {`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-130] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/validation/v12/dimensions.py:130:DIMENSION_BY_ID: Dict[str, ValidationDimension] = {`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-103] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/yi/adapter.py:103:        # 层 D: 象义推导链`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-178] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/yi/interpreter.py:178:        if s.status == YiStructureStatus.VALID:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-23] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `src/tongshu/yi/schema.py:23:    IMAGE = "IMAGE"                  # 层 D: 象扩展`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-143] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/collect_baseline.py:143:    print(f"Git HEAD: {out['baseline_commit_short']} ({out['baseline_t`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/fix_paths.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-3] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/fix_paths.py:3:修复 D:/shuntian 测试文件中的错误仓库路径`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-22] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/fix_paths.py:22:    content = re.sub(r'D:/?today', '.', content)`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-23] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/fix_paths.py:23:    content = re.sub(r'D:\\\\today', '.', content)`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-70] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/fix_paths.py:70:            if '.' in content or 'D:\\today' in content:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-45] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/heluo/test_h6_hua_gong.py:45:    """RESCUED: 卦中既有化工卦又有反卦"""`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-82] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/heluo/test_h6_hua_gong.py:82:    """UNRESOLVED: 卦中既无化工卦也无反卦"""`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-154] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/spec/test_p16_production_runtime_proof.py:154:        print(f"  Canonical ID: {result.canonica`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-2] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/spec/test_vertical_slice_runtime.py:2:P1.2-D: Real Bazi Runtime Vertical Slice`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-93] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/spec/test_vertical_slice_runtime.py:93:# ─── P1.2-D: Real Runtime Tests ──────────────────────`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-4] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_full_classification.py:4:sys.path.insert(0, r"D:\shuntian\backend\src")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_heluo_context.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_k2g_baziqa.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-67] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_m2a_migration.py:67:            if vs in VERIFIED:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_p5d_relationship.py:1:"""Phase 5-D: Relationship State Engine 测试"""`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_p5d_relationship_extended.py:1:"""Phase 5-D: Relationship State Engine 补充测试`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-178] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_p6c_3c2_permanent_negative.py:178:    # UNRESOLVED: 缺少必需Feature`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-203] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_p6c_3c2_permanent_negative.py:203:    print(f"  ✓ UNRESOLVED: 缺少必需Feature")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_p8d_analytics.py:1:"""Phase 8-D: Analytics Engine 测试"""`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_phase3_p0.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-516] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_profile_gate.py:516:        """VALID: 完整 profile → 200 + profile_status=PROFILE_CALCULATI`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_time_boundary.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-2] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_ziwei_feixing_production.py:2:"""Z13-D: 飞星派生产路径 Replay 验收。`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-191] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_ziwei_feixing_rule_graph.py:191:    """Z13-D: 生产路径集成测试。"""`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-214] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_ziwei_feixing_rule_graph.py:214:        # D: 验证无诊断语义（facts 只有结构性事实，不含 INCREASE/DECLINE/ST`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-221] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/test_ziwei_z14_same_chart.py:221:    """Z14-D: 多盘验证 — 不同命盘产生不同证据。"""`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-97] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/traditional_oracle.py:97:    if direction == TraditionalDirection.FORWARD:`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-25] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tests/yi/test_p0_compute_stage_heluo.py:25:_REPO_ROOT = Path(__file__).resolve().parents[3]  # D:\\t`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tools/extract_4dim_validation.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-11] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tools/extract_4dim_validation.py:11:sys.path.insert(0, r"D:\TODAY\backend\src")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-24] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tools/extract_4dim_validation.py:24:doc_path = r"D:\today\chinese-fortune\references\64hex-full.md"`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-75] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tools/extract_4dim_validation.py:75:corpus_path = r"D:\today\nihai-tianji-corpus\docs\09-六十四卦.md"`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-125] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tools/extract_4dim_validation.py:125:out_path = r"D:\TODAY\backend\data\research\64gua_4dim_validati`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tools/extract_nihai_64gua.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-7] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tools/extract_nihai_64gua.py:7:DOC = Path(r"D:\today\nihai-tianji-corpus\docs\09-六十四卦.md")`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-77] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tools/extract_nihai_64gua.py:77:out = Path(r"D:\TODAY\backend\data\research\nihai_64gua_extract.json`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-1] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tools/generate_assertion_table.py:1:#!/usr/bin/env python3`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔴 [P0-2-ABS-5] 发现绝对路径引用

- **类别**: PATH_DEPENDENCY
- **严重级别**: P0
- **证据**: `tools/generate_assertion_table.py:5:data = json.load(open(r"D:\TODAY\backend\data\research\64gua_4di`
- **影响**: 项目移动后必然失效
- **建议**: 必须改为相对路径

### 🔵 [P0-2-GIT] Git 历史中有路径相关提交

- **类别**: GIT_HISTORY
- **严重级别**: INFO
- **证据**: `f9616c17 [BOT-MASTER] P0修复: 预任务验证脚本
62c45caf [BOT-MASTER] P0修复: 路径引用清理 + Bot配置更新
1c809925 S14-fix: ZiweiEngine.full_chart() 补 stub fallback
57dbab9a P-A1收尾: 删除decadal_soul_effect，修复大限验证测试
3d7de5bc 紫微 `
- **建议**: 检查是否有路径修复 commit

### 🔵 [P0-3-STAT] Evidence 引用统计

- **类别**: DATA_INTEGRITY
- **严重级别**: INFO
- **证据**: `总引用数: 136, 已验证: 136, 未验证: 0, 验证率: 100.0%`
- **建议**: 目标是 100% 验证率

### 🟡 [P0-3-ORPHAN] EvidenceRegistry / RuleRegistry 未被导入使用

- **类别**: MISSING_IMPLEMENTATION
- **严重级别**: P1
- **证据**: `phase_b1_evidence_connection.py 存在但无导入`
- **影响**: Registry 仅是设计，未进入生产路径
- **建议**: 建立 Registry → RuleEvaluator 的连接

### 🔴 [P0-4-MATCHER-\bsum\(] RuleMatcher 包含禁止的聚合机制: \bsum\(

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `return sum(count_conditions(c) for c in conditions["all"])
return sum(count_conditions(c) for c in conditions["any"])`
- **影响**: 违反 BOT-MASTER 禁止 score/weight/vote 作为裁决机制的规定
- **建议**: 必须移除或重构为确定性条件判断

### 🔴 [P0-4-SIGNAL-\bconfiden] SignalEngine 包含禁止的聚合机制: \bconfidence\b

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `confidence=0.5,`
- **影响**: 违反 BOT-MASTER 禁止 score/weight/vote 作为裁决机制的规定
- **建议**: 必须移除或重构为确定性条件判断

### 🔴 [P0-4-SIGNAL-\bratio\b] SignalEngine 包含禁止的聚合机制: \bratio\b

- **类别**: ARCHITECTURE_VIOLATION
- **严重级别**: P0
- **证据**: `ratio = bazi.five_element_balance[bazi_key]
if ratio > _WUXING_OVER_THRESHOLD:
elif ratio < _WUXING_UNDER_THRESHOLD:`
- **影响**: 违反 BOT-MASTER 禁止 score/weight/vote 作为裁决机制的规定
- **建议**: 必须移除或重构为确定性条件判断

### 🟡 [P0-5-SIGNAL] Signal 类缺少 domain 字段

- **类别**: MISSING_IMPLEMENTATION
- **严重级别**: P1
- **证据**: `无法区分 Signal 属于哪个辨证域`
- **影响**: 无法进行 Domain-specific Judgment Synthesis
- **建议**: 在 Signal 类中添加 domain 字段

### 🔴 [P0-5-JUDGMENT] 未发现 Domain Judgment 实现

- **类别**: MISSING_IMPLEMENTATION
- **严重级别**: P0
- **证据**: `grep 返回空`
- **影响**: Signal 直接输出，没有经过 Domain Judgment 层
- **建议**: 建立 Domain Judgment 层，将 Signal 汇总为各域 Judgment

### 🔴 [P0-5-DOMAIN] 五大辨证域中以下领域无规则: ['yongshen', 'event']

- **类别**: MISSING_IMPLEMENTATION
- **严重级别**: P0
- **证据**: `领域分布: {'wangshuai': 14, 'pattern': 20, 'yongshen': 0, 'ten_god': 21, 'event': 0}`
- **影响**: 这些领域的 Judgment 无法产生
- **建议**: 补充缺失领域的规则

### 🟡 [P0-6-ENGINE] 以下领域无独立 Engine: ['旺衰', '格局', '用神', '十神语义', '事件判断']

- **类别**: MISSING_IMPLEMENTATION
- **严重级别**: P1
- **证据**: `已找到: []`
- **影响**: 领域判断可能混入主引擎，违反单一职责
- **建议**: 为每个领域建立独立的 Judgment Engine

### 🟡 [P0-6-ORCHESTRATOR-MISSING] CrossDomainOrchestrator 缺少 Synthesis 逻辑

- **类别**: MISSING_IMPLEMENTATION
- **严重级别**: P1
- **证据**: `未发现 synthesis/merge 关键词`
- **影响**: 五大领域可能各自独立，没有 Synthesis
- **建议**: 在 Orchestrator 中建立 Synthesis 机制

### 🟡 [P0-6-TRANSFORM] 未发现 Signal → Judgment 转换逻辑

- **类别**: MISSING_IMPLEMENTATION
- **严重级别**: P1
- **证据**: `grep 返回空`
- **影响**: Signal 可能直接作为输出，没有经过 Judgment 转换
- **建议**: 建立 Signal → Judgment 转换层

### 🔵 [P0-7-PIPELINE-OK] Pipeline 未直接调用 ContextAssembler

- **类别**: INFO
- **严重级别**: INFO
- **证据**: `未发现 ContextAssembler 引用`
- **建议**: 但仍需检查间接调用

### 🔵 [P0-7-COMPUTE-STAGE] ComputeStage 调用 bazi_engine.compute()（预期行为）

- **类别**: INFO
- **严重级别**: INFO
- **证据**: `ComputeStage 是合法的 BAZI 计算入口`
- **建议**: 确认此入口是唯一的排盘调用点

### 🔵 [P0-7-SIGNAL-PRODUCE] SignalEngine 产出 Signal

- **类别**: INFO
- **严重级别**: INFO
- **证据**: `发现 Signal 构造逻辑`
- **建议**: 验证 Signal 包含必要的可追溯字段

### 🔵 [P0-7-COMPOSER-SIGNAL] Composer 接收 Signal 输入

- **类别**: INFO
- **严重级别**: INFO
- **证据**: `发现 signals 字段`
- **建议**: 验证 Signal → Canonical Content 的转换是否正确
