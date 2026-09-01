"use client";
type ActionGuideData = { yi?: string[]; ji?: string[] };
export default function ActionGuide({ data }: { data: ActionGuideData }) {
  return (
    <div className="space-y-3">
      {data.yi?.length > 0 && (
        <div>
          <span className="block text-[11px] font-semibold text-[#8a8f98] uppercase tracking-[0.5px] mb-1.5">Günstig</span>
          <div className="flex flex-wrap gap-[6px]">
            {data.yi.map((y, i) => (
              <span key={i} className="text-[12px] font-medium text-[#2d9d6f] bg-[#2d9d6f]/12 px-[10px] py-[3px] rounded-[6px] border border-[#2d9d6f]/20">{y}</span>
            ))}
          </div>
        </div>
      )}
      {data.ji?.length > 0 && (
        <div>
          <span className="block text-[11px] font-semibold text-[#8a8f98] uppercase tracking-[0.5px] mb-1.5">Weniger</span>
          <div className="flex flex-wrap gap-[6px]">
            {data.ji.map((j, i) => (
              <span key={i} className="text-[12px] font-medium text-[#b84a4a] bg-[#b84a4a]/12 px-[10px] py-[3px] rounded-[6px] border border-[#b84a4a]/20">{j}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}