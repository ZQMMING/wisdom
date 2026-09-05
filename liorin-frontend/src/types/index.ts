/**
 * View Model Types
 * Frontend NEVER computes (SPEC §5) — all fields come from backend canonical state.
 */

export type YaoType = 'yang' | 'yin';
export type Entitlement = 'public' | 'authenticated' | 'premium';
export type ProfileStatus = 'none' | 'insufficient' | 'valid';

export interface Yao {
  position: number;          // 1-6
  type: YaoType;
  active?: boolean;
}

export interface Cycle {
  cycle_id: string;
  hexagram_id: string;
  hexagram_name: string;
  start_date: string;
  end_date: string;
  cycle_day: number;
  total_days: 6;
}

export interface ActiveYao {
  yao_id: string;
  position: number;
  type: YaoType;
  label: string;
}

export interface Guidance {
  classical: string;
  modern: string;
  action: string;
}

// =========================================
// 三体系数据（前端只 render）
// =========================================

export interface HeluoPanel {
  /** 河洛母题今天的关键数字组合（1-10） */
  numbers: number[];
  /** 一句话解读（"今日五行气运"） */
  summary: string;
  /** 详细字段（地图块） */
  fields: Array<{ label: string; value: string }>;
}

export interface YijingPanel {
  /** 本卦卦名（已是 cycle.hexagram_name，这里给卦辞原文） */
  hexagram_text: string;
  /** 变爻爻辞 */
  line_text: string;
  /** 一句话解读 */
  summary: string;
}

export interface ZiweiPanel {
  /** 紫微主星（如：紫微星 / 天机星 ...） */
  main_star: string;
  /** 宫位（如：命宫 / 迁移宫） */
  palace: string;
  /** 一句话解读 */
  summary: string;
}

// =========================================
// Insight / Action / Evidence（SPEC §38）
// =========================================

export interface InsightItem {
  kind: 'opportunity' | 'risk' | 'remedy';
  title: string;
  detail: string;
}

export interface ActionItem {
  index: number;             // 01 / 02 / 03
  title: string;
  detail: string;
}

export interface EvidenceItem {
  source: string;            // 原典出处，如《子平真诠·卷一》
  excerpt: string;
}

export interface PersonalToday {
  cycle: Cycle;
  yaos: Yao[];
  active_yao: ActiveYao;
  guidance: Guidance;
  heluo: HeluoPanel;
  yijing: YijingPanel;
  ziwei: ZiweiPanel;
  insights: InsightItem[];
  actions: ActionItem[];
  evidence: EvidenceItem[];
}

export interface ViewModel {
  entitlement: Entitlement;
  profile_status: ProfileStatus;
  today: PersonalToday;
}
