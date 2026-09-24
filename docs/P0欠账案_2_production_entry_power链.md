# P0欠账案_2：production_entry power链静默瘫痪

## 现状
- `production_entry.py` 第62行import已删模块 `daymaster_power_queries`
- 第74行活调用 `run_queries(network)`
- 外层try吞ImportError → `_build_power_network` 静默瘫痪
- 每次启动必走except，用户无感

## 归因
静默瘫痪型（与transit_power案同型：P0只删叶节点，活链底下的根没断）

## 影响面
- `run_queries` 全部调用点待grep统计
- except吞了之后的兜底行为待写进案卷

## 修复方向
与transit_power案合并——power体系根重建，按章程改纯规则

## 状态
冻结，与案1同批排期

## 系统性漏洞记录
P0清除"只删引用、未验启动路径覆盖"——以后删模块的标准动作补一条：**启动入口全量跑一遍看有没有ImportError被吞**
