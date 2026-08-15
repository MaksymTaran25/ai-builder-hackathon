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

  const step = view.name === 'intake' ? 1 : view.name === 'confirm' ? 2 : 3

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 border-b border-hairline bg-paper/90 backdrop-blur print:hidden">
        <div className="mx-auto flex h-14 max-w-[1080px] items-center justify-between px-6">
          <button onClick={() => setView({ name: 'intake' })} className="text-ink" aria-label="GovMatch home">
            <Logo />
          </button>
          <nav className="hidden items-center gap-6 text-[13px] sm:flex" aria-label="Progress">
            <Step n={1} label="Describe" active={step === 1} done={step > 1} />
            <Step n={2} label="Confirm" active={step === 2} done={step > 2} />
            <Step n={3} label="Your map" active={step === 3} done={false} />
          </nav>
          <span className="hidden text-[12px] text-ash md:block">Live federal data · runs locally</span>
        </div>
      </header>

      {view.name === 'intake' && <Intake onExtracted={(extract) => setView({ name: 'confirm', extract })} />}
      {view.name === 'confirm' && (
        <Confirm extract={view.extract} onRun={runMatch} onBack={() => setView({ name: 'intake' })} />
      )}
      {view.name === 'loading' && <Loading />}
      {view.name === 'map' && <OpportunityMap data={view.data} onBack={() => setView({ name: 'intake' })} />}
      {view.name === 'error' && (
        <div className="mx-auto max-w-[640px] px-6 pt-28">
          <div className="card p-8">
            <h2 className="text-[20px] font-medium text-ink">Something went wrong</h2>
            <p className="mt-2 text-[14px] text-graphite">{view.message}</p>
            <button className="btn btn-primary mt-6" onClick={() => setView({ name: 'intake' })}>
              Start over
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function Step({ n, label, active, done }: { n: number; label: string; active: boolean; done: boolean }) {
  return (
    <span className={`flex items-center gap-2 ${active ? 'text-ink' : done ? 'text-graphite' : 'text-ash'}`}>
      <span
        className={`num flex h-5 w-5 items-center justify-center rounded-full text-[11px] ${
          active ? 'bg-ink text-paper' : done ? 'bg-mist text-graphite' : 'border border-hairline text-ash'
        }`}
      >
        {done ? '✓' : n}
      </span>
      {label}
    </span>
  )
}

// step label + roughly how long it takes; the LLM read is the long one
const STEPS: [string, number][] = [
  ['Searching live federal opportunities', 1200],
  ['Reading every program against your company — a local model, no API calls', 10000],
  ['Pulling award history', 800],
  ['Ranking your matches', 800],
]

function Loading() {
  const [step, setStep] = useState(0)
  useEffect(() => {
    let i = 0
    let t: ReturnType<typeof setTimeout>
    const next = () => {
      i = Math.min(i + 1, STEPS.length - 1)
      setStep(i)
      if (i < STEPS.length - 1) t = setTimeout(next, STEPS[i][1])
    }
    t = setTimeout(next, STEPS[0][1])
    return () => clearTimeout(t)
  }, [])
  return (
    <div className="mx-auto max-w-[520px] px-6 pt-32">
      <div className="card p-8">
        <div className="text-[12px] uppercase tracking-wider text-ash">Building your map</div>
        <ul className="mt-4 space-y-3">
          {STEPS.map(([s], i) => (
            <li key={s} className={`flex items-center gap-3 text-[15px] ${i <= step ? 'text-ink' : 'text-ash'}`}>
              <span
                className={`flex h-5 w-5 items-center justify-center rounded-full text-[11px] ${
                  i < step ? 'bg-ink text-paper' : i === step ? 'border-2 border-ink' : 'border border-hairline'
                }`}
              >
                {i < step ? '✓' : ''}
              </span>
              {s}
            </li>
          ))}
        </ul>
        <div className="mt-6 h-1 w-full overflow-hidden rounded-full bg-mist">
          <div className="h-1 rounded-full bg-ink transition-all duration-1000" style={{ width: `${((step + 1) / STEPS.length) * 100}%` }} />
        </div>
      </div>
    </div>
  )
}
