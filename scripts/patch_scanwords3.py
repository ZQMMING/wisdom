# -*- coding: utf-8 -*-
import io
p=r'scripts/direction_scan.py'
s=io.open(p,encoding='utf-8').read()
old="QUOTE=re.compile(r'不可损|不可益|即余之|此两句|太旺太衰|经云|經云|书云|書云|语云|語云|岂不知|豈不知|旺之极者不|衰之极者不|以上.{0,4}造|五行极[旺衰]|極旺極衰')"
new="QUOTE=re.compile(r'不可损|不可益|即余之|此两句|太旺太衰|经云|經云|书云|書云|语云|語云|岂不知|豈不知|旺之极者不|衰之极者不|以上.{0,4}造|五行极[旺衰]|極旺極衰|何知其人|当令者倍之|當令者倍之|休囚者减半|休囚者減半|木三金四')"
assert s.count(old)==1
io.open(p,'w',encoding='utf-8',newline='').write(s.replace(old,new))
print('QUOTE 加法则/何知章远窗口拦截')
