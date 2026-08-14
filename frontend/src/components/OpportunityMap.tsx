import { fmtUSD, type MatchResponse, type Opportunity, type FitTier } from '../api'

const TIER_META: Record<FitTier, { label: string; cls: string; dot: string }> = {
  likely_fit: { label: 'Likely Fit', cls: 'bg-emerald-50 text-emerald-700 ring-emerald-200', dot: '🟢' },
  potential_fit: { label: 'Potential Fit — Verify', cls: 'bg-amber-50 text-amber-700 ring-amber-200', dot: '🟡' },
  adjacent: { label: 'Adjacent', cls: 'bg-orange-50 text-orange-700 ring-orange-200', dot: '🟠' },
  not_a_fit: { label: 'Probably Not a Fit', cls: 'bg-red-50 text-red-600 ring-red-200', dot: '🔴' },
}

export default function OpportunityMap({ data, onBack }: { data: MatchResponse; onBack: () => void }) {
  const s = data.summary
  return (
    <div className="mx-auto max-w-4xl px-6 pt-12 pb-24">
      <button onClick={onBack} className="mb-6 text-sm text-slate-400 hover:text-slate-600">
        ← Start over
      </button>

      <div className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
        Your Government Opportunity Map
      </div>
      <h2 className="text-3xl font-bold tracking-tight text-slate-900">
        {data.opportunities.length} opportunities found
      </h2>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat value={String(s.high_potential)} label="High-potential matches" />
        <Stat value={s.total_potential_value_usd ? `${fmtUSD(s.total_potential_value_usd)}+` : '—'} label="Potential funding" />
        <Stat value={String(s.agencies)} label="Relevant agencies" />
        <Stat value={String(s.closing_within_90_days)} label="Closing within 90 days" />
      </div>

      {s.overall_note && (
        <div className="mt-6 rounded-xl border border-slate-300 bg-white p-4 text-sm leading-relaxed text-slate-700 shadow-sm">
          <span className="mr-1.5">⚖️</span>
          <span className="font-semibold">Honest read:</span> {s.overall_note}
        </div>
      )}

      <div className="mt-8 space-y-5">
        {data.opportunities.map((o, i) => (
          <OppCard key={o.source_id} o={o} rank={i + 1} />
        ))}
      </div>
    </div>
  )
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="text-2xl font-bold text-slate-900">{value}</div>
      <div className="mt-0.5 text-xs text-slate-500">{label}</div>
    </div>
  )
}

function OppCard({ o, rank }: { o: Opportunity; rank: number }) {
  const tier = TIER_META[o.fit_tier]
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-start justify-between gap-4 border-b border-slate-100 p-5">
        <div className="min-w-0">
          <div className="mb-1.5 flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-slate-400">#{rank}</span>
            <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${tier.cls}`}>
              {tier.dot} {tier.label}
            </span>
            <span className="text-xs text-slate-400">{Math.round(o.score)}% match</span>
            {o.status && <span className="text-xs uppercase tracking-wide text-slate-400">{o.status}</span>}
          </div>
          <h3 className="text-[15px] font-semibold leading-snug text-slate-900">
            {o.url ? (
              <a href={o.url} target="_blank" rel="noreferrer" className="hover:text-blue-700 hover:underline">
                {o.title}
              </a>
            ) : (
              o.title
            )}
          </h3>
          <div className="mt-1 text-sm text-slate-500">
            {o.agency}
            {o.program && <span className="text-slate-400"> · {o.program}</span>}
          </div>
        </div>
        <div className="shrink-0 text-right text-sm">
          {(o.award_floor_usd || o.award_ceiling_usd) && (
            <div className="font-semibold text-slate-900">
              {fmtUSD(o.award_floor_usd)}–{fmtUSD(o.award_ceiling_usd)}
            </div>
          )}
          {o.close_date && <div className="mt-0.5 text-xs text-slate-400">Closes {o.close_date}</div>}
        </div>
      </div>

      {o.explanation && (
        <div className="grid gap-4 p-5 sm:grid-cols-2">
          <Section icon="✅" title="Why you may fit" text={o.explanation.why_fit} />
          <Section icon="⚠️" title="Potential concerns" text={o.explanation.concerns} />
          <Section icon="🔍" title="What to verify" text={o.explanation.verify} />
          <Section icon="👉" title="Next steps" text={o.explanation.next_steps} />
        </div>
      )}

      {o.history && o.history.similar_companies > 0 && (
        <div className="border-t border-slate-100 bg-slate-50/60 p-5">
          <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
            Who else has received this money?
          </div>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MiniStat value={String(o.history.similar_companies)} label="similar recipients" />
            <MiniStat value={fmtUSD(o.history.total_awarded_usd)} label="total awarded" />
            <MiniStat value={fmtUSD(o.history.median_award_usd)} label="median award" />
            <MiniStat value={String(o.history.in_state_recipients)} label="in your state" />
          </div>
          {o.history.sample_recipients.length > 0 && (
            <div className="mt-3 space-y-1">
              {o.history.sample_recipients.slice(0, 3).map((r, i) => (
                <div key={i} className="truncate text-xs text-slate-500">
                  → {r.name} · {r.agency} · {fmtUSD(r.amount)} · {r.year}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function Section({ icon, title, text }: { icon: string; title: string; text: string }) {
  if (!text) return null
  return (
    <div>
      <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-slate-400">
        {icon} {title}
      </div>
      <p className="text-sm leading-relaxed text-slate-600">{text}</p>
    </div>
  )
}

function MiniStat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="text-lg font-bold text-slate-900">{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  )
}
