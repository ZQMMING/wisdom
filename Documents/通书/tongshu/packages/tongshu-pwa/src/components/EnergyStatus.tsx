"use client";
export default function EnergyStatus({ level }: { level: "high" | "mid" | "low" }) {
  const cfg = {
    high: { text: "Stark", color: "#2d9d6f", bg: "#2d9d6f1a" },
    mid:  { text: "Ausgewogen", color: "#c9a84c", bg: "#c9a84c1a" },
    low:  { text: "Schwach", color: "#b84a4a", bg: "#b84a4a1a" },
  }[level];
  return (
    <span className="inline-flex items-center gap-1.5 px-[10px] py-[3px] rounded-[6px] font-medium text-[12px]"
      style={{ color: cfg.color, background: cfg.bg, border: `1px solid ${cfg.color}33` }}>
      <span className="w-[6px] h-[6px] rounded-full" style={{ background: cfg.color }} />
      {cfg.text}
    </span>
  );
}