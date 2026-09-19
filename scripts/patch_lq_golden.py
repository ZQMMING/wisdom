# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\tests\test_special_pattern_golden.py'
s=io.open(p,encoding='utf-8').read()

old1=("    ('戊戌辛酉戊戌辛酉', '金'),  # 土金成象, 取辛金伤官为用\n"
      "    ('癸亥甲寅癸亥甲寅', '木'),  # 水木清华, 水生木顺木(食伤)秀神\n"
      "]\n")
new1=("    ('戊戌辛酉戊戌辛酉', '金'),  # 土金成象, 取辛金伤官为用\n"
      "    # 癸亥甲寅(DTS L862)移出两气锚点: 寅亥合木、伤官太重泄身, 任注定性水木伤官格喜土金印官, 非两气; 见下方反例\n"
      "]\n")
assert s.count(old1)==1,('g1',s.count(old1)); s=s.replace(old1,new1)

old2=("          + ' 得=' + str(None if not lq else (lq.get('name'), lq.get('xiu'))))\n"
      "\n"
      "print()\n"
      "print('TOTAL', len(CASES) + len(MUMIE) + len(LIANGQI), 'FAILS', fails)\n")
new2=("          + ' 得=' + str(None if not lq else (lq.get('name'), lq.get('xiu'))))\n"
      "\n"
      "# 假两气反例(DTS L862 癸亥甲寅): 两行相生, 然日主根亥被寅亥合化为食伤木、伤官太重泄身,\n"
      "# 任注'水木伤官...己酉戊申二十年土金生化不悖'(逢克方反吉), 应回正格水木伤官用印, 不判两气成象\n"
      "_pp=gp('癸亥甲寅癸亥甲寅'); _ff=l0b(_pp); _tt=build_tian_he(_pp,_ff); _ww=build_wuxing_power(_pp,_ff,_tt)\n"
      "_ss=build_special_patterns(_pp,_ff,_ww,_tt); _lq=_ss.get('liangqi')\n"
      "_ok=(_lq is None)\n"
      "if not _ok: fails+=1\n"
      "print('PASS' if _ok else 'FAIL','癸亥甲寅癸亥甲寅 假两气应不判(回正格水木伤官) 得=',_lq)\n"
      "\n"
      "print()\n"
      "print('TOTAL', len(CASES) + len(MUMIE) + len(LIANGQI) + 1, 'FAILS', fails)\n")
assert s.count(old2)==1,('g2',s.count(old2)); s=s.replace(old2,new2)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('golden L862反例固化 done')
