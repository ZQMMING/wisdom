"use client";
export default function DailyRhythm({ data }: { data: { morning?: string; afternoon?: string; evening?: string } }) {
  const rows = [
    ["☀️", "Vormittag", data.morning?.split(": ")[1] || "—"],
    ["🌤", "Nachmittag", data.afternoon?.split(": ")[1] || "—"],
    ["🌙", "Abend", data.evening?.split(": ")[1] || "—"],
  ];
  return (
    <div className="border-t border-white/5 pt-3 space-y-2">
      {rows.map(([emo, lab, val]) => (
        <div key={lab} className="flex items-center gap-2.5">
          <span className="text-base w-6 text-center">{emo}</span>
          <div>
            <span className="block text-[12px] font-medium text-[#8a8f98]">{lab}</span>
            <span className="block text-[14px] font-medium text-[#d0d6e0]">{val}</span>
          </div>
        </div>
      ))}
    </div>
  );
}