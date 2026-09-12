# 任务单 DTS103-ROOT-01：旺衰链实现 DTS-103 日支通根打分维度（方案A）

**裁决**: User 2026-09-11 授权方案 A
**引擎**: BOT-ZIPING（子平）
**严重性**: P1 架构债务（藏干帮身力量未进入四维评分）

## 背景
1980-06-22 巳时男（丙寅日，月壬午，时癸巳）旺衰输出：
- 党众 help=0 drain=3 —— 按 DTS-105 口径"党众只看透干"，实现忠实，**不是 bug**
- 但 L521 注释承诺"藏干根属通根/得地范畴（DTS-103 日支通根）"
- **DTS-103 是僵尸引用**：只在 L125 citation map，无任何打分路径消费
- 结果：寅藏丙(比肩)、巳藏丙(比肩)、午藏丁(劫财) 对旺衰零贡献

## 施工目标
在 WANGSHUAI 四维评分中实现 DTS-103 日支通根维度：

1. 新增打分项 **tonggen_score**（建议 +1 有根 / -1 无根，权重由你定，理由写入规则引用注释）
2. 判定条件：日主藏干于日支主气为比肩/劫财 → 有根（与 DTS-103 rule body 的 condition `day_branch_main_ten_god in [比肩,劫财]` 保持一致）
3. 打分时 `cits.add("DTS-103")` + 消费 `E-DTS-103-001`
4. 综合评分 `total = get_ling + de_di + tonggen + dangzhong`，阈值 STRONG/WEAK 是否联动调整由你定并说明
5. reasoning_parts 增加通根说明行
6. score_detail 增加 `tonggen_score` / `tonggen_rooted` 字段

## 边界（ALLOWED）
- src/tongshu/reasoning/judgment.py（仅 WANGSHUAI 链 L396-507 + DTS-103 打分函数）
- 新增测试文件 tests/test_ziping_dts103_tonggen_*.py
- 不得改：GEJU/YONGSHEN/SHISHEN/SHIJIAN 逻辑、Bazi 冻结层、G1、MAP-1011、DTS-103 rule JSON 本体（status 保持 draft，实现消费不升格——升格属 P2.1-F 治理，不在本单）

## 验收
- [ ] 1980-06-22 案例：tonggen=+1（寅主气丙=比肩），total 变化可推演
- [ ] 新增 1 个无根反例（如日支主气非比劫）→ tonggen=-1
- [ ] T-3 全量回归 117/117 或报告漂移清单
- [ ] 单一 commit，引擎=ZIPING，报告 CHANGED FILES / TESTS / COMMIT

## 治理声明
开工前报告 BASE COMMIT / BRANCH / ALLOWED PATHS；完成后报告 CHANGED FILES / TESTS / COMMIT。
