# scripts/legacy — 废弃历史脚本归档

> 归档时间: 2026-09-07
> 归档原因: 一次性历史验证/修复脚本，含开发机硬编码绝对路径（C:/Users/wisdom、D:/shuntian等），无生产引用。
> 归档目的: 保留历史逻辑供参考，同时移出 PATH_INDEPENDENCY_AUDIT 审计范围（路径独立性 P0 红线）。

## 处理规则

- 本目录下所有脚本**不再维护、不再运行**，仅作历史参考
- 若需复用其中的算法逻辑：**复制到 `scripts/` 后改写为相对路径/环境变量绑定**，不得直接运行
- 迁移服务器前，本目录不参与部署（与 `tests/`、`docs/` 一致，非运行时资产）

## 已保留的运维/工具脚本（scripts/ 根目录）

| 脚本 | 用途 |
|------|------|
| path_independency_audit.py | 路径独立性审计（P0红线检查，CI 用） |
| bot-workspace-check.py | Bot 工作区合规验证 |
| pre_task_check.py | 任务启动前验证 |
| verify_p1_fix.py | P1 修复验证 |
| verify_corpus_phase4.py | CORPUS Phase 4 验证 |
| fix_p0_daymaster_strength.py | P0 日主强度修复 |
| audit_commit.sh | 边界审计（git hook 用） |
| audit_bot_config.sh | Bot 配置审计 |
| bot-workflow.sh | Bot 工作流 |

## 归档清单（61个）

含以下类别（均已废弃）：
- blind_*：盲派证据历史验证
- semantic_normalization*：语义归一化历史脚本
- complete_evidence* / complete_semantic*：证据字段补全
- phase*：历史阶段验证脚本（phase0~phase5）
- 其他一次性工具
