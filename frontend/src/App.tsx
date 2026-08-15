import { useEffect, useState } from 'react'
import { api, type ExtractResponse, type MatchResponse, type StartupProfile } from './api'
import Intake from './components/Intake'
import Confirm from './components/Confirm'
import OpportunityMap from './components/OpportunityMap'
import Logo from './components/Logo'

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
      <header className="mx-auto flex max-w-[640px] items-center px-6 pt-6 print:hidden">
        <button onClick={() => setView({ name: 'intake' })} className="text-ink" aria-label="GovMatch home">
          <Logo />
        </button>
      </header>

      {view.name === 'intake' && <Intake onExtracted={(extract) => setView({ name: 'confirm', extract })} />}
      {view.name === 'confirm' && (
        <Confirm extract={view.extract} onRun={runMatch} onBack={() => setView({ name: 'intake' })} />
      )}
      {view.name === 'loading' && <Loading />}
      {view.name === 'map' && <OpportunityMap data={view.data} onBack={() => setView({ name: 'intake' })} />}
      {view.name === 'error' && (
        <div className="mx-auto max-w-[640px] px-6 pt-28">
          <p className="text-[15px] text-ink-2">Something went wrong. {view.message}</p>
          <button className="mt-6 text-[14px] text-accent underline underline-offset-4" onClick={() => setView({ name: 'intake' })}>
            Start over
          </button>
        </div>
      )}
    </div>
  )
}

const STEPS = [
  'Searching live federal opportunities',
  'Reading each program against your company',
  'Pulling award history',
  'Ranking your matches',
]

function Loading() {
  const [step, setStep] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 2000)
    return () => clearInterval(id)
  }, [])
  return (
    <div className="mx-auto max-w-[640px] px-6 pt-36">
      <p className="text-[17px] text-ink">{STEPS[step]}…</p>
      <div className="mt-4 h-px w-full bg-hairline">
        <div className="h-px bg-ink transition-all duration-1000" style={{ width: `${((step + 1) / STEPS.length) * 100}%` }} />
      </div>
    </div>
  )
}
