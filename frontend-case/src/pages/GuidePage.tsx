import React from 'react'
import { Card, Tag } from '../components/ui'

const GuidePage: React.FC = () => {
  const sections = [
    { label: 'TIME', title: '东方时间观', text: '基于中国传统时间体系，结合现代计算引擎，提供准确的时间洞察。', icon: '◷' },
    { label: 'DATA', title: '计算而非随机', text: '所有结果基于确定性计算引擎，包括八字、紫微、河洛、易经等体系。', icon: '⚹' },
    { label: 'SYSTEM', title: '五部经典辨证', text: '滴天髓、子平真诠、穷通宝鉴、三命通会、渊海子平，各自独立辨证，互补不投票。', icon: '☰' },
    { label: 'ACTION', title: '可执行洞察', text: '从状态到机会、风险、建议，最终落到今日可执行的行动。', icon: '→' },
  ]

  return (
    <div className="page-container">
      <div className="page-header animate-fade-in-up">
        <div className="page-subtitle">Guide · 指引</div>
        <h1 className="page-title">LIORIN 如何运作</h1>
      </div>

      <div className="divider-gold" />

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '24px' }}>
        {sections.map((s, i) => (
          <Card key={i} variant="glass" hover className={`animate-fade-in-up delay-${i + 1}`}>
            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
              <div style={{
                width: '40px', height: '40px', flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                border: '1px solid var(--border-gold)', borderRadius: 'var(--radius-md)',
                fontSize: '18px', color: 'var(--gold-light)',
                background: 'var(--gold-soft)',
              }}>
                {s.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <Tag variant="gold" size="sm">{s.label}</Tag>
                </div>
                <h2 style={{
                  fontFamily: 'var(--font-display)', fontSize: '17px', fontWeight: 600,
                  color: 'var(--text-primary)', marginBottom: '6px', letterSpacing: '0.02em',
                }}>
                  {s.title}
                </h2>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                  {s.text}
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="divider-gold" style={{ marginTop: '32px' }} />

      <Card variant="gold" className="animate-fade-in-up delay-5" style={{ marginTop: '24px', textAlign: 'center' }}>
        <div style={{ fontSize: '11px', color: 'var(--gold)', letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: '8px' }}>
          Core Principle
        </div>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: '18px', color: 'var(--gold-light)', lineHeight: 1.6 }}>
          算准 → 辨准 → 解准
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px' }}>
          FROZEN ≠ PROVEN CORRECT
        </div>
      </Card>
    </div>
  )
}

export default GuidePage
