
import { astro } from './node_modules/iztro/lib/index.js';

const dates = ["1983-06-01"];
const timeIdx = [0];
const genders = ['male', 'female'];
const leaps = [true, false];
const STEMS = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'];
const BRANCHES = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'];

const out = [];
for (let i = 0; i < dates.length; i++) {
  const d = dates[i];
  const t = timeIdx[i % timeIdx.length];
  const g = genders[i % 2];
  const l = leaps[i % 2];
  const c = astro.bySolar(d, t, g, l, 'zh-CN');
  const j = c.toJSON();
  out.push({
    birthInfo: {
      year: parseInt(d.slice(0,4)), month: parseInt(d.slice(5,7)),
      day: parseInt(d.slice(8,10)), hour: t, gender: g, longitude: 120,
    },
    system: 'iztro-bridge',
    chart: {
      birthInfo: {
        year: parseInt(d.slice(0,4)), month: parseInt(d.slice(5,7)),
        day: parseInt(d.slice(8,10)), hour: t, gender: g, longitude: 120,
      },
      lunarInfo: {
        lunarYear: j.lunarDate.year, lunarMonth: j.lunarDate.month,
        lunarDay: j.lunarDate.day, yearStem: 0, yearBranch: 0, isLeapMonth: l,
      },
      mingGongBranch: 0, shenGongBranch: 0,
      wuxingJu: 5, wuxingJuName: '土五局', ziweiPos: 0,
      palaces: j.palaces.map(p => ({
        branch: BRANCHES.indexOf(p.earthlyBranch),
        stem: STEMS.indexOf(p.heavenlyStem),
        name: p.name,
        stars: [
          ...(p.majorStars || []).map(s => ({
            name: s.name, type: 'major',
            brightness: s.brightness || 'normal',
            mutagen: s.mutagen || '',
          })),
          ...(p.minorStars || []).map(s => ({
            name: s.name, type: 'minor', brightness: s.brightness || '',
            mutagen: s.mutagen || '',
          })),
          ...(p.adjectiveStars || []).map(s => ({
            name: s.name, type: 'lucky', brightness: '',
            mutagen: '',
          })),
        ],
        daXianAge: [0, 10],
        isMingGong: p.isMingGong,
        isShenGong: p.isBodyPalace,
        isCurrentDaXian: false,
      })),
    },
  });
}
console.log(JSON.stringify(out));
