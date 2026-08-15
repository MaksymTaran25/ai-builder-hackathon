import { useState } from 'react'
import { daysUntil, fmtUSD, type MatchResponse, type Opportunity, type FitTier } from '../api'

const TIER: Record<FitTier, { label: string; fg: string; dot: string }> = {
  likely_fit: { label: 'Likely fit', fg: 'text-likely', dot: 'bg-likely' },
  potential_fit: { label: 'Potential fit', fg: 'text-potential', dot: 'bg-potential' },
  adjacent: { label: 'Adjacent', fg: 'text-adjacent', dot: 'bg-adjacent' },
  not_a_fit: { label: 'Unlikely', fg: 'text-notfit', dot: 'bg-notfit' },
}

export default function OpportunityMap({ data, onBack }: { data: MatchResponse; onBack: () => void }) {
  const s = data.summary
  const federal = data.opportunities.filter((o) => o.source !== 'utah')
  const utah = data.opportunities.filter((o) => o.source === 'utah')

  return (
    <div className="mx-auto max-w-[640px] px-6 pt-20 pb-32">
      <div className="flex items-center justify-between print:hidden">
        <button onClick={onBack} className="text-[13px] text-ash transition-colors hover:text-ink">
          ← Start over
        </button>
        <button onClick={() => window.print()} className="text-[13px] text-ash transition-colors hover:text-ink">
          Export
        </button>
      </div>

      <h2 className="mt-8 text-[28px] font-medium leading-tight text-ink">
        {s.high_potential > 0 ? `${s.high_potential} strong ${s.high_potential === 1 ? 'match' : 'matches'}` : 'Your opportunity map'}
      </h2>
      <p className="mt-2 text-[15px] text-graphite">
        {federal.length} federal programs
        {s.total_potential_value_usd ? ` · ${fmtUSD(s.total_potential_value_usd)}+ potential` : ''}
        {s.closing_within_90_days ? ` · ${s.closing_within_90_days} closing within 90 days` : ''}
      </p>

      {s.overall_note && (
        <p className="mt-6 border-l-2 border-ink pl-4 text-[15px] leading-relaxed text-ink-2">{s.overall_note}</p>
      )}

      <div className="mt-10 border-t border-hairline">
        {federal.map((o) => (
          <Card key={o.source_id} o={o} />
        ))}
      </div>

      {data.similar_companies.length > 0 && (
        <section className="mt-16">
          <h3 className="text-[13px] font-medium uppercase tracking-wider text-graphite">Companies like you that got funded</h3>
          <div className="mt-3 border-t border-hairline">
            {data.similar_companies.slice(0, 5).map((c, i) => (
              <div key={i} className="flex items-baseline justify-between gap-4 border-b border-hairline py-3">
                <span className="truncate text-[15px] text-ink">
                  {c.name}
                  {c.state && <span className={`num ml-2 text-[11px] ${c.state === 'UT' ? 'text-accent' : 'text-ash'}`}>{c.state}</span>}
                </span>
                <span className="num shrink-0 text-[14px] text-graphite">{fmtUSD(c.total_usd)} · {c.agency}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {utah.length > 0 && (
        <section className="mt-16">
          <h3 className="text-[13px] font-medium uppercase tracking-wider text-graphite">Utah programs</h3>
          <div className="mt-3 border-t border-hairline">
            {utah.map((o) => (
              <a
                key={o.source_id}
                href={o.url ?? '#'}
                target="_blank"
                rel="noreferrer"
                className="block border-b border-hairline py-3 transition-colors hover:bg-paper-2"
              >
                <div className="text-[15px] text-ink">{o.title}</div>
                <div className="mt-0.5 text-[13px] text-graphite">{o.program}</div>
              </a>
            ))}
          </div>
        </section>
      )}

      <p className="mt-16 text-[12px] leading-relaxed text-ash">
        Guidance from official data, not an eligibility determination. Verify with the listing before applying.
      </p>
    </div>
  )
}

function Card({ o }: { o: Opportunity }) {
  const [open, setOpen] = useState(false)
  const t = TIER[o.fit_tier]
  const days = daysUntil(o.close_date)
  const value =
    o.award_floor_usd && o.award_ceiling_usd
      ? `${fmtUSD(o.award_floor_usd)}–${fmtUSD(o.award_ceiling_usd)}`
      : o.award_ceiling_usd || o.award_floor_usd
        ? `up to ${fmtUSD(o.award_ceiling_usd ?? o.award_floor_usd)}`
        : null
  const oneLine = o.llm_reason || o.explanation?.why_fit || ''
  const h = o.history

  return (
    <article className="border-b border-hairline">
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="grid w-full grid-cols-[1fr_auto] gap-6 py-5 text-left transition-colors hover:bg-paper-2 -mx-3 px-3"
      >
        <div className="min-w-0">
          <div className={`flex items-center gap-1.5 text-[12px] font-medium ${t.fg}`}>
            <span className={`h-1.5 w-1.5 rounded-full ${t.dot}`} />
            {t.label}
            {o.eligibility_flag === 'likely_ineligible' && <span className="ml-2 text-notfit">· for-profits likely ineligible</span>}
          </div>
          <div className="mt-1.5 text-[17px] font-medium leading-snug text-ink">{o.title}</div>
          <div className="mt-1 text-[13px] text-graphite">{o.agency}</div>
          {oneLine && <p className="mt-2 line-clamp-2 text-[14px] leading-relaxed text-ink-2">{oneLine}</p>}
        </div>
        <div className="num shrink-0 text-right text-[13px] leading-relaxed text-graphite">
          {value && <div className="text-ink">{value}</div>}
          {days != null && days >= 0 && (
            <div className={days <= 30 ? 'text-notfit' : ''}>{days === 0 ? 'closes today' : `${days}d left`}</div>
          )}
        </div>
      </button>

      {open && (
        <div className="space-y-6 pb-7 pl-0 pt-1">
          {o.explanation && (
            <div className="space-y-4">
              <Row title="Why you may fit" text={o.explanation.why_fit} />
              <Row title="What could disqualify you" text={o.explanation.concerns} />
              <Row title="Verify before applying" text={o.explanation.verify} />
              <Row title="Next steps" text={o.explanation.next_steps} />
            </div>
          )}

          {h && h.similar_companies > 0 && (
            <div>
              <div className="text-[12px] font-medium uppercase tracking-wider text-graphite">Who else got this money</div>
              <p className="num mt-1 text-[14px] text-ink-2">
                {h.similar_companies} recipients · median {fmtUSD(h.median_award_usd)}
                {h.in_state_recipients > 0 && ` · ${h.in_state_recipients} in your state`}
              </p>
              {h.sample_recipients.length > 0 && (
                <p className="mt-1 text-[13px] text-graphite">
                  {h.sample_recipients.slice(0, 3).map((r) => r.name).join(' · ')}
                </p>
              )}
            </div>
          )}

          {o.url && (
            <a href={o.url} target="_blank" rel="noreferrer" className="inline-block text-[14px] text-accent underline underline-offset-4">
              Open official listing
            </a>
          )}
        </div>
      )}
    </article>
  )
}

function Row({ title, text }: { title: string; text: string }) {
  if (!text) return null
  return (
    <div>
      <div className="text-[12px] font-medium uppercase tracking-wider text-graphite">{title}</div>
      <p className="mt-1 text-[14px] leading-relaxed text-ink-2">{text}</p>
    </div>
  )
}
