import type { StrategyRankedItem, TimelineMilestone } from '../types/opportunity';

export const mockRankedStrategy: StrategyRankedItem[] = [
  {
    rank: '01',
    opportunityId: 'nsf-seed-fund-2026',
    title: "NSF America's Seed Fund",
    agency: 'National Science Foundation',
    potentialValue: '$250K–$1.5M',
    rationale: 'Best alignment with your R&D and commercialization stage.',
    tag: 'Highest Technical Alignment',
  },
  {
    rank: '02',
    opportunityId: 'nih-hhs-sbir-2026',
    title: 'NIH / HHS (NINR Clinical AI)',
    agency: 'National Institutes of Health',
    potentialValue: '$400K–$2.2M',
    rationale: 'Strong healthcare alignment; verify solicitation-specific eligibility.',
    tag: 'Largest Healthcare Pool',
  },
  {
    rank: '03',
    opportunityId: 'arpa-h-sprint-2026',
    title: 'ARPA-H & Federal SBIR/STTR',
    agency: 'ARPA-H / Federal Seed Track',
    potentialValue: '$500K–$3.0M',
    rationale: 'Potential source of non-dilutive R&D funding with accelerated review.',
    tag: 'Accelerated Sprint Path',
  },
];

export const mockTimelineMilestones: TimelineMilestone[] = [
  {
    month: 'AUGUST',
    phase: 'Phase 1: Readiness & Discovery',
    action: 'Research eligibility & entity registrations',
    deliverables: [
      'Confirm SAM.gov UEI and CAGE active status',
      'Submit NSF Project Pitch (3 pages) in Research.gov',
      'Draft NIH Specific Aims page for Program Officer check-in',
    ],
    status: 'current',
  },
  {
    month: 'SEPTEMBER',
    phase: 'Phase 2: Proposal Drafting & Letters of Support',
    action: 'Prepare materials & clinical pilot metrics',
    deliverables: [
      'Gather 2 partner hospital nursing leadership letters of intent',
      'Finalize NSF 15-page project description & commercialization plan',
      'Submit ARPA-H BAA 4-page Executive Abstract',
    ],
    status: 'upcoming',
  },
  {
    month: 'OCTOBER',
    phase: 'Phase 3: Formal Federal Submission',
    action: 'Submit strongest opportunity & prep secondary application',
    deliverables: [
      'Submit NSF Phase I SBIR full proposal before deadline',
      'Complete NIH Fast-Track package via ASSIST portal',
      'Initiate VA VHA Innovation discovery briefing call',
    ],
    status: 'upcoming',
  },
];
