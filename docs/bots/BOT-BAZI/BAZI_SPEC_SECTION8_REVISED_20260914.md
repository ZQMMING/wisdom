# 八字排盘 L0 输出规范修订 —— §8 时间层字段表补全

> 依据 2026-09-14 最终裁决五：**"spec 漏了，不是实现漂移，修正 spec。"**
> 本文件是桌面《八字排盘.txt》（SHA-1 `16c958d`）第8组时间层的**修正版规范**，补全被遗漏的流月/流日/流时十神与各级关系字段。txt 原件未改动；如需回写桌面文件请另行指示。
> 实现状态：本表全部字段已在 `bazi_engine_spec.py` 落地（`build_spec_output` 顶层 + `time_axis_facts` 结构）。

---

## 一、原 spec 第8组（遗漏版）

```
dayun_list / dayun_gan / dayun_zhi / dayun_shishen        ✅ 有
liunian / liuyue / liuri                                  ✅ 有
dayun_yuanyuan / liunian_yuanyuan / liuyue_yuanyuan / liuri_yuanyuan  ✅ 有
liuyue_shishen / liuri_shishen                            ❌ 未列（实现有，spec 漏）
liushi / liushi_shishen                                   ❌ 未列
dayun_relations / liunian_relations / ...                 ❌ 未列
```

## 二、补全后 §8 时间层字段表（v2）

| 字段 | 类型 | 说明 | 实现位置 |
|---|---|---|---|
| dayun_list | list | 每步大运：pillar + start_age/end_age + **start_date/end_date（公历）** | `build_spec_output.dayun_list` |
| dayun_gan / dayun_zhi | str | 当前大运干支 | 顶层 |
| **dayun_shishen** | dict | 大运天干十神 + 支藏干十神 | 顶层 |
| **dayun_relations** | dict | 大运与原局关系（= relations_with_natal） | `time_axis_facts.dayun` |
| liunian_gan / liunian_zhi | str | 当前流年干支 | 顶层 |
| **liunian_shishen** | dict | 流年天干十神 + 支藏干十神 | 顶层 |
| **liunian_relations** | dict | 流年与原局 + 与大运关系 | `time_axis_facts.liunian` |
| liuyue_gan / liuyue_zhi | str | 当前流月干支 | 顶层 |
| **liuyue_shishen** ← 新增 | dict | 流月天干十神 + 支藏干十神 | 顶层（实现早已有） |
| **liuyue_relations** ← 新增 | dict | 流月与原局 + 大运 + 流年关系 | `time_axis_facts.liuyue` |
| liuri_gan / liuri_zhi | str | 当前流日干支 | 顶层 |
| **liuri_shishen** ← 新增 | dict | 流日天干十神 + 支藏干十神 | 顶层（实现早已有） |
| **liuri_relations** ← 新增 | dict | 流日与原局 + 大运 + 流年 + 流月关系 | `time_axis_facts.liuri` |
| liushi_gan / liushi_zhi | str | 当前流时干支（五鼠遁） | 顶层 `liushi` |
| **liushi_shishen** ← 新增 | dict | 流时天干十神 + 支藏干十神 | `time_axis_facts.liushi` |
| **liushi_relations** ← 新增 | dict | 流时与原局 + 大运 + 流年 + 流月 + 流日关系 | `time_axis_facts.liushi` |

## 三、relations 结构（统一约定）

每个 scope 的 relations 与上层逐级递进、**scope 独立不覆盖**：

```
dayun.relations_with_natal       = {liuhe, liuchong, sanhe, banhe, sanxing, liuchuan, liupo, liujue, anhe, gan_wuhe, gan_chong}
liunian.relations_with_natal     = 同上（vs 原局）
liunian.relations_with_dayun     = {gan: [...], zhi: [...]}（两柱间，干支分别）
liuyue.relations_with_liunian    = 同上（vs 上一层）
liuri.relations_with_liuyue      = 同上
liushi.relations_with_liuri      = 同上
```

## 四、铁律（与最终裁决四一致）

- 时间轴只出 **Fact**：干支、十神、与原局/大运/上一层关系、精确起止日期
- **禁止**：各 scope 的旺衰、格局、喜忌、任何判断
- 十神为客观对应关系（日主定十神），非吉凶判断

## 五、验收锚点（标准案例 1980-06-22 巳时，2026-09-14 12:00）

| scope | 干支 | 天干十神 | 起止 |
|---|---|---|---|
| dayun | 丁亥 | 劫财 | 2020-07-07 → 2030-07-07 |
| liunian | 丙午 | 比肩 | — |
| liuyue | 丁酉 | 劫财 | — |
| liuri | 辛卯 | 正财 | — |
| liushi | 甲午 | 偏印 | — |

（实测值见 `tests/test_bazi_spec_l0.py::test_time_axis_facts_six_scopes`）
