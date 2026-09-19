# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()

# 1. B2 食伤制杀 zhi_ok 收紧: 须食伤本气根/成势(干多不如根重), 中余气虚透不任制强杀
old1="                zhi_ok=stem(t['shi'])>=1 and qi(t['shi'])"
new1="                zhi_ok=stem(t['shi'])>=1 and (ben(t['shi'])>=1 or cs(t['shi']))  # 食伤须本气根/成势方任制杀, 中余气虚透不制强杀"
assert s.count(old1)==1, ('zhi_ok',s.count(old1))
s=s.replace(old1,new1)

# 2. B2 身弱杀重印无气、取印待运分支: 官杀当前攻身, 忌官杀再旺
old2=("                else:\n"
      "                    P(t['yin'],'BINGYAO','官杀重，取印化杀待运'); S(t['bi'])\n")
new2=("                else:\n"
      "                    P(t['yin'],'BINGYAO','官杀重身轻印无气，取印化杀待运'); S(t['bi'])\n"
      "                    if tier in SHUAI_TIER: A(t['guan'],'杀重身轻印未到位，官杀再旺攻身忌')\n")
assert s.count(old2)==1, ('B2else',s.count(old2))
s=s.replace(old2,new2)

# 3. 身弱食伤泄气太过: 食伤生财, 财亦泄身; 印无力化官则官杀亦忌
old3="            P(t['yin'],'BINGYAO','食伤泄气太过，印制食伤扶身'); S(t['bi']); A(t['shi'])"
new3="            P(t['yin'],'BINGYAO','食伤泄气太过，印制食伤扶身'); S(t['bi']); A(t['shi'],t['cai'])"
assert s.count(old3)==1, ('shi_xie',s.count(old3))
s=s.replace(old3,new3)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('身弱杀重/食伤泄 喜忌收紧 done')
