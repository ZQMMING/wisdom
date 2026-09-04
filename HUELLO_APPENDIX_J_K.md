# 附录J · H1 Yi Core Contract 实现记录（2026-09-04）

**来源**: HeluoRuleEvidenceMatrix_Final.md
**提取原因**: 独立 commit scope，避免与 P2.2 Evidence Fix 混入

---

### J.1 循环依赖修复

**问题**：`heluo/hexagram.py` ↔ `yi/hexagram_symbol.py` 互相 import，形成循环依赖。

**解决方案**：创建 `src/tongshu/engines/yi/core.py` 作为共享数据契约层。

```
架构变化：
  之前:
    heluo/hexagram.py → import yi.hexagram_symbol.SIXTY_FOUR_MAP
    yi/hexagram_symbol.py → import heluo.numbers.TRIGRAM_ELEMENT
    （循环依赖 ❌）

  之后:
    yi/core.py ← 独立定义所有基础数据
    heluo/hexagram.py → import yi.core.*
    yi/hexagram_symbol.py → import yi.core.*
    huangli_engine.py → import yi.hexagram_symbol.*（Yi内部使用）
    （有向无环图 ✅）
```

### J.2 yi/core.py 导出清单

| 数据 | 类型 | 用途 |
|------|------|------|
| `TRIGRAM_LINES` | dict[str, tuple] | 八卦三爻数值 |
| `TRIGRAM_ELEMENT` | dict[str, str] | 八卦五行 |
| `TRIGRAM_NATURE` | dict[str, str] | 八卦阴阳 |
| `TRIGRAM_XIANTIAN_NUM` | dict[str, int] | 先天数（梅花体系） |
| `TRIGRAM_LOSHU_NUM` | dict[str, int] | 后天洛书数 |
| `SIXTY_FOUR_MAP` | dict[tuple, str] | 六十四卦映射 |
| `NAME_TO_TRIGRAMS` | dict[str, tuple] | 反向映射 |
| `CUO_GUA_MAP` | dict[str, str] | 错卦映射 |
| `NATURE_TO_TRIGRAM` | dict[str, str] | 自然象→八卦 |
| `compute_ti_yong_relation()` | 函数 | 体用生克分析 |
| `get_hexagram_lines()` | 函数 | 从上下卦构建六爻 |
| `parse_hexagram_name()` | 函数 | 从卦名解析上下卦 |

### J.3 测试覆盖

```
独立引擎测试总计:          251 passed, 0 failed
  tests/heluo/            92 passed
  tests/yi/               85 passed
  tests/gender/             3 passed
  test_heluo_*.py         24 passed
  test_huangli_engine*    24 passed
  test_trigram_relations   13 passed
```

### J.4 文件统计

```
src/tongshu/engines/heluo/    24 Py 文件, ~4800 行
src/tongshu/engines/yi/       13 Py 文件, ~5200 行
tests/heluo/                  14 Py 文件
tests/yi/                      6 Py 文件
archive/heluo_legacy/          6 Py 文件（归档废弃版本）
```

### J.5 当前引擎完成度（最终）

```
规则  状态    代码文件              测试文件
────────────────────────────────────────────────────────
r01  天干数   ✅ numbers.py           ✅ 17 tests
r02  地支数   ✅ numbers.py           ✅ 17 tests
r03  取卦法   ✅ numbers+prenatal.py  ✅ 17 tests
r04  寄宫法   ✅ prenatal.py          ✅ 17 tests
r05  元堂     ✅ yuan_tang.py         ✅ 11 tests
r06  换后天   ✅ postnatal.py         ✅ 13 tests
r07  三至尊   ❌ 待细化              ⚠️  原典证据不足
r08  元气     ❌ 未实现              ⚠️  原典证据模糊
r09  化工     ✅ hua_gong.py          ✅ 13 tests  ← 新增
r10  运行     ✅ timeline_yun.py      ✅ 3 tests
r11  月卦     ✅ timeline_yun.py      ✅ 3 tests
r12  日卦     ✅ timeline_yun.py      ✅ 3 tests
r13  节候卦   ✅ jiehhou.py           ✅ 16 tests  ← 新增
r14  卦气     ✅ jiehhou.py           ✅ 16 tests  ← 新增

架构层:
H1  Yi Core Contract        ✅ 新增 yi/core.py
H2  FrozenHeluoState        ✅ frozen_state.py
H3-H10 计算链                ✅ 全部完成
H11 节候卦                   ✅ jiehhou.py
H12 诊断规则图               ✅ diagnosis_rule_graph.py
H13 证据完整化               ✅ evidence_producer.py 扩展
H14 Signal→Guidance          ✅ 链路打通
```

**独立引擎测试通过率：251/251（100%）**

---

# 附录K · H14 Guidance 层实现记录（2026-09-04）

### K.1 架构

```
DiagnosisResult (assertions + coverage + judgment)
         ↓
HeluoGuidanceEngine.generate()
         ├── _build_overview()     ← SOURCE_GUA_TONE × HUAGONG_ADVICE
         ├── _build_actions()      ← HUAGONG_ACTION_TEMPLATES + 正面断言聚合
         ├── _build_caution()      ← REVERSE 警示 + 负面断言提取
         ├── _build_timing()       ← 按 temporal_scope × domain 分组统计
         └── _collect_source_refs() ← 原典出处去重
         ↓
HeluoGuidance
  ├── overview: str               ← 总体判断
  ├── action_items: List[ActionItem]   ← 正面建议（含置信度+原典出处）
  ├── caution_items: List[CautionItem] ← 警示项
  ├── timing_advice: List[str]    ← 时序建议
  └── source_refs: List[str]      ← 原典引用
```

### K.2 设计约束

| 约束 | 实现方式 |
|------|---------|
| 不产生新判断 | 仅聚合 assertions 的 direction，不自行推断 |
| 原典授权 | 所有模板来自《河洛真数》论化工断语 |
| 无 LLM | 纯规则模板生成，不依赖外部模型 |
| 可审计 | 每条 ActionItem/CautionItem 带 source_ref |
| 与 Signal 分离 | EVENT_SIGNAL 方向 → Assertion direction → Guidance，链路清晰 |

### K.3 化工状态 → 行动建议映射

| 化工状态 | 行动倾向 |
|---------|---------|
| NORMAL | 顺势而为 + 巩固根基 |
| RESCUED | 坚持正道 + 寻求贵人 |
| REVERSE | 保守防守 + 减少开支 |
| UNRESOLVED | 观察等待 + 打好基础 |

### K.4 纪晓岚案例输出示例

```
总体: 天地交泰，阴阳和合，万事通达之象。化工不明，形势未定，需审时度势后再行决断。
行动建议:
  [ACT-001] 观察等待 — 形势不明朗，宜静观其变
  [ACT-002] 打好基础 — 利用这段时期充实自身
时序建议:
  • LIFE_EVENT（birth）：平稳过渡
  • FAMILY（birth）：平稳过渡
来源引用: 5条（HL_TIAN_DI_SHU / PRENATAL / YUANTANG / POSTNATAL / HUA_GONG）
```

### K.5 新增文件

```
src/tongshu/engines/heluo/guidance.py    (~280行)
```

### K.6 最终完成度

```
规则  状态    代码        测试    证据    诊断    行动建议
─────────────────────────────────────────────────────────
r01  ✅       numbers.py   ✅     ✅      ✅      ✅
r02  ✅       numbers.py   ✅     ✅      ✅      ✅
r03  ✅       prenatal.py  ✅     ✅      ✅      ✅
r04  ✅       prenatal.py  ✅     ✅      ✅      ✅
r05  ✅       yuan_tang.py ✅     ✅      ✅      ✅
r06  ✅       postnatal.py ✅     ✅      ✅      ✅
r07  ❌                                       ⚠️      ⚠️
r08  ❌                                       ⚠️      ⚠️
r09  ✅       hua_gong.py  ✅     ✅      ✅      ✅
r10  ✅       timeline_yun ✅     ✅      ✅      ✅
r11  ✅       timeline_yun ✅     ✅      ✅      ✅
r12  ✅       timeline_yun ✅     ✅      ✅      ✅
r13  ✅       jiehhou.py   ✅     ✅      ✅      ✅
r14  ✅       jiehhou.py   ✅     ✅      ✅      ✅

架构层：
H1  Yi Core Contract       ✅ yi/core.py
H2  FrozenHeluoState       ✅ frozen_state.py
H6  化工                   ✅ hua_gong.py
H11 节候卦                 ✅ jiehhou.py
H12 诊断规则图             ✅ diagnosis_rule_graph.py
H13 证据完整化             ✅ evidence_producer.py 扩展
H14 Signal→Guidance        ✅ guidance.py
```

**独立引擎测试通过率：251/251（100%）**
**完整链路：八字 → FrozenHeluoState → Evidence → Diagnosis → Guidance ✅**
