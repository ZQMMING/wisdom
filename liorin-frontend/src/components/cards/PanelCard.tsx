/**
 * 通用 Panel 容器
 * 河洛 / 易经 / 紫微三张卡共用同一个壳
 */

import type { ReactNode } from 'react';

interface Props {
  label: string;             // "河洛" / "易经" / "紫微"
  summary: string;
  detail?: ReactNode;        // 子内容（map / 卦辞 / 主星信息）
}

export function PanelCard({ label, summary, detail }: Props) {
  return (
    <article className="border border-liorin-border rounded-md p-4 bg-liorin-surface/40">
      <header className="flex items-baseline justify-between mb-2">
        <span className="font-mono text-[0.65rem] tracking-wide-2 text-liorin-accent">
          {label}
        </span>
      </header>
      <p className="text-sm text-liorin-text leading-relaxed mb-3">
        {summary}
      </p>
      {detail ? (
        <div className="text-sm text-liorin-muted">
          {detail}
        </div>
      ) : null}
    </article>
  );
}
