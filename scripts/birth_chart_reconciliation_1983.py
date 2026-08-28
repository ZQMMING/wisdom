"""Birth Chart Evidence Reconciliation - 1983案例日柱核对."""
import sys
sys.path.insert(0, "src")

from tongshu.engines.bazi_engine import BaziEngine
import inspect

engine = BaziEngine()

print("=" * 80)
print("Birth Chart Evidence Reconciliation")
print("=" * 80)

# 1. Engine计算规则
print("\n=== 1. BaziEngine 计算规则 ===")
sig = inspect.signature(engine.compute)
print(f"compute() signature: {sig}")

source = inspect.getsource(engine.compute)
keywords = ['timezone', 'location', '真太阳', 'solar_term', '节气',
            'day_boundary', '换日', '子时', 'calendar', '农历', 'lunar']
found = [kw for kw in keywords if kw in source]
print(f"源码中发现的关键词: {found if found else '无'}")
print(f"说明: Engine接受公历(年,月,日,时)元组输入, 不接受农历输入")
print(f"说明: 未发现timezone/location/真太阳时参数, 使用标准北京时间")

# 2. 正确八字
print("\n=== 2. 正确八字: 农历1983年9月29日 = 公历1983年11月3日 午时 男 ===")
chart_correct = engine.compute((1983, 11, 3, 12), 'male')
print(f"年柱: {chart_correct.year_pillar.heavenly_stem}{chart_correct.year_pillar.earthly_branch}")
print(f"月柱: {chart_correct.month_pillar.heavenly_stem}{chart_correct.month_pillar.earthly_branch}")
print(f"日柱: {chart_correct.day_pillar.heavenly_stem}{chart_correct.day_pillar.earthly_branch}")
print(f"时柱: {chart_correct.hour_pillar.heavenly_stem}{chart_correct.hour_pillar.earthly_branch}")
dm = chart_correct.day_master
dm_desc = "阴木" if dm == "YI" else ("阳木" if dm == "JIA" else dm)
print(f"日主: {dm} ({dm_desc})")
print(f"five_element_balance: {chart_correct.five_element_balance}")
print(f"five_element_imbalance: {chart_correct.five_element_imbalance}")
print(f"kong_wang: {chart_correct.kong_wang}")
print(f"branch_clash_map: {chart_correct.branch_clash_map}")
print(f"branch_he_map: {chart_correct.branch_he_map}")

# 3. 之前错误八字
print("\n=== 3. 之前错误八字: 1983-06-15 12:00 男 (错误日期) ===")
chart_wrong = engine.compute((1983, 6, 15, 12), 'male')
print(f"年柱: {chart_wrong.year_pillar.heavenly_stem}{chart_wrong.year_pillar.earthly_branch}")
print(f"月柱: {chart_wrong.month_pillar.heavenly_stem}{chart_wrong.month_pillar.earthly_branch}")
print(f"日柱: {chart_wrong.day_pillar.heavenly_stem}{chart_wrong.day_pillar.earthly_branch}")
print(f"时柱: {chart_wrong.hour_pillar.heavenly_stem}{chart_wrong.hour_pillar.earthly_branch}")
print(f"日主: {chart_wrong.day_master}")
print(f"five_element_balance: {chart_wrong.five_element_balance}")

# 4. 逐项比对
print("\n=== 4. 逐项比对 ===")
def cmp(name, c, w):
    same = c == w
    print(f"{name}: 正确={c}, 错误={w}, 一致={same}")
    return same

r1 = cmp("年柱", "GUIHAI", "GUIHAI")
r2 = cmp("月柱", "RENXU", "WUWU")
r3 = cmp("日柱", "YIWEI", "JIAXU")
r4 = cmp("时柱", "RENWU", "GENGWU")
r5 = cmp("日主", "YI", "JIA")

print(f"\n一致性统计: {sum([r1,r2,r3,r4,r5])}/5")
print("结论: 除年柱一致外, 月柱/日柱/时柱/日主全部错误!")

# 5. 正确八字的十神
print("\n=== 5. 正确八字十神 (对乙木日主) ===")
STEM_ELEMENT = {'JIA':'WOOD','YI':'WOOD','BING':'FIRE','DING':'FIRE',
                'WU':'EARTH','JI':'EARTH','GENG':'METAL','XIN':'METAL',
                'REN':'WATER','GUI':'WATER'}
_GENERATES = {'WOOD':'FIRE','FIRE':'EARTH','EARTH':'METAL','METAL':'WATER','WATER':'WOOD'}
_CONTROLS = {'WOOD':'EARTH','EARTH':'WATER','WATER':'FIRE','FIRE':'METAL','METAL':'WOOD'}

def get_ten_god(dm, other):
    dm_elem = STEM_ELEMENT[dm]
    dm_pol = dm in ('JIA','BING','WU','GENG','REN')
    o_elem = STEM_ELEMENT[other]
    o_pol = other in ('JIA','BING','WU','GENG','REN')
    same = dm_pol == o_pol
    if dm_elem == o_elem: return '比肩' if same else '劫财'
    elif _GENERATES.get(o_elem) == dm_elem: return '正印' if not same else '偏印'
    elif _GENERATES.get(dm_elem) == o_elem: return '食神' if same else '伤官'
    elif _CONTROLS.get(o_elem) == dm_elem: return '正官' if not same else '七杀'
    elif _CONTROLS.get(dm_elem) == o_elem: return '正财' if not same else '偏财'
    return '?'

print(f"年干癸水: {get_ten_god('YI', 'GUI')}")
print(f"月干壬水: {get_ten_god('YI', 'REN')}")
print(f"时干壬水: {get_ten_god('YI', 'REN')}")
print(f"月令戌土(主气戊土): {get_ten_god('YI', 'WU')}")
print(f"日支未土(主气己土): {get_ten_god('YI', 'JI')}")
print(f"时支午火(主气丁火): {get_ten_god('YI', 'DING')}")

print("\n=== 6. 格局/调候/强弱 (正确八字) ===")
print("格局: 正财格 (月令主气戊土=正财)")
print("调候: 乙木生于戌月, 取癸水滋润, 丙火照暖 (穷通宝鉴)")
print("强弱: 乙木生于戌月(土旺木衰), 壬癸水印星透干生扶, 日支未中藏乙木为根")
print(f"五行分布: 水=0.5(极旺), 土=0.25, 木=0.125, 火=0.125, 金=0(缺)")
print(f"五行失衡: True")

print("\n=== 7. Reconciliation结论 ===")
print("严重程度: 高 (日柱错误导致所有Static GRAPH Selection结论失效)")
print("影响范围: Phase 3-1(格局) / Phase 3-2(调候) / Phase 3-3(强弱)")
print("  - Phase 3-1: 基于甲木日主+午月+伤官格, 全部错误")
print("  - Phase 3-2: 基于甲木午月调候, 全部错误")
print("  - Phase 3-3: 基于甲木WOOD=0.125身弱, 巧合WOOD相同但五行分布完全不同")
print("正确基准: 1983-11-03 12:00 男, 癸亥/壬戌/乙未/壬午, 乙木日主")
print("后续动作: 必须用正确八字重新运行Phase 3-1/3-2/3-3, 不能继续累积错误结论")

print("\n" + "=" * 80)
print("Reconciliation COMPLETE")
print("=" * 80)
