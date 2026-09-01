"use client";
export default function DailyQuote({ quote, author }: { quote: string; author?: string }) {
  return (
    <div className="p-[18px] bg-[#0f1011] rounded-[10px] border border-white/8">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg text-[#c9a84c] opacity-80">「</span>
        <h3 className="text-[14px] font-semibold m-0">Weisheit des Tages</h3>
      </div>
      <p className="text-[16px] leading-[1.65] text-[#f7f8f8] italic">{quote}</p>
      {author && <p className="text-[13px] text-[#8a8f98] mt-2">— {author}</p>}
    </div>
  );
}