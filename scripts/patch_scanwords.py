# -*- coding: utf-8 -*-
import io
p=r'scripts/direction_scan.py'
s=io.open(p,encoding='utf-8').read()
old_w=",'身强杀浅','身強殺淺','旺相','發越','发越']"
new_w=",'身强杀浅','身強殺淺','旺相','發越','发越','日元强','臨旺','临旺','足以用官','足以任','可以任','旺而逢生','氣旺','气旺','太旺者似','旺極者似','旺极者似','木堅','木坚','金堅','金坚','水旺木堅','水旺木坚']"
old_s=",'孤弱','衰弱','气怯','氣怯','无力','無力']"
new_s=",'孤弱','衰弱','气怯','氣怯','无力','無力','不任','難任','难任','弱可知','衰可知','氣濁神枯','气浊神枯','神枯','泄盡','泄尽','休囚','太衰者似','衰極者似','衰极者似','衰者似','木焚','金沉']"
assert s.count(old_w)==1, ('w',s.count(old_w))
assert s.count(old_s)==1, ('s',s.count(old_s))
s=s.replace(old_w,new_w).replace(old_s,new_s)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('direction_scan 词表扩充')
