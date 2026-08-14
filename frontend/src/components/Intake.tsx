import { useState } from 'react'
import { api, type ExtractResponse } from '../api'
import { TEST_CASES } from '../testCases'

interface Props {
  onExtracted: (r: ExtractResponse, text: string) => void
}

export default function Intake({ onExtracted }: Props) {
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const submit = async () => {
    if (!text.trim() || busy) return
    setBusy(true)
    setError('')
    try {
      const r = await api.extract(text)
      onExtracted(r, text)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-6 pt-20 pb-16">
      <div className="text-center">
        <div className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
          Government Opportunity Finder
        </div>
        <h1 className="text-4xl font-bold tracking-tight text-slate-900">
          Tell us about your company.
        </h1>
        <p className="mx-auto mt-3 max-w-xl text-slate-500">
          Describe your startup the way you'd tell a friend — we translate it into
          government language and map the federal funding already out there for you.
        </p>
      </div>

      <div className="mt-10 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm">
        <textarea
          className="h-40 w-full resize-none rounded-xl p-4 text-[15px] leading-relaxed outline-none placeholder:text-slate-400"
          placeholder="e.g. We're a 15-person Utah company developing AI-powered software that helps hospitals reduce administrative work for nurses. We've raised $2.5M, have $1M ARR, and are looking for $500K–$2M of non-dilutive capital…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit()
          }}
        />
        <div className="flex items-center justify-between px-3 pb-2">
          <span className="text-xs text-slate-400">⌘↵ to run</span>
          <button
            onClick={submit}
            disabled={busy || !text.trim()}
            className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-40"
          >
            {busy ? 'Reading…' : 'Find my opportunities →'}
          </button>
        </div>
      </div>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      <div className="mt-8">
        <div className="mb-2 text-center text-xs font-medium uppercase tracking-wider text-slate-400">
          Try a sample company
        </div>
        <div className="flex flex-wrap justify-center gap-2">
          {TEST_CASES.map((tc) => (
            <button
              key={tc.label}
              onClick={() => setText(tc.text)}
              className="rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-sm text-slate-600 shadow-sm transition hover:border-blue-300 hover:text-blue-700"
            >
              {tc.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
