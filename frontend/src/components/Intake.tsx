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
      setError("Couldn't reach the matching service. Make sure the backend is running.")
      console.error(e)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-[1080px] px-6 pb-24 pt-16 lg:pt-24">
      <div className="grid gap-12 lg:grid-cols-[1fr_360px] lg:gap-20">
        {/* left: the ask */}
        <div>
          <h1 className="display text-[44px] text-ink sm:text-[56px]">
            Tell us about <em>your</em> company.
          </h1>
          <p className="mt-5 max-w-[520px] text-[17px] leading-relaxed text-graphite">
            We'll map the federal funding you may qualify for — and show you who else already received it.
          </p>

          <div className="mt-10">
            <textarea
              aria-label="Describe your company"
              className="field h-44 resize-none"
              placeholder="We're a 15-person Utah company building AI software for hospitals. $1M ARR, raised $2.5M, looking for $500K–$2M to fund product development and pilots…"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit()
              }}
            />
            <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap gap-2">
                {TEST_CASES.map((tc) => (
                  <button key={tc.label} onClick={() => setText(tc.text)} className="chip">
                    {tc.label.replace(/^[^\p{L}\p{N}]+/u, '')}
                  </button>
                ))}
              </div>
              <button onClick={submit} disabled={busy || !text.trim()} className="btn btn-primary">
                {busy ? 'Reading…' : 'Continue'}
                {!busy && <span aria-hidden="true">→</span>}
              </button>
            </div>
            {error && <p className="mt-4 text-[14px] text-notfit">{error}</p>}
          </div>
        </div>

        {/* right: what you get */}
        <aside className="lg:pt-3">
          <div className="card p-6">
            <div className="text-[12px] uppercase tracking-wider text-ash">What you'll get</div>
            <ul className="mt-4 space-y-4">
              <Item title="Ranked opportunities" body="Live federal grants and SBIR pathways, each with an honest fit tier — including when the answer is 'probably not'." />
              <Item title="Plain-English reasoning" body="Why you may fit, what could disqualify you, what to verify, and what to do next." />
              <Item title="Who else got the money" body="Real recipients, medians and in-state awards from USAspending and SBIR.gov." />
            </ul>
            <dl className="mt-6 grid grid-cols-2 gap-4 border-t border-hairline pt-4">
              <div>
                <dt className="num text-[18px] leading-none text-ink">900+</dt>
                <dd className="mt-1 text-[12px] text-ash">programs, refreshed nightly</dd>
              </div>
              <div>
                <dt className="num text-[18px] leading-none text-ink">39.8K</dt>
                <dd className="mt-1 text-[12px] text-ash">SBIR awards to compare</dd>
              </div>
            </dl>
          </div>
        </aside>
      </div>
    </div>
  )
}

function Item({ title, body }: { title: string; body: string }) {
  return (
    <li className="grid grid-cols-[14px_1fr] gap-3">
      <span className="mt-[7px] h-1.5 w-1.5 rounded-full bg-accent" aria-hidden="true" />
      <div>
        <div className="text-[14px] font-medium text-ink">{title}</div>
        <div className="mt-0.5 text-[13px] leading-relaxed text-graphite">{body}</div>
      </div>
    </li>
  )
}
