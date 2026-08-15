import { useState } from 'react'
import { daysUntil, fmtUSD, type MatchResponse, type Opportunity, type FitTier } from '../api'

const TIER: Record<FitTier, { label: string; fg: string; bg: string }> = {
  likely_fit: { label: 'Likely fit', fg: 'text-likely', bg: 'bg-likely' },
  potential_fit: { label: 'Potential fit — verify', fg: 'text-potential', bg: 'bg-potential' },
  adjacent: { label: 'Adjacent', fg: 'text-adjacent', bg: 'bg-adjacent' },
  not_a_fit: { label: 'Probably not a fit', fg: 'text-notfit', bg: 'bg-notfit' },
}

export default function OpportunityMap({ data, onBack }: { data: MatchResponse; onBack: () => void }) {
  const s = data.summary
  const federal = data.opportunities.filter((o) => o.source !== 'utah')
  const utah = data.opportunities.filter((o) => o.source === 'utah')

  return (
    <div className="mx-auto max-w-[760px] px-6 pt-16 pb-32">
      <div className="flex items-center justify-between print:hidden">
        <button onClick={onBack} className="eyebrow transition-colors hover:text-ink">
          ← Start over
        </button>
        <button
          onClick={() => window.print()}
          className="eyebrow border border-hairline px-3 py-1.5 transition-colors hover:border-ink hover:text-ink"
        >
          Export report
        </button>
      </div>

      <div className="eyebrow mt-10">Your Government Opportunity Map</div>
      <h2 className="mt-2 text-[32px] font-medium leading-tight text-ink">
        {federal.length} federal opportunities
        {utah.length > 0 && <span className="text-graphite"> + {utah.length} Utah programs</span>}
      </h2>

      {/* summary numbers — the heroes */}
      <div className="mt-8 grid grid-cols-2 gap-px border border-hairline bg-hairline sm:grid-cols-4">
        <Stat value={String(s.high_potential)} label="High-potential matches" />
        <Stat value={s.total_potential_value_usd ? `${fmtUSD(s.total_potential_value_usd)}+` : '—'} label="Potential award value" />
        <Stat value={String(s.agencies)} label="Relevant agencies" />
        <Stat value={String(s.closing_within_90_days)} label="Closing within 90 days" />
      </div>

      {s.overall_note && (
        <div className="mt-6 border-l-2 border-ink pl-4">
          <div className="eyebrow">Honest read</div>
          <p className="mt-1 text-[15px] leading-relaxed text-ink-2">{s.overall_note}</p>
        </div>
      )}

      {data.agency_map.length > 0 && (
        <section className="mt-12">
          <div className="eyebrow">Where your people are</div>
          <div className="mt-3 border-t border-hairline">
            {data.agency_map.map((a) => (
              <div key={a.agency} className="grid grid-cols-[1fr_auto] items-baseline gap-4 border-b border-hairline py-2.5">
                <div className="min-w-0">
                  <span className="text-[15px] font-medium text-ink">{a.short || a.agency}</span>
                  {a.agency !== a.short && <span className="ml-2 text-[13px] text-graphite">{a.agency}</span>}
                </div>
                <div className="num shrink-0 text-[12px] text-graphite">
                  {a.open_opportunities > 0 && <span>{a.open_opportunities} open</span>}
                  {a.open_opportunities > 0 && a.similar_awards_since_2018 > 0 && <span className="text-ash"> · </span>}
                  {a.similar_awards_since_2018 > 0 && <span>{a.similar_awards_since_2018} similar awards</span>}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="mt-14">
        <div className="eyebrow">Opportunities, ranked</div>
        <div className="mt-3 border-t border-hairline">
          {federal.map((o, i) => (
            <Card key={o.source_id} o={o} rank={i + 1} />
          ))}
        </div>
      </section>

      {data.similar_companies.length > 0 && (
        <section className="mt-14">
          <div className="eyebrow">Companies like you that got funded</div>
          <p className="mt-1 text-[14px] text-graphite">
            SBIR/STTR recipients since 2018 working on similar technology — proof this path works from where you are.
          </p>
          <div className="mt-3 border-t border-hairline">
            {data.similar_companies.map((c, i) => (
              <div key={i} className="grid grid-cols-[1fr_auto] items-start gap-4 border-b border-hairline py-3">
                <div className="min-w-0">
                  <div className="flex items-baseline gap-2">
                    <span className="truncate text-[15px] font-medium text-ink">{c.name}</span>
                    {c.state && (
                      <span className={`num text-[11px] ${c.state === 'UT' ? 'text-accent' : 'text-ash'}`}>{c.state}</span>
                    )}
                  </div>
                  <div className="mt-0.5 truncate text-[13px] text-graphite">{c.example_title}</div>
                </div>
                <div className="shrink-0 text-right">
                  <div className="num text-[15px] font-medium text-ink">{fmtUSD(c.total_usd)}</div>
                  <div className="num text-[11px] text-graphite">
                    {c.awards} award{c.awards > 1 ? 's' : ''} · {c.agency} · {c.latest_year}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {utah.length > 0 && (
        <section className="mt-14">
          <div className="eyebrow">The Utah advantage</div>
          <p className="mt-1 text-[14px] text-graphite">
            State programs you can tap alongside — or instead of — federal funding.
          </p>
          <div className="mt-3 border-t border-hairline">
            {utah.map((o, i) => (
              <Card key={o.source_id} o={o} rank={federal.length + i + 1} />
            ))}
          </div>
        </section>
      )}

      <p className="mt-16 max-w-[560px] text-[12px] leading-relaxed text-ash">
        Assessments are generated guidance from official data, not eligibility determinations.
        Verify with the official listing and program officer before applying.
      </p>
    </div>
  )
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="bg-paper p-4">
      <div className="num text-[30px] font-medium leading-none text-ink">{value}</div>
      <div className="mt-2 text-[12px] leading-snug text-graphite">{label}</div>
    </div>
  )
}

function Card({ o, rank }: { o: Opportunity; rank: number }) {
  const [open, setOpen] = useState(false)
  const t = TIER[o.fit_tier]
  const days = daysUntil(o.close_date)
  const value =
    o.award_floor_usd && o.award_ceiling_usd
      ? `${fmtUSD(o.award_floor_usd)}–${fmtUSD(o.award_ceiling_usd)}`
      : o.award_ceiling_usd || o.award_floor_usd
        ? `up to ${fmtUSD(o.award_ceiling_usd ?? o.award_floor_usd)}`
        : null

  return (
    <article className="grid grid-cols-[44px_1fr] gap-4 border-b border-hairline py-6">
      <div className="num pt-1 text-[13px] text-ash">{String(rank).padStart(2, '0')}</div>

      <div className="min-w-0">
        {/* status line */}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
          <span className={`inline-flex items-center gap-1.5 text-[12px] font-medium ${t.fg}`}>
            <span className={`h-1.5 w-1.5 rounded-full ${t.bg}`} />
            {t.label}
          </span>
          <span className="num text-[12px] text-graphite">{Math.round(o.score)}% match</span>
          {o.eligibility_flag === 'ok' && o.source === 'grants_gov' && (
            <span className="text-[12px] text-graphite">Small businesses eligible</span>
          )}
          {o.eligibility_flag === 'likely_ineligible' && (
            <span className="text-[12px] text-notfit">For-profits likely ineligible</span>
          )}
          {o.eligibility_flag === 'verify' && (
            <span className="text-[12px] text-graphite">Verify eligibility</span>
          )}
          {days != null && days >= 0 && days <= 90 && (
            <span className={`num text-[12px] ${days <= 30 ? 'text-notfit' : 'text-potential'}`}>
              {days === 0 ? 'closes today' : `${days} days left`}
            </span>
          )}
        </div>

        {/* title + agency */}
        <h3 className="mt-2 text-[18px] font-medium leading-snug text-ink">
          {o.url ? (
            <a href={o.url} target="_blank" rel="noreferrer" className="hover:underline hover:decoration-hairline hover:underline-offset-4">
              {o.title}
            </a>
          ) : (
            o.title
          )}
        </h3>
        <div className="mt-1 flex flex-wrap items-baseline gap-x-3 text-[13px] text-graphite">
          <span>{o.agency}</span>
          {o.program && <span className="num text-ash">{o.program}</span>}
          {value && <span className="num text-ink">{value}</span>}
          {o.close_date && <span className="num text-ash">closes {o.close_date}</span>}
        </div>

        {/* analyst verdict */}
        {o.llm_reason && (
          <div className="mt-3 border-l-2 border-analyst pl-3">
            <span className="eyebrow mr-2" style={{ color: 'var(--analyst)' }}>Analyst</span>
            <span className="text-[14px] leading-relaxed text-ink-2">{o.llm_reason}</span>
          </div>
        )}

        {/* explanation grid */}
        {o.explanation && (
          <div className="mt-4 grid gap-x-8 gap-y-3 sm:grid-cols-2">
            <Section title="Why you may fit" text={o.explanation.why_fit} />
            <Section title="Potential concerns" text={o.explanation.concerns} />
            <Section title="What to verify" text={o.explanation.verify} />
            <Section title="Next steps" text={o.explanation.next_steps} />
          </div>
        )}

        {/* history */}
        {o.history && o.history.similar_companies > 0 && (
          <div className="mt-5 bg-paper-2 p-4">
            <div className="eyebrow">Who else has received this money</div>
            <div className="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-4">
              <Mini value={String(o.history.similar_companies)} label="recipients" />
              <Mini value={fmtUSD(o.history.total_awarded_usd)} label="total awarded" />
              <Mini value={fmtUSD(o.history.median_award_usd)} label="median award" />
              <Mini value={String(o.history.in_state_recipients)} label="in your state" />
            </div>
            {o.history.sample_recipients.length > 0 && (
              <div className="mt-3 space-y-1 border-t border-hairline pt-3">
                {o.history.sample_recipients.slice(0, 3).map((r, i) => (
                  <div key={i} className="grid grid-cols-[1fr_auto] gap-3 text-[13px]">
                    <span className="truncate text-ink-2">{r.name}</span>
                    <span className="num shrink-0 text-graphite">{fmtUSD(r.amount)} · {r.year}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* synopsis expander */}
        {o.summary && (
          <div className="mt-4">
            <button onClick={() => setOpen(!open)} className="eyebrow transition-colors hover:text-ink">
              {open ? '− Program description' : '+ Program description'}
            </button>
            {open && <p className="mt-2 text-[14px] leading-relaxed text-ink-2">{o.summary}</p>}
          </div>
        )}
      </div>
    </article>
  )
}

function Section({ title, text }: { title: string; text: string }) {
  if (!text) return null
  return (
    <div>
      <div className="eyebrow">{title}</div>
      <p className="mt-1 text-[14px] leading-relaxed text-ink-2">{text}</p>
    </div>
  )
}

function Mini({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="num text-[20px] font-medium leading-none text-ink">{value}</div>
      <div className="mt-1 text-[11px] text-graphite">{label}</div>
    </div>
  )
}
