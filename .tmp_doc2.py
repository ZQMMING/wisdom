# -*- coding: utf-8 -*-
import io
p = "docs/v2/盲派9例对齐验证_V3.4.3.md"
src = io.open(p, encoding="utf-8").read()
old = """## 测试
"""
new = """## 深度复核（第二轮，逐条回原文取证）
"""
# 在测试段前插入
if "深度复核" not in src:
    src = src.replace(old, new, 1)
# 替换测试段
old2 = """## 测试
- 盲派全套 86 passed / 7 subtests passed（themes/golden/negative/rule_compliance/signal_regression/integration_bazi/yingqi）。
- 全量 2979 passed；159 fail/err 经 stash 基线对比确认**全部预先存在**（紫微/子平用户端代码 + 缺 `docs/k2g/datasets/baziqa_2021.json` 等数据文件），与本次改动无关。
- 盲派相关失败：0。
"""
new2 = """## 深度复核（第二轮，逐条回原文取证）

复核发现并修复 **3 处新缺陷**（第一轮修复不完整）：

1. **归因抢注缺陷**（`_analyze_zuogong` L705）：同一做功方式存在多个配对时，首个（可能宾位 INEFFECTIVE）抢注方法名，主位 EFFECTIVE 版本被 `triggered` 丢弃。
   - 案例3：日支申制时支巳七杀（主位制杀），被"月未丁官制年支申比肩(宾位)"抢注成 INEFFECTIVE
   - 案例7：日支巳财制年支申印（主位财制印），被"月未丁财制年支申印"抢注成 INEFFECTIVE
   - 修复：同方法后续配对只允许 INEFFECTIVE→EFFECTIVE 升级（主位覆盖宾位，不允许降级）
2. **燥土脆金伤禄遗漏**（`_resolve_body_candidate`）：案例3 原文"申金被**未土脆克**+巳火合克，禄神环境恶劣"——第一轮只补了合克，漏了脆金。补 VERIFY-BLIND-034 判据（禄金 + 未/戌燥土 + 四柱无水）。
3. **R2 天干明克制官**（`_resolve_zheng_fan_ju`）：反证 D28（己巳乙亥壬申丁未，牢狱）原文"左边伤官制官（乙木克己土）"=年柱天干紧贴明克，做功层按宾位判 INEFFECTIVE 丢失 → 反局误放行。补"相邻(含同柱)天干伤官克正官"判据，D28 恢复 FAN_JU ✓。

**反证验证**（R2 收紧未误放行真反局）：
- D28 牢狱：FAN_JU ✓（R2 日主合正财 vs 伤官制官）
- D19 反局、乾隆（制净）：ZHENG ✓（无合官/合财+去官结构）
- #9 复合做功（合财+制杀）：ZHENG ✓（非冲突）

**规则延伸标注**：#8 新增 BODY_LU_ATTACK（辛酉坐禄被未土脆金，VERIFY-BLIND-034 合理推论；原文 #8 未提身体，属规则延伸非原文断语）；#3/#4 财从 UNTAKEN→ESTABLISHED（归因升级副作用，原文未涉财，方向不冲突）。

## 测试
- 盲派全套 86 passed / 7 subtests passed（themes/golden/negative/rule_compliance/signal_regression/integration_bazi/yingqi）。
- 全量 2979 passed；159 fail/err 经 stash 基线对比确认**全部预先存在**（紫微/子平用户端代码 + 缺 `docs/k2g/datasets/baziqa_2021.json` 等数据文件），与本次改动无关。
- 盲派相关失败：0。
"""
assert old2 in src, "测试段OLD NOT FOUND"
src = src.replace(old2, new2, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 文档已更新")
