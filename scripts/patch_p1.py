# -*- coding: utf-8 -*-
with open('scripts/dayun_align.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = "} if _dx_judg != 'neutral' and _dx_judg != expect else {'has_conflict': False}"

new = """} if _dx_judg != 'neutral' and _dx_judg != expect else {'has_conflict': False}
        # V7.23 P1: 十干级调候匹配类型(不改变主判断, 只输出信息)
        _stem_match_type = dx_step.get('stem_match_type', 'NONE')
        stem_match_info = {
            'type': _stem_match_type,
            'candidates': [c['stem'] for c in ye.get('climate_stem_candidates', [])],
            'note': 'EXACT_STEM=大运天干精确匹配调候用神; ELEMENT_MATCH=五行匹配但天干不同; NONE=无匹配'
        }"""

if old in content:
    content = content.replace(old, new)
    with open('scripts/dayun_align.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Old string not found')
