import { useState, useCallback } from 'react'
import AppShell from './components/shell/AppShell'
import PersonalToday from './pages/today/PersonalToday'
import PublicToday from './pages/today/PublicToday'
import GuidePage from './pages/GuidePage'
import InsightsPage from './pages/InsightsPage'
import MePage from './pages/MePage'
import {
  MOCK_PUBLIC_TODAY,
  MOCK_PERSONAL_DAY3,
  MOCK_PROFILE_INSUFFICIENT,
  MOCK_PREMIUM,
  MOCK_CALCULATION_ERROR,
} from './mock/data'
import type { PageName } from './components/navigation/BottomNav'
import type { Entitlement, ProfileStatus, TodayData, PublicTodayData } from './mock/data'

type SimulatedState =
  | 'public'
  | 'authenticated-no-profile'
  | 'authenticated-insufficient'
  | 'authenticated-valid'
  | 'premium'
  | 'calculation-error'

function getTodayData(state: SimulatedState): { data: TodayData | PublicTodayData; isPublic: boolean } {
  switch (state) {
    case 'public':
      return { data: MOCK_PUBLIC_TODAY, isPublic: true }
    case 'authenticated-no-profile':
      return {
        data: { ...MOCK_PROFILE_INSUFFICIENT, user_state: { entitlement: 'AUTHENTICATED', profile_status: 'NONE' as ProfileStatus } },
        isPublic: false,
      }
    case 'authenticated-insufficient':
      return { data: MOCK_PROFILE_INSUFFICIENT, isPublic: false }
    case 'authenticated-valid':
      return { data: MOCK_PERSONAL_DAY3, isPublic: false }
    case 'premium':
      return { data: MOCK_PREMIUM, isPublic: false }
    case 'calculation-error':
      return { data: MOCK_CALCULATION_ERROR, isPublic: false }
    default:
      return { data: MOCK_PUBLIC_TODAY, isPublic: true }
  }
}

function getEntitlement(state: SimulatedState): Entitlement {
  switch (state) {
    case 'public': return 'PUBLIC'
    case 'premium': return 'PREMIUM'
    default: return 'AUTHENTICATED'
  }
}

function App() {
  const [currentPage, setCurrentPage] = useState<PageName>('today')
  const [simState, setSimState] = useState<SimulatedState>('authenticated-valid')

  const entitlement = getEntitlement(simState)
  const { data, isPublic } = getTodayData(simState)

  const handleLangChange = useCallback(() => {}, [])
  const handleTimezoneChange = useCallback(() => {}, [])

  const entitlementLabel = entitlement === 'PREMIUM' ? 'Private' : 'More'

  const renderPage = () => {
    switch (currentPage) {
      case 'today':
        if (isPublic) {
          return <PublicToday data={data as PublicTodayData} />
        }
        return (
          <PersonalToday
            data={data as TodayData}
            isPremium={entitlement === 'PREMIUM'}
          />
        )
      case 'guide':
        return <GuidePage />
      case 'insights':
        return <InsightsPage />
      case 'me':
        return <MePage />
      default:
        return null
    }
  }

  return (
    <AppShell
      activePage={currentPage}
      onPageChange={setCurrentPage}
      onLangChange={handleLangChange}
      onTimezoneChange={handleTimezoneChange}
      entitlementLabel={entitlementLabel}
    >
      {renderPage()}

      {/* Dev state switcher — remove in production */}
      <div
        style={{
          position: 'fixed',
          bottom: '68px',
          right: '16px',
          zIndex: 50,
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
        }}
        aria-label="Dev state switcher"
      >
        {(
          [
            ['public', 'Public'],
            ['authenticated-no-profile', 'No Profile'],
            ['authenticated-insufficient', 'Incomplete'],
            ['authenticated-valid', 'Valid'],
            ['premium', 'Premium'],
            ['calculation-error', 'Error'],
          ] as [SimulatedState, string][]
        ).map(([state, label]) => (
          <button
            key={state}
            onClick={() => setSimState(state)}
            style={{
              background: simState === state ? 'var(--accent)' : 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              color: simState === state ? '#fff' : 'var(--text-muted)',
              fontFamily: 'var(--font-mono)',
              fontSize: '9px',
              letterSpacing: '0.05em',
              cursor: 'pointer',
              padding: '4px 8px',
              transition: 'all 150ms ease',
            }}
          >
            {label}
          </button>
        ))}
      </div>
    </AppShell>
  )
}

export default App
