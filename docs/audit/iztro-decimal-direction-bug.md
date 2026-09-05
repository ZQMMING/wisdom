# 紫微大限方向 Bug 报告

## 发现时间
2026-09-02

## 问题描述
`iztro` 库的大限方向计算存在系统性错误，所有阴阳组合的输出都与传统规则相反。

## 传统规则
**阳男阴女顺，阴男阳女逆**
- 阳干 + 男命 → 顺行
- 阳干 + 女命 → 逆行
- 阴干 + 男命 → 逆行
- 阴干 + 女命 → 顺行

## iztro 实际实现
文件：`node_modules/iztro/lib/astro/palace.js` line 163

```javascript
var idx = data_1.GENDER[genderKey] === data_1.earthlyBranches[earthlyBranch].yinYang 
    ? (0, utils_1.fixIndex)(soulIndex + i)   // 顺行
    : (0, utils_1.fixIndex)(soulIndex - i);  // 逆行
```

### 问题分析
1. **比较对象错误**：比较的是性别阴阳 vs 年支阴阳，而非年干阴阳
2. **逻辑反了**：即使按年支比较，相等时应该逆行而非顺行

### iztro 实际行为
| 案例 | 年干 | 性别 | 期望方向 | iztro输出 | 状态 |
|------|------|------|---------|----------|------|
| 阳男 | 甲(阳) | male | 顺 | 逆 | ✗ 错误 |
| 阳女 | 甲(阳) | female | 逆 | 顺 | ✗ 错误 |
| 阴男 | 乙(阴) | male | 逆 | 顺 | ✗ 错误 |
| 阴女 | 乙(阴) | female | 顺 | 逆 | ✗ 错误 |

## 影响范围
- 所有依赖 `iztro` 大限方向的计算
- 可能影响四化、应期等其他功能

## 建议修复方案
### 方案A：修复 iztro 上游
- 创建 issue 到 https://github.com/SylarLong/iztro
- 提供测试用例和传统规则说明
- 等待官方修复或 fork

### 方案B：本地 patch
- 在 `ziwei_engine.py` 中添加方向修正逻辑
- 计算后反转大限序列
- 风险：需要维护 patch

### 方案C：独立实现
- 完全不依赖 iztro 的大限计算
- 使用独立规则函数计算 expected
- 优点：可控性强
- 缺点：工作量较大

## 当前临时方案
在 Runtime Harness 中使用独立规则计算 expected，不信任引擎输出。

## 相关文件
- Bug 复现脚本：`scripts/debug_iztro_decadal_bug.py`
- Harness 当前版本：`scripts/ziwei_runtime_output_audit.py` (v3)
