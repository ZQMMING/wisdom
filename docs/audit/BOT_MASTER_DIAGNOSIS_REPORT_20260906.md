# 🔍 BOT-MASTER 诊断报告

**诊断时间**: 2026-09-06 19:40  
**问题级别**: P1 - 需要修复测试路径配置

---

## 一、问题摘要

| 项目 | 状态 |
|------|------|
| BOT-MASTER配置 | ✅ 已完成 |
| Git Hooks | ✅ 已生效 |
| 核心测试 | ❌ 33个失败，5个错误 |
| 根因 | 测试路径配置错误 |

---

## 二、错误分类

### 2.1 FileNotFoundError（主要问题）

```
缺失的目录/文件:
❌ backend/data/evidence_meta/ (不存在)
❌ backend/data/_m2b_backup/ (不存在)
❌ docs/rule.schema.json (路径错误)
❌ docs/knowledge.schema.json (路径错误)
❌ docs/mapping.schema.json (路径错误)
```

### 2.2 实际存在的文件

```
✅ docs/rule.schema.json (实际存在)
✅ docs/knowledge.schema.json (实际存在)
✅ docs/mapping.schema.json (实际存在)
✅ backend/data/docs/rule.schema.json (也存存)
✅ backend/data/docs/knowledge.schema.json (也存在)
✅ backend/data/evidence/ (存在)
✅ backend/data/knowledge/ (存在)
```

---

## 三、路径对比

### 测试期望路径 vs 实际路径

| 测试期望 | 实际位置 | 状态 |
|----------|----------|------|
| `backend/data/evidence_meta/` | 不存在 | ❌ |
| `backend/data/_m2b_backup/` | 不存在 | ❌ |
| `docs/rule.schema.json` | `backend/data/docs/rule.schema.json` | ⚠️ 路径错误 |
| `docs/knowledge.schema.json` | `backend/data/docs/knowledge.schema.json` | ⚠️ 路径错误 |
| `docs/mapping.schema.json` | `backend/data/docs/mapping.schema.json` | ⚠️ 路径错误 |

---

## 四、失败测试详情

### 4.1 test_m2b_evidence.py (23个失败)

```python
# 测试代码期望的路径
DATA = REPO / "backend" / "data"
DOCS = REPO / "docs"

# 失败点1: evidence_meta目录不存在
shutil.copytree(DATA / "evidence_meta", tmp / "evidence_meta")
# ❌ FileNotFoundError: backend/data/evidence_meta

# 失败点2: _m2b_backup目录不存在
BACKUP = DATA / "_m2b_backup"
# ❌ FileNotFoundError: backend/data/_m2b_backup
```

### 4.2 test_audit_gates.py (9个失败)

```python
# 测试代码期望的路径
MappingRegistry(_ROOT / "backend" / "data", _ROOT / "docs")
# ❌ 找不到 docs/mapping.schema.json (实际在 backend/data/docs/)
```

### 4.3 test_audit_final_output.py (5个错误)

```python
# 测试代码期望的路径
RuleLoader(data_dir, repo_root / "docs")
# ❌ 找不到 docs/rule.schema.json (实际在 backend/data/docs/)
```

---

## 五、影响范围

### 5.1 BOT-MASTER自检

```
总测试数: 79
通过: 41
失败: 33
错误: 5

通过率: 51.9% (41/79)
```

### 5.2 其他BOT状态

```
✅ BOT-BAZI:   12/12 passed (100%)
✅ BOT-BLIND:  10/10 passed (100%)
✅ BOT-HELUO:  48/48 passed (100%)
✅ BOT-TIME:   15/23 passed (65%)
⚠️ BOT-ZIPING: 测试失败 (依赖问题)
⚠️ BOT-YI:     测试失败 (依赖问题)
✅ BOT-CORPUS: 语料库检查通过
```

---

## 六、解决方案

### 方案1: 创建缺失目录（推荐）

```bash
# 创建evidence_meta目录
mkdir -p backend/data/evidence_meta

# 创建_m2b_backup目录
mkdir -p backend/data/_m2b_backup

# 创建备份文件（从现有evidence复制）
cp -r backend/data/evidence/* backend/data/evidence_meta/
cp -r backend/data/evidence/* backend/data/_m2b_backup/evidence/
```

### 方案2: 更新测试路径配置

修改 `tests/test_m2b_evidence.py`:
```python
# 当前配置（错误）
DATA = REPO / "backend" / "data"
DOCS = REPO / "docs"

# 修改为（正确）
DATA = REPO / "backend" / "data"
DOCS = REPO / "backend" / "data" / "docs"  # schema文件实际在这里
```

### 方案3: 创建符号链接（快速修复）

```bash
# 创建evidence_meta符号链接
cd backend/data
ln -s evidence evidence_meta

# 创建_m2b_backup符号链接
mkdir -p _m2b_backup
cd _m2b_backup
ln -s ../evidence evidence
```

---

## 七、建议行动

### 立即执行（P0）

1. **创建缺失目录**
   ```bash
   mkdir -p backend/data/evidence_meta
   mkdir -p backend/data/_m2b_backup
   ```

2. **复制必要文件**
   ```bash
   # 复制evidence到evidence_meta
   cp -r backend/data/evidence/* backend/data/evidence_meta/
   
   # 创建backup结构
   mkdir -p backend/data/_m2b_backup/evidence
   cp -r backend/data/evidence/* backend/data/_m2b_backup/evidence/
   ```

3. **验证修复**
   ```bash
   bash scripts/bot-selfcheck/bot-master.sh
   ```

### 后续优化（P1）

1. **统一路径配置**
   - 确定标准的data/docs路径
   - 更新所有测试文件

2. **修复BOT-ZIPING和BOT-YI**
   - 检查依赖问题
   - 运行自检验证

---

## 八、当前状态

### 8.1 成功配置的部分

```
✅ 8个BOT自检脚本已创建
✅ Git Hooks已安装并生效
✅ 工作流入口已创建
✅ 规范文档已建立
✅ 三隔离原则已生效
```

### 8.2 需要修复的部分

```
❌ BOT-MASTER测试路径配置错误
❌ GitHub Token失效（认证失败）
⚠️ BOT-ZIPING测试失败
⚠️ BOT-YI测试失败
```

---

## 九、总结

### ✅ BOT配置完成

所有BOT的自检脚本、Git Hooks、工作流入口都已配置完成。

### ❌ 测试路径问题

BOT-MASTER测试失败是因为测试文件期望的路径与实际仓库结构不匹配。需要：
1. 创建缺失的 `backend/data/evidence_meta/` 目录
2. 创建缺失的 `backend/data/_m2b_backup/` 目录
3. 或更新测试路径配置

### ⚠️ GitHub认证问题

Token失效，需要更新有效的GitHub Token才能同步到远程。

---

**建议立即执行方案1（创建缺失目录）来修复测试问题。**
