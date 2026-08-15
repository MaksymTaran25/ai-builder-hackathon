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

  const rows: [string, string | null | undefined][] = [
    ['Industry', profile.industry],
    ['Location', profile.state],
    ['Employees', profile.employees != null ? String(profile.employees) : null],
    ['Revenue', profile.revenue_usd != null ? fmtUSD(profile.revenue_usd) : null],
    ['Raised', profile.capital_raised_usd != null ? fmtUSD(profile.capital_raised_usd) : null],
    [
      'Seeking',
      profile.capital_need_max_usd != null
        ? `${fmtUSD(profile.capital_need_min_usd)} – ${fmtUSD(profile.capital_need_max_usd)}`
        : null,
    ],
    ['Technology', (profile.technology ?? []).join(', ') || null],
  ]

  return (
    <div className="mx-auto max-w-[760px] px-6 pt-20 pb-24">
      <button onClick={onBack} className="eyebrow mb-8 transition-colors hover:text-ink">
        ← Edit description
      </button>
      <h2 className="text-[32px] font-medium leading-tight text-ink">Here's what we understood.</h2>

      <dl className="mt-8 border-t border-hairline">
        {rows.map(([k, v]) => (
          <div key={k} className="grid grid-cols-[140px_1fr] gap-4 border-b border-hairline py-3">
            <dt className="eyebrow pt-0.5">{k}</dt>
            <dd className={`text-[15px] ${v ? 'text-ink' : 'text-ash'} ${k !== 'Industry' && k !== 'Technology' ? 'num' : ''}`}>
              {v ?? 'not stated'}
            </dd>
          </div>
        ))}
      </dl>

      <p className="mt-6 text-[14px] leading-relaxed text-graphite">{profile.description}</p>

      {extract.followups.length > 0 && (
        <div className="mt-10 border-t border-hairline pt-6">
          <div className="eyebrow">A few quick questions</div>
          <p className="mt-1 text-[14px] text-graphite">
            Optional — answering sharpens the match. Skip anything you're unsure of.
          </p>
          <div className="mt-5 space-y-5">
            {extract.followups.map((q) => (
              <label key={q.field} className="block">
                <span className="text-[15px] text-ink">{q.question}</span>
                <input
                  className="mt-2 w-full border-0 border-b border-hairline bg-transparent px-0 py-2 text-[15px] text-ink outline-none transition-colors focus:border-ink"
                  value={answers[q.field] ?? ''}
                  onChange={(e) => setAnswers({ ...answers, [q.field]: e.target.value })}
                  placeholder="—"
                />
              </label>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={apply}
        className="mt-12 w-full bg-ink py-4 text-[15px] font-medium text-paper transition-opacity hover:opacity-90"
      >
        Build my Government Opportunity Map
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
