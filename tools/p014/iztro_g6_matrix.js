// P0-14: G6 A/B + timeIndex 矩阵。目标:确认 iztro 实际如何解释输入。
const { bySolar } = require('iztro').astro;

function fingerprint(a) {
  const map = {};
  for (const p of a.palaces) {
    const majors = (p.majorStars||[]).map(s=>s.name).join('+');
    map[p.name] = `${p.earthlyBranch}|${majors}`;
  }
  return map;
}
function dump(label, dateStr, ti) {
  try {
    const a = bySolar(dateStr, ti, 'male', true);
    const fp = fingerprint(a);
    console.log(`--- ${label}  bySolar(${dateStr}, ti=${ti}) ---`);
    console.log(`  solarDate=${a.solarDate}  lunarDate=${a.lunarDate}`);
    console.log(`  chineseDate=${a.chineseDate}`);
    console.log(`  timeIndex=${a.timeIndex} timeRange=${JSON.stringify(a.timeRange)}`);
    console.log(`  soulPalace=${a.earthlyBranchOfSoulPalace}  bodyPalace=${a.earthlyBranchOfBodyPalace}`);
    console.log(`  soulPalace_stars=${fp['命宫']}  soul fiveElements=${a.fiveElementsClass}`);
    // 核心盘结构指纹:全部 12 宫
    console.log(`  fp=${JSON.stringify(fp)}`);
    return {solarDate:a.solarDate, lunarDate:a.lunarDate, chineseDate:a.chineseDate,
            soul:a.earthlyBranchOfSoulPalace, body:a.earthlyBranchOfBodyPalace, fp};
  } catch(e) {
    console.log(`--- ${label}  bySolar(${dateStr}, ti=${ti}) ---`);
    console.log(`  ERROR: ${e.message}`);
    return {error: e.message};
  }
}

console.log('################ G6 A/B ################');
const A = dump('G6-A civil date  早子时', '2020-01-02', 0);   // civil 00:10 → ti0
const B = dump('G6-B solar-derived 晚子时', '2020-01-01', 12); // solar 23:51 → ti12

console.log('\n################ A vs B 差异 ################');
console.log('A.chineseDate =', A.chineseDate);
console.log('B.chineseDate =', B.chineseDate);
console.log('A.lunarDate   =', A.lunarDate);
console.log('B.lunarDate   =', B.lunarDate);
console.log('chart identical?', JSON.stringify(A.fp) === JSON.stringify(B.fp));

console.log('\n################ timeIndex 矩阵 (固定日期 2020-01-02) ################');
for (const ti of [10, 11, 12, 13]) {
  dump(`ti=${ti}`, '2020-01-02', ti);
}

console.log('\n################ 23:00 边界:同日 ti11 vs ti12 vs 次日 ti0 ################');
const c11 = dump('前一日 22:00 → ti11 (亥)', '2020-01-01', 11);
const c12 = dump('前一日 23:00 → ti12 (晚子)', '2020-01-01', 12);
const d0  = dump('当日 00:00 → ti0 (早子)', '2020-01-02', 0);
console.log('chineseDate c11=', c11.chineseDate, '| c12=', c12.chineseDate, '| d0=', d0.chineseDate);
console.log('c12 日柱是否已翻到次日?', c12.chineseDate && c12.chineseDate.split(' ')[2]);
