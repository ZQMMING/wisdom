# -*- coding: utf-8 -*-
# 从官/从杀格忌食伤: 身已从官杀, 食伤克所从之神(食神制杀/伤官见官)=逆局破格
# 原典: 从格顺用; L300 己丑丙子丁亥庚子(从杀水)辛未土食伤制杀"比劫夺财大凶";
#       L1656 乙卯己卯戊辰癸亥(从官木)癸酉金食伤当令冲卯克官"落职而亡"。
# 财生官杀为喜(S财); 印比统一在块尾A; 此补食伤A。
import io
fp=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(fp,encoding='utf-8').read()
old="""        elif '从官' in cong or '从杀' in cong or '从煞' in cong:
            P(t['guan'],'CONG_SHUN','从官杀顺官杀'); S(t['cai'],'财生官杀')"""
assert s.count(old)==1, s.count(old)
new="""        elif '从官' in cong or '从杀' in cong or '从煞' in cong:
            P(t['guan'],'CONG_SHUN','从官杀顺官杀'); S(t['cai'],'财生官杀'); A(t['shi'],'从官杀忌食伤(制杀/伤官见官破格)')"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched congguan/sha ji shishang')
