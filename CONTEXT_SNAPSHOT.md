# 顺天命理项目 · 上下文快照 V11
> 保存时间：2026-08-28（V11架构全部落地后）
> 用途：防止上下文爆炸，跨对话交接用

## 一、项目位置
- 后端：`D:\today\backend`（git仓库根是 `D:\today`，注意 add 文件要用相对cwd路径，勿 `add -A` 否则会把父目录资料误加）
- 虚拟环境：`D:\today\backend\.venv`（Python 3.11.15）
- 测试运行：`cd D:\today\backend; $env:PYTHONPATH="src"; .\.venv\Scripts\python.exe -m pytest tests/`
- 测试基线：**1646 passed / 5 skipped / 1 xfailed，零失败**

## 二、V11 核心方法论（用户确立，最高原则）
1. **互补不比较**：各体系各司其职，从不同维度印证同一命主，不投票、不比较
2. **反方向 = 算法错误**：体系内在同源，出现反方向即断言层/算法有BUG，当错误修，不设"冲突"状态
3. **每个引擎回归本位强项**：不被统一"方向"壳束缚
- 架构蓝图：`D:\today\backend\ARCHITECTURE_V11.md`

## 三、V11 架构落地（git commit）
```
P1 契约改造    6e222c3  废弃CONFLICTED, 新增AuditFlag
P2-1 子平本位  9470105  旺衰/格局/调候用神/扶抑喜用
P2-2/3 紫微+盲派 4c62dc4 紫微分宫细象, 盲派做功/宾主体用
P3 主题层重写   c0f47cf  投票→互补印证, 反方向不硬决方向
P4 审计流程     645e712  audit_report定位可疑引擎
```

### 断言目录 `src/tongshu/assertion/`
| 文件 | 作用 |
|---|---|
| contract.py | Assertion契约 + **AuditFlag**(V11) + audit_flags字段 |
| systems.py | 4大Producer：Ziwei/Blind/Heluo/Ziping（已本位化） |
| topics.py | 主题Producer + **互补印证聚合**(V11) + _detect_conflict |
| **audit_report.py** | **审计流程(V11-P4)：反方向→定位可疑引擎** |
| advice_optimizer.py | 结构化advice |
| classical_citations.py | 古籍引用注册表 |
| classical_validation.py | 古籍交叉验证 |
| engine.py / flow_year.py / mizhu.py / environmental_fit.py | 其他 |

## 四、各引擎本位维度（V11已回归本位）
| 引擎 | 本位 | 输出(mechanism结构化) |
|---|---|---|
| **子平** | 旺衰/格局/用神 | 旺衰(身强/身弱/从格)+格局(月令立格)+调候用神(《穷通宝鉴》)+扶抑喜用。复用 `strength_engine.evaluate_strength` |
| **紫微** | 星曜/宫位/四化 | 命宫主星+三方四正+**分宫细象**(夫妻/财帛/官禄/疾厄/迁移)+四化 |
| **盲派** | 做功/应期 | **做功结构**(印化官杀/食伤制杀...)+宾主体用(ti/yong)+应期 |
| **河洛** | 卦象/数理 | 先天卦/元堂/后天卦+卦辞+大象+流年卦+人间道(已本位,未改) |

## 五、关键权重表 SYSTEM_WEIGHTS（V11作用：印证权重，非投票）
| 主题 | 紫微 | 盲派 | 河洛 | 子平 |
|---|---|---|---|---|
| 事业 | 0.85 | 0.75 | 0.65 | 0.80 |
| 财运 | 0.75 | 0.85 | 0.70 | 0.80 |
| 婚姻 | 0.90 | 0.70 | 0.60 | 0.75 |
| 健康 | 0.70 | 0.75 | 0.80 | 0.85 |
> 权重只影响"印证度"，**不参与方向表决**（V11）

## 六、审计流程用法（P4）
```python
from tongshu.assertion.audit_report import build_audit_report
r = build_audit_report([断言列表])
# r["most_suspect_engine"] = 冲突频次最高的引擎(最可能算法错)
# r["topics"] = 各主题反方向详情
```
- 反方向时主题层 direction 置 NEUTRAL + 降级待审计，不硬决方向

## 七、当前发现的关键问题（下一步焦点，尚未解决）
用真实命例(1974-04-28申时男)跑审计，**四个主题全部反方向，且阵营系统性相反**：
```
紫微 + 盲派 → 全 positive
子平 + 河洛 → 全 negative
```
- **非主题冲突，是引擎层系统性方向偏差**：子平/河洛整体判负 vs 紫微/盲派整体判正
- 按方法论必有一方方向映射错。最可疑：**子平方向映射**——`evaluate_strength`判身强，但方向映射成negative（身强≠负，要看喜忌：身强喜克泄，遇克泄为吉）
- 下一步：**逐个引擎校准方向映射逻辑**，先查子平（身强/用神已算对，方向映射可能把"身强"固定成某方向）

## 八、用户偏好（对话中确认）
- 粤语为主沟通
- 严禁瞎猜、答案附1-10信心指数（≤7需标注）、数字引文给来源
- 交叉验证（案例+书籍+断言层多维）才下结论
- 不要被测试题带偏，引擎先行校对
- 一级一级递进优化，不搞其他，避免返工
- 保存上下文再继续大工程
