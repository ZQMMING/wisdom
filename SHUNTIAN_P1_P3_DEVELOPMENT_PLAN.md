# ⚠️  ARCHIVED / SUPERSEDED — 本计划已被 V13 取代，不得再作为开发依据

> 归档原因：本文档定义的 EVENT_SIGNAL 方向/置信度/冲突裁定体系与
> `ARCHITECTURE_V13_FINAL.md` 明确冲突。继续使用本文档作为任务书
> 会导致多个 Agent 按不同架构编写代码（即 "三个 Agent 看三份架构" 问题）。
>
> 权威依据：ARCHITECTURE_V13_FINAL.md（拍板时间 2026-08-28）
>
> 本文件保留仅用于历史追踪，任何新开发须以 V13 为准。

---

## 一、P0 已完成（背景，无需重做）

### 新增文件
- `src/tongshu/engines/heluo/timeline_yun.py` — 应期链核心实现：
  - `compute_dayun_liyao`：大运（爻位值运，阳爻9年/阴爻6年，元堂起行先天再接后天）
  - `compute_liunian`：流年卦逐岁推演（元堂阳爻/阴爻两套规则 + 应爻：一四应/二五应/三六应）
  - `compute_liuyue`：流月卦（以流年卦变元堂→阳月/阴月）
  - `compute_liuri`：流日卦（以月卦变爻，分五段每段六天）

### 修改文件
- `src/tongshu/engines/heluo/canonical.py`：
  - `calculate()` 新增 `birth_year` 参数
  - Step 6 由占位 `timeline=None` → 调用 `_build_timeline()` 产出完整时间序列
  - 新增 `_build_timeline()` 方法（大运+流年+流月）

### 验证结果（已确认）
- 纪晓岚 Golden Case：**PASS**（化数→先天地天泰→元堂六四→后天无妄，未破坏）
- 许家印（戊戌 壬戌 己未 乙亥，1958生）：先天水风井→元堂上六(阴)→后天巽为风，100年流年卦+每年12月卦+大运12段全通
- 项目测试：**181 passed，无回归**（唯一失败 `test_source_engine_enum` 为预存 Blind 引擎问题，与本任务无关）

### 接口说明（P1 需要消费这些产物）
`HeluoCanonical.calculate(bazi, gender, birth_hour, era, birth_year).timeline.yearly_hexagrams` 每个元素：
```python
{
  "age": int, "year": int, "ganzhi": str, "yang_year": bool,
  "hexagram": str,        # 流年卦名，如 "泽雷随"
  "upper": str, "lower": str, "lines": [int×6],  # 1=阳, -1=阴
  "months": [ {month, name, upper, lower, lines, kind(阳月/阴月)}, ×12 ]
}
```

---

## 二、P1：易经解卦层（下一个任务，优先做）

### 目标
把 `timeline_yun` 产出的流年卦/流月卦名，接到项目已有的易经卦爻辞数据上，解出**吉凶方向 + 应期信号**，输出统一 `EVENT_SIGNAL`。

### 已有数据（无需造数据，直接引用）
- `src/tongshu/engines/yi/yao_ci_data.py`：
  - `get_yao_ci(hexagram_name, line_position)` — 按卦名+爻位取爻辞
  - `get_all_yao_ci(hexagram_name)` — 取全部6条爻辞
- `src/tongshu/engines/yi/classical_text.py`：`get_classical_text(...)` — 卦辞
- `src/tongshu/engines/yi/hexagram_symbol.py` + `interpreter.py`：`analyze_line_symbol` / `expand_image` — 爻象解析
- 数据量：64卦 384爻辞齐备

### 开发步骤
1. **新建 `src/tongshu/engines/heluo/yi_interpreter.py`**（不要在 timeline_yun.py 里堆，保持体系隔离）
2. 对每个流年卦（canonical.timeline.yearly_hexagrams[i]）：
   - `get_classical_text(卦名)` → 卦辞
   - `get_all_yao_ci(卦名)` → 爻辞
   - 用元堂爻位 + 应爻 → `analyze_line_symbol` 判定动爻吉凶方向
3. **输出统一 `EVENT_SIGNAL`**（对接未来多体系收敛）：
```python
{
  "system": "HELUO",
  "rule_id": "HL-YN-<year>",
  "theme": "EVENT",
  "direction": "POSITIVE|NEGATIVE|NEUTRAL|MIXED",
  "strength": "HIGH|MEDIUM|LOW",
  "time_scope": {"year": int, "month": int|None},
  "hexagram": "泽雷随",
  "evidence": ["卦辞", "爻辞", "元堂爻位"],
  "confidence": 0.0~1.0
}
```
4. 接入 `_build_timeline()`：在 yearly 元素中附加 `yi` 解释结果

### 验收
- 许家印 2021（泽雷随）、2023（火雷噬嗑）、2017（水风井）等关键流年能解出明确吉凶方向
- 每条输出含 `evidence`（可审计），不含无据断语
- `pytest tests/ -k "heluo or yi"` 全过

---

## 三、P3：多体系互补收敛（P1 完成后再做）

### 目标
河洛流年卦信号 + 子平/盲派/紫微信号 → 同向/部分收敛/冲突/缺失裁定，替换现有占位。

### 现状
- `src/tongshu/engines/.../annual_event_evaluator.py` 里的 `HeluoScorer`/`YiScorer` 是**占位打分**（YiScorer 不看卦象、按天干硬编码0.3），必须替换为真实信号。
- 项目已有：子平引擎、盲派引擎、紫微引擎、河洛引擎（现完整）。

### 开发步骤
1. 建立 `CrossSystemValidator`：输入多个体系 `EVENT_SIGNAL`，判定：
   - `STRONG_CONVERGENCE`（多体系同主题同方向）
   - `MODERATE_CONVERGENCE`（部分同向）
   - `CONFLICT`（方向相反，不强行平均，转冲突分析）
   - `SINGLE_SOURCE`（仅单体系有据）
   - `NO_EVIDENCE`（证据不足，拒断）
2. 替换 `annual_event_evaluator.py` 中 `HeluoScorer`/`YiScorer` → 用 P1 的真实 `EVENT_SIGNAL`
3. 每个体系信号必须独立可观测、可追溯（不互相污染）

### 验收
- 同一命例、同一时间窗口，能输出收敛/冲突裁定及证据链
- 保留 27.3% 为"单一八字岁运基线"，每加一体系验证**增量**（incremental predictive value）

---

## 四、约束与红线（所有阶段）
1. **Input Boundary**：只依赖八字+出生地+性别+时间，不要求用户补行业/人际关系/事件
2. **古籍无据不妄断**：证据不足输出 `NO_EVIDENCE`，不强行生成
3. **体系隔离**：一个体系不得覆盖/污染另一体系；Signal Producer 独立可观测
4. **不破坏冻结口径**：化数→先天→元堂→后天（Golden Case 锁定）不得改动
5. **可审计**：每步保留 evidence/source_locator

---

## 五、参考文件索引
- 河洛应期链实现：`src/tongshu/engines/heluo/timeline_yun.py`
- 河洛主入口：`src/tongshu/engines/heluo/canonical.py`
- 易经数据：`src/tongshu/engines/yi/yao_ci_data.py`、`classical_text.py`
- 收敛评估：`annual_event_evaluator.py`（替换占位处）
