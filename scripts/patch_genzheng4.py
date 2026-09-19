# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()

# 修1: gen_zheng 加月令印本气当令托身(提纲为命之主宰, 印当令即使不透亦不从, L1436卯印当令待比劫运)
old1="    gen_zheng = yin_load or dm_ben_real\n"
new1=("    # 月令本气为印且当令有本气根=提纲托身, 印虽不透亦不从(待运透比劫; L1436丙生卯月卯印本气, 丙午比劫破酉封诰吉, 不从官)\n"
      "    _yueyin_tuoshen = BRANCH_WX.get(mz)==t['yin'] and ben(t['yin'])>=1\n"
      "    gen_zheng = yin_load or dm_ben_real or _yueyin_tuoshen\n")
assert s.count(old1)==1,('g1',s.count(old1)); s=s.replace(old1,new1)

# 修2: 印比双透阻断加例外(皆虚透无本气/中余气根、被成势财克尽则虚印比不能留正格, L1618乙丙双透坐丑、金财ben3克尽去印从财)
old2=("    cong_shun = (conf_cong or (cand_cong and not gen_zheng)) and stem(t['yin'])<2 \\\n"
      "        and not (stem(t['yin'])>=1 and stem(t['bi'])>=1)\n")
new2=("    # 印比双透但皆虚透(无本气、无中余气根)而财成势(ben>=3/成局)克尽者, 虚印比不能留正格(L1618)\n"
      "    _yin_bi_xu = stem(t['yin'])>=1 and stem(t['bi'])>=1 and ben(t['yin'])==0 \\\n"
      "        and zhong(t['yin'])+yu(t['yin'])==0 and ben(t['bi'])==0 and zhong(t['bi'])+yu(t['bi'])==0 \\\n"
      "        and (ben(t['cai'])>=3 or cs(t['cai']))\n"
      "    cong_shun = (conf_cong or (cand_cong and not gen_zheng)) and stem(t['yin'])<2 \\\n"
      "        and (not (stem(t['yin'])>=1 and stem(t['bi'])>=1) or _yin_bi_xu)\n")
assert s.count(old2)==1,('g2',s.count(old2)); s=s.replace(old2,new2)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('假从边界两修 done(月令印托身 + 印比双虚被财克尽不阻断)')
