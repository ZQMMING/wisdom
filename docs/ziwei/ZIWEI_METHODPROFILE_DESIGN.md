# 紫微斗数 MethodProfile 设计文档

> **创建时间**：2026-09-04  
> **状态**：设计完成，待实现  
> **基于**：证据搜集报告 ZIWEI_SCHOOL_METHODS_VERIFIED.md

---

## 一、设计目标

为四种流派（三合/飞星/中州/钦天）提供统一的配置抽象层，使引擎能够根据 MethodProfile 切换不同的计算规则。

---

## 二、MethodProfile 数据模型

```python
@dataclass(frozen=True)
class MethodProfile:
    """紫微斗数流派方法配置"""
    
    # 流派标识
    school: str  # "sanhe" | "zhongzhou" | "feixing" | "qintian"
    name: str    # "三合派" | "中州派" | "飞星派" | "钦天门"
    
    # 四化表版本
    sihua_version: str  # "classic" | "zhongzhou" | "ming"
    
    # 运限体系
    use_xiaoxian: bool      # 是否使用小限
    use_stream_flowers: bool # 是否使用流曜（运马、运羊等）
    has_liuchangliuqu: bool  # 是否有流昌流曲
    
    # 宫位处理
    empty_palace_policy: str  # "none" | "partial" | "full"
    
    # 自化系统
    enable_self_hua: bool     # 是否启用自化
    enable_liji_gong: bool    # 是否启用立极宫
    
    # 飞化优先级
    gonggan_feihua_priority: bool  # 宫干飞化是否优先于生年四化
```

---

## 三、各流派配置

### 3.1 三合派（南派）

```python
SANHE_PROFILE = MethodProfile(
    school="sanhe",
    name="三合派",
    sihua_version="classic",           # 通行版四化
    use_xiaoxian=True,                  # 使用小限
    use_stream_flowers=True,            # 使用流曜
    has_liuchangliuqu=False,           # 无流昌流曲
    empty_palace_policy="partial",      # 空宫部分借星
    enable_self_hua=False,              # 不启用自化
    enable_liji_gong=False,            # 不启用立极宫
    gonggan_feihua_priority=False,      # 生年四化优先
)
```

**依据**：《紫微斗数全书》《捷览》《全集》

### 3.2 中州派

```python
ZHONGZHOU_PROFILE = MethodProfile(
    school="zhongzhou",
    name="中州派",
    sihua_version="zhongzhou",         # 戊干改太阳化科
    use_xiaoxian=True,                  # 使用小限
    use_stream_flowers=True,            # 使用流曜
    has_liuchangliuqu=True,            # **独有流昌流曲**
    empty_palace_policy="full",         # **空宫全借对宫**
    enable_self_hua=False,              # 不启用自化
    enable_liji_gong=False,            # 不启用立极宫
    gonggan_feihua_priority=False,      # 生年四化优先
)
```

**依据**：王亭之《谈斗数》《紫微斗数讲义》《紫微星诀》

### 3.3 飞星派（梁若瑜系）

```python
FEIXING_PROFILE = MethodProfile(
    school="feixing",
    name="飞星派",
    sihua_version="classic",           # 通行版四化
    use_xiaoxian=False,                 # **不用小限**
    use_stream_flowers=False,           # **不用流曜**
    has_liuchangliuqu=False,           # 无流昌流曲
    empty_palace_policy="partial",      # 空宫部分借星
    enable_self_hua=True,               # 启用基础自化
    enable_liji_gong=False,            # 不启用立极宫
    gonggan_feihua_priority=True,       # **宫干飞化优先**
)
```

**依据**：梁若瑜《专论四化》《十八飞星秘仪》

### 3.4 钦天门（北派）

```python
QINTIAN_PROFILE = MethodProfile(
    school="qintian",
    name="钦天门",
    sihua_version="classic",           # 通行版四化
    use_xiaoxian="partial",             # 视情况使用小限
    use_stream_flowers=True,            # 使用流曜
    has_liuchangliuqu=False,           # 无流昌流曲
    empty_palace_policy="partial",      # 空宫视情况
    enable_self_hua=True,               # **核心：向心/离心自化**
    enable_liji_gong=True,              # **核心：立极宫系统**
    gonggan_feihua_priority=True,       # 宫干飞化优先
)
```

**依据**：蔡明宏《华山钦天四化紫微斗数飞星秘仪》

---

## 四、四化表映射

### 4.1 明代原版（《全书》）

```python
MING_SIHUA = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},  # 右弼化科
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "天府", "忌": "天同"},  # 天府化科
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "天府", "忌": "武曲"},  # 天府化科
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}
```

### 4.2 通行版（《全集》）

```python
CLASSIC_SIHUA = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "太阴", "忌": "天同"},  # 太阴化科
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "左辅", "忌": "武曲"},  # 左辅化科
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}
```

### 4.3 中州派

```python
ZHONGZHOU_SIHUA = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "太阳", "忌": "天机"},  # 太阳化科
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "天府", "忌": "天同"},
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "天府", "忌": "武曲"},
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}
```

---

## 五、实现路径

### Phase 1: 数据结构定义
1. 在 `src/tongshu/types.py` 中添加 `MethodProfile` 数据类
2. 在 `src/tongshu/engines/ziwei_engine.py` 中定义四化表常量

### Phase 2: 配置加载
1. 创建 `src/tongshu/engines/ziwei_profile.py`
2. 实现 `load_profile(school: str) -> MethodProfile` 函数

### Phase 3: 引擎适配
1. 修改 `ZiweiEngine` 接受 `MethodProfile` 参数
2. 根据 Profile 切换四化表、运限逻辑

### Phase 4: API 扩展
1. 在 `pipeline.py` 中添加 `method_profile` 参数
2. 支持运行时切换流派

---

## 六、兼容性说明

- **向后兼容**：默认使用三合派配置，现有代码无需修改
- **渐进式实现**：先实现数据结构，再逐步适配引擎逻辑
- **测试保障**：每次修改后运行完整测试套件

---

## 七、参考文档

- `docs/ziwei/ZIWEI_SCHOOL_METHODS_VERIFIED.md` - 流派方法考证
- `docs/ziwei/ZIWEI_RULES_VERIFICATION_FINAL.md` - 规则验证报告
- `docs/audit/ZIWEI_CURRENT_ARCHITECTURE_AUDIT.md` - 架构审计
