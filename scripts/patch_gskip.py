# -*- coding: utf-8 -*-
# g类噪声skip(不计分母), 两型:
# (混句 L435) 同一切片"初交A吉,一交B凶"含他运(在本造大运序列内)转折, 单步无法归属 -> skip
# (流年 L1473) 大凶明指流年"X年...亡/死/不禄"而非本运 -> skip
# 严条件: 他运干支必须在 dy 序列; 流年须配死亡词。切段三次证伪, 此处只整句skip不切。
import io
fp=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(fp,encoding='utf-8').read()
old="""        if blob and blob.lstrip().startswith('【原注】'):
            v=None
        if not v or v=='hun' or v=='lao':"""
assert s.count(old)==1, s.count(old)
new="""        if blob and blob.lstrip().startswith('【原注】'):
            v=None
        if blob and v:
            _dygz=set(dy); _cur=g+z
            _other_yun=re.findall(r'[交至走逢又]+\\s*([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])', blob)
            _liunian=re.findall(r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])年', blob)
            _hun=any(x!=_cur and x in _dygz for x in _other_yun)
            _ln=any(x!=_cur for x in _liunian) and re.search(r'亡|死|不禄', blob)
            if _hun or _ln: v=None
        if not v or v=='hun' or v=='lao':"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched g-skip hunju/liunian')
