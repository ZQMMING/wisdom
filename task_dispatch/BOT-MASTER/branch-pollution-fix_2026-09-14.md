# BOT-KNOWLEDGE 分支治理报告

**时间**: 2026-09-14 03:14
**事件**: 发现 BOT-KNOWLEDGE 向 main 提交污染代码

---

## 一、问题发现

`agent/knowledge-b1-yhzp` 分支包含越界代码：
- `src/tongshu/engines/bazi_engine_spec.py` (1646行)
- `src/tongshu/engines/ziwei/rules/qintian/*.py` (多个文件)
- `tests/test_bazi_spec_l0.py`
- 其他非知识工程文件

这些代码通过 BOT-KNOWLEDGE 的提交进入了 main 分支。

---

## 二、处理措施

### 1. 分支隔离
| 操作 | 分支 | 状态 |
|------|------|------|
| main | 回滚到 345769dc | ✅ clean state |
| agent/knowledge-b1-yhzp | 重命名为 backup/ | ✅ 已隔离 |
| agent/knowledge-engine | 新建独立分支 | ✅ BOT-KNOWLEDGE 工作分支 |
| feat/yuhai-b1 | 已清理 | ✅ 仅含合法产出 |

### 2. 重新提交
- Commit: `1049d694`
- 内容：B1-YHZP Source/Rule + 六部经典原典更新
- 分支：`agent/knowledge-engine`
- 已推送到 GitHub

---

## 三、新规则

### BOT 提交规则（2026-09-14 确立）
```
1. 所有 BOT 禁止独立提交到任何分支
2. BOT 工作完成后必须回报给 BOT-MASTER 审核
3. BOT-MASTER 负责边界检查、质量审核、统一提交
4. 每个 BOT 使用独立工作分支
5. commit 前必须运行：git diff --name-only
6. 禁止 BOT 直接操作 main 分支
```

### 分支命名规范
| 类型 | 格式 | 示例 |
|------|------|------|
| BOT工作分支 | agent/<bot-name> | agent/knowledge-engine |
| 引擎功能分支 | feat/<engine>-<task> | feat/yuhai-b1 |
| 备份分支 | backup/<原名称>-<日期> | backup/knowledge-polluted-20260914 |
| 主分支 | main | main (clean) |

---

## 四、当前状态

```
main                    345769dc (clean)
agent/knowledge-engine  1049d694 (BOT-KNOWLEDGE 工作分支)
backup/knowledge-polluted-20260914  污染分支备份
```

---

## 五、下一步

1. ✅ 清理分支污染 - 完成
2. ✅ 六部经典原典替换 - 完成
3. ⏳ B4-SFTK Rule 生成 - 待执行
4. ⏳ DTS/QTBJ 缺失内容补充 - 待执行
5. ⏳ 推送分支到远端 - 进行中

---

**裁决人**: BOT-MASTER
**生效时间**: 2026-09-14 03:14
