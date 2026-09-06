# BOT-ZIPING 审计任务单

## 任务信息

| 字段 | 值 |
|------|-----|
| **任务ID** | T-BOT-ZIPING-001 |
| **Bot ID** | BOT-ZIPING |
| **类型** | audit |
| **优先级** | P1 |
| **状态** | 🟡 PENDING → STARTING |
| **开始时间** | 2026-09-06 |
| **依赖** | 无（Phase 2，BOT-BAZI时间解析修复后启动） |

---

## 审计范围

### 1. 源代码审计

#### 1.1 核心引擎
- `src/tongshu/engines/bazi_engine.py` (1172行) - 八字主引擎
- `src/tongshu/engines/bazi_adapter.py` (56行) - 适配器层
- `src/tongshu/engines/bazi/evidence_producer.py` - 证据生产模块

#### 1.2 测试文件
- `tests/test_bazi_engine.py` - 基础功能测试
- `tests/test_bazi_boundary.py` - 边界条件测试
- `tests/test_k2g_baziqa.py` - 案例QA测试

### 2. 证据资产审计

| 证据目录 | 文件数 | 内容概述 |
|----------|--------|----------|
| `data/evidence/yuan_hai_zi_ping/` | 119 | 渊海子平证据 |
| `data/evidence/ziping_zhenquan/` | 11 | 子平真诠证据 |
| `data/evidence/di_tian_sui/` | 44 | 滴天髓证据 |
| `data/evidence/qiong_tong_bao_jian/` | 1233 | 穷通宝鉴证据（最大） |
| `data/evidence/san_ming_tong_hui/` | 9 | 三命通会证据 |

**合计证据**: ~1416个JSON文件

### 3. 审计检查清单

#### 3.1 架构合规性检查
- [ ] 是否存在未被授权的方法或类
- [ ] 是否违反了SOUL_HARD_CONSTRAINTS.md中的规则
- [ ] 代码分层是否清晰（引擎/适配器/数据层分离）
- [ ] 是否存在硬编码的魔法数字或字符串

#### 3.2 证据溯源检查
- [ ] 每个证据文件是否都有正确的来源标注
- [ ] 证据是否与源码中的规则/常量有明确引用关系
- [ ] 是否存在证据不足或来源不明的规则

#### 3.3 测试覆盖率检查
- [ ] 现有测试是否覆盖所有核心功能
- [ ] 测试断言是否基于权威数据而非sxtwl输出
- [ ] 是否存在未测试的边界情况

#### 3.4 性能与安全性检查
- [ ] 是否存在潜在的除零错误或类型错误
- [ ] 大时间跨度计算的性能问题
- [ ] 输入验证是否充分

---

## 输出要求

### 报告格式
生成以下文件：
1. `docs/bots/BOT-ZIPING/REPORT.md` - 完整审计报告
2. `docs/bots/BOT-ZIPING/TASK.md` - 本文件（任务跟踪）

### 报告内容
```markdown
# BOT-ZIPING 审计报告

## 执行摘要
- 任务: xxx
- 开始时间: xxx
- 结束时间: xxx
- 状态: SUCCESS/FAILED/BLOCKED

## 发现的问题
| ID | 严重性 | 描述 | 位置 | 状态 |
|----|--------|------|------|------|

## 修复的问题
| ID | 描述 | 修复说明 |

## 验证结果
- 测试通过: X/Y
- 证据文件: Z个
- Golden Dataset: 无修改

## 遗留问题
[列出未解决的P0/P1问题]

---
*Bot: BOT-ZIPING | Timestamp: xxx*
```

---

## 验收标准

- [ ] 所有源代码文件已审计
- [ ] 所有证据文件已抽样验证
- [ ] 所有测试已通过
- [ ] 问题已按严重性分类并记录
- [ ] 报告已保存到指定路径

---

*任务单创建时间: 2026-09-06*
*创建者: BOT-MASTER*
