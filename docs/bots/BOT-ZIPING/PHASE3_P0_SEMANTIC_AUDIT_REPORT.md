# Phase 3 P0 语义审计任务报告

**任务ID**: T-BOT-ZIPING-PHASE3-P0  
**审计日期**: 2026-09-07  
**审计范围**: 子平五大辨证域 Judgment 算法  
**审计标准**: 子平五经（滴天髓/子平真诠/穷通宝鉴/三命通会/渊海子平）  
**审计人**: BOT-ZIPING

---

## 一、审计执行摘要

### 审计目的
Phase 2 仅验证"数据正确性"（四柱计算、十神关系、地支关系），Phase 3 需验证"语义正确性"（旺衰、格局、用神判断是否符合子平经典）。

### 核心发现

| 辨证域 | 当前实现 | 语义正确性 | 严重性 |
|--------|----------|-----------|--------|
| WANGSHUAI (旺衰) | 简化布尔判断 | ❌ 不合格 | **P0** |
| GEJU (格局) | 信号类型检查 | ❌ 不合格 | **P0** |
| YONGSHEN (用神) | UNKNOWN 占位符 | ❌ 不合格 | **P0** |
| SHISHEN (十神) | 基础语义检测 | 🟡 部分合格 | P1 |
| SHIJIAN (事件) | 基础事件检测 | 🟡 部分合格 | P1 |

### 总体结论
**P0-1-C 修复完成，但 Phase 3 语义层存在重大缺陷**。Judgment 层是子平辨证的入口，若算法不正确，后续所有诊断都会偏离经典。

---

## 二、问题清单（按严重性排序）

### P0-1: WANGSHUAIJudgment 算法严重简化

**问题位置**: `src/tongshu/reasoning/judgment.py:121-180`

**当前实现**:
```python
has_sheng = any(s.get("type") == "SUPPORT" for s in signals)
has_ke = any(s.get("type") == "CONSTRAINT" for s in signals)

if has_sheng and not has_ke:
    conclusion = JudgmentConclusion.STRONG
elif has_ke and not has_sheng:
    conclusion = JudgmentConclusion.WEAK
else:
    conclusion = JudgmentConclusion.MODERATE
```

**子平经典算法要求**:
根据《滴天髓·通神论》和《子平真诠·论身强身弱》:

```
日主旺衰判定 = 得令 + 得地 + 得势 + 寒暖燥湿 + 生克制化 + 结构条件

1. 得令 (月令):
   - 月支主气为印比劫 → 得令偏旺
   - 月支主气为官杀财食 → 得令偏弱
   - 杂气月需透干才论令

2. 得地 (通根):
   - 日主在日支/时支有根 → 得地
   - 根之强弱: 临官/帝旺 > 沐浴/冠带 > 长生 > 余气

3. 得势 (党众):
   - 四柱天干透比劫印星 → 得势
   - 党众数量 > 克泄耗数量 → 偏旺

4. 寒暖燥湿:
   - 冬生喜火暖局, 夏生喜水润局
   - 调候会影响旺衰判断

5. 生克制化:
   - 月令被围克 → 得令不成立
   - 通关情况影响最终判断

6. 结构条件:
   - 从格/化格优先于普通旺衰判断
```

**置信度**: LOW (当前实现无法区分中和与偏强/偏弱)

---

### P0-2: GEJUJudgment 算法严重简化

**问题位置**: `src/tongshu/reasoning/judgment.py:183-217`

**当前实现**:
```python
has_geju_signal = any(s.get("type") in ("ACTION", "OUTPUT") for s in signals)

if has_geju_signal:
    conclusion = JudgmentConclusion.ESTABLISHED
else:
    conclusion = JudgmentConclusion.UNKNOWN
```

**子平经典算法要求**:
根据《子平真诠·立成格》:

```
格局判断 = 月令取格 + 透干成格 + 破格条件 + 成败判断

1. 月令取格:
   - 月支主气透干 → 取本气格
   - 月支中气透干 → 取中气格
   - 月支余气透干 → 取余气格
   - 杂气月 (辰戌丑未) → 主气透干方成格

2. 成格条件:
   - 正格: 印绶、官星、财星、食神、伤官、七杀
   - 变格: 从格、化格、专旺格

3. 破格条件:
   - 财破印格
   - 伤官见官
   - 七杀无制
   - 用神被冲克

4. 成败标准:
   - 成格: 用神有力、相神有情
   - 破格: 用神受损、相神无力
```

**置信度**: LOW (当前仅检查信号类型，无完整格局逻辑)

---

### P0-3: YONGSHENJudgment 完全未实现

**问题位置**: `src/tongshu/reasoning/judgment.py:220-244`

**当前实现**:
```python
return DomainJudgment(
    domain=JudgmentDomain.YONGSHEN,
    conclusion=JudgmentConclusion.UNKNOWN,
    reasoning="用神规则尚未完整授权",
    signal_ids=[],
)
```

**子平经典算法要求**:
根据《穷通宝鉴》和《子平真诠·论用神》:

```
用神判断优先级:

1. 格局用神 (优先):
   - 正格 → 取格中所需之神
   - 从格 → 顺势而为
   - 化格 → 从化神

2. 扶抑用神 (次之):
   - 身旺 → 克泄耗
   - 身弱 → 生扶

3. 调候用神 (补充):
   - 冬生 → 丙火为主
   - 夏生 → 壬水为主

4. 通关用神 (特殊):
   - 两神相战 → 取中间五行通关

5. 病药用神 (特殊):
   - 某五行过旺/过弱 → 针对性用神
```

**置信度**: NONE (当前为占位符，无实质逻辑)

---

## 三、证据追溯表

### 已存在的 Rule 证据

| Rule ID | 标题 | 来源 | 状态 | 证据引用 |
|---------|------|------|------|----------|
| DTS-101 | 日主得令(月支主气生扶)→ SUPPORT | 滴天髓 | DRAFT | E-DTS-101-001 |
| DTS-102 | 日主失令(月支主气克泄耗)→ CONSTRAINT | 滴天髓 | DRAFT | E-DTS-101-001 |
| DTS-103 | 日支通根(主气比劫)→ SUPPORT | 滴天髓 | DRAFT | E-DTS-103-001 |
| DTS-104 | 月支临官帝旺(十二长生得地)→ SUPPORT | 滴天髓 | DRAFT | E-DTS-104-001 |
| DTS-105 | 比劫透干得势(党众)→ SUPPORT | 滴天髓 | DRAFT | E-DTS-105-001 |
| DTS-106 | 得令但月令被围克→身弱 | 滴天髓 | DRAFT | E-DTS-106-001 |

**证据库统计**:
- 滴天髓 (DTS): 6 条规则
- 子平真诠 (ZPZ): 待查
- 穷通宝鉴 (QTB): 待查
- 三命通会 (SMT): 待查
- 渊海子平 (YHZP): 待查

### 缺失的证据

1. **旺衰完整判定链**: 仅 6 条规则，缺少:
   - 寒暖燥湿判定规则
   - 通根强弱判定规则
   - 党众数量对比规则

2. **格局判定链**: 0 条规则
   - 月令取格规则
   - 透干成格规则
   - 破格条件规则

3. **用神判定链**: 0 条规则
   - 扶抑用神规则
   - 调候用神规则
   - 通关用神规则

---

## 四、修复建议

### 短期修复 (Phase 3)

#### 1. WANGSHUAIJudgment 修复

**方向**: 实现完整的得令+得地+得势+寒暖燥湿算法

**核心逻辑**:
```python
class WANGSHUAIJudgment:
    @staticmethod
    def judge(signals, context):
        # 1. 得令判断
        month_god = context.month_hidden_main_ten_god
        day_master = context.day_master
        
        if month_god in ["ZHENGYIN", "PIANYIN", "BIJIAN", "JIECAI"]:
            get_ling_score = 3  # 得令
        elif month_god in ["QI_SHA", "ZHENGUAN", "ZHENGCai", "PIANCAI", "SHISHEN", "SHANGGUAN"]:
            get_ling_score = -2  # 失令
        
        # 2. 得地判断 (通根)
        di_zhi_stems = [p.hidden_stems for p in context.pillars]
        root_score = calculate_root_strength(day_master, di_zhi_stems)
        
        # 3. 得势判断 (党众)
        stems = [p.heavenly_stem for p in context.pillars]
        dangzhong_score = count_dangzhong(day_master, stems)
        
        # 4. 寒暖燥湿修正
        season_score = adjust_by_season(context.month_branch)
        
        # 5. 综合判断
        total_score = get_ling_score + root_score + dangzhong_score + season_score
        
        if total_score >= 4:
            return STRONG
        elif total_score <= -3:
            return WEAK
        else:
            return MODERATE
```

**证据引用**: 
- E-DTS-101-001 (得令)
- E-DTS-103-001 (通根)
- E-DTS-105-001 (党众)
- E-QTB-xxx-xxx (调候)

#### 2. GEJUJudgment 修复

**方向**: 实现月令→透干→成格/破格完整链

**核心逻辑**:
```python
class GEJUJudgment:
    @staticmethod
    def judge(signals, context):
        # 1. 月令取格
        month_god = context.month_hidden_main_ten_god
        month_stem_transparent = check_transparent(month_god, context.stems)
        
        # 2. 成格判断
        if month_god in ["ZHENGUAN", "QI_SHA", "ZHENGCai", "PIANCAI", ...]:
            ge_type = "正格"
        elif check_conging_pattern(context):
            ge_type = "从格"
        elif check_hua_pattern(context):
            ge_type = "化格"
        
        # 3. 破格判断
        broken = check_po_ge_conditions(context)
        
        # 4. 结论
        if not broken and ge_type in ["正格", "从格", "化格"]:
            return ESTABLISHED
        elif broken:
            return BROKEN
        else:
            return UNKNOWN
```

**证据引用**: 
- E-ZPZ-xxx-xxx (子平真诠·立成格)
- E-DTS-xxx-xxx (滴天髓·格局篇)

#### 3. YONGSHENJudgment 修复

**方向**: 实现优先级完整的用神判断链

**核心逻辑**:
```python
class YONGSHENJudgment:
    @staticmethod
    def judge(signals, context):
        # 1. 格局用神 (优先)
        if context.geju_type == "正格":
            yongshen = get_geju_yongshen(context)
        elif context.geju_type == "从格":
            yongshen = get_conging_yongshen(context)
        
        # 2. 扶抑用神 (次之)
        if not yongshen or yongshen == "UNKNOWN":
            if context.wangshuai == "STRONG":
                yongshen = get_ke_xie_hao_yongshen(context)
            else:
                yongshen = get_sheng_fu_yongshen(context)
        
        # 3. 调候用神 (补充)
        tiao_hou = get_tiao_hou_yongshen(context)
        
        return PRIMARY if yongshen else UNKNOWN
```

**证据引用**: 
- E-QTB-xxx-xxx (穷通宝鉴)
- E-ZPZ-xxx-xxx (子平真诠·论用神)

---

## 五、置信度评估

### 当前实现置信度

| 辨证域 | 置信度 | 原因 |
|--------|--------|------|
| WANGSHUAI | LOW | 仅用布尔判断，无法区分中和与偏强 |
| GEJU | LOW | 仅检查信号类型，无格局逻辑 |
| YONGSHEN | NONE | 完全占位符，返回 UNKNOWN |
| SHISHEN | MODERATE | 有基础语义检测，需完善 |
| SHIJIAN | MODERATE | 有基础事件检测，需完善 |

### 目标置信度

| 辨证域 | 目标置信度 | 实现条件 |
|--------|-----------|----------|
| WANGSHUAI | HIGH | 完整算法 + 五经证据 |
| GEJU | HIGH | 完整算法 + 五经证据 |
| YONGSHEN | HIGH | 完整算法 + 五经证据 |
| SHISHEN | MODERATE | 基础实现 + 证据追溯 |
| SHIJIAN | MODERATE | 基础实现 + 证据追溯 |

---

## 六、关键约束确认

### BOT-MASTER 明确约束

1. **禁止修改 BAZI 代码**: ✅ 已确认，本次审计仅涉及 ZIPING 判断层
2. **禁止修改 Golden Dataset**: ✅ 已确认
3. **禁止硬编码 MODERATE fallback**: ✅ 本次审计将指出此类问题

### 子平五经体系约束

1. **证据来源**: 必须引用五部经典（滴天髓/子平真诠/穷通宝鉴/三命通会/渊海子平）
2. **推理过程**: 每个判断必须有证据 ID 和推理文本
3. **禁止投票/概率**: 判断必须是确定性条件判断，非概率推断

---

## 七、下一步行动

### 紧急修复 (P0)

1. **WANGSHUAIJudgment**: 实现完整算法，引入 DTS-101~106 规则
2. **GEJUJudgment**: 实现月令→透干→成格/破格链
3. **YONGSHENJudgment**: 实现优先级用神判断链

### 完善修复 (P1)

4. **SHISHENJudgment**: 补充十神组合意义
5. **SHIJIANJudgment**: 补充事件应期判断

### 验证

6. 新增测试用例，覆盖经典案例
7. 运行负向测试，防止 regression
8. 向 BOT-MASTER 申请裁决

---

## 八、附录：关键 Rule 证据摘录

### DTS-101: 日主得令

```json
{
  "rule_id": "DTS-101",
  "title": "日主得令(月支主气生扶)→ SUPPORT",
  "source": {"work": "滴天髓", "chapter": "通神论·衰旺"},
  "evidence_refs": ["E-DTS-101-001"],
  "conditions": {
    "month_hidden_main_ten_god": ["正印", "偏印", "比肩", "劫财"]
  },
  "conclusion": "SUPPORT"
}
```

### DTS-106: 得令但月令被围克

```json
{
  "rule_id": "DTS-106",
  "title": "得令但月令被围克→身弱",
  "source": {"work": "滴天髓", "chapter": "通神论·衰旺"},
  "evidence_refs": ["E-DTS-106-001"],
  "rationale": "《滴天髓》:生方怕动库宜开,败地逢冲仔细推。月令虽得令但被围克,得令不成立,反断身弱。"
}
```

---

**审计完成时间**: 2026-09-07  
**下次更新**: 等待 BOT-MASTER 裁决后执行修复
