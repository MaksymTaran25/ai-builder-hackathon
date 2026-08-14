import { useState } from 'react'
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
      {view.name === 'intake' && (
        <Intake onExtracted={(extract) => setView({ name: 'confirm', extract })} />
      )}
      {view.name === 'confirm' && (
        <Confirm
          extract={view.extract}
          onRun={runMatch}
          onBack={() => setView({ name: 'intake' })}
        />
      )}
      {view.name === 'loading' && <Loading />}
      {view.name === 'map' && (
        <OpportunityMap data={view.data} onBack={() => setView({ name: 'intake' })} />
      )}
      {view.name === 'error' && (
        <div className="mx-auto max-w-xl px-6 pt-24 text-center">
          <p className="text-red-600">{view.message}</p>
          <button
            className="mt-4 text-sm text-blue-600 underline"
            onClick={() => setView({ name: 'intake' })}
          >
            Start over
          </button>
        </div>
      )}
    </div>
  )
}

const STEPS = [
  'Translating your company into government language…',
  'Searching live federal grant opportunities…',
  'Checking SBIR/STTR award history…',
  'Ranking and explaining your matches…',
]

function Loading() {
  return (
    <div className="mx-auto max-w-md px-6 pt-32 text-center">
      <div className="mx-auto mb-6 h-10 w-10 animate-spin rounded-full border-[3px] border-slate-200 border-t-blue-600" />
      <div className="space-y-2 text-sm text-slate-500">
        {STEPS.map((s, i) => (
          <p key={i} className="animate-pulse" style={{ animationDelay: `${i * 400}ms` }}>
            {s}
          </p>
        ))}
      </div>
    </div>
  )
}
