# -*- coding: utf-8 -*-
import io
p=r'engines/common/yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old=("        _lp=paths[-1] if paths else ''\n"
     "        if _lp=='WANG_KE':\n"
     "            # 逆用官杀/财修旺(实=正格身旺, 克泄耗为用): 忌印比帮身抗官杀, 喜食伤泄秀; P官则喜财生官, P财滋弱杀则喜官\n"
     "            A(yw,t['bi'])\n"
     "            S(sw,'身旺食伤泄秀')\n"
     "            if primary==gw: S(cw,'财生官杀')\n"
     "            if primary==cw: S(gw,'官杀得财滋')\n"
     "        else:\n"
     "            # 顺用ZHUANWANG / 调候QIHOU: 顺印比、忌官杀逆克、忌财(调候分支已显式S者由互斥收敛保留)\n"
     "            S(yw,'顺性喜印'); S(t['bi'],'顺性喜比劫')\n"
     "            if primary!=gw: A(gw)\n"
     "            if primary!=cw: A(cw)\n")
new=("        _lp=paths[-1] if paths else ''\n"
     "        if _lp=='WANG_KE':\n"
     "            # 逆用官杀/财修旺(实=正格身旺, 克泄耗为用): 忌印比帮身, 喜食伤泄秀、财(身旺任财/财生官杀)\n"
     "            A(yw,t['bi'])\n"
     "            S(sw,'身旺食伤泄秀'); S(cw,'身旺任财/财生官杀')\n"
     "            if primary==cw: S(gw,'官杀得财滋')\n"
     "        elif _lp=='QIHOU':\n"
     "            # 调候(润燥暖局): 喜忌由分支显式给出, 块尾不默认顺印比、不笼统忌财官\n"
     "            pass\n"
     "        else:\n"
     "            # 顺用ZHUANWANG: 顺比劫、顺食伤; 官杀岁运至犯旺恒忌。财喜忌看官杀透否:\n"
     "            # 官杀透干(虽虚)则财生官杀逆局, 忌财; 官杀不透则财顺食伤生(顺泄生财/身旺任财), 喜财。\n"
     "            # 印不默认喜(专旺气壅、且印克食伤断秀), 仅在分支显式用印时喜。\n"
     "            S(t['bi'],'顺性喜比劫')\n"
     "            if stem(gw)>=1:\n"
     "                A(gw,cw)\n"
     "            else:\n"
     "                A(gw); S(cw,'食伤生财/身旺任财')\n")
assert s.count(old)==1, s.count(old)
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('专旺块尾财喜忌系统修正 done')
