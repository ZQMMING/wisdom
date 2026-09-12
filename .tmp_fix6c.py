# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_judgment.py"
src = io.open(p, encoding="utf-8").read()

old = """        if ms == 'BROKEN':
            evts.append(self._make_event(
                'MARRIAGE', 'MARRIAGE_BROKEN', JDGDirection.IN_AUSPICIOUS,
                f"spouse_palace={m.get('spouse_palace')}(day)+star_weakened={m.get('spouse_star_weakened')}",
                ['EVT-MARRIAGE-001', 'JDG-MARRIAGE-001'], ['BLIND-DJ-004'],
                'day', 'spouse_star', 'EVT-MARRIAGE-001', None))
            rules.append('JDG-MARRIAGE-001')
"""
new = """        if ms == 'BROKEN':
            evts.append(self._make_event(
                'MARRIAGE', 'MARRIAGE_BROKEN', JDGDirection.IN_AUSPICIOUS,
                f"spouse_palace={m.get('spouse_palace')}(day)+star_weakened={m.get('spouse_star_weakened')}"
                f"+star_into_muku={m.get('spouse_star_into_muku')}",
                ['EVT-MARRIAGE-001', 'JDG-MARRIAGE-001'],
                ['BLIND-DJ-012'] if m.get('spouse_star_into_muku') == 'True' else ['BLIND-DJ-004'],
                'day', 'spouse_star', 'EVT-MARRIAGE-001', None))
            rules.append('JDG-MARRIAGE-001')
"""
assert old in src, "婚姻BROKEN OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 婚姻BROKEN detail 已补")
