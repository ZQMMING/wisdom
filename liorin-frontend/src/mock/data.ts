import type { ViewModel } from '../types';

/**
 * MOCK ONLY — NOT FOR PRODUCTION
 * 前端禁计算（SPEC §5），所有字段由后端 canonical state 提供
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
  },
};
