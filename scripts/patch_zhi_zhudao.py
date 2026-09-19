# -*- coding: utf-8 -*-
# 干支异向-运支成势主导(优先级, 非数量): 正格身衰(衰极/太衰/衰)、运干fav虚透复合tier<=1、
# 运支为财(我克)或官杀(克我)且复合成势tier>=2、且运干非食伤(食伤制杀/调候为发用真神, 不适用被压)
# -> 身弱难任财官, 支凶主导av_l(比劫/印fav虚透被成势财官压: 帮身无力/财坏印)。
# 从格/专旺/化气/两气顺用不适用。
# 对: L1264庚午(比劫虚、午杀成势)、L437甲申乙酉(印虚、财成势财坏印)、L646己巳(印虚、官杀成势官晦印);
# 排除误伤: L70丁未/L751丙戌(食伤制杀调候, 原文科甲/选知县吉)。
import io
fp=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(fp,encoding='utf-8').read()
old="""        if lc is None:
            ss={gc,zc}"""
assert s.count(old)==1, s.count(old)
new="""        # 身衰正格、运支财/官杀成势压虚透喜干(非食伤) -> 支凶主导(身弱难任财官, 优先级非数量)
        if lc is None and _spec in ('衰极','太衰','衰') and gc=='fav' and zc!='fav':
            _dmwZ=GAN_WX[dm]; _KEMEZ={vv:kk for kk,vv in KE.items()}
            _ppZ='/'.join(ye.get('yongshen_paths') or [])
            if (BRANCH_WX[z] in (KE.get(_dmwZ), _KEMEZ.get(_dmwZ))
                    and GAN_WX[g] != SHENG.get(_dmwZ)
                    and not any(x in _ppZ for x in ('CONG','ZHUANWANG','HUA_QI','LIANGQI'))
                    and element_power_tier(tp['wuxing_power'],BRANCH_WX[z])['tier']>=2
                    and element_power_tier(tp['wuxing_power'],GAN_WX[g])['tier']<=1):
                lc='av_l'
        if lc is None:
            ss={gc,zc}"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched shen-shuai zhi chengshi zhudao (exclude shishang)')
