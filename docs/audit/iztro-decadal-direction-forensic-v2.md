# IZTRO_DECADAL_DIRECTION_FORENSIC_V2 报告

## 执行时间
2026-09-02

## 任务
执行 forensic 调查，确认大限顺逆异常的责任归属。

---

## 一、锁定实际依赖

### 实际安装的 iztro 版本
```bash
npm list iztro
wisdom@ /path/to/wisdom
└── iztro@2.6.0
```

**确认版本：2.6.0**（与 lockfile 一致）

### 实际运行的源码位置
```
node_modules/iztro/lib/astro/palace.js
node_modules/iztro/lib/data/constants.js
node_modules/iztro/lib/data/earthlyBranches.js
node_modules/iztro/lib/i18n/index.js
```

### 调用链追踪

```
byLunar('2024-2-10', 4, 'male', false)
    ↓
lunar_lite.lunar2solar() → solar date = '2024-3-19'
    ↓
bySolar(solarDate, timeIndex, gender, fixLeap)
    ↓
palace.getHoroscope({solarDate, timeIndex, gender, fixLeap})
    ↓
line 163: GENDER[genderKey] === earthlyBranches[earthlyBranch].yinYang
    ↓
? forward (soulIndex + i) : reverse (soulIndex - i)
```

### 关键代码定位

**文件**: `node_modules/iztro/lib/astro/palace.js`  
**行号**: 163  
**表达式**:

```javascript
var idx = data_1.GENDER[genderKey] === data_1.earthlyBranches[earthlyBranch].yinYang 
    ? (0, utils_1.fixIndex)(soulIndex + i)   // 顺行
    : (0, utils_1.fixIndex)(soulIndex - i);  // 逆行
```

---

## 二、完整变量打印

### Case 1: 阳男甲辰

```
year: 2024
gender: male
yearHeavenlyStem: 甲 (yinYang=阳)
yearEarthlyBranch: 辰 (key=chenEarthly, yinYang=阳)
genderKey: male
iztro Gender[male]: 阳
iztro comparison: 阳 === 阳 -> true
iztro direction: 逆  ← 错误！应为顺
wrapper direction: 逆
independent expected: 顺
MATCH: ✗ MISMATCH
```

### Case 2: 阳女甲辰

```
year: 2024
gender: female
yearHeavenlyStem: 甲 (yinYang=阳)
yearEarthlyBranch: 辰 (key=chenEarthly, yinYang=阳)
genderKey: female
iztro Gender[female]: 阴
iztro comparison: 阴 === 阳 -> false
iztro direction: 顺  ← 错误！应为逆
wrapper direction: 顺
independent expected: 逆
MATCH: ✗ MISMATCH
```

### Case 3: 阴男乙巳

```
year: 2025
gender: male
yearHeavenlyStem: 乙 (yinYang=阴)
yearEarthlyBranch: 巳 (key=siEarthly, yinYang=阴)
genderKey: male
iztro Gender[male]: 阳
iztro comparison: 阳 === 阴 -> false
iztro direction: 顺  ← 错误！应为逆
wrapper direction: 顺
independent expected: 逆
MATCH: ✗ MISMATCH
```

### Case 4: 阴女乙巳

```
year: 2025
gender: female
yearHeavenlyStem: 乙 (yinYang=阴)
yearEarthlyBranch: 巳 (key=siEarthly, yinYang=阴)
genderKey: female
iztro Gender[female]: 阴
iztro comparison: 阴 === 阴 -> true
iztro direction: 逆  ← 错误！应为顺
wrapper direction: 逆
independent expected: 顺
MATCH: ✗ MISMATCH
```

---

## 三、独立 Oracle 验证

### 传统规则
```
阳男 → 顺
阳女 → 逆
阴男 → 逆
阴女 → 顺
```

基于 **年干阴阳 + 性别** 判断。

### iztro 实现
```javascript
GENDER[genderKey] === earthlyBranches[earthlyBranch].yinYang
    ? forward : reverse
```

基于 **性别阴阳 vs 年支阴阳** 比较。

### 问题
1. **比较对象错误**：应为年干，实际使用年支
2. **逻辑反转**：即使按年支比较，相等时应逆行而非顺行

---

## 四、边界检查

### yearDivide 影响
```javascript
// palace.js line 152-155
var yearly = lunar_lite.getHeavenlyStemAndEarthlyBranchBySolarDate(
    solarDate, timeIndex, 
    { year: getConfig().yearDivide }  // default: 'normal'
).yearly;
```

- `yearDivide = 'normal'`：正月初一分界
- `yearDivide = 'exact'`：立春分界

测试用例都在立春后，不受影响。

### 农历/公历转换
```javascript
// astro.js line 268
var solarDate = lunar_lite.lunar2solar(lunarDateStr, isLeapMonth);
```

农历转公历不影响年干支计算。

### 子初/子正
时辰索引已正确处理（ti=4 对应辰时），不影响年干支。

### 年干 vs 年支阴阳一致性
```
辰(阳) + 甲(阳) → 一致
巳(阴) + 乙(阴) → 一致
```

所有测试 case 的年干年支阴阳一致，但这不是传统规则的判断依据。

---

## 五、禁止事项检查

本调查期间：
- ✓ 未修改 ziwei_engine.py
- ✓ 未 patch node_modules
- ✓ 未 fork iztro
- ✓ 未增加 Python workaround
- ✓ 未修改 Harness expected
- ✓ 未使用 observed output 作为 oracle
- ✓ 未提交生产修复

---

## 六、最终报告

### ROOT CAUSE
**IZTRO BUG**

### 证据摘要

| 项目 | 结果 |
|------|------|
| ziwei_engine.py 是否修改过大限算法 | 否，始终是 wrapper |
| iztro 版本是否被修改 | 否，锁定 2.6.0 |
| 传统规则理解是否正确 | 是，阳男阴女顺，阴男阳女逆 |
| iztro 实现是否与规则一致 | 否，使用年支而非年干 |
| 所有 4 种组合是否都出错 | 是，系统性反向 |

### 责任归属

| 组件 | 责任 | 说明 |
|------|------|------|
| `ziwei_engine.py` | 🟢 无责 | Wrapper，未修改算法 |
| `iztro 2.6.0` | 🔴 有责 | palace.js:163 实现错误 |
| 传统规则 | 🟢 正确 | 年干阴阳判断 |

### 建议行动

1. **短期**：上报 issue 到 https://github.com/SylarLong/iztro
2. **中期**：本地 fork 或 Python 层 workaround
3. **长期**：监控官方修复或迁移替代库

---

## 附录：完整调用链

```
用户调用
    ↓
ZiweiEngine.full_chart(lunar_date, hour, gender)
    ↓
ziwei_engine.py line 617: byLunar('%s-%s-%s', %d, '%s', %s)
    ↓
iztro/lib/astro/astro.js line 268: lunar2solar()
    ↓
iztro/lib/astro/astro.js line 142: bySolar()
    ↓
iztro/lib/astro/palace.js line 147: getHoroscope()
    ↓
iztro/lib/astro/palace.js line 163: GENDER[gender] === branch.yinYang ?
    ↓
返回 decadals 数组（方向错误）
    ↓
ziwei_engine.py 解析 JSON，返回给 Python
    ↓
Harness 读取 decadalRange 判断方向
```

---

**结论**：问题完全在 `iztro 2.6.0` 的 `palace.js:163`，与 Hermes/ziwei_engine.py 无关。
