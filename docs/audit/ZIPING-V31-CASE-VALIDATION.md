# ZIPING V3.1 案例端到端验证

> 5/5 案例 PASS, 0 FAIL 项.


【1980-06-22 巳 男 (旗舰)】
  排盘=['庚申', '壬午', '丙寅', '癸巳'] 期望=['庚申', '壬午', '丙寅', '癸巳'] ✓
  丙日午月 同火得令; 寅丙长生; 壬癸官杀混杂浊; 午夏HOT; 建禄根被申冲降条件
  ✓ LING=DE_LING rule=['LING-010'] ev=['E-ZQ-LING-001']
  ✓ GROWTH=ROOTING rule=['GROWTH-003'] ev=['E-YH-GROWTH-003']
  ✓ STRENGTH=WANG_BUT_NOT_STRONG rule=['STRENGTH-011'] ev=['E-DT-STRENGTH-011']
  ✓ CLIMATE=HOT rule=['CLIMATEFACT-003'] ev=['E-DT-CLIMATEFACT-003']
  ✓ QING=TURBID rule=['QING-005'] ev=['E-ZQ-QING-005']
  ✓ QI=CONCENTRATED rule=['QI-001'] ev=['E-DT-QI-001']

【1985-01-01 子 男 (冬水寒)】
  排盘=['甲子', '丙子', '庚子', '丙子'] sxtwl=['甲子', '丙子', '庚子', '丙子'] ✓ 一致
  1月1日 在小寒(1/5)前 → 仍属丑月(冬) → COLD; 日主由 sxtwl 独立排定
  ✓ CLIMATE=COLD rule=['CLIMATEFACT-002'] ev=['E-DT-CLIMATEFACT-002']

【1990-07-15 午 男 (夏火旺)】
  排盘=['庚午', '癸未', '辛巳', '甲午'] sxtwl=['庚午', '癸未', '辛巳', '甲午'] ✓ 一致
  午月夏 HOT; 日主看排盘
  ✓ CLIMATE=HOT rule=['CLIMATEFACT-003'] ev=['E-DT-CLIMATEFACT-003']

【1995-11-08 酉 女 (亥月冬)】
  排盘=['乙亥', '丁亥', '癸卯', '辛酉'] sxtwl=['乙亥', '丁亥', '癸卯', '辛酉'] ✓ 一致
  sxtwl 排定 亥月(立冬后) → 冬 COLD; 女命; 日主 丁 看排盘
  ✓ CLIMATE=COLD rule=['CLIMATEFACT-002'] ev=['E-DT-CLIMATEFACT-002']

【1988-03-20 辰 男 (卯月春)】
  排盘=['戊辰', '乙卯', '甲戌', '戊辰'] sxtwl=['戊辰', '乙卯', '甲戌', '戊辰'] ✓ 一致
  sxtwl 排定 乙卯(卯月=春), 甲日; 非寒暖极端 → CLIMATE 可UNDETERMINED
  ✓ CLIMATE=UNDETERMINED(FACT_MISSING) fail-closed
