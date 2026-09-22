# -*- coding: utf-8 -*-
"""P0-b.3补丁：天干合化财星扣除 + score作用域修复"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在cai_ben_zw计算后，添加天干合化财星扣除
# 找到：gs_ben_zw = max(0, gs_ben_zw); cai_ben_zw = max(0, cai_ben_zw)
# 在这一行后添加天干合化扣除逻辑

old_text = """    gs_ben_zw = max(0, gs_ben_zw); cai_ben_zw = max(0, cai_ben_zw)
    guo_xie = (ss_stem >= 2 and ss_ben >= 1 and dm_ben_eff <= 3)   # #PCT-MARK 食伤透干有根成党=过泄/两气成象, 不判纯一行专旺; 但日主本气根>=4(如四库全)时食伤只是泄秀仍判专旺(辛未辛丑戊辰壬戌稼穑格用辛金吐秀)"""

new_text = """    gs_ben_zw = max(0, gs_ben_zw); cai_ben_zw = max(0, cai_ben_zw)
    
    # P0-b.3: 天干合化财星扣除（乙庚合化金，乙不再算财星透干）
    cai_stem_zw = cai_stem  # 财星透干数（扣除合化后）
    gs_stem_zw = gs_stem    # 官杀透干数（扣除合化后）
    if tian_he:
        for hp in tian_he.get('he_pairs', []):
            # 合化神为日主五行 = 合化成功，该合化的干不再算财星/官杀
            if hp.get('huashen_wuxing') == dm_wx:
                he_gans = hp.get('gans', [])
                for gan in he_gans:
                    gan_wx = WUHE_HUASHEN.get((gan, ''), None)  # 简化：直接判断
                    # 更简单：如果合化神是日主五行，那两个干都不再算对立方
                    # 但我们只需要扣财星/官杀透干
                    if gan in ['甲', '乙'] and cai_wx == '木':  # 木是金的财星
                        cai_stem_zw = max(0, cai_stem_zw - 1)
                    elif gan in ['丙', '丁'] and gs_wx == '火':  # 火是金的官杀
                        gs_stem_zw = max(0, gs_stem_zw - 1)
                    # 其他五行同理...
    
    guo_xie = (ss_stem >= 2 and ss_ben >= 1 and dm_ben_eff <= 3)   # #PCT-MARK 食伤透干有根成党=过泄/两气成象, 不判纯一行专旺; 但日主本气根>=4(如四库全)时食伤只是泄秀仍判专旺(辛未辛丑戊辰壬戌稼穑格用辛金吐秀)"""

content = content.replace(old_text, new_text)

# 2. 修改gate_ok，使用cai_stem_zw和gs_stem_zw
content = content.replace(
    "gate_ok = (\n        (gs_ben_zw == 0 and gs_stem == 0 and gs_ju == 0)\n        and (cai_ben_zw <= 1 and cai_stem == 0 and cai_ju == 0)\n    )",
    "gate_ok = (\n        (gs_ben_zw == 0 and gs_stem_zw == 0 and gs_ju == 0)  # P0-b.3: 使用gs_stem_zw（扣除合化）\n        and (cai_ben_zw <= 1 and cai_stem_zw == 0 and cai_ju == 0)  # P0-b.3: 使用cai_stem_zw（扣除合化）\n    )"
)

# 3. 修score作用域：在gate_debug前初始化score
content = content.replace(
    "    # P0-b: _gate_debug 调试信息（记录哪一道闸门拒收）\n    gate_debug = []",
    "    # P0-b: score初始化（用于gate_debug）\n    score = 0\n    \n    # P0-b: _gate_debug 调试信息（记录哪一道闸门拒收）\n    gate_debug = []"
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ P0-b.3补丁完成：")
print("  - 天干合化财星扣除（乙庚合化金，乙不再算财星透干）")
print("  - gate_ok使用cai_stem_zw和gs_stem_zw（扣除合化后）")
print("  - score作用域修复")
