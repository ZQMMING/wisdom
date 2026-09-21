# -*- coding: utf-8 -*-
with open('engines/common/yongshen_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在return之前增加_qtbj_assertions计算
old = """    return {'module':'YONGSHEN_ENGINE_V4.1','namespace':'daymaster_yongshen_engine',"""

new = """    # V7.23 P3-001: 生成QTBJ_STEM_ASSERTION结构(只做结构落地, 不进入Judgment)
    _qtbj_assertions = []
    for _i, _c in enumerate(hou_stem):
        _ap = _c.get('applicability', 'APPLICABLE')
        _stem = _c.get('stem', '')
        _el = _c.get('element', '')
        _pri = _c.get('priority', 99)
        _rid = 'QTBJ-' + mz + _stem
        _rt = _stem + '为' + mz + '月调候用'
        _cond = _c.get('applicability_reason', '')
        _prov = 'DIRECT(穷通宝鉴原文)' if _ap == 'APPLICABLE' else 'ENGINEERING_DERIVED'
        _valid = _ap == 'APPLICABLE'
        _qtbj_assertions.append({
            'assertion_id': 'QTBJ-STEM-' + dm + '-' + str(_i+1).zfill(2),
            'track': 'QTBJ',
            'stem': _stem,
            'element': _el,
            'priority': _pri,
            'source_id': _rid,
            'source_text': _rt,
            'assertion_type': 'CLIMATE_STEM',
            'applicability': _ap,
            'condition': _cond,
            'provenance': _prov,
            'valid': _valid,
        })

    return {'module':'YONGSHEN_ENGINE_V4.1','namespace':'daymaster_yongshen_engine',"""

content = content.replace(old, new)

# 在climate_stem_candidates字段后增加qtbj_stem_assertions字段
old2 = "            'climate_stem_candidates': hou_stem,  # V7.23 PATCH: 十干级调候候选(不降级为五行)"
new2 = """            'climate_stem_candidates': hou_stem,  # V7.23 PATCH: 十干级调候候选(不降级为五行)
            'qtbj_stem_assertions': _qtbj_assertions,  # V7.23 P3-001: 十干级调候Assertion结构"""

content = content.replace(old2, new2)

with open('engines/common/yongshen_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
