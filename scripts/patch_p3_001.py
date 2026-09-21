# -*- coding: utf-8 -*-
"""V7.23 P3-001: 建立QTBJ_STEM_ASSERTION结构
只做结构落地, 不进入Judgment
"""

with open('engines/common/yongshen_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在climate_stem_candidates输出前, 增加qtbj_stem_assertions生成逻辑
old = "            'climate_stem_candidates': hou_stem,  # V7.23 PATCH: 十干级调候候选(不降级为五行)"

new = """            # V7.23 P3-001: 生成QTBJ_STEM_ASSERTION结构(只做结构落地, 不进入Judgment)
            # 注意: INAPPLICABLE不是删除候选, 只是不形成有效Assertion
            _qtbj_assertions = []
            for _i, _c in enumerate(hou_stem):
                _ap = _c.get('applicability', 'APPLICABLE')
                _assertion = {
                    'assertion_id': f'QTBJ-STEM-{dm}-{_i+1:02d}',
                    'track': 'QTBJ',
                    'stem': _c.get('stem', ''),
                    'element': _c.get('element', ''),
                    'priority': _c.get('priority', 99),
                    'source_id': f'QTBJ-{mz}{_c.get("stem","")}',
                    'source_text': f'{_c.get("stem","")}为{mz}月调候用',
                    'assertion_type': 'CLIMATE_STEM',
                    'applicability': _ap,
                    'condition': _c.get('applicability_reason', ''),
                    'provenance': 'DIRECT(穷通宝鉴原文)' if _ap == 'APPLICABLE' else 'ENGINEERING_DERIVED',
                    'valid': _ap == 'APPLICABLE',  # 只有APPLICABLE形成有效Assertion
                }
                _qtbj_assertions.append(_assertion)
            'qtbj_stem_assertions': _qtbj_assertions,  # V7.23 P3-001: 十干级调候Assertion结构
            'climate_stem_candidates': hou_stem,  # V7.23 PATCH: 十干级调候候选(不降级为五行)"""

content = content.replace(old, new)

with open('engines/common/yongshen_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
