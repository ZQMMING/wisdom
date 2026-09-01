import React from 'react'

/**
 * INSIGHTS page — Section 38-44 of LIORIN spec
 */
const InsightsPage: React.FC = () => {
  return (
    <div style={{ maxWidth: '640px', margin: '0 auto', padding: '48px 24px 64px' }}>
      <div style={{
        fontSize: '9px', letterSpacing: '0.2em', textTransform: 'uppercase',
        color: 'var(--text-muted)', marginBottom: '12px',
      }}>
        Insights
      </div>
      <h1 style={{
        fontFamily: 'var(--font-display)', fontSize: '26px', fontWeight: 400,
        color: 'var(--text-primary)', marginBottom: '32px',
      }}>
        洞察
      </h1>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Period card */}
        <div>
          <div style={{
            fontSize: '9px', letterSpacing: '0.2em', textTransform: 'uppercase',
            color: 'var(--text-muted)', marginBottom: '8px',
          }}>
            Period
          </div>
          <h2 style={{
            fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 400,
            color: 'var(--text-primary)', marginBottom: '8px',
          }}>
            申月 · 金旺水相
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
            当前处于农历七月，金气旺盛，水得生助。
          </p>
        </div>

        <div style={{ width: '100%', height: '1px', background: 'var(--border)' }} />

        {/* Trend card */}
        <div>
          <div style={{
            fontSize: '9px', letterSpacing: '0.2em', textTransform: 'uppercase',
            color: 'var(--text-muted)', marginBottom: '8px',
          }}>
            Trend
          </div>
          <h2 style={{
            fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 400,
            color: 'var(--text-primary)', marginBottom: '8px',
          }}>
            收敛 · 整理 · 准备
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
            未来数日呈现能量内收的态势，适合整理与准备，不宜大规模行动。
          </p>
          <button style={{
            background: 'none', border: 'none', color: 'var(--text-muted)',
            fontFamily: 'var(--font-body)', fontSize: '10px', letterSpacing: '0.15em',
            textTransform: 'uppercase', cursor: 'pointer', padding: '8px 0',
            marginTop: '8px', transition: 'color 150ms ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
          >
            查看全部 →
          </button>
        </div>
      </div>
    </div>
  )
}

export default InsightsPage
