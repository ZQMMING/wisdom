# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old=("    # 假从回正格: 日主有本气同字根(真从须无根)或比劫坐本气根, 即不从人、待扶抑。\n"
     "    # 土日主特例: 辰丑湿土蓄水藏金, 满盘水金、无火印燥土则湿土从水势(从财), 不作日主根;\n"
     "    # 未戌燥土藏丁火印、火土帮身方为真根(原典: 辰丑湿土从水, 未戌燥土帮身)。\n"
     "    dm_ben_real = ben(dmw)>=1\n"
     "    if dmw=='土':\n"
     "        zao=sum(1 for b in brs if b in ('未','戌','巳','午'))\n"
     "        huo=ben('火')>=1 or stem('火')>=1\n"
     "        if zao==0 and not huo and (ben('水')>=1 or stem('水')>=1):\n"
     "            dm_ben_real=False\n"
     "    gen_zheng = yin_load or dm_ben_real or (dmw!='土' and stem(t['bi'])>=1 and ben(t['bi'])>=1)\n")
new=("    # 假从回正格: 日主有原始本气同字根(真从须无根)。用l0原始藏干本气判定, 三合三会/六合归化\n"
     "    # 不抹煞日主自坐身库本根(申酉戌会金不夺戊土坐戌身库), 避免身库被会局误判真从。\n"
     "    _ganwx={}\n"
     "    for _gs,_wx in [('甲乙','木'),('丙丁','火'),('戊己','土'),('庚辛','金'),('壬癸','水')]:\n"
     "        for _c in _gs: _ganwx[_c]=_wx\n"
     "    _pks=('year','month','day','hour')\n"
     "    raw_ben_branch=[]\n"
     "    for _i,_k in enumerate(_pks):\n"
     "        _hs=facts.get('hidden_stems',{}).get(_k) or []\n"
     "        if _hs and _ganwx.get(_hs[0])==dmw: raw_ben_branch.append(brs[_i])\n"
     "    dm_ben_real=bool(raw_ben_branch)\n"
     "    if dmw=='土':\n"
     "        # 辰丑湿土蓄水藏金: 本气根仅在辰丑湿土、满盘亥子/壬癸水、无丙丁巳午火印与未戌燥土,\n"
     "        # 则湿土从水势(从财)不作日主根; 未戌燥土/火印帮身方为真根(辰丑湿土从水, 未戌燥土帮身)。\n"
     "        zao=any(b in ('未','戌') for b in raw_ben_branch) or any(b in ('巳','午') for b in brs)\n"
     "        huo=stem('火')>=1 or any(b in ('巳','午') for b in brs)\n"
     "        water=stem('水')>=1 or any(b in ('亥','子') for b in brs)\n"
     "        if not zao and not huo and water: dm_ben_real=False\n"
     "    gen_zheng = yin_load or dm_ben_real\n")
assert s.count(old)==1, ('genzheng',s.count(old))
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('gen_zheng 原始藏干本气根(不被会局夺) done')
