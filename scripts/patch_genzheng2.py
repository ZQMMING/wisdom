# -*- coding: utf-8 -*-
import io
p=r'engines/common/yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old="    gen_zheng = yin_load or ben(dmw)>=1 or (stem(t['bi'])>=1 and ben(t['bi'])>=1)  # 假从回正格: 日主有本气同字根(真从须无根, 从化气CONFIRMED一致)或比劫透干坐本气根, 即不从人、待扶抑\n"
new=("    # 假从回正格: 日主有本气同字根(真从须无根)或比劫坐本气根, 即不从人、待扶抑。\n"
     "    # 土日主特例: 辰丑湿土蓄水藏金, 满盘水金、无火印燥土则湿土从水势(从财), 不作日主根;\n"
     "    # 未戌燥土藏丁火印、火土帮身方为真根(原典: 辰丑湿土从水, 未戌燥土帮身)。\n"
     "    dm_ben_real = ben(dmw)>=1\n"
     "    if dmw=='土':\n"
     "        zao=sum(1 for b in brs if b in ('未','戌','巳','午'))\n"
     "        huo=ben('火')>=1 or stem('火')>=1\n"
     "        if zao==0 and not huo and (ben('水')>=1 or stem('水')>=1):\n"
     "            dm_ben_real=False\n"
     "    gen_zheng = yin_load or dm_ben_real or (dmw!='土' and stem(t['bi'])>=1 and ben(t['bi'])>=1)\n")
assert s.count(old)==1, s.count(old)
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('gen_zheng 湿土燥土区分 done')
