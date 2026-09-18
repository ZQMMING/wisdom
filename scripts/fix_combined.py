# -*- coding: utf-8 -*-
f = 'engines/common/daymaster_power_queries.py'
c = open(f, encoding='utf-8').read()
old = """                    if huashen:
                        return True
    return False"""
new = """                    if huashen and month_wx == huashen:
                        return True
    return False"""
c = c.replace(old, new)
open(f, 'w', encoding='utf-8').write(c)
print('done')
