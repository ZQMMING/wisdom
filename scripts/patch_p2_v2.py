# -*- coding: utf-8 -*-
with open('engines/common/yongshen_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = "    hou = [c['element'] for c in hou_stem]  # 原hou逻辑不变，保持向后兼容"

new = """    hou = [c['element'] for c in hou_stem]  # 原hou逻辑不变，保持向后兼容
    # V7.23 P2: 给调候候选增加applicability字段(区分"冲突"与"不适用")
    _ZW_WX = {'炎上':'火','曲直':'木','从革':'金','润下':'水','稼穑':'土'}
    _KE = {'火':'水','木':'金','金':'火','水':'土','土':'木'}
    for _c in hou_stem:
        _wx = _c.get('element', '')
        _ap = 'APPLICABLE'
        _ap_r = '正格/普通命局, 调候轨适用'
        for _zn, _zw in _ZW_WX.items():
            if _zn in (zw or ''):
                if _KE.get(_zw) == _wx:
                    _ap = 'INAPPLICABLE'
                    _ap_r = _zn + '格可顺不可逆, ' + _wx + '为忌(调候不适用)'
                elif _zw == _wx:
                    _ap = 'CONDITIONAL'
                    _ap_r = _zn + '格, ' + _wx + '需泄秀(条件适用)'
                break
        if _ap == 'APPLICABLE':
            if '从财' in (cong or ''):
                if _wx in ('木', '火'):
                    _ap = 'INAPPLICABLE'
                    _ap_r = '从财格忌印比帮身(调候不适用)'
            elif '从杀' in (cong or ''):
                _ap = 'INAPPLICABLE'
                _ap_r = '从杀格忌食伤制杀(调候不适用)'
            elif '从儿' in (cong or ''):
                _ap = 'INAPPLICABLE'
                _ap_r = '从儿格忌印克食伤(调候不适用)'
        _c['applicability'] = _ap
        _c['applicability_reason'] = _ap_r"""

if old in content:
    content = content.replace(old, new)
    with open('engines/common/yongshen_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Old string not found')
