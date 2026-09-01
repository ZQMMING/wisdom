import React from 'react'

interface HeaderProps {
  brand?: string
  timezone?: string
  lang?: string
  onLangChange?: () => void
  onTimezoneChange?: () => void
}

/**
 * App Shell Header — Section 31 of LIORIN spec
 * Logo + language + timezone. No divination info here.
 */
const Header: React.FC<HeaderProps> = ({
  brand = 'LIORIN',
  timezone = 'GMT+8',
  lang = '中文',
  onLangChange,
  onTimezoneChange,
}) => {
  return (
    <header
      className="app-header"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 32px',
        height: '56px',
        borderBottom: '1px solid var(--border)',
        background: 'var(--bg-primary)',
        flexShrink: 0,
        position: 'sticky',
        top: 0,
        zIndex: 'var(--z-header)',
      }}
      role="banner"
    >
      <div
        style={{
          fontSize: '13px',
          fontWeight: 500,
          letterSpacing: '0.15em',
          textTransform: 'uppercase',
          color: 'var(--text-primary)',
        }}
      >
        {brand}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button
          className="control-btn"
          onClick={onLangChange}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            fontFamily: 'var(--font-body)',
            fontSize: '11px',
            cursor: 'pointer',
            padding: '6px 8px',
            transition: 'color 150ms ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
          aria-label="切换语言"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <line x1="2" y1="12" x2="22" y2="12" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>
          <span>{lang}</span>
        </button>

        <button
          className="control-btn"
          onClick={onTimezoneChange}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            fontFamily: 'var(--font-body)',
            fontSize: '11px',
            cursor: 'pointer',
            padding: '6px 8px',
            transition: 'color 150ms ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
          aria-label="切换时区"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          <span>{timezone}</span>
        </button>
      </div>
    </header>
  )
}

export default Header
