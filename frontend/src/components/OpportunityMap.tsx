import { useState } from 'react'
import { daysUntil, fmtUSD, type MatchResponse, type Opportunity, type FitTier } from '../api'

const TIER: Record<FitTier, { label: string; fg: string; dot: string; rail: string }> = {
  likely_fit: { label: 'Likely fit', fg: 'text-likely', dot: 'bg-likely', rail: 'var(--likely)' },
  potential_fit: { label: 'Potential fit', fg: 'text-potential', dot: 'bg-potential', rail: 'var(--potential)' },
  adjacent: { label: 'Adjacent', fg: 'text-adjacent', dot: 'bg-adjacent', rail: 'var(--adjacent)' },
  not_a_fit: { label: 'Unlikely', fg: 'text-notfit', dot: 'bg-notfit', rail: 'var(--notfit)' },
}

const TOP_N = 15

export default function OpportunityMap({ data, onBack }: { data: MatchResponse; onBack: () => void }) {
  const [showAll, setShowAll] = useState(false)
  const s = data.summary
  const federal = data.opportunities.filter((o) => o.source !== 'utah')
  const utah = data.opportunities.filter((o) => o.source === 'utah')

  return (
    <div className="mx-auto max-w-[1080px] px-6 pb-32 pt-12">
      {/* header */}
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <button onClick={onBack} className="btn btn-ghost -ml-3 h-9 px-3 text-[13px] print:hidden">
            ← Start over
          </button>
          <h2 className="display mt-4 text-[44px] text-ink">
            {s.high_potential > 0 ? (
              <>
                <span className="num">{s.high_potential}</span> strong <em>{s.high_potential === 1 ? 'match' : 'matches'}</em>
              </>
            ) : (
              <>Your opportunity <em>map</em></>
            )}
          </h2>
          <p className="mt-2 text-[15px] text-graphite">
            {federal.length} federal programs reviewed
            {s.total_potential_value_usd ? ` · ${fmtUSD(s.total_potential_value_usd)}+ potential award value` : ''}
            {s.closing_within_90_days ? ` · ${s.closing_within_90_days} closing within 90 days` : ''}
          </p>
        </div>
        <button onClick={() => window.print()} className="btn btn-ghost h-10 border border-hairline bg-surface px-4 text-[13px] print:hidden">
          Export report
        </button>
      </div>

      {s.overall_note && (
        <div className="card mt-8 border-l-[3px] border-l-ink p-5">
          <div className="text-[12px] uppercase tracking-wider text-ash">Honest read</div>
          <p className="mt-1 text-[15px] leading-relaxed text-ink-2">{s.overall_note}</p>
        </div>
      )}

      <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_320px]">
        {/* main list */}
        <div className="space-y-3">
          {(showAll ? federal : federal.slice(0, TOP_N)).map((o, i) => (
            <Card key={o.source_id} o={o} index={i} />
          ))}
          {federal.length > TOP_N && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="w-full rounded-lg border border-dashed border-hairline py-3 text-[14px] text-graphite transition-colors hover:border-ink hover:text-ink print:hidden"
            >
              {showAll
                ? 'Show fewer'
                : `Show ${federal.length - TOP_N} more programs we reviewed`}
            </button>
          )}
          <p className="pt-6 text-[12px] leading-relaxed text-ash">
            Guidance generated from official data — not an eligibility determination. Verify with the listing before applying.
          </p>
        </div>

        {/* sidebar */}
        <aside className="space-y-6 lg:sticky lg:top-20 lg:self-start">
          {data.similar_companies.length > 0 && (
            <div className="card p-5">
              <div className="text-[12px] uppercase tracking-wider text-ash">Companies like you that got funded</div>
              <ul className="mt-3 divide-y divide-hairline">
                {data.similar_companies.slice(0, 5).map((c, i) => (
                  <li key={i} className="flex items-baseline justify-between gap-3 py-2.5">
                    <span className="min-w-0 truncate text-[14px] text-ink">
                      {c.name}
                      {c.state && (
                        <span className={`num ml-1.5 text-[10px] ${c.state === 'UT' ? 'text-accent' : 'text-ash'}`}>{c.state}</span>
                      )}
                    </span>
                    <span className="num shrink-0 text-[13px] text-graphite">{fmtUSD(c.total_usd)}</span>
                  </li>
                ))}
              </ul>
              <p className="mt-3 text-[12px] text-ash">SBIR/STTR recipients since 2018 with similar technology.</p>
            </div>
          )}

          {utah.length > 0 && (
            <div className="card p-5">
              <div className="text-[12px] uppercase tracking-wider text-ash">Utah programs</div>
              <ul className="mt-3 divide-y divide-hairline">
                {utah.map((o) => (
                  <li key={o.source_id} className="py-2.5">
                    <a href={o.url ?? '#'} target="_blank" rel="noreferrer" className="group block">
                      <div className="text-[14px] text-ink group-hover:underline group-hover:underline-offset-4">{o.title}</div>
                      <div className="mt-0.5 text-[12px] text-graphite">{o.program}</div>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}

function Card({ o, index }: { o: Opportunity; index: number }) {
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
    <article
      className="card rise overflow-hidden"
      style={{ animationDelay: `${Math.min(index, 8) * 50}ms`, boxShadow: open ? `inset 3px 0 0 ${t.rail}, var(--shadow)` : undefined }}
    >
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="grid w-full grid-cols-[1fr_auto] gap-6 p-5 text-left transition-colors hover:bg-paper-2/60"
      >
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            <span className={`inline-flex items-center gap-1.5 text-[12px] font-medium ${t.fg}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${t.dot}`} />
              {t.label}
            </span>
            {o.eligibility_flag === 'ok' && o.source === 'grants_gov' && (
              <span className="text-[12px] text-graphite">Small businesses eligible</span>
            )}
            {o.eligibility_flag === 'likely_ineligible' && (
              <span className="text-[12px] text-notfit">For-profits likely ineligible</span>
            )}
            {days != null && days >= 0 && days <= 30 && (
              <span className="num text-[12px] text-notfit">{days === 0 ? 'Closes today' : `${days} days left`}</span>
            )}
          </div>
          <h3 className="mt-2 text-[17px] font-medium leading-snug text-ink">{o.title}</h3>
          <div className="mt-1 text-[13px] text-graphite">{o.agency}</div>
          {oneLine && <p className="mt-2.5 line-clamp-2 text-[14px] leading-relaxed text-ink-2">{oneLine}</p>}
        </div>

        <div className="shrink-0 text-right">
          <div
            className={`num text-[28px] leading-none ${t.fg}`}
            title="Relevance: how closely this program's own description matches your company, as read by our local model. Green programs score 70–100, yellow 45–69. Not a probability of funding."
          >
            {Math.round(o.score)}<span className="text-[13px] text-ash">%</span>
          </div>
          <div className="mt-0.5 text-[10px] uppercase tracking-wider text-ash">relevance</div>
          <div className="num mt-3 space-y-0.5 text-[12px] text-graphite">
            {value && <div className="text-ink">{value}</div>}
            {days != null && days > 30 && <div>{days} days left</div>}
          </div>
        </div>
      </button>

      {open && (
        <div className="border-t border-hairline bg-paper-2/40 px-5 py-6">
          {o.explanation && (
            <div className="grid gap-x-8 gap-y-5 sm:grid-cols-2">
              <Row title="Why you may fit" text={o.explanation.why_fit} />
              <Row title="What could disqualify you" text={o.explanation.concerns} />
              <Row title="Verify before applying" text={o.explanation.verify} />
              <Row title="Next steps" text={o.explanation.next_steps} />
            </div>
          )}

          {h && h.similar_companies > 0 && (
            <div className="mt-6 border-t border-hairline pt-5">
              <div className="text-[12px] uppercase tracking-wider text-ash">Who else got this money</div>
              <div className="mt-3 grid grid-cols-3 gap-4 sm:max-w-[420px]">
                <Mini value={String(h.similar_companies)} label="recipients" />
                <Mini value={fmtUSD(h.median_award_usd)} label="median award" />
                <Mini value={String(h.in_state_recipients)} label="in your state" />
              </div>
              {h.sample_recipients.length > 0 && (
                <p className="mt-3 text-[13px] text-graphite">
                  {h.sample_recipients.slice(0, 3).map((r) => r.name).join(' · ')}
                </p>
              )}
            </div>
          )}

          {o.url && (
            <a href={o.url} target="_blank" rel="noreferrer" className="mt-6 inline-flex items-center gap-1.5 text-[14px] font-medium text-accent hover:underline hover:underline-offset-4">
              Open official listing <span aria-hidden="true">↗</span>
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
      <div className="text-[12px] uppercase tracking-wider text-ash">{title}</div>
      <p className="mt-1.5 text-[14px] leading-relaxed text-ink-2">{text}</p>
    </div>
  )
}

function Mini({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="num text-[22px] leading-none text-ink">{value}</div>
      <div className="mt-1 text-[11px] text-graphite">{label}</div>
    </div>
  )
}
