// 完整 timeIndex 矩阵 0..12:确认每个索引的时辰与时柱。
const { bySolar } = require('iztro').astro;
console.log('ti | timeRange      | chineseDate(年 月 日 时) | soulBranch | soulStars');
for (let ti=0; ti<=12; ti++) {
  const a = bySolar('2020-01-02', ti, 'male', true);
  const soul = a.palaces.find(p=>p.name==='命宫');
  const stars = (soul.majorStars||[]).map(s=>s.name).join('+');
  console.log(`${String(ti).padStart(2)} | ${a.timeRange.padEnd(13)} | ${a.chineseDate.padEnd(23)} | ${a.earthlyBranchOfSoulPalace}         | ${stars}`);
}
