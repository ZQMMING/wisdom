# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在用神引擎输出中增加theory_source字段
old = """    return {'module':'YONGSHEN_ENGINE_V2','namespace':'daymaster_yongshen_engine',
            'day_master':dm,'daymaster_wuxing':dmw,'spectrum_tier':tier,'special':spec_name,
            'yongshen_primary':primary,'yongshen_secondary':secondary,'yongshen_avoid':avoid,
            'yongshen_paths':paths,"""

new = """    # V4.1: 理论来源标签 (基于primary用神的路径标签映射到理论来源)
    # 路径标签 -> 理论来源映射
    PATH_TO_THEORY = {
        'HUA_QI': 'THEORY_ZIPING',      # 化气格 -> 子平真诠
        'CONG_SHUN': 'THEORY_ZIPING',   # 从格顺用 -> 子平真诠
        'WANG_KE': 'THEORY_ZIPING',     # 旺极克泄 -> 子平真诠
        'ZHUANWANG': 'THEORY_ZIPING',   # 专旺格 -> 子平真诠
        'QIHOU': 'THEORY_QIONGTONG',    # 调候 -> 穷通宝鉴
        'LIANGQI': 'THEORY_ZIPING',     # 两气格 -> 子平真诠
        'BINGYAO': 'THEORY_SHENFENG',   # 病药 -> 神峰通考
        'FUYI': 'THEORY_ZIPING',        # 扶抑 -> 子平真诠
        'TONGGUAN': 'THEORY_ZIPING',    # 通关 -> 子平真诠
    }
    primary_path = paths[0] if paths else ''
    theory_source = PATH_TO_THEORY.get(primary_path, 'THEORY_ZIPING')  # 默认子平真诠
    
    return {'module':'YONGSHEN_ENGINE_V4.1','namespace':'daymaster_yongshen_engine',
            'day_master':dm,'daymaster_wuxing':dmw,'spectrum_tier':tier,'special':spec_name,
            'theory_source':theory_source,  # 理论来源标签 (ZIPING/QIONGTONG/SHENFENG)
            'yongshen_primary':primary,'yongshen_secondary':secondary,'yongshen_avoid':avoid,
            'yongshen_paths':paths,"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.1完成(增加theory_source字段: 基于路径标签映射到ZIPING/QIONGTONG/SHENFENG)')
