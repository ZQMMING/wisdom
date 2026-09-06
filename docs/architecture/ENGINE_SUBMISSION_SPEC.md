# 引擎独立提交规范 v1.0

**生效时间**: 2026-09-06  
**适用范围**: 所有引擎开发、修复、验证提交

---

## 一、提交隔离原则

### 1.1 核心规则

**每个引擎的变更必须独立提交，禁止混合提交。**

| 引擎 | 代码路径 | 测试路径 | 提交前缀 |
|------|----------|----------|----------|
| 子平（八字排盘） | `src/tongshu/engines/bazi_engine.py` | `tests/test_bazi*.py` | `P:` |
| 盲派 | `src/tongshu/engines/blind/` | `tests/test_blind*.py` | `BL:` |
| 河洛 | `src/tongshu/engines/heluo/` | `tests/test_heluo*.py` | `H:` |
| 紫微 | `src/tongshu/engines/ziwei_engine.py` | `tests/test_ziwei*.py` | `Z:` |
| 易经 | `src/tongshu/engines/meihua.py` | `tests/test_yi*.py` | `Y:` |
| 时间计算 | `src/tongshu/engines/time/` | `tests/test_time*.py` | `T:` |
| 治理架构 | `src/tongshu/assertion/`, `src/tongshu/governance/` | `tests/test_*_governance*.py` | `G:` |
| 证据系统 | `backend/data/evidence/`, `src/tongshu/phase_b*.py` | - | `E:` |

### 1.2 禁止事项

```
❌ 禁止在同一commit中混合多个引擎的变更
❌ 禁止治理修改与引擎代码修改混在一起
❌ 禁止测试文件与引擎文件混在一个提交
❌ 禁止docs/audit/与其他代码混提交
```

### 1.3 允许事项

```
✅ 同一引擎的多文件变更可以合并提交
✅ 同一引擎的代码+测试可以合并提交
✅ 纯文档/审计更新可以独立提交
✅ 多个治理模块变更可以合并提交
```

---

## 二、提交模板

### 2.1 引擎开发提交

```
{PREFIX}: {引擎名} - {变更类型} - {核心内容}

## 变更范围
- {文件1}: {说明}
- {文件2}: {说明}

## 测试覆盖
- {test1}: {说明}
- {test2}: {说明}

## 验证状态
- 测试: X/Y PASS
- 证据: {evidence_id} VERIFIED
- 架构: {状态}
```

示例：
```
Z: ZiweiEngine - 架构修复 - FrozenZiweiChart别名补全

## 变更范围
- ziwei_engine.py: 添加FrozenZiweiChart别名
- ziwei/rules/feixing_rule_graph.py: 修复导入

## 测试覆盖
- test_ziwei_feixing_production.py: 验证导入
- test_ziwei_palace_resolution.py: 验证契约

## 验证状态
- 测试: 3/3 PASS
- 证据: 无
- 架构: 向后兼容
```

### 2.2 治理提交

```
G: {治理域} - {阶段} - {核心内容}

## 治理对象
- {文件/模块}: {说明}

## 验证方式
- {方法1}: {说明}
- {方法2}: {说明}

## 状态
- Gate: {通过/失败}
- Blockers: {无/列出}
```

### 2.3 证据提交

```
E: {证据域} - {阶段} - {核心内容}

## 新增/修改
- evidence/{id}.json: {说明}
- {相关文件}: {说明}

## 验证
- 原典: {来源}
- 边界: {覆盖}
- 数量: {N个证据}
```

---

## 三、提交前检查清单

### 3.1 代码隔离检查

```bash
# 检查是否有其他引擎文件
git diff --cached --name-only | grep -E "ziwei|heluo|blind|bazi|meihua"

# 如果输出包含多个引擎路径，拆分提交
```

### 3.2 测试隔离检查

```bash
# 检查测试是否覆盖当前引擎
git diff --cached --name-only | grep "test_"
pytest tests/test_{引擎}*.py -v --tb=short
```

### 3.3 提交信息检查

```bash
# 检查前缀是否符合规范
git diff --cached --name-only | head -20
git commit -m "{PREFIX}: {内容}"
```

---

## 四、工作流规范

### 4.1 单引擎开发流程

```
1. 切换引擎分支（可选）
   git checkout -b feature/{引擎}-{功能}

2. 开发代码
   # 只修改当前引擎相关文件

3. 运行测试
   pytest tests/test_{引擎}*.py -v

4. 提交
   git add {引擎相关文件}
   git commit -m "Z: ZiweiEngine - ... (只提交紫微)"

5. 推送
   git push origin feature/{引擎}-{功能}
```

### 4.2 多引擎并行开发

```
# 为每个引擎创建独立分支
git checkout -b feature/ziwei-fix-X
git checkout -b feature/heluo-fix-Y
git checkout -b feature/blind-fix-Z

# 各自独立开发、测试、提交
# 最后单独合并到master
```

### 4.3 禁止的提交模式

```
❌ 一次提交混合 Ziwei + Heluo 代码
❌ 治理提交包含引擎代码修改
❌ 测试提交包含无关引擎文件
❌ docs/audit/ 混入生产代码提交
```

---

## 五、违规处理

### 5.1 发现违规提交

```bash
# 查看最近提交的包含文件
git log --oneline -5 --stat

# 如果发现问题，执行交互式rebase
git rebase -i HEAD~5
```

### 5.2 拆分混合提交

```bash
# 使用 git add -p 交互式选择文件
git reset HEAD~1
git add src/tongshu/engines/ziwei_engine.py tests/test_ziwei_*.py
git commit -m "Z: ... (紫微部分)"
git add src/tongshu/engines/heluo/canonical.py tests/test_heluo_*.py
git commit -m "H: ... (河洛部分)"
```

---

## 六、裁决隔离保障

### 6.1 为什么需要独立提交

1. **追溯清晰**: 每个引擎的问题可以精确定位到具体commit
2. **回滚安全**: 单引擎问题可以快速回滚，不影响其他引擎
3. **审计明确**: 证据、断言、规则的变更可以独立验证
4. **避免污染**: 一个引擎的测试失败不会掩盖另一个引擎的问题

### 6.2 裁决职责边界

| 角色 | 职责 | 权限 |
|------|------|------|
| Hermes (总调度) | 监督提交规范 | 审核、拦截违规提交 |
| 裁决者 | 架构/计算争议 | 审查特定引擎的commit |
| Bot (引擎) | 本引擎开发 | 只修改本引擎文件 |
| Bot Master | 治理/证据 | 只修改治理相关文件 |

### 6.3 拦截规则

```
发现混合提交 → 拦截 → 要求拆分 → 重新验证 → 批准合并
```

---

## 七、工具支持

### 7.1 提交前检查脚本

```bash
#!/bin/bash
# pre-commit-check.sh

ENGINES=("ziwei" "heluo" "blind" "bazi" "yi" "meihua")

echo "=== 引擎隔离检查 ==="
FILES=$(git diff --cached --name-only)

for engine in "${ENGINES[@]}"; do
    count=$(echo "$FILES" | grep -c "$engine")
    if [ $count -gt 0 ]; then
        echo "✓ $engine: $count files"
    fi
done

# 检查是否有混合
ZIWEI_COUNT=$(echo "$FILES" | grep -c "ziwei")
HELUE_COUNT=$(echo "$FILES" | grep -c "heluo")
BLIND_COUNT=$(echo "$FILES" | grep -c "blind")

TOTAL_ENGINE=$(($ZIWEI_COUNT + $HELUE_COUNT + $BLIND_COUNT))

if [ $TOTAL_ENGINE -gt 1 ]; then
    echo "❌ 错误: 检测到混合引擎提交！"
    echo "   Ziwei: $ZIWEI_COUNT, Heluo: $HELUE_COUNT, Blind: $BLIND_COUNT"
    exit 1
fi

echo "✅ 引擎隔离检查通过"
```

### 7.2 提交信息模板

```bash
#!/bin/bash
# commit-template.sh

PREFIX=$1
ENGINE=$2
TYPE=$3
CONTENT=$4

echo "$PREFIX: $ENGINE - $TYPE - $CONTENT"
echo ""
echo "## 变更范围"
git diff --cached --name-only
echo ""
echo "## 测试覆盖"
pytest tests/test_${ENGINE}*.py -v --tb=short
```

---

## 八、执行记录

### 8.1 历史问题追踪

| Commit | 问题 | 处理方式 |
|--------|------|----------|
| 43f1c91e | 同步提交混合 | 保留历史，建立规范 |
| 9b9dd16f | 同步提交混合 | 保留历史，建立规范 |
| a72e2b30 | 同步提交混合 | 保留历史，建立规范 |

### 8.2 规范生效

- **生效日期**: 2026-09-06
- **生效commit**: bb4e6a32
- **后续提交**: 严格执行本规范

---

**本文档由 Hermes Agent 制定，经裁决者批准生效。**
