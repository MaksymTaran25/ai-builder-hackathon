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
      setError("Couldn't reach the matching service.")
      console.error(e)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-[640px] px-6 pt-28 pb-24">
      <h1 className="text-[34px] font-medium leading-tight text-ink">Tell us about your company.</h1>
      <p className="mt-3 text-[16px] leading-relaxed text-graphite">
        We'll map the federal funding you may qualify for and show who else received it.
      </p>

      <textarea
        aria-label="Describe your company"
        className="mt-10 h-40 w-full resize-none border-b border-hairline bg-transparent pb-4 text-[17px] leading-relaxed text-ink outline-none transition-colors focus:border-ink"
        placeholder="We're a 15-person Utah company building AI software for hospitals. $1M ARR, raised $2.5M, looking for $500K–$2M…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit()
        }}
      />

      <div className="mt-6 flex items-center justify-between">
        <div className="flex flex-wrap gap-x-4 gap-y-1">
          {TEST_CASES.map((tc) => (
            <button
              key={tc.label}
              onClick={() => setText(tc.text)}
              className="text-[13px] text-ash transition-colors hover:text-ink"
            >
              {tc.label.replace(/^[^\p{L}\p{N}]+/u, '')}
            </button>
          ))}
        </div>
        <button
          onClick={submit}
          disabled={busy || !text.trim()}
          className="shrink-0 bg-ink px-5 py-2.5 text-[14px] font-medium text-paper transition-opacity hover:opacity-85 disabled:opacity-25"
        >
          {busy ? 'Reading…' : 'Continue'}
        </button>
      </div>

      {error && <p className="mt-4 text-[14px] text-notfit">{error}</p>}
    </div>
  )
}
