import { useState } from 'react'

interface ScrapedPage {
  url: string
  title?: string
  meta_description?: string
  headings?: { h1?: string[]; h2?: string[]; h3?: string[] }
  text?: string
  links?: string[]
  depth?: number
}

interface ScrapeResult {
  base_url: string
  scraped_at: string
  total_pages_scraped: number
  pages: ScrapedPage[]
  errors?: { url: string; error: string }[]
}

const SUGGESTED = [
  { label: 'SBIR.gov', url: 'https://www.sbir.gov' },
  { label: 'Utah GOEO', url: 'https://business.utah.gov' },
  { label: 'NSF Seed Fund', url: 'https://seedfund.nsf.gov' },
  { label: 'NIH SEED', url: 'https://seed.nih.gov' },
]

export default function ExtendedSearch({ onBack }: { onBack: () => void }) {
  const [url, setUrl] = useState('')
  const [pages, setPages] = useState(20)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<ScrapeResult | null>(null)
  const [q, setQ] = useState('')

  const run = async (target = url) => {
    const clean = target.trim()
    if (!clean || busy) return
    setBusy(true)
    setError('')
    setResult(null)
    try {
      const r = await fetch('/graphql', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          query: 'query S($url:String!,$n:Int!){ scrape_site(url:$url, max_pages:$n, max_depth:2) }',
          variables: { url: clean.startsWith('http') ? clean : `https://${clean}`, n: pages },
        }),
      })
      const d = await r.json()
      if (d.errors?.length) throw new Error(d.errors[0].message)
      setResult(d.data.scrape_site)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Scrape failed')
    } finally {
      setBusy(false)
    }
  }

  const shown = (result?.pages ?? []).filter((p) => {
    if (!q.trim()) return true
    const hay = `${p.title ?? ''} ${p.meta_description ?? ''} ${p.text ?? ''}`.toLowerCase()
    return q.toLowerCase().split(/\s+/).every((w) => hay.includes(w))
  })

  return (
    <div className="mx-auto max-w-[1080px] px-6 pb-24 pt-12">
      <button onClick={onBack} className="btn btn-ghost -ml-3 h-9 px-3 text-[13px]">
        ← Back
      </button>

      <h2 className="display mt-4 text-[40px] text-ink">
        Extended <em>search</em>
      </h2>
      <p className="mt-2 max-w-[620px] text-[15px] leading-relaxed text-graphite">
        Crawl any funding site — an agency program page, a state portal — and read every subpage
        in one place. Useful for sources that aren't in Grants.gov.
      </p>

      {/* search bar */}
      <div className="card mt-8 p-5">
        <div className="flex flex-wrap items-end gap-3">
          <label className="min-w-[280px] flex-1">
            <span className="text-[12px] uppercase tracking-wider text-ash">Site to crawl</span>
            <input
              className="field mt-1.5 h-11 py-0"
              placeholder="business.utah.gov"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && run()}
            />
          </label>
          <label>
            <span className="text-[12px] uppercase tracking-wider text-ash">Max pages</span>
            <select
              className="field mt-1.5 h-11 w-[110px] py-0"
              value={pages}
              onChange={(e) => setPages(Number(e.target.value))}
            >
              {[10, 20, 50, 100].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </label>
          <button onClick={() => run()} disabled={busy || !url.trim()} className="btn btn-primary">
            {busy ? 'Crawling…' : 'Search'}
          </button>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-[12px] text-ash">Try:</span>
          {SUGGESTED.map((s) => (
            <button
              key={s.url}
              className="chip"
              onClick={() => {
                setUrl(s.url)
                run(s.url)
              }}
            >
              {s.label}
            </button>
          ))}
        </div>
        {error && <p className="mt-3 text-[14px] text-notfit">{error}</p>}
      </div>

      {busy && (
        <p className="mt-8 text-[15px] text-graphite">
          Crawling {url} — following internal links up to {pages} pages…
        </p>
      )}

      {result && (
        <>
          <div className="mt-8 flex flex-wrap items-center justify-between gap-4">
            <p className="text-[15px] text-graphite">
              <span className="num text-ink">{result.total_pages_scraped}</span> pages from{' '}
              <span className="text-ink">{result.base_url}</span>
              {result.errors?.length ? ` · ${result.errors.length} unreachable` : ''}
            </p>
            <input
              className="field h-10 w-[260px] py-0 text-[14px]"
              placeholder="Filter these pages…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>

          <div className="mt-4 space-y-2">
            {shown.map((p) => (
              <PageRow key={p.url} p={p} />
            ))}
            {shown.length === 0 && (
              <p className="py-8 text-center text-[14px] text-ash">No pages match "{q}".</p>
            )}
          </div>
        </>
      )}
    </div>
  )
}

function PageRow({ p }: { p: ScrapedPage }) {
  const [open, setOpen] = useState(false)
  const h1 = p.headings?.h1?.[0]
  const snippet = (p.meta_description || p.text || '').slice(0, 220)

  return (
    <article className="card overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="grid w-full grid-cols-[1fr_auto] gap-4 p-4 text-left transition-colors hover:bg-paper-2/60"
      >
        <div className="min-w-0">
          <h3 className="truncate text-[16px] font-medium text-ink">{p.title || h1 || p.url}</h3>
          <div className="num mt-0.5 truncate text-[12px] text-graphite">{p.url}</div>
          {snippet && <p className="mt-1.5 line-clamp-2 text-[13px] leading-relaxed text-ink-2">{snippet}</p>}
        </div>
        <div className="num shrink-0 text-right text-[11px] text-ash">
          depth {p.depth ?? 0}
          <div>{p.links?.length ?? 0} links</div>
        </div>
      </button>

      {open && (
        <div className="border-t border-hairline bg-paper-2/40 px-4 py-4">
          {p.headings?.h2?.length ? (
            <div className="mb-3">
              <div className="text-[12px] uppercase tracking-wider text-ash">Sections</div>
              <p className="mt-1 text-[13px] text-ink-2">{p.headings.h2.slice(0, 10).join(' · ')}</p>
            </div>
          ) : null}
          {p.text && (
            <p className="max-h-[220px] overflow-y-auto text-[13px] leading-relaxed text-ink-2">
              {p.text.slice(0, 1500)}
            </p>
          )}
          <a
            href={p.url}
            target="_blank"
            rel="noreferrer"
            className="mt-3 inline-block text-[14px] font-medium text-accent hover:underline hover:underline-offset-4"
          >
            Open page ↗
          </a>
        </div>
      )}
    </article>
  )
}
