import { useEffect, useState } from 'react'
import { api, type ExtractResponse, type MatchResponse, type StartupProfile } from './api'
import Intake from './components/Intake'
import Confirm from './components/Confirm'
import OpportunityMap from './components/OpportunityMap'

type View =
  | { name: 'intake' }
  | { name: 'confirm'; extract: ExtractResponse }
  | { name: 'loading' }
  | { name: 'map'; data: MatchResponse }
  | { name: 'error'; message: string }

export default function App() {
  const [view, setView] = useState<View>({ name: 'intake' })

  const runMatch = async (profile: StartupProfile) => {
    setView({ name: 'loading' })
    try {
      const data = await api.match(profile)
      setView({ name: 'map', data })
    } catch (e) {
      setView({ name: 'error', message: String(e) })
    }
  }

  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-[760px] items-center justify-between px-6 pt-6 print:hidden">
        <button
          onClick={() => setView({ name: 'intake' })}
          className="flex items-center gap-2 text-[14px] font-medium tracking-tight text-ink"
        >
          <span className="inline-block h-2 w-2 bg-accent" />
          GovMatch
        </button>
        <span className="num text-[11px] text-ash">local · no keys · live federal data</span>
      </header>

      {view.name === 'intake' && (
        <Intake onExtracted={(extract) => setView({ name: 'confirm', extract })} />
      )}
      {view.name === 'confirm' && (
        <Confirm extract={view.extract} onRun={runMatch} onBack={() => setView({ name: 'intake' })} />
      )}
      {view.name === 'loading' && <Loading />}
      {view.name === 'map' && <OpportunityMap data={view.data} onBack={() => setView({ name: 'intake' })} />}
      {view.name === 'error' && (
        <div className="mx-auto max-w-[760px] px-6 pt-24">
          <div className="eyebrow">Something went wrong</div>
          <p className="mt-2 text-[15px] text-ink-2">{view.message}</p>
          <button className="mt-6 text-[14px] text-accent underline underline-offset-4" onClick={() => setView({ name: 'intake' })}>
            Start over
          </button>
        </div>
      )}
    </div>
  )
}

const STEPS = [
  'Translating your company into government language',
  'Searching live federal grant opportunities',
  'Reading each program against your profile',
  'Pulling award history from USAspending and SBIR',
  'Ranking and explaining your matches',
]

function Loading() {
  const [step, setStep] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 1700)
    return () => clearInterval(id)
  }, [])
  return (
    <div className="mx-auto max-w-[760px] px-6 pt-32">
      <div className="eyebrow">Building your map</div>
      <div className="mt-6 border-t border-hairline">
        {STEPS.map((s, i) => (
          <div key={s} className="grid grid-cols-[44px_1fr] gap-4 border-b border-hairline py-3">
            <span className={`num text-[13px] ${i <= step ? 'text-ink' : 'text-ash'}`}>
              {i < step ? '✓' : i === step ? '·' : ' '}
            </span>
            <span className={`text-[15px] ${i <= step ? 'text-ink' : 'text-ash'}`}>{s}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
