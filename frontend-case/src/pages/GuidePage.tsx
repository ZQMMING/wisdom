import React from 'react'

/**
 * GUIDE page — Section 31-37 of LIORIN spec
 */
const GuidePage: React.FC = () => {
  const sections = [
    {
      label: 'Time',
      title: '东方时间观',
      text: 'LIORIN 基于中国传统时间体系，结合现代计算引擎，为您提供准确的时间洞察。',
    },
    {
      label: 'Data',
      title: '计算而非随机',
      text: '所有结果基于确定性的计算引擎，包括八字、紫微、河洛、易经等体系。',
    },
    {
      label: 'Relationship',
      title: '综合解读',
      text: '多个体系交叉验证，提供一致的综合结论，而非单一视角。',
    },
    {
      label: 'Action',
      title: '可执行洞察',
      text: '从状态到机会、风险、建议，最终落到今日可执行的行动。',
    },
  ]

  return (
    <div style={{ maxWidth: '640px', margin: '0 auto', padding: '48px 24px 64px' }}>
      <div style={{
        fontSize: '9px', letterSpacing: '0.2em', textTransform: 'uppercase',
        color: 'var(--text-muted)', marginBottom: '12px',
      }}>
        Guide
      </div>
      <h1 style={{
        fontFamily: 'var(--font-display)', fontSize: '26px', fontWeight: 400,
        color: 'var(--text-primary)', marginBottom: '32px',
      }}>
        How LIORIN Works
      </h1>

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {sections.map((s, i) => (
          <div
            key={i}
            style={{
              padding: '24px 0',
              borderBottom: i < sections.length - 1 ? '1px solid var(--border)' : 'none',
            }}
          >
            <div style={{
              fontSize: '9px', letterSpacing: '0.2em', textTransform: 'uppercase',
              color: 'var(--text-muted)', marginBottom: '8px',
            }}>
              {s.label}
            </div>
            <h2 style={{
              fontFamily: 'var(--font-display)', fontSize: '18px', fontWeight: 400,
              color: 'var(--text-primary)', marginBottom: '8px',
            }}>
              {s.title}
            </h2>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
              {s.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default GuidePage
