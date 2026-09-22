# -*- coding: utf-8 -*-
"""P0-b.5补丁：修正天干合化扣除逻辑的键名（gans→stems）"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修正：he_pairs里的键是'stems'，不是'gans'
old_text = """    # P0-b.3: 天干合化财星扣除（乙庚合化金，乙不再算财星透干）
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
                    # 其他五行同理..."""

new_text = """    # P0-b.3: 天干合化财星扣除（乙庚合化金，乙不再算财星透干）
    cai_stem_zw = cai_stem  # 财星透干数（扣除合化后）
    gs_stem_zw = gs_stem    # 官杀透干数（扣除合化后）
    if tian_he:
        for hp in tian_he.get('he_pairs', []):
            # 合化神为日主五行 = 合化成功，该合化的干不再算财星/官杀
            if hp.get('huashen_wuxing') == dm_wx:
                he_stems = hp.get('stems', [])
                for gan in he_stems:
                    # 如果合化神是日主五行，那两个干都不再算对立方
                    # 但我们只需要扣财星/官杀透干
                    # 财星五行是KE[dm_wx]（克我者为官杀，我克者为财）
                    # 不对：我克者为财，克我者为官杀
                    # dm_wx的财星是KE[dm_wx]（我克），官杀是KE_ME[dm_wx]（克我）
                    gan_wx = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
                              '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}.get(gan)
                    if gan_wx == cai_wx:  # 该干是财星
                        cai_stem_zw = max(0, cai_stem_zw - 1)
                    elif gan_wx == gs_wx:  # 该干是官杀
                        gs_stem_zw = max(0, gs_stem_zw - 1)"""

content = content.replace(old_text, new_text)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ P0-b.5补丁完成：修正天干合化扣除逻辑的键名（gans→stems）")
