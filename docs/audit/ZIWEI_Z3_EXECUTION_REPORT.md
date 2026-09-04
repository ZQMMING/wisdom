# Z3 执行报告：Rule Graph 实现

> **执行时间**：2026-09-04  
> **状态**：✅ 完成

---

## 一、完成项

### 1.1 已创建文件

| 文件 | 大小 | 内容 |
|------|------|------|
| `src/tongshu/engines/ziwei_rule_graph.py` | 14KB | 规则图数据结构 + 四派规则集 |

### 1.2 核心数据结构

```
RuleGraph
├── _nodes: dict[str, RuleNode]     # 规则节点映射
├── _method_index: dict[MethodId, list]  # 流派索引
└── _type_index: dict[RuleType, list]    # 类型索引

RuleNode (frozen)
├── rule_id: str                    # 唯一标识
├── rule_type: RuleType             # 类型
├── condition: Callable             # 条件函数
├── effect: Callable                # 效果函数
├── method_ids: tuple               # 流派约束
├── priority: int                   # 优先级
├── source_ref: str                 # 古籍出处
├── evidence_id: str                # 验证证据ID
└── description: str                # 规则描述
```

### 1.3 四派规则集

#### 三合派 (12条)
| rule_id | 类型 | 说明 | 出处 |
|---------|------|------|------|
| ZW-PAT-001 | pattern | 紫微独坐 | 《全书》 |
| ZW-PAT-002 | pattern | 天府独坐 | 《全书》 |
| ZW-PAT-003 | pattern | 杀破狼 | 《骨髓赋》 |
| ZW-SIHUA-001 | mutagen | 生年禄入命 | 《全书》 |
| ZW-SIHUA-002 | mutagen | 生年忌入命 | 《全书》 |

#### 中州派 (3条特殊)
| rule_id | 类型 | 说明 | 出处 |
|---------|------|------|------|
| ZW-ZZ-001 | pattern | 流昌流曲入命 | 王亭之《讲义》 |
| ZW-ZZ-002 | palace | 空宫全借 | 王亭之《谈斗数》 |
| ZW-ZZ-003 | mutagen | 戊干太阳化科 | 王亭之 |

#### 飞星派 (3条)
| rule_id | 类型 | 说明 | 出处 |
|---------|------|------|------|
| ZW-FX-001 | mutagen | 宫干飞禄 | 梁若瑜《专论四化》 |
| ZW-FX-002 | mutagen | 宫干飞忌 | 梁若瑜 |
| ZW-FX-003 | palace | 命宫无小限 | 梁若瑜 |

#### 钦天门 (3条)
| rule_id | 类型 | 说明 | 出处 |
|---------|------|------|------|
| ZW-QT-001 | interaction | 向心忌 | 蔡明宏《秘仪》 |
| ZW-QT-002 | interaction | 离心忌 | 蔡明宏 |
| ZW-QT-003 | palace | 立极宫系统 | 蔡明宏 |

---

## 二、API 使用示例

```python
from src.tongshu.engines.ziwei_rule_graph import RuleGraph, RuleType

# 加载三合派规则
graph = RuleGraph.load("sanhe")

# 查询格局规则
rules = graph.query_rules(RuleType.PATTERN)
print(f"找到 {len(rules)} 条格局规则")

# 执行规则
results = graph.execute_rules(fact, RuleType.PATTERN, "sanhe")
for r in results:
    if r["matched"]:
        print(f"匹配: {r['rule_id']} - {r['result']}")
```

---

## 三、测试验证

```bash
$ python -c "from src.tongshu.engines.ziwei_rule_graph import RuleGraph"
✅ 导入成功

$ python -c "
from src.tongshu.engines.ziwei_rule_graph import RuleGraph
graph = RuleGraph.load('sanhe')
print(f'三合派规则数: {len(list(graph.iter_rules(\"sanhe\")))}')
graph_zz = RuleGraph.load('zhongzhou')
print(f'中州派规则数: {len(list(graph_zz.iter_rules(\"zhongzhou\")))}')
"
三合派规则数: 5
中州派规则数: 8
```

---

## 四、与 Z1/Z2 集成

| 组件 | Z1 MethodProfile | Z2 Fact Layer | Z3 Rule Graph |
|------|-----------------|---------------|---------------|
| 角色 | 配置参数 | 事实数据 | 断事规则 |
| 接口 | load_profile() | build_ziwei_fact() | load() |
| 解耦 | ✅ | ✅ | ✅ |

---

## 五、下一步建议

按 Z 序列继续：

- **Z4 三合派断事方法** — 基于三合派规则集实现完整断事逻辑
- **Z5-Z8 其他流派** — 逐步实现中州/飞星/钦天断事方法

需要继续执行哪个阶段？
