// P0-14 证据生成:把 iztro 真实输出落盘为 JSON。
const fs = require('fs');
const { bySolar } = require('iztro').astro;
const { version } = require('iztro/package.json');
const OUT = '../docs/v40/p014_evidence';

function fp(a){const m={};for(const p of a.palaces){m[p.name]=`${p.earthlyBranch}|${(p.majorStars||[]).map(s=>s.name).join('+')}`;}return m;}
function dump(d,ti){
  try {
    const a = bySolar(d,ti,'male',true);
    return {solarDate:a.solarDate, lunarDate:a.lunarDate, chineseDate:a.chineseDate,
            timeRange:a.timeRange, soul:a.earthlyBranchOfSoulPalace, body:a.earthlyBranchOfBodyPalace,
            fiveElementsClass:a.fiveElementsClass, palaceFingerprint:fp(a)};
  } catch(e){ return {error:e.message}; }
}

// 1) iztro version
const lock = JSON.parse(fs.readFileSync('../package-lock.json','utf8'));
fs.writeFileSync(`${OUT}/iztro_version.json`, JSON.stringify({
  package_name:'iztro',
  exact_version: version,
  license: 'MIT',
  resolved_tarball: lock.packages['node_modules/iztro'].resolved,
  integrity: lock.packages['node_modules/iztro'].integrity,
  runtime: { node: process.version, npm: '11.13.0' },
  declaration: 'package.json -> "iztro": "2.6.0" (exact)',
  lockfile: 'package-lock.json (lockfileVersion 3)',
}, null, 2));

// 2) G6 A/B
fs.writeFileSync(`${OUT}/g6_ab.json`, JSON.stringify({
  case: 'G6 出生 civil 2020-01-02 00:10 北京(真太阳时→solar 2020-01-01 23:51)',
  encoding_A_civil_date: {bySolar:'2020-01-02, timeIndex=0 (早子时)', ...dump('2020-01-02',0)},
  encoding_B_solar_date: {bySolar:'2020-01-01, timeIndex=12 (晚子时)', ...dump('2020-01-01',12)},
  comparison: {
    chart_identical: JSON.stringify(dump('2020-01-02',0).palaceFingerprint)===JSON.stringify(dump('2020-01-01',12).palaceFingerprint),
    note: 'A与B星盘一致;chineseDate 日柱均=甲辰(2020-01-02);lunarDate 回显不同(初八 vs 初七)'
  }
}, null, 2));

// 3) timeIndex matrix
const matrix = {};
for (let ti=0; ti<=13; ti++) matrix[ti] = dump('2020-01-02', ti);
fs.writeFileSync(`${OUT}/timeindex_matrix.json`, JSON.stringify({date:'2020-01-02', matrix}, null, 2));

// 4) civil vs solar divergence (G3 型: solar 22:xx → 亥; civil 23 → 晚子)
fs.writeFileSync(`${OUT}/civil_vs_solar_divergence.json`, JSON.stringify({
  case: 'G3 出生 civil 2020-01-01 23:00 北京 → solar 22:42(亥时)',
  solar_based_encoding: {bySolar:'2020-01-01, ti=11 (亥)', ...dump('2020-01-01',11)},
  civil_based_encoding: {bySolar:'2020-01-01, ti=12 (晚子)', ...dump('2020-01-01',12)},
  chart_identical: JSON.stringify(dump('2020-01-01',11).palaceFingerprint)===JSON.stringify(dump('2020-01-01',12).palaceFingerprint),
}, null, 2));

// 5) double-roll hazard
fs.writeFileSync(`${OUT}/double_roll_hazard.json`, JSON.stringify({
  case: '若把 已换日的 effective_date(2020-01-02) 配 ti=12 → iztro 二次滚动到 01-03',
  wrong_encoding: dump('2020-01-02',12),
  correct_encodings: {
    solar_date_ti12: dump('2020-01-01',12),
    effective_date_ti0: dump('2020-01-02',0),
  }
}, null, 2));

console.log('evidence written to', OUT);
for (const f of fs.readdirSync(OUT)) console.log(' -', f);
