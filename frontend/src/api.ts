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
  estimated_total_funding_usd?: number | null
  expected_awards?: number | null
  cost_sharing?: boolean | null
  eligibility_flag?: 'ok' | 'verify' | 'likely_ineligible' | null
  eligible_applicants: string[]
  url?: string | null
  summary: string
  score: number
  fit_tier: FitTier
  llm_reason: string
  explanation?: Explanation | null
  history?: HistoricalStats | null
}

export interface SimilarCompany {
  name: string
  state: string
  agency: string
  program: string
  total_usd: number
  awards: number
  latest_year?: number | null
  example_title: string
}

export interface AgencyMapEntry {
  agency: string
  short: string
  open_opportunities: number
  similar_awards_since_2018: number
  note: string
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
  similar_companies: SimilarCompany[]
  agency_map: AgencyMapEntry[]
}

export function daysUntil(dateStr?: string | null): number | null {
  if (!dateStr) return null
  const m = dateStr.match(/(\d{2})\/(\d{2})\/(\d{4})/)
  const d = m ? new Date(+m[3], +m[1] - 1, +m[2]) : new Date(dateStr)
  if (isNaN(d.getTime())) return null
  return Math.round((d.getTime() - Date.now()) / 86400000)
}

// ---- GraphQL transport (the only data path) ----

const PROFILE_FIELDS = `description industry technology city state employees revenue_usd
  capital_raised_usd funding_stage rd_activities product_maturity target_customers
  capital_need_min_usd capital_need_max_usd use_of_funds`

const OPPORTUNITY_FIELDS = `source source_id title agency agency_code program status cfda
  open_date close_date award_floor_usd award_ceiling_usd estimated_total_funding_usd
  expected_awards cost_sharing eligibility_flag eligible_applicants url summary score fit_tier llm_reason
  explanation { why_fit concerns verify next_steps }
  history { similar_companies total_awarded_usd median_award_usd in_state_recipients
    sample_recipients { name agency program amount year } }`

const EXTRACT_QUERY = `query Extract($text: String!) {
  extract_profile(text: $text) {
    profile { ${PROFILE_FIELDS} }
    followups { field question }
  }
}`

const MATCH_QUERY = `query Match($profile: StartupProfileInput!) {
  match(profile: $profile) {
    summary { high_potential total_potential_value_usd agencies closing_within_90_days overall_note }
    opportunities { ${OPPORTUNITY_FIELDS} }
    similar_companies { name state agency program total_usd awards latest_year example_title }
    agency_map { agency short open_opportunities similar_awards_since_2018 note }
  }
}`

async function gql<T>(query: string, variables: Record<string, unknown>): Promise<T> {
  const r = await fetch('/graphql', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query, variables }),
  })
  if (!r.ok) throw new Error(`graphql failed: ${r.status}`)
  const d = await r.json()
  if (d.errors?.length) throw new Error(`graphql: ${d.errors[0].message}`)
  return d.data
}

export const api = {
  extract: async (text: string): Promise<ExtractResponse> => {
    const d = await gql<{ extract_profile: ExtractResponse }>(EXTRACT_QUERY, { text })
    return d.extract_profile
  },
  match: async (profile: StartupProfile): Promise<MatchResponse> => {
    const d = await gql<{ match: MatchResponse }>(MATCH_QUERY, { profile })
    return d.match
  },
}

export const fmtUSD = (n?: number | null) => {
  if (n == null || n === 0) return '—'
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(n % 1_000_000 === 0 ? 0 : 1)}M`
  if (n >= 1_000) return `$${Math.round(n / 1_000)}K`
  return `$${n}`
}
