"use client";
export default function StateInterpretation({ content_de, content_zh }: { content_de: string; content_zh?: string }) {
  return (
    <div>
      <p className="text-[15px] leading-[1.6] text-[#d0d6e0]">{content_de}</p>
      {content_zh && <p className="text-[13px] leading-[1.5] text-[#c9a84ccb] italic mt-2">{content_zh}</p>}
    </div>
  );
}