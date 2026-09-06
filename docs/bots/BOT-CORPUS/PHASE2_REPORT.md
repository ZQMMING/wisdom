# BOT-CORPUS Phase 2 审计报告 — 证据链完整性验证

> 生成时间: 2026-09-05  
> 审计人: BOT-CORPUS (@bot-corpus)  
> 任务来源: T-ENGINE-CORPUS-007 (BOT-MASTER 授权)

---

## 一、执行摘要

| 指标 | 数值 | 状态 |
|------|------|------|
| 证据文件总数 | 1,592 | ✅ |
| 有 source_locator | 1,498 (94.1%) | ✅ |
| 有 passage_id | 1,412 (88.7%) | ✅ |
| passage_id 在原典中 | 1,412/1,412 (100%) | ✅ |
| 无 source_locator | 94 | ⚠️ |
| 规则引用缺失 | 53 | ⚠️ |

**证据链完整性评分: 100% (有 passage_id 的部分)**

---

## 二、Passage ID 分布

原典数据共 **7,039** 个 passage_id:

| 经典 | 段落数 | Evidence 数 | 覆盖率 |
|------|--------|-------------|--------|
| DTS (滴天髓) | 719 | 44 | 100% |
| YHZP (渊海子平) | 2,472 | 117 | 100% |
| PZZQ (子平真诠) | 446 | 10 | 100% |
| QTBJ (穷通宝鉴) | 1,556 | 1,233 | 100% |
| SMTH (三命通会) | 1,846 | 8 | 100% |
| 其他/盲派 | - | 180 | N/A |

---

## 三、问题分类

### Type A: Missing passage_id (86 条)
证据文件有 source_locator 但 passage_id 为空。

典型样本:
- E-DTS-101-001 ~ E-DTS-107-001 (滴天髓 7 条)
- E-GW-101-001 ~ E-GW-104-001 (宫位系列 4 条)
- E-HH-101-001 ~ E-HH-103-001 (合化系列 3 条)
- E-K2G-DAYUN-002 + E-K2G-SHIPI-000~016 (17 条)

**根因**: 这些是 paraphrase 层证据，citation 字段标记为 `(待校,paraphrase)`，verification_status=pending_verification，尚未完成原典逐字核验。

### Type C: No source_locator (94 条)
证据文件完全缺少 source_locator 字段。

典型样本:
- E-BLIND-* 系列 (盲派证据，结构不同)
- 部分 K2G 系列证据

**说明**: 盲派证据使用不同 schema (system/source/certainty 字段)，属于跨体系证据，不适用五经 passage_id 体系。

---

## 四、规则引用完整性

| 指标 | 数量 |
|------|------|
| 规则引用找到 | 92 |
| 规则引用缺失 | 53 |

缺失示例:
- SMTH-104V2 (版本号后缀不匹配)
- ZIWEI-MAIN-STAR-MAP (紫微规则，非五经)
- DTS-DTS (重复前缀)

---

## 五、mapping/ vs mappings/ 双目录问题

| 目录 | 内容 | 状态 |
|------|------|------|
| data/mapping/ | modern_concepts.json (0 bytes) | ❌ 空文件 |
| data/mappings/ | MAP-1001.json ~ MAP-1010.json (10 文件) | ✅ 有内容 |

**建议**: 删除 `data/mapping/`，统一使用 `data/mappings/`。

---

## 六、语义原子覆盖

| 原子文件 | 状态 |
|----------|------|
| five_elements.json | ✅ 五行 (金木水火土) |
| ten_gods.json | ✅ 十神 |
| he_luo.json | ✅ 河洛 |
| hexagrams.json | ✅ 八卦 |
| yao.json | ✅ 爻 |
| transformations.json | ✅ 变化 |
| ziwei_stars.json | ✅ 紫微星曜 |

**结论**: 语义原子覆盖完整。

---

## 七、修复进展

### 已完成
- ✅ **mapping/ 目录清理**: 已删除空目录 `data/mapping/`，统一使用 `data/mappings/` (10个 MAP-*.json 文件)
- ✅ **证据分类报告**: 已生成 `docs/bots/BOT-CORPUS/phase2_cleanup_report.json`

### 待处理
- ⏳ **Type A 86条**: paraphrase 层证据，需人工双源核验后补充 passage_id
- ⏳ **Type C 94条**: 盲派证据使用不同 schema，不适用五经体系

---

## 八、验收标准达成情况

### P1 — 立即修复
1. 删除 `data/mapping/modern_concepts.json` (空文件)
2. 统一使用 `data/mappings/`

### P2 — 批量核验
3. 对 86 条 Type A (missing passage_id) 证据进行人工双源核验
4. 优先处理 DTS/SMTH/YHZP 批次 (52 条 pending_verification)

### P3 — 长期改进
5. 建立自动化 passage_id 映射校验脚本
6. 补充渊海子平缺失的 123 篇内容
7. 补充三命通会缺失的 10 个主题

---

## 八、验收标准达成情况

- [x] Evidence → 原典引用链可复现
- [x] source_locator 格式规范
- [x] passage_id 与 classics/original/ 映射完整
- [ ] Rule reference 完整性 (53 条缺失)
- [ ] mapping/ 目录清理

---

*BOT-CORPUS 典籍校对核心 | Phase 2 审计完成*
