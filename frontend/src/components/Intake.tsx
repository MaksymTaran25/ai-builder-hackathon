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
      setError('Could not reach the matching service. Is the backend running on :8000?')
      console.error(e)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-[760px] px-6 pt-24 pb-24">
      <div className="eyebrow mb-6">Government Opportunity Finder</div>
      <h1 className="text-[40px] font-medium leading-[1.1] text-ink">
        Tell us about your company.
      </h1>
      <p className="mt-4 max-w-[560px] text-[17px] leading-relaxed text-graphite">
        Describe it the way you would to a friend. We translate that into how the
        federal government talks about money, and map the programs already out there
        for you — with the award history behind each one.
      </p>

      <div className="mt-10 border-t border-hairline pt-6">
        <label className="eyebrow block" htmlFor="company">
          Your company
        </label>
        <textarea
          id="company"
          className="mt-3 h-44 w-full resize-none border-0 bg-transparent p-0 text-[17px] leading-relaxed text-ink outline-none"
          placeholder="We're a 15-person Utah company developing AI-powered software that helps hospitals reduce administrative work for nurses. We've raised $2.5M, have $1M in ARR, and are looking for $500K–$2M of non-dilutive capital…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit()
          }}
        />
        <div className="mt-2 flex items-center justify-between border-t border-hairline pt-4">
          <span className="num text-[12px] text-ash">⌘ ↵ to run</span>
          <button
            onClick={submit}
            disabled={busy || !text.trim()}
            className="bg-accent px-5 py-2.5 text-[14px] font-medium text-accent-ink transition-opacity hover:opacity-90 disabled:opacity-30"
          >
            {busy ? 'Reading…' : 'Find my opportunities'}
          </button>
        </div>
      </div>

      {error && <p className="mt-4 text-[14px] text-notfit">{error}</p>}

      <div className="mt-14">
        <div className="eyebrow mb-3">Sample companies</div>
        <div className="flex flex-wrap gap-x-5 gap-y-2">
          {TEST_CASES.map((tc) => (
            <button
              key={tc.label}
              onClick={() => setText(tc.text)}
              className="text-[14px] text-graphite underline decoration-hairline underline-offset-4 transition-colors hover:text-ink hover:decoration-ink"
            >
              {tc.label.replace(/^[^\p{L}\p{N}]+/u, '')}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-24 grid gap-8 border-t border-hairline pt-8 sm:grid-cols-3">
        <Fact n="900+" label="live federal opportunities, refreshed nightly" />
        <Fact n="39,847" label="SBIR/STTR awards since 2018 to compare against" />
        <Fact n="0" label="API keys — every judgment runs on this machine" />
      </div>
    </div>
  )
}

function Fact({ n, label }: { n: string; label: string }) {
  return (
    <div>
      <div className="num text-[28px] font-medium leading-none text-ink">{n}</div>
      <div className="mt-2 text-[13px] leading-snug text-graphite">{label}</div>
    </div>
  )
}
