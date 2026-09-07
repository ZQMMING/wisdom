import React from 'react'
import { Card, Tag, Button } from '../components/ui'

const InsightsPage: React.FC = () => {
  const trends = [
    { label: 'ENERGY', title: '收敛 · 整理 · 准备', desc: '未来数日能量内收，适合整理与准备，不宜大规模行动。', tag: '收敛', tagVariant: 'warning' as const },
    { label: 'ELEMENT', title: '金旺水相', desc: '当前月令金气旺盛，水得生助，木火处于休囚状态。', tag: '金', tagVariant: 'muted' as const },
    { label: 'ACTION', title: '宜静不宜动', desc: '适合复盘、学习、规划，不适合启动新项目或重大决策。', tag: '宜静', tagVariant: 'success' as const },
  ]

  return (
    <div className="page-container">
      <div className="page-header animate-fade-in-up">
        <div className="page-subtitle">Insights · 洞察</div>
        <h1 className="page-title">周期与趋势</h1>
      </div>

      {/* 当前月令大卡 */}
      <Card variant="gold" className="animate-fade-in-up delay-1" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <Tag variant="gold" size="sm" style={{ marginBottom: '10px' }}>CURRENT PERIOD</Tag>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '24px', fontWeight: 600, color: 'var(--gold-light)', marginBottom: '4px' }}>
              申月
            </h2>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>农历七月 · 金旺水相</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '32px', color: 'var(--gold)', opacity: 0.6 }}>☰</div>
          </div>
        </div>
        <div className="divider-gold" style={{ margin: '16px 0' }} />
        <div style={{ display: 'flex', gap: '24px' }}>
          <div>
            <div style={{ fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>旺</div>
            <div style={{ fontSize: '16px', fontFamily: 'var(--font-display)', color: 'var(--text-primary)' }}>金</div>
          </div>
          <div>
            <div style={{ fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>相</div>
            <div style={{ fontSize: '16px', fontFamily: 'var(--font-display)', color: 'var(--text-primary)' }}>水</div>
          </div>
          <div>
            <div style={{ fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>休</div>
            <div style={{ fontSize: '16px', fontFamily: 'var(--font-display)', color: 'var(--text-muted)' }}>木</div>
          </div>
          <div>
            <div style={{ fontSize: '9px', color: 'var(--text-muted)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>囚</div>
            <div style={{ fontSize: '16px', fontFamily: 'var(--font-display)', color: 'var(--text-muted)' }}>火</div>
          </div>
        </div>
      </Card>

      {/* 趋势列表 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {trends.map((t, i) => (
          <Card key={i} variant="glass" hover className={`animate-fade-in-up delay-${i + 2}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <Tag variant={t.tagVariant} size="sm" dot>{t.label}</Tag>
                  <Tag variant="accent" size="sm">{t.tag}</Tag>
                </div>
                <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                  {t.title}
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{t.desc}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div style={{ marginTop: '24px', textAlign: 'center' }} className="animate-fade-in-up delay-5">
        <Button variant="ghost" size="md">查看全部周期洞察 →</Button>
      </div>
    </div>
  )
}

export default InsightsPage
