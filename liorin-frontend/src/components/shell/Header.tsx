/**
 * Header — LIORIN logo + 语言 + 时区
 * SPEC §31 App Shell — Logo / Language / Timezone
 */

export function Header() {
  return (
    <header className="flex items-center justify-between px-4 py-3 border-b border-liorin-border">
      <span className="font-display text-base tracking-wide-1 text-liorin-text">
        LIORIN
      </span>
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="font-mono text-xs tracking-wide-1 px-2 py-1 text-liorin-muted hover:text-liorin-text transition-colors"
          aria-label="切换语言"
        >
          🌐 中文
        </button>
        <button
          type="button"
          className="font-mono text-xs tracking-wide-1 px-2 py-1 text-liorin-muted hover:text-liorin-text transition-colors"
          aria-label="切换时区"
        >
          ◷ GMT+8
        </button>
      </div>
    </header>
  );
}
