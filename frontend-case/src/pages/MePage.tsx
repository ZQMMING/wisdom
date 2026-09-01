import React from 'react'

/**
 * ME page — Section 45-53 of LIORIN spec
 */
const MePage: React.FC = () => {
  const menuItems = [
    { label: 'Profile', title: '完善个人资料', sub: '出生日期、时间、地点' },
    { label: 'My Chart', title: '命盘查看', sub: '八字 · 紫微 · 河洛' },
    { label: 'Settings', title: '语言与时区', sub: '显示偏好' },
    { label: 'Subscription', title: '免费版', sub: '每日一次免费洞察' },
  ]

  return (
    <div style={{ maxWidth: '640px', margin: '0 auto', padding: '48px 24px 64px' }}>
      <div style={{
        fontSize: '9px', letterSpacing: '0.2em', textTransform: 'uppercase',
        color: 'var(--text-muted)', marginBottom: '12px',
      }}>
        Me
      </div>
      <h1 style={{
        fontFamily: 'var(--font-display)', fontSize: '26px', fontWeight: 400,
        color: 'var(--text-primary)', marginBottom: '32px',
      }}>
        个人资料
      </h1>

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {menuItems.map((item, i) => (
          <div
            key={i}
            style={{
              padding: '16px 0',
              borderBottom: i < menuItems.length - 1 ? '1px solid var(--border)' : 'none',
              cursor: 'pointer',
            }}
          >
            <div style={{
              fontSize: '9px', letterSpacing: '0.2em', textTransform: 'uppercase',
              color: 'var(--text-muted)', marginBottom: '4px',
            }}>
              {item.label}
            </div>
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            }}>
              <div>
                <div style={{
                  fontSize: '14px', color: 'var(--text-primary)',
                }}>
                  {item.title}
                </div>
                <div style={{
                  fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px',
                }}>
                  {item.sub}
                </div>
              </div>
              <span style={{ color: 'var(--text-muted)', fontSize: '16px' }}>›</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default MePage
