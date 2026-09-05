/**
 * 视图模型类型
 * 字段前端只 render，禁计算（参见 SPEC §0）
 */

export type YaoType = 'yang' | 'yin';

export interface Yao {
  position: number;          // 1-6
  type: YaoType;
  active?: boolean;          // 是否今日动爻
}

export interface Cycle {
  cycle_id: string;
  hexagram_id: string;
  hexagram_name: string;     // 例："大有"
  start_date: string;
  end_date: string;
  cycle_day: number;          // 1-6
  total_days: 6;
}

export interface ActiveYao {
  yao_id: string;
  position: number;
  type: YaoType;
  label: string;              // 例："三爻"
}

export interface Guidance {
  classical: string;
  modern: string;
  action: string;
}

export interface PersonalToday {
  cycle: Cycle;
  yaos: Yao[];
  active_yao: ActiveYao;
  guidance: Guidance;
}

export type Entitlement = 'public' | 'authenticated' | 'premium';
export type ProfileStatus = 'none' | 'insufficient' | 'valid';

export interface ViewModel {
  entitlement: Entitlement;
  profile_status: ProfileStatus;
  today: PersonalToday;
}
