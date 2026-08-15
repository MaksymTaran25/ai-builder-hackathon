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

  const rows: [string, string | null][] = [
    ['Industry', profile.industry ?? null],
    ['Location', profile.state ?? null],
    ['Team', profile.employees != null ? `${profile.employees} employees` : null],
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
    <div className="mx-auto max-w-[680px] px-6 pb-24 pt-16">
      <button onClick={onBack} className="btn btn-ghost -ml-3 h-9 px-3 text-[13px]">
        ← Edit description
      </button>
      <h2 className="display mt-6 text-[40px] text-ink">Does this look <em>right</em>?</h2>

      <div className="card mt-8 overflow-hidden">
        <dl>
          {rows.map(([k, v], i) => (
            <div key={k} className={`grid grid-cols-[130px_1fr] gap-4 px-6 py-3.5 ${i > 0 ? 'border-t border-hairline' : ''}`}>
              <dt className="text-[13px] text-graphite">{k}</dt>
              <dd className={`text-[15px] ${v ? 'text-ink' : 'text-ash'} ${k !== 'Industry' && k !== 'Technology' && v ? 'num' : ''}`}>
                {v ?? 'Not stated'}
              </dd>
            </div>
          ))}
        </dl>
      </div>

      {extract.followups.length > 0 && (
        <div className="card mt-6 p-6">
          <div className="text-[12px] uppercase tracking-wider text-ash">A few quick questions</div>
          <p className="mt-1 text-[13px] text-graphite">Optional — each answer sharpens the match.</p>
          <div className="mt-5 space-y-4">
            {extract.followups.map((q) => (
              <label key={q.field} className="block">
                <span className="text-[14px] text-ink">{q.question}</span>
                <input
                  className="field mt-2 h-11 py-0"
                  value={answers[q.field] ?? ''}
                  onChange={(e) => setAnswers({ ...answers, [q.field]: e.target.value })}
                  placeholder="Optional"
                />
              </label>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8 flex items-center justify-between">
        <span className="text-[13px] text-ash">Takes about ten seconds.</span>
        <button onClick={apply} className="btn btn-primary">
          Show my opportunities <span aria-hidden="true">→</span>
        </button>
      </div>
    </div>
  )
}

function parseMoney(s: string): number | null {
  const m = s.replace(/[$,\s]/g, '').toLowerCase().match(/^([\d.]+)([kmb]?)$/)
  if (!m) return null
  const mult = m[2] === 'k' ? 1e3 : m[2] === 'm' ? 1e6 : m[2] === 'b' ? 1e9 : 1
  return Math.round(parseFloat(m[1]) * mult)
}
