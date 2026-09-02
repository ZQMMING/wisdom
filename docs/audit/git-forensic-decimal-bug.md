# Git Forensic 报告：紫微大限方向 Bug 根因分析

## 执行时间
2026-09-02

## 调查目标
确定大限方向计算错误的根因：
- A. Hermes 修改了 ziwei_engine.py？
- B. iztro 库本身有问题？
- C. 传统规则理解有误？

---

## 方法

### 1. Git 历史追踪

```bash
git log --all --oneline --follow -- src/tongshu/engines/ziwei_engine.py
```

**结果**：
```
bb33867 初始提交: 干净迁移自 D:\today\backend (2026-08-28)
5caab22 紫微架构清理: 删除违规项，冻结Deterministic Core
57dbab9 P-A1收尾: 删除decadal_soul_effect，修复大限验证测试
```

### 2. 初始提交分析

```bash
git show bb33867:src/tongshu/engines/ziwei_engine.py | grep -c "decadal\|byLunar"
```

**结果**：50 处引用

### 3. 当前版本对比

```bash
cat src/tongshu/engines/ziwei_engine.py | grep -c "decadal\|byLunar"
```

**结果**：27 处引用

### 4. 差异分析

**已删除的内容**（架构清理）：
- `decadal_soul_effect()` 方法
- `native_direction()` 方法
- `native_direction_for_year()` 方法
- `SIHUA_EFFECT` 映射（含 "direction": "INCREASE"/"DECREASE"）

**保留的内容**：
- `full_chart()` 方法调用 `byLunar`
- `flow_decadal_mutagen()` 方法
- `GAN_SIHUA` 四化表

---

## 关键发现

### 发现 1：ziwei_engine.py 一直是 Wrapper

从初始提交到当前版本，`ziwei_engine.py` **从未实现过大限方向算法**。

核心代码始终：
```python
script = '''
const { byLunar } = require('iztro').astro;
const a = byLunar('%s-%s-%s', %d, '%s', %s);
...
'''
```

所有大限计算都委托给 `iztro` 库。

### 发现 2：iztro 版本锁定

```json
// package.json
{
  "dependencies": {
    "iztro": "^2.6.0"
  }
}

// package-lock.json
"node_modules/iztro": {
  "version": "2.6.0",
  "resolved": "https://registry.npmjs.org/iztro/-/iztro-2.6.0.tgz"
}
```

版本锁定在 2.6.0，无自定义修改。

### 发现 3：iztro 内部实现分析

文件：`node_modules/iztro/lib/astro/palace.js` line 163

```javascript
var idx = data_1.GENDER[genderKey] === data_1.earthlyBranches[earthlyBranch].yinYang 
    ? (0, utils_1.fixIndex)(soulIndex + i)   // 顺行
    : (0, utils_1.fixIndex)(soulIndex - i);  // 逆行
```

**问题**：
- 比较的是 **性别阴阳** vs **年支阴阳**
- 传统规则应该是：**年干阴阳** vs **性别**

### 发现 4：测试验证

使用 4 个案例测试：
- 阳男甲辰：期望顺，实际逆 ✗
- 阳女甲辰：期望逆，实际顺 ✗
- 阴男乙巳：期望逆，实际顺 ✗
- 阴女乙巳：期望顺，实际逆 ✗

**结论**：所有 case 输出反向，系统性错误。

---

## 根因判定

| 因素 | 责任 | 说明 |
|------|------|------|
| `ziwei_engine.py` | 🟢 无责 | 始终是 wrapper，未修改算法 |
| `iztro 2.6.0` | 🔴 有责 | 大限方向实现有 bug |
| 传统规则 | 🟢 正确 | 阳男阴女顺，阴男阳女逆 |

---

## 建议行动

### 短期（本周）
1. 上报 issue 到 https://github.com/SylarLong/iztro
2. 本地 fork 或 patch `palace.js:163`
3. Python 层添加方向修正（推荐方案）

### 中期（本月）
1. 监控 iztro 官方修复
2. 测试修复后的行为
3. 更新 Harness 断言

### 长期（下月）
1. 考虑迁移到维护更活跃的库
2. 或自行实现完整排盘算法

---

## 相关文档

- Bug 详情：`docs/audit/iztro-decimal-direction-bug.md`
- Harness：`scripts/ziwei_runtime_output_audit.py` (v4)
- 复现脚本：`scripts/debug_iztro_decadal_bug.py`
