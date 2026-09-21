# -*- coding: utf-8 -*-
"""V7.23 P2: 给climate_stem_candidates增加applicability字段"""

with open('engines/common/yongshen_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在第759行前增加applicability判断
old = "            'climate_stem_candidates': hou_stem,  # V7.23 PATCH: 十干级调候候选(不降级为五行)"

new = """            # V7.23 P2: 给调候候选增加applicability字段(区分"冲突"与"不适用")
            # 三态: APPLICABLE / INAPPLICABLE / CONDITIONAL
            _zhuanwang_wx = {'炎上':'火','曲直':'木','从革':'金','润下':'水','稼穑':'土'}
            _cong_wx = {'从财':'财','从杀':'杀','从儿':'儿','从强':'强','从弱':'弱'}
            for _cand in hou_stem:
                _cand_wx = _cand.get('element', '')
                _applicability = 'APPLICABLE'
                _applicability_reason = '正格/普通命局, 调候轨适用'
                # 专旺格: 调候克专旺五行 → INAPPLICABLE
                for _zw_name, _zw_wx in _zhuanwang_wx.items():
                    if _zw_name in (zw or ''):
                        # 克专旺五行的调候 → 不适用
                        _ke_wx = {'火':'水','木':'金','金':'火','水':'土','土':'木'}
                        if _ke_wx.get(_zw_wx) == _cand_wx:
                            _applicability = 'INAPPLICABLE'
                            _applicability_reason = f'{_zw_name}格可顺不可逆, {_cand_wx}为忌(调候不适用)'
                            break
                        # 专旺五行本身 → CONDITIONAL(需泄秀)
                        elif _zw_wx == _cand_wx:
                            _applicability = 'CONDITIONAL'
                            _applicability_reason = f'{_zw_name}格, {_cand_wx}需泄秀(条件适用)'
                            break
                # 从格: 调候违从格之势 → INAPPLICABLE
                if _applicability == 'APPLICABLE':
                    if '从财' in (cong or ''):
                        # 从财忌印比
                        if _cand_wx in ('木','火'):  # 印比(假设日主木, 印=水, 比=木)
                            _applicability = 'INAPPLICABLE'
                            _applicability_reason = '从财格忌印比帮身(调候不适用)'
                    elif '从杀' in (cong or ''):
                        # 从杀忌食伤
                        if _cand_wx in ('木','火','土','金','水'):  # 简化: 食伤制杀
                            _applicability = 'INAPPLICABLE'
                            _applicability_reason = '从杀格忌食伤制杀(调候不适用)'
                    elif '从儿' in (cong or ''):
                        # 从儿忌印
                        if _cand_wx in ('水','土','火','木','金'):  # 简化: 印克食伤
                            _applicability = 'INAPPLICABLE'
                            _applicability_reason = '从儿格忌印克食伤(调候不适用)'
                _cand['applicability'] = _applicability
                _cand['applicability_reason'] = _applicability_reason
            'climate_stem_candidates': hou_stem,  # V7.23 PATCH: 十干级调候候选(不降级为五行)"""

content = content.replace(old, new)

with open('engines/common/yongshen_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
