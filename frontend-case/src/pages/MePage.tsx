import React from 'react'
import { Card, Tag, Button } from '../components/ui'

const MePage: React.FC = () => {
  const menuItems = [
    { label: 'PROFILE', title: '完善个人资料', sub: '出生日期 · 时间 · 地点', icon: '◉', badge: null },
    { label: 'CHART', title: '命盘查看', sub: '八字 · 紫微 · 河洛 · 易经', icon: '☯', badge: null },
    { label: 'CLASSICS', title: '五部经典', sub: '滴天髓 · 子平真诠 · 穷通宝鉴', icon: '☰', badge: '5' },
    { label: 'SETTINGS', title: '语言与时区', sub: '显示偏好 · 真太阳时', icon: '⚙', badge: null },
    { label: 'SUBSCRIPTION', title: '免费版', sub: '每日一次免费洞察', icon: '✦', badge: 'FREE' },
  ]

  return (
    <div className="page-container">
      {/* 用户头像区 */}
      <div className="animate-fade-in-up" style={{ textAlign: 'center', marginBottom: '32px', paddingTop: '16px' }}>
        <div style={{
          width: '72px', height: '72px', margin: '0 auto 16px',
          borderRadius: '50%', border: '2px solid var(--border-gold)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '28px', color: 'var(--gold-light)',
          background: 'radial-gradient(circle, var(--gold-soft), transparent)',
          boxShadow: 'var(--shadow-glow-gold)',
        }}>
          ☯
        </div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '22px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
          顺天使用者
        </h1>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '8px' }}>
          <Tag variant="gold" size="sm">AUTHENTICATED</Tag>
          <Tag variant="muted" size="sm">FREE</Tag>
        </div>
      </div>

      <div className="divider-gold" />

      {/* 菜单列表 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '24px' }}>
        {menuItems.map((item, i) => (
          <Card key={i} variant="glass" hover className={`animate-fade-in-up delay-${i + 1}`} style={{ cursor: 'pointer' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={{
                width: '36px', height: '36px', flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
                fontSize: '16px', color: 'var(--text-secondary)',
                background: 'var(--bg-elevated)',
              }}>
                {item.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
                    {item.label}
                  </span>
                  {item.badge && <Tag variant={item.badge === 'FREE' ? 'accent' : 'gold'} size="sm">{item.badge}</Tag>}
                </div>
                <div style={{ fontSize: '14px', color: 'var(--text-primary)', fontWeight: 500, marginTop: '2px' }}>
                  {item.title}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '1px' }}>
                  {item.sub}
                </div>
              </div>
              <span style={{ color: 'var(--text-muted)', fontSize: '18px', flexShrink: 0 }}>›</span>
            </div>
          </Card>
        ))}
      </div>

      <div className="divider-gold" style={{ marginTop: '32px' }} />

      {/* 底部信息 */}
      <div style={{ textAlign: 'center', marginTop: '24px', marginBottom: '32px' }} className="animate-fade-in-up delay-6">
        <div style={{ fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: '4px' }}>
          LIORIN · 顺天
        </div>
        <div style={{ fontSize: '10px', color: 'var(--text-muted)', opacity: 0.6 }}>
          v0.1.0 · 算准 → 辨准 → 解准
        </div>
      </div>
    </div>
  )
}

export default MePage
