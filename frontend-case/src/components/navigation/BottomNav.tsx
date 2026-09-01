import React from 'react'

type PageName = 'today' | 'guide' | 'insights' | 'me' | 'more'

interface BottomNavProps {
  activePage: PageName
  onPageChange: (page: PageName) => void
  entitlementLabel?: string
}

/**
 * Bottom Navigation — Section 30 of LIORIN spec
 * 5 tabs: TODAY / GUIDE / INSIGHTS / ME / MORE
 */
const BottomNav: React.FC<BottomNavProps> = ({ activePage, onPageChange, entitlementLabel }) => {
  const tabs: { name: PageName; label: string; icon: React.ReactNode }[] = [
    {
      name: 'today',
      label: 'Today',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          <line x1="2" y1="12" x2="22" y2="12" />
        </svg>
      ),
    },
    {
      name: 'guide',
      label: 'Guide',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        </svg>
      ),
    },
    {
      name: 'insights',
      label: 'Insights',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      ),
    },
    {
      name: 'me',
      label: 'Me',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      ),
    },
    {
      name: 'more',
      label: entitlementLabel || 'More',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
          <circle cx="12" cy="12" r="1" />
          <circle cx="19" cy="12" r="1" />
          <circle cx="5" cy="12" r="1" />
        </svg>
      ),
    },
  ]

  return (
    <nav
      className="bottom-nav"
      style={{
        height: '60px',
        borderTop: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-around',
        background: 'var(--bg-primary)',
        flexShrink: 0,
        position: 'sticky',
        bottom: 0,
        zIndex: 'var(--z-nav)',
      }}
      role="navigation"
      aria-label="主导航"
    >
      {tabs.map((tab) => {
        const isActive = activePage === tab.name
        return (
          <button
            key={tab.name}
            className={`nav-item${isActive ? ' active' : ''}`}
            onClick={() => onPageChange(tab.name)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
              color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
              background: 'none',
              border: 'none',
              fontFamily: 'var(--font-body)',
              fontSize: '9px',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              cursor: 'pointer',
              padding: '8px 12px',
              transition: 'color 150ms ease',
            }}
            onMouseEnter={(e) => {
              if (!isActive) e.currentTarget.style.color = 'var(--text-secondary)'
            }}
            onMouseLeave={(e) => {
              if (!isActive) e.currentTarget.style.color = 'var(--text-muted)'
            }}
            aria-current={isActive ? 'page' : undefined}
            aria-label={tab.label}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        )
      })}
    </nav>
  )
}

export type { PageName }
export default BottomNav
