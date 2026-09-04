# Z2 执行报告：Fact Layer 实现

> **执行时间**：2026-09-04  
> **状态**：✅ 完成

---

## 一、完成项

### 1.1 已创建文件

| 文件 | 大小 | 内容 |
|------|------|------|
| `src/tongshu/engines/ziwei_fact_layer.py` | 8.5KB | 事实层数据结构定义 + 构建函数 |

### 1.2 核心数据结构

```
ZiweiFact (frozen dataclass)
├── five_elements_class: str          # 五行局
├── soul_earthly_branch: str          # 命宫地支
├── body_earthly_branch: str          # 身宫地支
├── soul_borrowed: bool               # 命宫是否借星
├── palaces: dict[str, PalaceFact]    # 12宫完整数据
│   ├── name: str                     # 宫名
│   ├── earthly_branch: str           # 地支
│   ├── heavenly_stem: str            # 天干
│   ├── major_stars: tuple            # 主星
│   ├── minor_stars: tuple            # 辅星
│   ├── decadal_range: tuple          # 大限范围
│   ├── decadal_stem: str             # 大限天干
│   ├── is_empty: bool                # 空宫标记
│   └── self_mutagen: tuple           # 自化列表
├── birth_mutagen: MutagenFact        # 生年四化
├── decadal_mutagen: MutagenFact      # 大限四化
├── yearly_mutagen: MutagenFact       # 流年四化
├── monthly_mutagen: MutagenFact      # 流月四化
└── daily_mutagen: MutagenFact        # 流日四化
```

### 1.3 关键设计决策

| 决策 | 说明 |
|------|------|
| **immutable** | 所有 dataclass 均为 frozen=True |
| **tuple 代替 list** | 不可变性保证 |
| **派生属性** | soul_main_stars, empty_palaces 等 |
| **工厂函数** | build_ziwei_fact() 从 raw dict 构建 |
| **空宫标记** | 自动计算，无需外部设置 |

---

## 二、与现有架构对比

| 维度 | ZiweiChart (现有) | ZiweiFact (新) |
|------|------------------|----------------|
| 数据完整性 | 仅命宫摘要 | 12宫完整 |
| 空宫处理 | 隐式（无标记） | 显式（is_empty 字段） |
| 四化存储 | 仅命宫 | 全周期（生/大/流/月/日） |
| MethodProfile | 无关联 | 独立于 Fact |
| 不可变性 | frozen | frozen（一致） |

---

## 三、测试验证

```bash
$ python -c "from src.tongshu.engines.ziwei_fact_layer import ZiweiFact"
✅ 导入成功

$ python -m pytest tests/test_ziwei_engine.py tests/test_ziwei_pattern.py -v
22 passed
✅ 向后兼容，无回归
```

---

## 四、下一步建议

按 Z 序列继续：

- **Z3 Rule Graph** — 建立带 method_id 的规则图
- **Z4-Z8 各流派断事方法** — 实现四派断事逻辑

需要继续执行 Z3 吗？
