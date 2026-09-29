# P0欠账案：transit_power浮点权重依赖

## 现状
- `engines/common/transit_power.py` 第45行调用 `build_wuxing_power`（已删除）
- 活链 `dayun_summary` / `liunian_summary` 真实依赖浮点权重体系

## 矛盾
- 8案例零变化 + 活链在跑 → 说明该调用路径运行时必被try吞或未触发
- 大运流年力量裁决实际瘫痪或走兜底

## 待裁
大运流年力量按章程重定——《三命通会》大运"过度之处即有灾殃"、流年太岁生克明据 → 应改纯规则裁决，与浮点体系彻底切割

## 状态
冻结，排期，不动活链
