# -*- coding: utf-8 -*-
f = 'engines/common/daymaster_root_class.py'
c = open(f, encoding='utf-8').read()
old = "        return _r(daymaster, branch, LIGHT_YU_QI, hidden_stems, matched_hidden,\n                  '阴干帝旺位(不论羊刃, 作余气根)', same_char, same_element, False)"
new = "        return _r(daymaster, branch, HEAVY_WANG, hidden_stems, matched_hidden,\n                  '阴干帝旺位(不论羊刃, 但作重根)', same_char, same_element, True)"
c = c.replace(old, new)
open(f, 'w', encoding='utf-8').write(c)
print('done')
