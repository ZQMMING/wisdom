// 判别实验:晚子时(ti12)的星盘到底用输入日 还是 次日。
const { bySolar } = require('iztro').astro;
function fp(a){const m={};for(const p of a.palaces){m[p.name]=`${p.earthlyBranch}|${(p.majorStars||[]).map(s=>s.name).join('+')}`;}return m;}
function run(label,d,ti){
  const a=bySolar(d,ti,'male',true);
  const f=fp(a);
  const hash=JSON.stringify(f);
  console.log(`${label}  (${d}, ti=${ti}): solar=${a.solarDate} lunar=${a.lunarDate} gz=${a.chineseDate} soul=${a.earthlyBranchOfSoulPalace}`);
  console.log(`    fp_hash=${hash.slice(0,70)}...  soulStars=${f['命宫']}  fiveElements=${a.fiveElementsClass}`);
  return hash;
}
const h_j1_ti0 = run('A  Jan1 早子', '2020-01-01', 0);
const h_j1_ti12= run('B  Jan1 晚子', '2020-01-01', 12);
const h_j2_ti0 = run('C  Jan2 早子', '2020-01-02', 0);
const h_j2_ti12= run('D  Jan2 晚子', '2020-01-02', 12);
const h_j3_ti0 = run('E  Jan3 早子', '2020-01-03', 0);

console.log('\n==== 判定 ====');
console.log('B(Jan1 ti12) == C(Jan2 ti0)? 星盘', h_j1_ti12===h_j2_ti0 ? 'SAME → ti12 按次日布星' : 'DIFFERENT');
console.log('B(Jan1 ti12) == A(Jan1 ti0)? 星盘', h_j1_ti12===h_j1_ti0 ? 'SAME → ti12 按当日布星' : 'DIFFERENT');
console.log('D(Jan2 ti12) == E(Jan3 ti0)? 星盘', h_j2_ti12===h_j3_ti0 ? 'SAME → ti12 按次日布星' : 'DIFFERENT');
console.log('D(Jan2 ti12) == C(Jan2 ti0)? 星盘', h_j2_ti12===h_j2_ti0 ? 'SAME → ti12 按当日布星' : 'DIFFERENT');
console.log('\nA vs C (跨日同 ti0):', h_j1_ti0===h_j2_ti0?'SAME':'DIFFERENT (预期不同:腊月初七 vs 初八)');
