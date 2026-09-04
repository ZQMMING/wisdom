# 紫微斗数 Z4-Z8 实现计划

> **创建时间**：2026-09-04  
> **状态**：设计完成，待实现  
> **前置条件**: Z1 MethodProfile ✅ + Z2 Fact Layer ✅ + Z3 Rule Graph ✅

---

## 一、实现顺序

```
Z4 三合派断事方法 → Z5 中州派断事方法 → Z6 飞星派断事方法 → Z7 钦天门断事方法 → Z8 API 集成
```

---

## 二、各阶段设计

### Z4 三合派断事方法

**文件**: `src/tongshu/engines/ziwei_sanhe.py`

**职责**:
- 基于 RuleGraph 的三合派规则集
- 实现格局识别（三方四正分析）
- 实现四化解读
- 实现命盘整体分析

**关键方法**:
```python
class SanheAnalyzer:
    def __init__(self, fact: ZiweiFact):
        self.fact = fact
        self.rules = RuleGraph.load("sanhe")
    
    def analyze_palace(self, palace_name: str) -> dict:
        """分析指定宫位"""
    
    def analyze_sihua(self) -> list[dict]:
        """分析生年四化落宫"""
    
    def analyze_pattern(self) -> list[dict]:
        """识别格局"""
    
    def full_analysis(self) -> dict:
        """完整命盘分析"""
```

**依据**: 《紫微斗数全书》《全集》

---

### Z5 中州派断事方法

**文件**: `src/tongshu/engines/ziwei_zhongzhou.py`

**职责**:
- 继承三合派基础
- 添加流昌流曲分析
- 修改空宫处理（全借对宫）
- 特殊四化解读（戊干太阳化科）

**关键扩展**:
```python
class ZhongzhouAnalyzer(SanheAnalyzer):
    def __init__(self, fact: ZiweiFact):
        super().__init__(fact)
        self.rules = RuleGraph.load("zhongzhou")
    
    def analyze_liuchangliuqu(self) -> dict:
        """分析流昌流曲"""
    
    def analyze_empty_palace(self) -> dict:
        """全借对宫分析"""
```

**依据**: 王亭之《谈斗数》《紫微斗数讲义》

---

### Z6 飞星派断事方法

**文件**: `src/tongshu/engines/ziwei_feixing.py`

**职责**:
- 完全不同的分析逻辑
- 宫干飞化路径建模
- 禄忌轨迹分析
- 不使用小限

**关键方法**:
```python
class FeixingAnalyzer:
    def __init__(self, fact: ZiweiFact):
        self.fact = fact
        self.rules = RuleGraph.load("feixing")
    
    def trace_gonggan_feihua(self, palace_name: str) -> list[dict]:
        """追踪宫干飞化路径"""
    
    def analyze_lu_ji_trajectory(self) -> dict:
        """分析禄忌轨迹"""
    
    def analyze_gonggan(self) -> dict:
        """宫干系统分析"""
```

**依据**: 梁若瑜《专论四化》《十八飞星秘仪》

---

### Z7 钦天门断事方法

**文件**: `src/tongshu/engines/ziwei_qintian.py`

**职责**:
- 向心/离心忌系统
- 立极宫分析
- 四化飞星深度解读

**关键方法**:
```python
class QintianAnalyzer:
    def __init__(self, fact: ZiweiFact):
        self.fact = fact
        self.rules = RuleGraph.load("qintian")
    
    def analyze_xiangxin_ji(self) -> list[dict]:
        """分析向心忌"""
    
    def analyze_lixin_ji(self) -> list[dict]:
        """分析离心忌"""
    
    def liji_analysis(self, center_palace: str) -> dict:
        """立极宫分析"""
```

**依据**: 蔡明宏《华山钦天四化紫微斗数飞星秘仪》

---

### Z8 API 集成

**文件**: `src/tongshu/pipeline_stages/ziwei_pipeline.py`

**职责**:
- 统一入口
- 根据 method_profile 切换流派
- 返回标准化结果

**关键接口**:
```python
class ZiweiPipeline:
    def analyze(
        self,
        birth_date: tuple[int, int, int],
        birth_hour: int,
        gender: str,
        method_profile: MethodProfile | None = None,
    ) -> dict:
        """统一分析接口"""
    
    def get_chart(self, ...) -> ZiweiFact:
        """获取事实层"""
    
    def get_analysis(self, fact: ZiweiFact, method_id: str) -> dict:
        """按流派分析"""
```

---

## 三、依赖关系

```
Z4 ← Z3 RuleGraph
Z5 ← Z4 + Z3
Z6 ← Z3 (独立)
Z7 ← Z3 (独立)
Z8 ← Z1 + Z2 + Z4-Z7
```

---

## 四、测试策略

每个流派独立测试：
- `tests/test_ziwei_sanhe.py`
- `tests/test_ziwei_zhongzhou.py`
- `tests/test_ziwei_feixing.py`
- `tests/test_ziwei_qintian.py`

集成测试：
- `tests/test_ziwei_pipeline.py`

---

## 五、预估工作量

| 阶段 | 预估代码量 | 预估时间 |
|------|-----------|---------|
| Z4 三合派 | ~500行 | 2h |
| Z5 中州派 | ~200行 | 1h |
| Z6 飞星派 | ~400行 | 2h |
| Z7 钦天门 | ~400行 | 2h |
| Z8 API集成 | ~300行 | 1.5h |
| **总计** | ~1800行 | **8.5h** |

---

## 六、建议执行顺序

1. **Z4 三合派** — 基础流派，先实现
2. **Z5 中州派** — 在 Z4 基础上扩展
3. **Z6 飞星派** — 独立实现，对比验证
4. **Z7 钦天门** — 独立实现
5. **Z8 API 集成** — 统一入口

每完成一个阶段运行测试：
```bash
python -m pytest tests/test_ziwei_*.py -v
```