export type FitLevel = 'likely' | 'potential' | 'adjacent' | 'unlikely';

export interface StartupProfile {
  name: string;
  story: string;
  industry: string;
  technology: string;
  location: string;
  employees: number | string;
  revenue: string;
  fundingStage: string;
  capitalRaised: string;
  fundingNeed: string;
  rdActivities: string;
  productMaturity: string;
  targetCustomers: string;
  capitalRequired: string;
  useOfFunds: string;
}

export interface HistoricalAward {
  id: string;
  company: string;
  program: string;
  agency: string;
  amount: string;
  year: number;
  location: string;
  projectTitle: string;
}

export interface ActionStep {
  step: number;
  title: string;
  timeline: string;
  detail: string;
}

export interface HistoricalIntelligence {
  similarCompaniesFunded: number;
  totalHistoricalAwards: string;
  medianAward: string;
  localRecipients: string;
  topRecipientsSummary: string;
}

export interface OpportunityDetailData {
  whyShouldICare: string;
  whatCouldMakeMeIneligible: string[];
  whatShouldIVerify: string[];
  whatShouldIDoNext: string[];
  actionSequence: ActionStep[];
}

export interface Opportunity {
  id: string;
  title: string;
  programCode: string;
  agency: string;
  agencyShort: string;
  matchScore: number;
  fitLevel: FitLevel;
  fitLabel: string;
  potentialValue: string;
  deadline: string;
  daysLeft: number;
  closingSoon: boolean;
  category: 'R&D Grant' | 'Procurement' | 'Translational Health' | 'Defense SBIR' | 'Consortium / Adjacent';
  summary: string;
  whyFit: string[];
  concerns: string[];
  historicalIntelligence: HistoricalIntelligence;
  detailedOverview: OpportunityDetailData;
  historicalAwards: HistoricalAward[];
}

export interface StrategyRankedItem {
  rank: string;
  opportunityId: string;
  title: string;
  agency: string;
  potentialValue: string;
  rationale: string;
  tag: string;
}

export interface TimelineMilestone {
  month: string;
  phase: string;
  action: string;
  deliverables: string[];
  status: 'current' | 'upcoming';
}

export type ViewStage = 'landing' | 'intake' | 'analyzing' | 'confirm' | 'map';
