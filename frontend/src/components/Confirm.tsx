import { useState } from 'react'
import { fmtUSD, type ExtractResponse, type StartupProfile } from '../api'

interface Props {
  extract: ExtractResponse
  onRun: (profile: StartupProfile) => void
  onBack: () => void
}

export default function Confirm({ extract, onRun, onBack }: Props) {
  const [profile] = useState<StartupProfile>(extract.profile)
  const [answers, setAnswers] = useState<Record<string, string>>({})

  const apply = () => {
    const p = { ...profile }
    for (const [field, raw] of Object.entries(answers)) {
      if (!raw.trim()) continue
      const v = raw.trim()
      if (field === 'employees') p.employees = parseInt(v) || null
      else if (field === 'capital_need_max_usd') {
        const n = parseMoney(v)
        if (n) p.capital_need_max_usd = n
      } else if (field === 'state') p.state = v.length === 2 ? v.toUpperCase() : v
      else (p as Record<string, unknown>)[field] = v
    }
    onRun(p)
  }

  const facts = [
    profile.industry,
    profile.state,
    profile.employees != null ? `${profile.employees} employees` : null,
    profile.revenue_usd != null ? `${fmtUSD(profile.revenue_usd)} revenue` : null,
    profile.capital_raised_usd != null ? `${fmtUSD(profile.capital_raised_usd)} raised` : null,
    profile.capital_need_max_usd != null
      ? `seeking ${fmtUSD(profile.capital_need_min_usd)}–${fmtUSD(profile.capital_need_max_usd)}`
      : null,
  ].filter(Boolean) as string[]

  return (
    <div className="mx-auto max-w-[640px] px-6 pt-28 pb-24">
      <button onClick={onBack} className="text-[13px] text-ash transition-colors hover:text-ink">
        ← Edit
      </button>
      <h2 className="display mt-6 text-[44px] text-ink">Does this look <em>right</em>?</h2>

      <p className="mt-6 text-[17px] leading-relaxed text-ink">{facts.join(' · ')}</p>

      {extract.followups.length > 0 && (
        <div className="mt-10 space-y-6">
          {extract.followups.map((q) => (
            <label key={q.field} className="block">
              <span className="text-[15px] text-graphite">{q.question}</span>
              <input
                className="mt-1 w-full border-b border-hairline bg-transparent py-2 text-[16px] text-ink outline-none transition-colors focus:border-ink"
                value={answers[q.field] ?? ''}
                onChange={(e) => setAnswers({ ...answers, [q.field]: e.target.value })}
                placeholder="Optional"
              />
            </label>
          ))}
        </div>
      )}

      <button
        onClick={apply}
        className="mt-12 bg-ink px-6 py-3 text-[15px] font-medium text-paper transition-opacity hover:opacity-85"
      >
        Show my opportunities
      </button>
    </div>
  )
}

function parseMoney(s: string): number | null {
  const m = s.replace(/[$,\s]/g, '').toLowerCase().match(/^([\d.]+)([kmb]?)$/)
  if (!m) return null
  const mult = m[2] === 'k' ? 1e3 : m[2] === 'm' ? 1e6 : m[2] === 'b' ? 1e9 : 1
  return Math.round(parseFloat(m[1]) * mult)
}
