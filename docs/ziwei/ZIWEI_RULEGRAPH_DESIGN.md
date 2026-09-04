# 紫微斗数 Z3 Rule Graph 设计文档

> **创建时间**：2026-09-04  
> **状态**：设计完成，待实现  
> **基于**：Z1 MethodProfile + Z2 Fact Layer

---

## 一、设计目标

建立带 `method_id` 的规则图，使不同流派可以使用不同的规则来分析同一事实。

---

## 二、RuleGraph 数据模型

```python
@dataclass(frozen=True)
class RuleNode:
    """规则图节点"""
    
    rule_id: str                  # 规则唯一标识
    rule_type: str               # "pattern" | "mutagen" | "palace" | "interaction"
    condition: Callable           # 条件检查函数
    effect: Callable              # 效果函数（可选）
    
    # 流派约束
    method_ids: tuple[str, ...]  # 适用的流派 ("sanhe", "zhongzhou", "feixing", "qintian")
    priority: int = 0            # 优先级（越高越先执行）
    
    # 证据
    source_ref: str = ""         # 古籍出处引用
    evidence_id: str = ""        # 验证证据ID
    
    # 元数据
    version: str = "2026.09"     # 规则版本
```

---

## 三、三合派规则集

### 3.1 格局规则

| rule_id | 条件 | 流派 | 出处 |
|---------|------|------|------|
| ZW-PAT-001 | 紫微独坐命宫 | sanhe, zhongzhou | 《全书》 |
| ZW-PAT-002 | 天府独坐命宫 | sanhe, zhongzhou | 《全书》 |
| ZW-PAT-003 | 杀破狼同宫 | sanhe, zhongzhou | 《骨髓赋》 |
| ZW-PAT-004 | 日月同宫 | sanhe, zhongzhou | 《全书》 |

### 3.2 四化规则

| rule_id | 条件 | 流派 | 出处 |
|---------|------|------|------|
| ZW-SIHUA-001 | 生年禄入命宫 | sanhe | 《全书》 |
| ZW-SIHUA-002 | 生年忌入命宫 | sanhe | 《全书》 |
| ZW-SIHUA-003 | 大限禄入本命宫 | sanhe | 《全集》 |

---

## 四、中州派特殊规则

| rule_id | 条件 | 流派 | 出处 |
|---------|------|------|------|
| ZW-ZZ-001 | 流昌流曲入命宫 | zhongzhou | 王亭之《讲义》 |
| ZW-ZZ-002 | 命宫空宫全借对宫 | zhongzhou | 王亭之《谈斗数》 |
| ZW-ZZ-003 | 戊干太阳化科 | zhongzhou | 王亭之 |

---

## 五、飞星派特殊规则

| rule_id | 条件 | 流派 | 出处 |
|---------|------|------|------|
| ZW-FX-001 | 宫干飞禄入他宫 | feixing | 梁若瑜《专论四化》 |
| ZW-FX-002 | 宫干飞忌入他宫 | feixing | 梁若瑜 |
| ZW-FX-003 | 命宫无小限 | feixing | 梁若瑜 |

---

## 六、钦天门特殊规则

| rule_id | 条件 | 流派 | 出处 |
|---------|------|------|------|
| ZW-QT-001 | 向心忌（他宫化忌入本命） | qintian | 蔡明宏《秘仪》 |
| ZW-QT-002 | 离心忌（本命化忌入他宫） | qintian | 蔡明宏 |
| ZW-QT-003 | 立极宫系统 | qintian | 蔡明宏 |

---

## 七、实现路径

### Phase 1: 数据结构
1. 在 `ziwei_rule_graph.py` 定义 `RuleNode`
2. 定义 `RuleGraph` 类（有向图）

### Phase 2: 三合派规则
1. 实现基本格局规则（10条）
2. 实现四化规则（生年/大限）

### Phase 3: 中州派规则
1. 添加流昌流曲规则
2. 修改空宫处理逻辑

### Phase 4: 飞星/钦天规则
1. 实现飞化路径计算
2. 实现向心/离心忌

---

## 八、兼容性

- **向后兼容**：默认使用三合派规则集
- **渐进式**：先实现核心规则，再添加流派特殊规则
- **测试保障**：每次修改后运行完整测试套件

---

## 九、参考文档

- `docs/ziwei/ZIWEI_SCHOOL_METHODS_VERIFIED.md` - 流派方法考证
- `docs/ziwei/ZIWEI_RULES_VERIFICATION_FINAL.md` - 规则验证报告
- `docs/audit/ZIWEI_Z1_EXECUTION_REPORT.md` - MethodProfile 实现
- `docs/audit/ZIWEI_Z2_EXECUTION_REPORT.md` - Fact Layer 实现
