// P0-14 iztro 行为探针:转储 bySolar 的 astrolabe 结构。
const { bySolar } = require('iztro').astro;
const a = bySolar('2020-01-02', 0, 'male', true);
console.log('=== top-level keys ===');
console.log(Object.keys(a).join(', '));
console.log('=== scalar fields ===');
for (const k of ['name','solarDate','lunarDate','chineseDate','timeIndex','gender','fixLeap','earthlyBranchOfSoulPalace','earthlyBranchOfBodyPalace','onum']) {
  if (a[k] !== undefined) console.log(k, '=>', JSON.stringify(a[k]));
}
console.log('=== palaces (name/branch/main stars) ===');
for (const p of a.palaces) {
  const majors = (p.majorStars||[]).map(s=>s.name).join('+');
  console.log(p.name, '|', p.earthlyBranch, '|', majors);
}
