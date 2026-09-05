import type { ViewModel } from '../types';

/**
 * MOCK ONLY — NOT FOR PRODUCTION
 * 前端禁计算（SPEC §5）。所有字段由后端 canonical state 提供。
 */

export const MOCK_PERSONAL_DAY3: ViewModel = {
  entitlement: 'authenticated',
  profile_status: 'valid',
  today: {
    cycle: {
      cycle_id: 'c-001',
      hexagram_id: '14',
      hexagram_name: '大有',
      start_date: '2026-08-30',
      end_date: '2026-09-04',
      cycle_day: 3,
      total_days: 6,
    },
    yaos: [
      { position: 1, type: 'yang' },
      { position: 2, type: 'yang' },
      { position: 3, type: 'yang', active: true },
      { position: 4, type: 'yin'  },
      { position: 5, type: 'yang' },
      { position: 6, type: 'yang' },
    ],
    active_yao: {
      yao_id: 'y3',
      position: 3,
      type: 'yang',
      label: '三爻',
    },
    guidance: {
      classical: '九三：公用享于天子，小人害。',
      modern:   '今日宜把握机会，展现能力，但需守正。',
      action:   '专注于当下职责，避免越界。',
    },

    heluo: {
      numbers: [1, 6, 8],
      summary: '今日水生木，五行气运偏上，利于沟通与表达。',
      fields: [
        { label: '天干', value: '壬' },
        { label: '地支', value: '寅' },
        { label: '五行局', value: '水二局' },
        { label: '值日星', value: '文曲' },
      ],
    },

    yijing: {
      hexagram_text: '大有：元亨。',
      line_text: '九三：公用享于天子，小人害。',
      summary: '光明盛大之象，宜守正而不居功。',
    },

    ziwei: {
      main_star: '紫微星',
      palace: '命宫',
      summary: '主星入命，贵人相助，今日决策以稳为主。',
    },

    insights: [
      { kind: 'opportunity', title: '沟通窗口', detail: '上午 9-11 点适合发起重要对话与提案。' },
      { kind: 'risk',        title: '过劳信号', detail: '下午容易感到疲惫，注意适时休息。' },
      { kind: 'remedy',      title: '行运调和', detail: '短途步行与清淡饮食可稳定气运。' },
    ],

    actions: [
      { index: 1, title: '回复关键邮件', detail: '上午优先处理悬而未决的两封邮件。' },
      { index: 2, title: '整理本周清单', detail: '把待办重新按优先级排序，砍掉非关键项。' },
      { index: 3, title: '提前 30 分钟结束', detail: '给自己一个缓冲，避免加班。' },
    ],

    evidence: [
      { source: '《子平真诠·卷一》', excerpt: '用神得力，格局自成。' },
      { source: '《滴天髓》',       excerpt: '强众而敌寡者，势在去其寡。' },
      { source: '《渊海子平·气象》', excerpt: '水生木而木秀，气运上行。' },
    ],
  },
};
