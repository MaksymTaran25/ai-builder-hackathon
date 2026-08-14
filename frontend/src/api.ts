// Types mirror backend/app/models.py

export interface StartupProfile {
  description: string
  industry?: string | null
  technology?: string[]
  city?: string | null
  state?: string | null
  employees?: number | null
  revenue_usd?: number | null
  capital_raised_usd?: number | null
  funding_stage?: string | null
  rd_activities?: string | null
  product_maturity?: string | null
  target_customers?: string | null
  capital_need_min_usd?: number | null
  capital_need_max_usd?: number | null
  use_of_funds?: string | null
}

export interface FollowUpQuestion {
  field: string
  question: string
}

export interface ExtractResponse {
  profile: StartupProfile
  followups: FollowUpQuestion[]
}

export type FitTier = 'likely_fit' | 'potential_fit' | 'adjacent' | 'not_a_fit'

export interface Explanation {
  why_fit: string
  concerns: string
  verify: string
  next_steps: string
}

export interface HistoricalStats {
  similar_companies: number
  total_awarded_usd: number
  median_award_usd: number
  in_state_recipients: number
  sample_recipients: { name?: string; program?: string; agency?: string; amount?: number; year?: number }[]
}

export interface Opportunity {
  source: string
  source_id: string
  title: string
  agency: string
  program: string
  status: string
  cfda: string[]
  open_date?: string | null
  close_date?: string | null
  award_floor_usd?: number | null
  award_ceiling_usd?: number | null
  url?: string | null
  summary: string
  score: number
  fit_tier: FitTier
  explanation?: Explanation | null
  history?: HistoricalStats | null
}

export interface MatchSummary {
  high_potential: number
  total_potential_value_usd: number
  agencies: number
  closing_within_90_days: number
  overall_note: string
}

export interface MatchResponse {
  summary: MatchSummary
  opportunities: Opportunity[]
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(path, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(`${path} failed: ${r.status}`)
  return r.json()
}

export const api = {
  extract: (text: string) => post<ExtractResponse>('/api/profile/extract', { text }),
  match: (profile: StartupProfile) => post<MatchResponse>('/api/match', profile),
}

export const fmtUSD = (n?: number | null) => {
  if (n == null || n === 0) return '—'
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(n % 1_000_000 === 0 ? 0 : 1)}M`
  if (n >= 1_000) return `$${Math.round(n / 1_000)}K`
  return `$${n}`
}
