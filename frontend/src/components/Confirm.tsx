import { useState } from 'react'
import { fmtUSD, type ExtractResponse, type StartupProfile } from '../api'

interface Props {
  extract: ExtractResponse
  onRun: (profile: StartupProfile) => void
  onBack: () => void
}

const chip = 'rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600'

export default function Confirm({ extract, onRun, onBack }: Props) {
  const [profile, setProfile] = useState<StartupProfile>(extract.profile)
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
    setProfile(p)
    onRun(p)
  }

  return (
    <div className="mx-auto max-w-3xl px-6 pt-16 pb-16">
      <button onClick={onBack} className="mb-6 text-sm text-slate-400 hover:text-slate-600">
        ← Edit description
      </button>
      <h2 className="text-2xl font-bold text-slate-900">Here's what we understood</h2>

      <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap gap-2">
          {profile.industry && <span className={chip}>{profile.industry}</span>}
          {profile.state && <span className={chip}>📍 {profile.state}</span>}
          {profile.employees != null && <span className={chip}>{profile.employees} employees</span>}
          {profile.revenue_usd != null && <span className={chip}>{fmtUSD(profile.revenue_usd)} revenue</span>}
          {profile.capital_raised_usd != null && <span className={chip}>{fmtUSD(profile.capital_raised_usd)} raised</span>}
          {profile.capital_need_max_usd != null && (
            <span className={chip}>
              seeking {fmtUSD(profile.capital_need_min_usd)}–{fmtUSD(profile.capital_need_max_usd)}
            </span>
          )}
          {(profile.technology ?? []).map((t) => (
            <span key={t} className={chip}>{t}</span>
          ))}
        </div>
        <p className="mt-4 text-sm leading-relaxed text-slate-500">{profile.description}</p>
      </div>

      {extract.followups.length > 0 && (
        <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-6">
          <div className="mb-3 text-sm font-semibold text-amber-900">
            A few quick questions to sharpen your matches
          </div>
          <div className="space-y-3">
            {extract.followups.map((q) => (
              <label key={q.field} className="block">
                <span className="text-sm text-amber-800">{q.question}</span>
                <input
                  className="mt-1 w-full rounded-lg border border-amber-200 bg-white px-3 py-2 text-sm outline-none focus:border-amber-400"
                  value={answers[q.field] ?? ''}
                  onChange={(e) => setAnswers({ ...answers, [q.field]: e.target.value })}
                  placeholder="Optional — skip if unsure"
                />
              </label>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={apply}
        className="mt-8 w-full rounded-xl bg-blue-600 py-3.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
      >
        Build my Government Opportunity Map →
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
