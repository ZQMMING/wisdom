/**
 * Bottom Navigation — TODAY / GUIDE / INSIGHTS / ME
 * SPEC §30 Navigation
 */

interface NavItem {
  key: string;
  label: string;
  icon: string;
}

const ITEMS: NavItem[] = [
  { key: 'today',    label: 'TODAY',    icon: '◐' },
  { key: 'guide',    label: 'GUIDE',    icon: '○' },
  { key: 'insights', label: 'INSIGHTS', icon: '◇' },
  { key: 'me',       label: 'ME',       icon: '●' },
];

interface Props {
  active?: string;
  onChange?: (key: string) => void;
}

export function BottomNav({ active = 'today', onChange }: Props) {
  return (
    <nav
      className="sticky bottom-0 bg-liorin-black/95 backdrop-blur border-t border-liorin-border"
      aria-label="主导航"
    >
      <ul className="flex items-stretch justify-around">
        {ITEMS.map((item) => {
          const isActive = item.key === active;
          return (
            <li key={item.key} className="flex-1">
              <button
                type="button"
                onClick={() => onChange?.(item.key)}
                aria-current={isActive ? 'page' : undefined}
                className={`w-full min-h-[var(--touch-min)] py-2 flex flex-col items-center gap-1 transition-colors ${
                  isActive
                    ? 'text-liorin-accent'
                    : 'text-liorin-muted hover:text-liorin-text'
                }`}
              >
                <span aria-hidden="true" className="text-lg leading-none">
                  {item.icon}
                </span>
                <span className="font-mono text-[10px] tracking-wide-1">
                  {item.label}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
