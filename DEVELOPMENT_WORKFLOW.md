# 顺天命理系统 — 开发工作流

> 从 2026-09-01 起，所有开发工作以 GitHub 仓库 `ZQMMING/wisdom` 为准。

---

## 一、仓库地址

```
https://github.com/ZQMMING/wisdom
```

---

## 二、分支策略

| 分支 | 用途 |
|------|------|
| `main` | 主分支，生产代码 |
| `audit-*` | 审计专项分支 |
| `feature/*` | 功能开发分支 |

---

## 三、本地开发流程

```bash
# 1. 克隆仓库
git clone https://github.com/ZQMMING/wisdom.git
cd wisdom

# 2. 创建开发分支
git checkout -b feature/your-feature-name

# 3. 开发、测试、提交
# ...

# 4. 推送到远程
git push origin feature/your-feature-name

# 5. 合并前同步 main
git fetch origin
git rebase origin/main
git push --force-with-lease
```

---

## 四、五部经典数据位置

```
data/classics/original/
├── DTS_滴天髓_完整全文.md
├── DTS_滴天髓_段落数据.json
├── PZZQ_子平真诠_完整全文.md
├── PZZQ_子平真诠_段落数据.json
├── QTBJ_穷通宝鉴_完整全文.md
├── QTBJ_穷通宝鉴_段落数据.json
├── SMTH_三命通会_完整全文.md
├── SMTH_三命通会_段落数据.json
├── YHZP_渊海子平_完整全文.md
├── YHZP_渊海子平_段落数据.json
├── 五部经典完整数据_汇总.json
├── 深度检查报告.json
└── README.md  ← 数据索引
```

---

## 五、引擎目录

```
src/tongshu/engines/
├── bazi_engine.py          # 八字排盘引擎
├── bazi_l1_facts.py        # 八字L1事实（十二长生、藏干）
├── blind_bazi_engine.py    # 盲派八字引擎
├── blind_yingqi.py         # 盲派应期引擎
├── ziwei_engine.py         # 紫微斗数引擎
├── huangli_engine.py       # 黄历引擎
├── judgment_engine.py      # 断言引擎
├── strength_engine.py      # 旺衰引擎
├── heluo/                  # 河洛理数引擎
├── yi/                     # 易经引擎
├── time/                   # 时间解析引擎
└── ...
```

---

## 六、测试运行

```bash
# 运行全部测试
pytest tests/ -v

# 运行特定引擎测试
pytest tests/test_bazi_engine.py -v
pytest tests/test_ziwei_engine.py -v
pytest tests/test_huangli_engine.py -v

# 运行全量测试
pytest tests/ --tb=short
```

---

## 七、当前阶段状态

| 阶段 | 状态 |
|------|------|
| P6.1 Canonical State | 🔒 FROZEN |
| P6.2 Assertion Admission | 🔒 FROZEN |
| P6.3 Cross-Domain Integration | 🔒 FROZEN |
| P6.4 Asset Production Protocol | 🔒 FROZEN |
| P6.5 Batch Production | 🟡 进行中 |
| P6-CALC Calculation Integrity | 🔵 当前施工区 |
| Step 9 Phase 7.5 | ✅ 完成 |

---

## 八、权限矩阵

| 角色 | 职责 |
|------|------|
| **User** | 最终裁定权 |
| **Hermes** | 编排与复核 |
| **Claude** | 首席架构师+审计师 |
| **OpenCode** | 执行 |

---

## 九、重要原则

1. **原典授权 ≠ 条件成立 ≠ 断事结论授权**
2. **三重取证纪律**：调用图取证 + 生产入口链取证 + 测试对象核对
3. **禁止**：`git add -A`、降级断言、修改 Golden 期望值凑绿
4. **EngineEvidence 只保留事实**：不产生 direction/polarity/strength/confidence

---

*最后更新: 2026-09-01*
