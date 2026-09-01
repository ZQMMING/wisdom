import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface ProfileData {
  birth_date: string;
  birth_time: string;
  gender: "male" | "female";
  city: string;
  profile_id?: string;
}

interface DailyModule {
  id: string;
  title_de: string;
  title_zh: string;
  content_de: string;
  content_zh?: string;
  [key: string]: any;
}

interface DailyData {
  date: string;
  lunar: string;
  ganzhi: { year: string; month: string; day: string };
  solar_term?: string;
  moduls: DailyModule[];
  personal?: { match: string; advice_de: string };
}

interface TongshuStore {
  profile: ProfileData | null;
  daily: DailyData | null;
  loading: boolean;
  error: string | null;
  setProfile: (p: ProfileData) => void;
  clearProfile: () => void;
  fetchDaily: () => Promise<void>;
}

export const useTongshuStore = create<TongshuStore>()(
  persist(
    (set, get) => ({
      profile: null,
      daily: null,
      loading: false,
      error: null,
      setProfile: (p) => set({ profile: p }),
      clearProfile: () => set({ profile: null, daily: null }),
      fetchDaily: async () => {
        const { profile } = get();
        set({ loading: true, error: null });
        try {
          const params = profile?.profile_id ? `?profile_id=${profile.profile_id}` : "";
          const r = await fetch(`/daily${params}`);
          const d = await r.json();
          set({ daily: d, error: null });
        } catch (e: any) {
          set({ error: e.message });
        } finally {
          set({ loading: false });
        }
      },
    }),
    { name: "tongshu-storage", partialize: (s) => ({ profile: s.profile }) }
  )
);