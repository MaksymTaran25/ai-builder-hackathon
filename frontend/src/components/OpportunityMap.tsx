import { daysUntil, fmtUSD, type MatchResponse, type Opportunity, type FitTier } from '../api'

const TIER_META: Record<FitTier, { label: string; cls: string; dot: string }> = {
  likely_fit: { label: 'Likely Fit', cls: 'bg-emerald-50 text-emerald-700 ring-emerald-200', dot: '🟢' },
  potential_fit: { label: 'Potential Fit — Verify', cls: 'bg-amber-50 text-amber-700 ring-amber-200', dot: '🟡' },
  adjacent: { label: 'Adjacent', cls: 'bg-orange-50 text-orange-700 ring-orange-200', dot: '🟠' },
  not_a_fit: { label: 'Probably Not a Fit', cls: 'bg-red-50 text-red-600 ring-red-200', dot: '🔴' },
}

export default function OpportunityMap({ data, onBack }: { data: MatchResponse; onBack: () => void }) {
  const s = data.summary
  const federal = data.opportunities.filter((o) => o.source !== 'utah')
  const utah = data.opportunities.filter((o) => o.source === 'utah')
  return (
    <div className="mx-auto max-w-4xl px-6 pt-12 pb-24">
      <div className="flex items-center justify-between print:hidden">
        <button onClick={onBack} className="text-sm text-slate-400 hover:text-slate-600">
          ← Start over
        </button>
        <button
          onClick={() => window.print()}
          className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-600 shadow-sm hover:border-slate-300"
        >
          🖨️ Export report
        </button>
      </div>

      <div className="mt-4 mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
        Your Government Opportunity Map
      </div>
      <h2 className="text-3xl font-bold tracking-tight text-slate-900">
        {federal.length} federal opportunities{utah.length > 0 ? ` + ${utah.length} Utah programs` : ''}
      </h2>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat value={String(s.high_potential)} label="High-potential matches" />
        <Stat value={s.total_potential_value_usd ? `${fmtUSD(s.total_potential_value_usd)}+` : '—'} label="Potential award value" />
        <Stat value={String(s.agencies)} label="Relevant agencies" />
        <Stat value={String(s.closing_within_90_days)} label="Closing within 90 days" />
      </div>

      {s.overall_note && (
        <div className="mt-6 rounded-xl border-l-4 border-slate-400 bg-white p-4 text-sm leading-relaxed text-slate-700 shadow-sm">
          <span className="font-semibold">⚖️ Honest read:</span> {s.overall_note}
        </div>
      )}

      {data.agency_map.length > 0 && (
        <div className="mt-8">
          <SectionTitle color="text-blue-600">🏛️ Your agency map</SectionTitle>
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {data.agency_map.map((a) => (
              <div key={a.agency} className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-2.5 shadow-sm">
                <div className="min-w-0">
                  <div className="truncate text-sm font-semibold text-slate-800">{a.short || a.agency}</div>
                  <div className="truncate text-xs text-slate-400">{a.agency !== a.short ? a.agency : ''}</div>
                </div>
                <div className="ml-3 shrink-0 text-right text-xs text-slate-500">
                  {a.open_opportunities > 0 && <div>{a.open_opportunities} open now</div>}
                  {a.similar_awards_since_2018 > 0 && <div>{a.similar_awards_since_2018} similar awards</div>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-10 space-y-5">
        {federal.map((o, i) => (
          <OppCard key={o.source_id} o={o} rank={i + 1} />
        ))}
      </div>

      {data.similar_companies.length > 0 && (
        <div className="mt-12">
          <SectionTitle color="text-emerald-600">🧭 Companies like you that got funded</SectionTitle>
          <p className="mt-1 text-sm text-slate-500">
            SBIR/STTR recipients since 2018 working on similar technology — proof this path works.
          </p>
          <div className="mt-3 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            {data.similar_companies.map((c, i) => (
              <div
                key={i}
                className={`flex items-center justify-between gap-3 px-4 py-3 ${i > 0 ? 'border-t border-slate-100' : ''}`}
              >
                <div className="min-w-0">
                  <div className="truncate text-sm font-semibold text-slate-800">
                    {c.name}
                    {c.state && (
                      <span className={`ml-2 rounded px-1.5 py-0.5 text-[10px] font-bold ${c.state === 'UT' ? 'bg-orange-100 text-orange-700' : 'bg-slate-100 text-slate-500'}`}>
                        {c.state}
                      </span>
                    )}
                  </div>
                  <div className="truncate text-xs text-slate-400">{c.example_title}</div>
                </div>
                <div className="shrink-0 text-right">
                  <div className="text-sm font-bold text-slate-900">{fmtUSD(c.total_usd)}</div>
                  <div className="text-xs text-slate-400">
                    {c.awards} award{c.awards > 1 ? 's' : ''} · {c.agency} · {c.latest_year}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {utah.length > 0 && (
        <div className="mt-12">
          <SectionTitle color="text-orange-600">🏔️ The Utah advantage</SectionTitle>
          <p className="mt-1 text-sm text-slate-500">
            State programs your company can tap alongside (or instead of) federal funding.
          </p>
          <div className="mt-4 space-y-5">
            {utah.map((o, i) => (
              <OppCard key={o.source_id} o={o} rank={federal.length + i + 1} />
            ))}
          </div>
        </div>
      )}

      <p className="mt-12 text-center text-xs text-slate-400">
        Assessments are AI-generated guidance, not eligibility determinations — always verify with
        the official listing and program officer.
      </p>
    </div>
  )
}

function SectionTitle({ children, color }: { children: React.ReactNode; color: string }) {
  return <div className={`text-xs font-semibold uppercase tracking-[0.2em] ${color}`}>{children}</div>
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="text-2xl font-bold text-slate-900">{value}</div>
      <div className="mt-0.5 text-xs text-slate-500">{label}</div>
    </div>
  )
}

function EligibilityBadge({ o }: { o: Opportunity }) {
  if (o.eligibility_flag === 'likely_ineligible')
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-red-50 px-2.5 py-0.5 text-xs font-semibold text-red-600 ring-1 ring-red-200">
        ⛔ For-profits likely ineligible
      </span>
    )
  if (o.eligibility_flag === 'verify')
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-slate-50 px-2.5 py-0.5 text-xs font-medium text-slate-500 ring-1 ring-slate-200">
        Verify eligibility
      </span>
    )
  if (o.eligibility_flag === 'ok' && o.source === 'grants_gov')
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-600 ring-1 ring-blue-200">
        ✓ Small businesses eligible
      </span>
    )
  return null
}

function UrgencyChip({ o }: { o: Opportunity }) {
  const days = daysUntil(o.close_date)
  if (days == null || days < 0) return null
  if (days <= 30)
    return <span className="rounded-full bg-red-50 px-2 py-0.5 text-xs font-semibold text-red-600">⏰ {days}d left</span>
  if (days <= 90)
    return <span className="rounded-full bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700">⏳ {days}d left</span>
  return null
}

function OppCard({ o, rank }: { o: Opportunity; rank: number }) {
  const tier = TIER_META[o.fit_tier]
  const statBits: string[] = []
  if (o.estimated_total_funding_usd) statBits.push(`${fmtUSD(o.estimated_total_funding_usd)} program pool`)
  if (o.expected_awards) statBits.push(`~${o.expected_awards} awards expected`)
  if (o.cost_sharing) statBits.push('cost sharing required')
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
            <EligibilityBadge o={o} />
            <UrgencyChip o={o} />
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
          {o.llm_reason && (
            <div className="mt-2 flex items-start gap-1.5 text-[13px] leading-snug text-slate-600">
              <span className="mt-px shrink-0 rounded bg-violet-50 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-violet-700 ring-1 ring-violet-200">
                Analyst
              </span>
              <span className="italic">{o.llm_reason}</span>
            </div>
          )}
          {statBits.length > 0 && (
            <div className="mt-1.5 text-xs text-slate-400">{statBits.join(' · ')}</div>
          )}
        </div>
        <div className="shrink-0 text-right text-sm">
          {(o.award_floor_usd || o.award_ceiling_usd) && (
            <div className="font-semibold text-slate-900">
              {o.award_floor_usd && o.award_ceiling_usd
                ? `${fmtUSD(o.award_floor_usd)}–${fmtUSD(o.award_ceiling_usd)}`
                : `up to ${fmtUSD(o.award_ceiling_usd ?? o.award_floor_usd)}`}
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

      {o.summary && (
        <details className="border-t border-slate-100 px-5 py-3 print:hidden">
          <summary className="cursor-pointer select-none text-xs font-medium text-slate-400 hover:text-slate-600">
            Official program description
          </summary>
          <p className="mt-2 text-sm leading-relaxed text-slate-500">{o.summary}</p>
        </details>
      )}

      {o.history && o.history.similar_companies > 0 && (
        <div className="border-t border-slate-100 bg-slate-50/60 p-5">
          <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
            Who else has received this money?
          </div>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MiniStat value={String(o.history.similar_companies)} label="recipients (recent)" />
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
