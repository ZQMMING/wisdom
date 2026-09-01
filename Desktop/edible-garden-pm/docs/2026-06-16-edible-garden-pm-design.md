> [!NOTE]
> This document may not reflect the current implementation.
> See the final report for up-to-date state:
> [Final Report](edible-garden-pm-report.md)

# 可食花园项目经理 Agent 设计文档

## [S1] 问题定义

城市近郊土地需要一种新的商业模式，将传统共享菜园升维为"高情绪价值的奢侈品容器"。需要一个AI Agent来帮助主理人将碎片化灵感转化为兼具商业逻辑与艺术美感的项目方案。

## [S2] 解决方案概述

创建一个Codex Skill，实现可食花园项目经理的全流程管理能力。该技能包含：
- 完整的人格定义（美学驱动、降维洞察、严谨务实、自演进）
- 结构化的五阶段工作流程
- 模板化的输出格式
- 可扩展的案例库和框架库

## [S3] 技能文件结构

```
桌面/edible-garden-pm/
├── SKILL.md              # 主技能文件（人格、工作流、指令）
├── reference/
│   ├── cases.md          # 全球案例库（可选）
│   └── frameworks.md     # 商业模式框架（可选）
└── templates/
    ├── research.md       # 调研模板
    ├── analysis.md       # 分析模板
    └── proposal.md       # 方案模板
```

## [S4] 核心工作流程

1. **阶段零：自学习** - 加载案例库和框架知识
2. **阶段一：前期调研** - 物理环境分析、客群画像
3. **阶段二：数据分析** - 面积推演、商业平衡计算
4. **阶段三：空间规划** - 入口意象、景观隔离带、单元框架
5. **阶段四：方案编写** - 定位层→业务层→变现层→空间层

每个阶段使用question工具与用户交互，确保方向正确。

## [S5] 输入/输出格式

**输入格式：**
- 地块信息（坐标、面积、边界）
- 周边环境（交通、产业、人群）
- 主理人想法（碎片灵感）

**输出格式：**
- Markdown格式的项目方案文档
- 包含：定位层、业务层、变现层、空间层
- 可选：可视化图表建议

## [S6] 集成点

**与MiMoCode集成：**
- 作为skill安装到 ~/.codex/skills/
- 用户可通过 `skill edible-garden-pm` 调用
- 自动加载reference和templates

**与其他工具集成：**
- 可调用Bash运行数据分析脚本
- 可使用webfetch获取在线案例
- 可生成文件保存方案文档

## [S7] 实现方案

选择标准技能方案：
- SKILL.md 主文件
- reference目录存放案例库和框架
- templates目录存放输出模板
- 简单直接，易于维护
