# -*- coding: utf-8 -*-
import io
p=r'engines/common/yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old="    gen_zheng = yin_load or (ben(dmw)>=1 and ben(t['yin'])>=1)"
new=("    gen_zheng = yin_load or ben(dmw)>=1 or (stem(t['bi'])>=1 and ben(t['bi'])>=1)  "
     "# 假从回正格: 日主有本气同字根(真从须无根, 从化气CONFIRMED一致)或比劫透干坐本气根, 即不从人、待扶抑\n")
assert s.count(old)==1, s.count(old)
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('gen_zheng 补日主本气根/比劫坐根 done')
