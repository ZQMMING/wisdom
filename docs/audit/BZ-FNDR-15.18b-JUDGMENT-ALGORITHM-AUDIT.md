# BZ-FNDR-15.18b — Judgment Algorithm Audit (五域 provenance 实测)

> **Audit-only / Code=0 / Evidence=0 / Rule=0 / Algorithm=0 / 单文件审计记录**
>
> 前置：15.18 commit `568c1d89` 锁定 "Loaded ≠ Production-Admitted"
> User 2026-09-11 授权 15.18b：逐域实测 DomainJudgment 的真实 conclusion / rule_refs / evidence_refs
>
> **3 状态分类** (User 锁定)：
> ① 算法 UNKNOWN → 不应产 Claim
> ② 有结论但 ref 缺失 → **Judgment Algorithm 缺陷**（Composer 不补）
> ③ 有结论 + refs 完整 → 才有资格进入 Composer

---

## 0. 元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.18b |
| 前置 | 15.18 |
| 探针 | `scripts/audit_15_18b_judgment.py`（一次性, 探针已删） |
| 状态 | **AUDIT COMPLETE** |

---

## 1. 实测方法

调用真实 production 入口 `tongshu.reasoning.ziping_bridge.run_ziping_judgment(bazi_chart)`：

```python
# 拿真实 bazi_chart (production TONGSHUPipeline.compute_stage)
bazi_chart = pipeline.compute_stage.run(...).bazi_chart
synthesis = run_ziping_judgment(bazi_chart)
```

实测输入参数：birth_date=(1990,1,1,12) gender=male analysis_date=(2024,1,1)
（与 15.17b 实测同输入，便于对比）

---

## 2. 五域实测结果（真实 production 调用）

### 2.1 WANGSHUAI 域

```text
conclusion:    WEAK
rule_refs:     ['DTS-102', 'DTS-106', 'DTS-105']
evidence_refs: ['E-DTS-101-001', 'E-DTS-106-001', 'E-DTS-105-001']
signal_ids:    []
reasoning:     失令:月令ZI主气正官克泄耗日主BING(-2); 月令ZI被WU冲(围克),
               得令不成立(-2); 十二干生旺死绝:日主BING于月支ZI处胎(中性);
               党众:帮身(印比劫)1 vs 克泄耗1(+0);
               综合评分-4<=-3,判身弱(衰)
```

**状态：③ 有结论 + refs 完整 ✅**

**实现机制**（实测 judgment.py L347-496）：
- 使用 `_Citations` 类（L149-164）：每次 `cits.add("DTS-101")` 自动从 CITATION 表（L123-144）查 `(rule_id, evidence_id)` 双填
- WANGSHUAI 8 处 cits.add 调用，覆盖 DTS-101/102/104/105/106/107 + SMTH-101/102
- 部分 evidence 复用（E-DTS-101-001 服务 DTS-101/102 反义）

### 2.2 GEJU 域

```text
conclusion:    BROKEN
rule_refs:     ['ZPZ-111', 'ZPZ-106', 'ZPZ-110', 'DTS-106']
evidence_refs: []          ← 空
signal_ids:    []
reasoning:     月令取格:月支ZI主气正官→正官格; 伤官见官; 月令ZI被冲,格有破损
```

**状态：② 有结论但 evidence_refs 缺失 ⚠️**

**实现缺陷定位**（实测 judgment.py L662-715）：
- GEJU judge 函数有 **8 处** `rule_refs.append("ZPZ-xxx")` 调用
- **0 处** `evidence_refs.append(...)` 调用
- 域主 return 路径（L735-741）确实填 `evidence_refs=list(dict.fromkeys(evidence_refs))`，但 evidence_refs list 自始未被填充
- **这是 Judgment Algorithm 已知缺陷，不是 Composer 能修补的**

### 2.3 YONGSHEN 域

```text
conclusion:    PRIMARY
rule_refs:     []          ← 空
evidence_refs: []          ← 空
signal_ids:    []
reasoning:     格局用神:正官格→取正印; 调候用神:季节WINTER→比肩
```

**状态：② 有结论但 refs 全空 ❌**

**实现缺陷定位**（实测 judgment.py L750-902）：
- YONGSHEN judge 函数 L815-817 有 `rule_refs.append(rr[0])` + `evidence_refs.append(rr[1])` 模式
- 模式仅在 **"格局用神" 路径**触发（L804-818）
- L813 `rr = GEJU_RULE_BY_GE.get(ge_type, (None, None))` — 当 ge_type="正官格" 等主流格局时，**`GEJU_RULE_BY_GE` 表只有 5 个键**：
  - 建禄格 / 月劫格 / 阳刃格 / 从格 / 专旺格
  - 缺：正官格 / 七杀格 / 正印格 / 偏印格 / 正财格 / 偏财格 / 食神格 / 伤官格（8 个主流格）
  - 实测 case 是 "正官格" → `GEJU_RULE_BY_GE.get("正官格")` → `(None, None)` → **refs 全空**
- **这是 Judgment 数据表不完整缺陷**（不是 Composer 能修补的）

### 2.4 SHISHEN 域

```text
dj = None (域未执行)
```

**状态：① 算法没有产生结论 (域未执行)**

**实测原因**：SHISHENJudgment (judgment.py L941-984) STATUS="P1-REVIEW" PRODUCTION_READY=False（15.18 已锁定）。
且 `ziping_bridge.run_ziping_judgment` signals_by_domain 为空时，该域直接不创建 DomainJudgment。
即便创建，SHISHEN judge L979-984 也**完全没有 rule_refs/evidence_refs 字段**（默认空 list）。

### 2.5 SHIJIAN 域

```text
dj = None (域未执行)
```

**状态：① 算法没有产生结论 (域未执行)**

**实测原因**：SHIJIANJudgment (judgment.py L987-1014+) 同 SHISHEN：STATUS="P1-REVIEW"。
且 15.14 审计已坐实：6 候选方法（冲/刑/害/合/三合/空亡）③Method / ④Event Mapping 全仓 0 命中。
**15.18b 不允许因为 Composer 接入而"补出事件结论"（User 红线）**。

---

## 3. 五域状态矩阵

| 域 | conclusion | rule_refs | evidence_refs | 状态 | 来源 |
|---|---|---|---|---|---|
| WANGSHUAI | WEAK | DTS-102/106/105 | E-DTS-101-001/106-001/105-001 | **③ 完整** ✅ | cits.add + CITATION 双填 |
| GEJU | BROKEN | ZPZ-111/106/110 + DTS-106 | **[]** | **② 缺 ev** ⚠️ | algorithm 缺 evidence_refs.append |
| YONGSHEN | PRIMARY | **[]** | **[]** | **② refs 全空** ❌ | GEJU_RULE_BY_GE 表不完整（缺 8 主流格） |
| SHISHEN | None | — | — | **① 域未执行** | P1-REVIEW, 不生产 |
| SHIJIAN | None | — | — | **① 域未执行** | P1-REVIEW, 15.14 FAIL |

**③ 域数：1/5 = 20%**（仅 WANGSHUAI 有资格进入 Composer）
**② 域数：2/5 = 40%**（GEJU/YONGSHEN 有 Judgment Algorithm 缺陷）
**① 域数：2/5 = 40%**（SHISHEN/SHIJIAN 域未执行）

---

## 4. Judgment Algorithm 缺陷精确定位

### 4.1 GEJU evidence_refs 缺失

**judgment.py L662/670/682/700/703/704/710/715**：8 处 `rule_refs.append(...)` 调用
**judgment.py L662-715 区间**：0 处 `evidence_refs.append(...)` 调用

**最小修复方案**（不替你拍板）：在每处 `rule_refs.append("ZPZ-xxx")` 后补 `evidence_refs.append("E-ZPZ-xxx-001")`，需要查 CITATION 表。

### 4.2 YONGSHEN refs 全空

**judgment.py L257-280** `GEJU_RULE_BY_GE` 表：只有 5 个格局键
缺：正官/七杀/正印/偏印/正财/偏财/食神/伤官（共 8 个主流格）

**最小修复方案**：在 GEJU_RULE_BY_GE 表补 8 个主流格 → (rule_id, evidence_id) 映射。

### 4.3 SHISHEN/SHIJIAN P1-REVIEW 状态

SHISHEN/SHIJIAN 两个域：
- `STATUS = "P1-REVIEW"` 是类的静态字段
- `PRODUCTION_READY = False`
- 等待 Pipeline 注入 `semantic_signals` / `event_signals` 后才能开启

**不是 Composer 修补的范围**——是 Pipeline 信号注入层的责任（已登记 P1）。

---

## 5. 与 15.18 Rule Admission 的交叉验证

| 域 | 15.18 Rule 可用性 | 15.18b Judgment 引用 | 交叉验证 |
|---|---|---|---|
| WANGSHUAI | DTS-101/102/106/105 + SMTH-101 + DTS-104/107 全部命中 RuleLoader.rules | cits.add 完整 | ✅ 算法引用 ⊆ 生产 RuleLoader |
| GEJU | ZPZ-111/106/110 + DTS-106 全部命中 | rule_refs 完整 | ⚠️ 算法引用 ⊆ RuleLoader，但 evidence_refs 算法侧缺 |
| YONGSHEN | 期望引用 ZPZ-*（主流格）但 GEJU_RULE_BY_GE 不覆盖 | refs 全空 | ⚠️ RuleLoader 已加载，但 Judgment 算法不引用 |
| SHISHEN | — | 域未执行 | N/A |
| SHIJIAN | — | 域未执行 | N/A |

**关键观察**：
- RuleLoader 加载的 21 条 ZiPing rules **已被 Judgment 算法部分引用**（WANGSHUAI/GEJU 实测命中）
- 但 Judgment 算法本身**实现不完整**（GEJU 缺 evidence_refs，YONGSHEN 缺主流格映射）
- 这是**双向断裂**：
  - 16 条 active+validated ZiPing rules 中仅 8 条被引用
  - 被引用的 8 条中部分缺 evidence 链接

---

## 6. Composer activation 的真实阻碍图（修正后）

```text
Composer ON 真正需要的条件:

Step 1: WANGSHUAI ✅  (refs 完整)
Step 2: GEJU      ⚠️  → judgment.py 修补 evidence_refs.append (algorithm 改动)
Step 3: YONGSHEN  ❌  → judgment.py 补 GEJU_RULE_BY_GE 主流格 8 条 (data 改动)
Step 4: SHISHEN   🔒  → Pipeline 注入 semantic_signals (Stage 1 红线外)
Step 5: SHIJIAN   🔒  → 15.14 Method Audit PASS + 信号注入 (冻结)
Step 6: 21 Ziping rules admission  → 15.18 Path X (production admitted)
Step 7: RenderStage mapping      → 15.19 (词库覆盖 AC-ZP-*)
Step 8: Composer activation       → Stage 2 解锁

所有 Step 都没碰 G1 / 不需要修改 G1 (实测坐实 G1 不是 bug)
但每一个 Step 都触发不同的施工门
```

---

## 7. 当前门状态

```text
G0-1 Index                       🟢 PASS
G0-2 Provenance                  🟢 PASS
INT-01~03 Stage 1                🟢 CLOSED
INT-05 Composer Module           🟢 MODULE PASS
INT-06 接入点                     🟢 CODE PASS
15.17 Activation Contract        🟢 AUDIT COMPLETE
15.17b Rule ID Investigation     🟢 COMPLETE
15.18 Rule Admission Audit       🟢 COMPLETE
15.18b Judgment Algorithm Audit  🟢 COMPLETE (本次, 5 域 provenance 实测坐实)

Composer Production              🔴 BLOCKED
P0-1 完整闭环                     🔴 NOT CLOSED (3 独立路径未闭合)
SHIJIAN Event-Signal             🔴 FAIL / FROZEN
G1                               🔒 LOCKED
RenderStage                      🔒 LOCKED
GitHub push                      🔴 暂不推 (17 commits 本地领先)
```

---

## 8. 待你裁决

### 8.1 15.18b 实测结论接受？

特别确认：
1. **5 域实测分类**：① SHISHEN/SHIJIAN (40%) / ② GEJU/YONGSHEN (40%, Judgment 算法缺陷) / ③ WANGSHUAI (20%)
2. **GEJU 缺陷**：8 处 rule_refs.append 无对应 evidence_refs.append（算法实现不完整）
3. **YONGSHEN 缺陷**：GEJU_RULE_BY_GE 表只覆盖 5 特殊格，缺 8 个主流格映射
4. **WANGSHUAI 是唯一完整域**，可独立走 Composer 测试（如果 User 单独授权）

### 8.2 下一步（按 User 锁定顺序）

| 步骤 | 选项 |
|---|---|
| ✅ 15.18b 已完成 | Judgment Algorithm Audit |
| 下一步 → | **15.19 RenderStage Mapping Audit**——评估 AC-ZP-* mapping_registry 覆盖可行性 |
| 之后 | 15.20 Admission Architecture Audit——X/Y/Z 路径选择 |

按 B → C → D 顺序，继续启动 **15.19 RenderStage Mapping Audit**？

*Generated by BOT-MASTER on 2026-09-11*
*Code Change = 0 / Evidence Change = 0 / Rule Change = 0 / Algorithm Change = 0*
*5 域实测 (run_ziping_judgment + bazi_chart) + judgment.py 缺陷精确定位*
*探针脚本 (scripts/audit_15_18b_judgment.py) 已删除*
