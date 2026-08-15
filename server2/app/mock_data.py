"""
Government Opportunity Data Layer (Mock Repository)
===================================================
NOTE FOR FUTURE MONGODB INTEGRATION:
When MongoDB is finalized, replace the in-memory `MOCK_OPPORTUNITIES` list with
read-only MongoDB queries via motor/pymongo in `get_all_opportunities()` and `get_opportunity_by_id()`.

Example future MongoDB implementation:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client["federal_funding"]
    
    def get_all_opportunities() -> List[OpportunityItem]:
        docs = list(db["opportunities"].find())
        return [OpportunityItem(**doc) for doc in docs]
"""

from typing import List, Optional
from .models import (
    OpportunityItem,
    HistoricalAward,
    HistoricalIntelligence,
    DetailedOverview,
    ActionStep,
)


MOCK_OPPORTUNITIES: List[OpportunityItem] = [
    OpportunityItem(
        id="nsf-seed-fund-2026",
        title="NSF — America's Seed Fund (Phase I/II SBIR/STTR)",
        program_code="NSF-SBIR-2026-04",
        agency="National Science Foundation",
        agency_short="NSF",
        category="R&D Grant",
        summary="Non-dilutive federal funding supporting early-stage startups conducting unproven technical R&D with high commercial potential in AI-driven biomedical workflows.",
        potential_value="$250K–$1.5M",
        potential_value_min=250000.0,
        potential_value_max=1500000.0,
        deadline="September 30, 2026",
        days_left=47,
        closing_soon=True,
        target_domains=["Healthcare Technology", "Artificial Intelligence", "Biomedical", "DeepTech"],
        target_technologies=["Artificial Intelligence / SaaS", "Machine Learning", "NLP", "Algorithms", "Software"],
        base_eligibility_criteria=[
            "For-profit small business located in the United States",
            "Fewer than 500 employees including affiliates",
            "At least 51% owned by U.S. citizens or permanent residents",
            "Principal Investigator primary employment (>51%) with startup"
        ],
        keywords=["ai", "artificial intelligence", "nurse", "healthcare", "hospital", "workflow", "clinical", "software", "deep tech", "r&d"],
        historical_intelligence=HistoricalIntelligence(
            similar_companies_funded=17,
            total_historical_awards="$8.4M",
            median_award="$420K",
            local_recipients="3 Utah recipients",
            top_recipients_summary="17 clinical AI and nurse workflow startups funded across Phase I and II over the past 3 fiscal cycles."
        ),
        detailed_overview=DetailedOverview(
            why_should_i_care="America's Seed Fund provides up to $1.5M in 100% non-dilutive equity-free capital. NSF does not take equity, IP rights, or board seats, allowing your team to de-risk nurse burden AI algorithms while accelerating hospital deployment.",
            what_could_make_me_ineligible=[
                "More than 50% owned by foreign corporate entities or foreign institutional funds",
                "Principal Investigator (PI) devoting less than 51% of primary employment to the startup during Phase I execution",
                "Purely standard software integration lacking genuine scientific/technical unproven risk"
            ],
            what_should_i_verify=[
                "Confirm you submit a mandatory Project Pitch (response window is typically 3 weeks)",
                "Verify SAM.gov Unique Entity Identifier (UEI) and CAGE code are fully active",
                "Confirm clinical data privacy compliance architecture in your system architecture description"
            ],
            what_should_i_do_next=[
                "Draft a 3-page NSF Project Pitch focusing on technical innovation vs. market adoption",
                "Establish advisory letters of support from participating Utah hospital pilot leads",
                "Register primary investigator profile in Research.gov and FastLane"
            ],
            action_sequence=[
                ActionStep(
                    step=1,
                    title="Submit NSF Project Pitch",
                    timeline="Weeks 1–2 (August 2026)",
                    detail="Submit executive overview (max 3 pages) outlining the technological innovation, technical hurdles, and market potential."
                ),
                ActionStep(
                    step=2,
                    title="Receive NSF Official Invitation",
                    timeline="Weeks 3–4 (Late August 2026)",
                    detail="NSF Program Director reviews pitch and issues formal invitation to submit the full Phase I proposal."
                ),
                ActionStep(
                    step=3,
                    title="Prepare Full Phase I Proposal",
                    timeline="Month 2 (September 2026)",
                    detail="Assemble 15-page project description, commercialization plan, biosketches, and letters of intent from hospital systems."
                ),
                ActionStep(
                    step=4,
                    title="Final Submission Window",
                    timeline="September 30, 2026",
                    detail="Upload complete application bundle to Research.gov prior to the 5:00 PM local submission deadline."
                )
            ]
        ),
        historical_awards=[
            HistoricalAward(
                id="aw-01",
                company="VigilantNurse AI",
                program="NSF SBIR Phase II",
                agency="NSF",
                amount="$1,000,000",
                year=2025,
                location="Salt Lake City, UT",
                project_title="Automated Nursing Handoff EHR Summarization Using Edge Transformers"
            ),
            HistoricalAward(
                id="aw-02",
                company="ClinicalSynapse Labs",
                program="NSF SBIR Phase I",
                agency="NSF",
                amount="$275,000",
                year=2025,
                location="Boulder, CO",
                project_title="Real-time Clinical Documentation Ingestion for Inpatient Care Staff"
            ),
            HistoricalAward(
                id="aw-03",
                company="MedScribe Automation",
                program="NSF SBIR Phase II",
                agency="NSF",
                amount="$1,250,000",
                year=2024,
                location="Provo, UT",
                project_title="Adaptive Ambient Speech Parsing in High-Acuity ICU Environments"
            ),
            HistoricalAward(
                id="aw-04",
                company="CareVector Health",
                program="NSF SBIR Phase I",
                agency="NSF",
                amount="$256,000",
                year=2024,
                location="Seattle, WA",
                project_title="Predictive Shift Workload Allocation for Hospital Nursing Units"
            )
        ]
    ),
    OpportunityItem(
        id="nih-hhs-sbir-2026",
        title="NIH / HHS — Commercialization of AI in Clinical Workflows & Nursing (Fast-Track)",
        program_code="RFA-NR-26-002",
        agency="National Institutes of Health (NINR / NLM)",
        agency_short="NIH / HHS",
        category="Translational Health",
        summary="Targeted non-dilutive grant program funding software innovations specifically aimed at reducing burnout, cognitive overload, and administrative documentation friction among clinical nursing staff.",
        potential_value="$400K–$2.2M",
        potential_value_min=400000.0,
        potential_value_max=2200000.0,
        deadline="October 15, 2026",
        days_left=62,
        closing_soon=True,
        target_domains=["Healthcare Technology", "Clinical Informatics", "Nursing", "Health Systems"],
        target_technologies=["Artificial Intelligence / SaaS", "EHR Integration", "Clinical NLP", "Decision Support"],
        base_eligibility_criteria=[
            "U.S. small business qualifying under federal SBIR guidelines",
            "Must demonstrate clinical relevance to NIH institute priority areas",
            "Human subjects research protocol compliance for hospital data"
        ],
        keywords=["nih", "hhs", "nursing", "clinical", "hospital", "administrative", "burnout", "ai", "documentation", "ehr"],
        historical_intelligence=HistoricalIntelligence(
            similar_companies_funded=24,
            total_historical_awards="$19.2M",
            median_award="$780K",
            local_recipients="5 Utah recipients",
            top_recipients_summary="Over $19M allocated to health informatics startups reducing clinician charting overhead since 2023."
        ),
        detailed_overview=DetailedOverview(
            why_should_i_care="NIH Fast-Track allows qualifying healthcare startups with pilot data to apply for Phase I and Phase II simultaneously, unlocking up to $2.2M in funding without waiting 12 months between phases.",
            what_could_make_me_ineligible=[
                "Failure to show human subject protection compliance when testing with live nurse workflow data",
                "Lack of a qualified Principal Investigator with health informatics or relevant domain background",
                "Non-compliance with HHS peer review standard scoring criteria"
            ],
            what_should_i_verify=[
                "Confirm whether your hospital pilot involves identifiable patient health information (HIPAA/PHI)",
                "Verify eRA Commons and ASSIST login credentials at least 4 weeks ahead of deadline",
                "Engage the NINR Scientific Program Officer for a pre-submission review call"
            ],
            what_should_i_do_next=[
                "Secure 2 letters of collaboration from nursing leadership at partner health systems",
                "Complete eRA Commons institutional registrations",
                "Schedule a 20-minute briefing with the NIH Program Officer in charge of RFA-NR-26-002"
            ],
            action_sequence=[
                ActionStep(
                    step=1,
                    title="eRA Commons & Grants.gov Setup",
                    timeline="August 2026",
                    detail="Finalize organization registrations in eRA Commons and assign PI role permissions."
                ),
                ActionStep(
                    step=2,
                    title="Specific Aims Page & PO Review",
                    timeline="Early September 2026",
                    detail="Write a concise 1-page Specific Aims document and send to NINR Program Officer for scoping alignment."
                ),
                ActionStep(
                    step=3,
                    title="Draft Fast-Track Research Strategy",
                    timeline="Mid-September 2026",
                    detail="Structure Phase I technical feasibility milestones and Phase II commercialization/clinical validation protocol."
                ),
                ActionStep(
                    step=4,
                    title="Submit via ASSIST Portal",
                    timeline="October 15, 2026",
                    detail="Complete federal electronic package submission before 5:00 PM EST."
                )
            ]
        ),
        historical_awards=[
            HistoricalAward(
                id="aw-05",
                company="NurseFlow Informatics",
                program="NIH Fast-Track SBIR",
                agency="NIH / NINR",
                amount="$1,850,000",
                year=2025,
                location="Salt Lake City, UT",
                project_title="Automated Nursing Shift Handoff Synthesis to Decrease Inpatient Medical Errors"
            ),
            HistoricalAward(
                id="aw-06",
                company="ChartAssist AI",
                program="NIH Phase I SBIR",
                agency="NIH / NLM",
                amount="$395,000",
                year=2025,
                location="San Francisco, CA",
                project_title="Context-Aware Clinical Event Extraction for Bedside Nursing Systems"
            ),
            HistoricalAward(
                id="aw-07",
                company="CarePulse Systems",
                program="NIH Phase II SBIR",
                agency="NIH / NINR",
                amount="$1,920,000",
                year=2024,
                location="Durham, NC",
                project_title="AI-Guided Bedside Triage and Task Prioritization for ICU Nurses"
            )
        ]
    ),
    OpportunityItem(
        id="arpa-h-sprint-2026",
        title="ARPA-H — Scalable Health Administration & Workforce Augmentation (Sprint)",
        program_code="ARPA-H-BAA-26-09",
        agency="Advanced Research Projects Agency for Health",
        agency_short="ARPA-H",
        category="Translational Health",
        summary="High-velocity milestone-driven awards for breakthrough technology platforms that radically eliminate administrative friction and restore clinical focus to healthcare providers.",
        potential_value="$500K–$3.0M",
        potential_value_min=500000.0,
        potential_value_max=3000000.0,
        deadline="September 18, 2026",
        days_left=35,
        closing_soon=True,
        target_domains=["Healthcare Technology", "Health Systems Transformation", "Clinical Workforce"],
        target_technologies=["Artificial Intelligence / SaaS", "Autonomous Agents", "Workflow Automation"],
        base_eligibility_criteria=[
            "U.S. entities including commercial startups, consortia, and university spinouts",
            "Must demonstrate 10x administrative friction reduction potential",
            "Ability to enter into Other Transaction Authority (OTA) agreements"
        ],
        keywords=["arpa-h", "workforce", "nursing", "administrative", "friction", "burnout", "hospitals", "automation", "ota"],
        historical_intelligence=HistoricalIntelligence(
            similar_companies_funded=9,
            total_historical_awards="$14.1M",
            median_award="$1.4M",
            local_recipients="1 Utah recipient",
            top_recipients_summary="9 health tech startups funded under ARPA-H BAA sprints with average cycle turnaround under 90 days."
        ),
        detailed_overview=DetailedOverview(
            why_should_i_care="ARPA-H operates like a venture-backed tech accelerator with non-dilutive government capital, issuing milestone contracts rapidly without standard grant bureaucratic lag.",
            what_could_make_me_ineligible=[
                "Proposals with only incremental 5–10% productivity gains (ARPA-H mandates 10x breakthrough metrics)",
                "Lack of technical architecture to handle multi-hospital federated EHR environments"
            ],
            what_should_i_verify=[
                "Confirm capability to demonstrate measurable nurse time savings in live or simulated hospital pilots",
                "Verify contract IP retention terms under Other Transaction Authority (OTA)"
            ],
            what_should_i_do_next=[
                "Submit a 4-page Executive Abstract to ARPA-H Health Systems Transformation Office",
                "Gather baseline nurse time-motion telemetry metrics from existing hospital deployments"
            ],
            action_sequence=[
                ActionStep(
                    step=1,
                    title="Executive Abstract Submission",
                    timeline="August 24, 2026",
                    detail="Submit high-impact abstract presenting current pilot baseline vs. breakthrough 10x reduction goals."
                ),
                ActionStep(
                    step=2,
                    title="ARPA-H Pitch Pitch Session",
                    timeline="September 5, 2026",
                    detail="Virtual 30-minute demonstration and Q&A with ARPA-H Program Managers."
                ),
                ActionStep(
                    step=3,
                    title="Negotiate Milestone SOW",
                    timeline="September 18, 2026",
                    detail="Finalize OTA milestone deliverables, data verification schedules, and funding tranches."
                )
            ]
        ),
        historical_awards=[
            HistoricalAward(
                id="aw-08",
                company="ReliefPoint Health",
                program="ARPA-H Sprint OTA",
                agency="ARPA-H",
                amount="$2,100,000",
                year=2025,
                location="Park City, UT",
                project_title="Cognitive Offloading Platform for Emergency Room Nursing Operations"
            ),
            HistoricalAward(
                id="aw-09",
                company="Synthetix BioAI",
                program="ARPA-H Sprint OTA",
                agency="ARPA-H",
                amount="$1,800,000",
                year=2024,
                location="Austin, TX",
                project_title="Automated Real-Time Nursing Care Pathway Validation Engine"
            )
        ]
    ),
    OpportunityItem(
        id="va-nurse-procure-2026",
        title="VA — Clinical Burden Reduction Pilot Procurement (VHA Innovation)",
        program_code="VA-VHA-IE-26-P01",
        agency="Veterans Health Administration",
        agency_short="VA / VHA",
        category="Procurement",
        summary="Direct pilot procurement contract with the Veterans Health Administration to test and deploy AI-assisted nursing workflow software inside VA Medical Centers.",
        potential_value="$350K–$1.2M",
        potential_value_min=350000.0,
        potential_value_max=1200000.0,
        deadline="November 12, 2026",
        days_left=90,
        closing_soon=True,
        target_domains=["Healthcare Technology", "Veterans Health", "Federal Procurement"],
        target_technologies=["Artificial Intelligence / SaaS", "Hospital Operations", "Clinical Software"],
        base_eligibility_criteria=[
            "Registered vendor on SAM.gov with commercial software product",
            "Ability to achieve VA Authority to Operate (ATO) cybersecurity accreditation"
        ],
        keywords=["va", "vha", "procurement", "hospital", "nursing", "pilot", "commercial", "enterprise"],
        historical_intelligence=HistoricalIntelligence(
            similar_companies_funded=12,
            total_historical_awards="$11.8M",
            median_award="$650K",
            local_recipients="2 Utah recipients (Salt Lake City VA pilot)",
            top_recipients_summary="12 pilot contracts awarded with 4 transitioning to full multi-year VHA enterprise master contracts."
        ),
        detailed_overview=DetailedOverview(
            why_should_i_care="The VA is the largest integrated healthcare network in the United States. Winning a pilot procurement contract establishes government revenue credibility and acts as a springboard for multi-million dollar defense and civilian contracts.",
            what_could_make_me_ineligible=[
                "Lack of cybersecurity compliance roadmap or willingness to achieve VA security accreditation",
                "Inability to integrate with Oracle Cerner / VistA EHR data exchange standards"
            ],
            what_should_i_verify=[
                "Confirm if small business set-aside clauses apply (VOSB/SDVOSB preference or general Small Business)",
                "Verify SAM.gov representations and certifications (FAR Part 12 Commercial Item)"
            ],
            what_should_i_do_next=[
                "Attend the VHA Innovation Ecosystem Industry Day webinar",
                "Schedule a discovery call with the Salt Lake City VA Medical Center innovation director"
            ],
            action_sequence=[
                ActionStep(
                    step=1,
                    title="Respond to Sources Sought Notice",
                    timeline="September 2026",
                    detail="Submit capability statement outlining software capabilities and hospital case studies."
                ),
                ActionStep(
                    step=2,
                    title="Security Architecture Audit",
                    timeline="October 2026",
                    detail="Draft VA ATO compliance readiness checklist for cloud architecture."
                ),
                ActionStep(
                    step=3,
                    title="Commercial Proposal Submission",
                    timeline="November 12, 2026",
                    detail="Submit fixed-price pilot proposal for a 6-month single-facility trial deployment."
                )
            ]
        ),
        historical_awards=[
            HistoricalAward(
                id="aw-10",
                company="CareOps Federal",
                program="VA Innovation Pilot",
                agency="VA / VHA",
                amount="$750,000",
                year=2025,
                location="Salt Lake City, UT",
                project_title="VA Bedside Nursing Workflow Telemetry and Automated Shift Reporting"
            )
        ]
    ),
    OpportunityItem(
        id="onc-healthit-2026",
        title="HHS / ONC — Health IT Interoperability & Workforce Innovation Grant",
        program_code="HHS-2026-ONC-WKF-03",
        agency="Office of the National Coordinator for Health Information Technology",
        agency_short="HHS / ONC",
        category="Consortium / Adjacent",
        summary="Cooperative agreement funding software platforms demonstrating FHIR API interoperability and reducing data entry duplication for inpatient nursing teams.",
        potential_value="$150K–$500K",
        potential_value_min=150000.0,
        potential_value_max=500000.0,
        deadline="October 28, 2026",
        days_left=75,
        closing_soon=False,
        target_domains=["Healthcare Technology", "Health IT Standards", "Interoperability"],
        target_technologies=["FHIR APIs", "Health Informatics", "SaaS"],
        base_eligibility_criteria=[
            "U.S. health IT vendor or developer",
            "Commitment to open FHIR API standards and interoperability compliance"
        ],
        keywords=["onc", "fhir", "interoperability", "ehr", "health it", "workforce", "hhs"],
        historical_intelligence=HistoricalIntelligence(
            similar_companies_funded=14,
            total_historical_awards="$5.2M",
            median_award="$320K",
            local_recipients="2 Utah recipients",
            top_recipients_summary="14 interoperability tools funded focusing on HL7 FHIR and EHR workflow reduction."
        ),
        detailed_overview=DetailedOverview(
            why_should_i_care="Ideal if you want to certify FHIR compliance while subsidizing your engineering costs for EHR integration modules.",
            what_could_make_me_ineligible=[
                "Proprietary closed systems that refuse to support public FHIR API endpoints",
                "Absence of partner hospital co-applicant or letter of commitment"
            ],
            what_should_i_verify=[
                "Check specific cost-share matching requirements (some ONC grants require 10% in-kind matching)"
            ],
            what_should_i_do_next=[
                "Review the ONC USCDI v5 data element specifications",
                "Assess whether your current hospital pilots utilize FHIR bulk data APIs"
            ],
            action_sequence=[
                ActionStep(
                    step=1,
                    title="Review FOA Technical Requirements",
                    timeline="September 2026",
                    detail="Ensure FHIR API architecture aligns with ONC HTI-1 final rule specifications."
                ),
                ActionStep(
                    step=2,
                    title="Partner Endorsement Letters",
                    timeline="October 10, 2026",
                    detail="Secure interoperability validation letters from hospital IT leadership."
                ),
                ActionStep(
                    step=3,
                    title="Grant Submission",
                    timeline="October 28, 2026",
                    detail="Submit application via Grants.gov."
                )
            ]
        ),
        historical_awards=[
            HistoricalAward(
                id="aw-11",
                company="BridgeHealth FHIR",
                program="ONC Workforce Grant",
                agency="HHS / ONC",
                amount="$450,000",
                year=2024,
                location="Denver, CO",
                project_title="Smart On FHIR Nursing Hand-Off Plug-in for Epic & Cerner Systems"
            )
        ]
    ),
    OpportunityItem(
        id="dod-dha-sbir-2026",
        title="DoD / DHA — Defense Health Agency Military Hospital Nurse Efficiency SBIR",
        program_code="DOD-SBIR-26.2-DHA04",
        agency="Defense Health Agency / Dept of Defense",
        agency_short="DoD / DHA",
        category="Defense SBIR",
        summary="Dual-use SBIR opportunity seeking commercial clinical software to optimize nurse workload distribution and automated clinical logging in military treatment facilities (MTFs).",
        potential_value="$200K–$1.8M",
        potential_value_min=200000.0,
        potential_value_max=1800000.0,
        deadline="August 29, 2026",
        days_left=15,
        closing_soon=True,
        target_domains=["Defense Health", "Military Treatment Facilities", "Healthcare Operations"],
        target_technologies=["Artificial Intelligence / SaaS", "Dual-Use Software", "Clinical Workflows"],
        base_eligibility_criteria=[
            "U.S. small business meeting DoD SBIR criteria",
            "Demonstrated dual-use commercial & defense market roadmap"
        ],
        keywords=["dod", "dha", "military", "hospital", "defense", "nursing", "workload", "sbir", "dual-use"],
        historical_intelligence=HistoricalIntelligence(
            similar_companies_funded=8,
            total_historical_awards="$7.6M",
            median_award="$550K",
            local_recipients="1 Utah recipient",
            top_recipients_summary="8 dual-use health AI companies awarded Phase I contracts over past 2 years."
        ),
        detailed_overview=DetailedOverview(
            why_should_i_care="Defense Health Agency manages over 50 military hospitals globally and is actively seeking dual-use commercial tech with rapid transition potential.",
            what_could_make_me_ineligible=[
                "Foreign ownership or lack of US citizen personnel on key technical roles",
                "Inability to submit proposal through Defense SBIR/STTR Innovation Portal (DSIP) before cutoff"
            ],
            what_should_i_verify=[
                "Verify your account on DSIP (Defense SBIR/STTR Innovation Portal)",
                "Check military hospital dual-use requirements in Section 3 of topic description"
            ],
            what_should_i_do_next=[
                "If planning to submit for this cycle, immediately prepare the 5-page DSIP technical volume",
                "Alternatively target the 26.3 cycle if additional preparation time is required"
            ],
            action_sequence=[
                ActionStep(
                    step=1,
                    title="DSIP Portal Registration",
                    timeline="Immediate",
                    detail="Register company profile in DSIP and link active SAM.gov UEI."
                ),
                ActionStep(
                    step=2,
                    title="Technical Volume Writing",
                    timeline="August 20–25, 2026",
                    detail="Draft 5-page defense and commercial application statement."
                ),
                ActionStep(
                    step=3,
                    title="DSIP Upload & Confirmation",
                    timeline="August 29, 2026",
                    detail="Submit through DSIP by 12:00 PM EST deadline."
                )
            ]
        ),
        historical_awards=[
            HistoricalAward(
                id="aw-12",
                company="TacticalHealth AI",
                program="DoD DHA Phase I SBIR",
                agency="DoD / DHA",
                amount="$250,000",
                year=2025,
                location="San Antonio, TX",
                project_title="Automated Nursing Workload Balancing for Military Treatment Facilities"
            )
        ]
    ),
    OpportunityItem(
        id="doe-hpc-energy-2026",
        title="DOE — High Performance Computing & Clean Energy Infrastructure Consortium",
        program_code="DE-FOA-0003189",
        agency="Department of Energy (Office of Science)",
        agency_short="DOE",
        category="Consortium / Adjacent",
        summary="Consortium grant targeting exascale computing algorithms for power grid modeling, nuclear simulation, and energy storage chemistry.",
        potential_value="$1.0M–$5.0M",
        potential_value_min=1000000.0,
        potential_value_max=5000000.0,
        deadline="December 15, 2026",
        days_left=123,
        closing_soon=False,
        target_domains=["Clean Energy", "Power Grid", "Computational Physics", "Nuclear"],
        target_technologies=["Exascale HPC", "Quantum Chemistry", "Grid Simulation"],
        base_eligibility_criteria=[
            "Consortia involving National Laboratories, universities, and commercial supercomputing firms"
        ],
        keywords=["energy", "grid", "supercomputing", "doe", "physics", "power", "chemistry"],
        historical_intelligence=HistoricalIntelligence(
            similar_companies_funded=3,
            total_historical_awards="$12.0M",
            median_award="$3.5M",
            local_recipients="0 healthcare startups funded under this topic",
            top_recipients_summary="Exclusively allocated to national energy research institutes and computational physics teams."
        ),
        detailed_overview=DetailedOverview(
            why_should_i_care="This opportunity is listed to demonstrate filtering accuracy. While the dollar amount is large ($5M), the strategic and technical alignment with healthcare workflow software is minimal.",
            what_could_make_me_ineligible=[
                "Lack of clean energy or computational physics research methodology",
                "Lack of formal DOE National Laboratory co-principal investigator"
            ],
            what_should_i_verify=[
                "We strongly recommend prioritizing NSF, NIH, and ARPA-H instead of allocating resources to this solicitation"
            ],
            what_should_i_do_next=[
                "Pass on this solicitation to keep team focused on clinical health tech opportunities"
            ],
            action_sequence=[
                ActionStep(
                    step=1,
                    title="Opportunity Deprioritized",
                    timeline="N/A",
                    detail="Excluded from recommended 90-day action pipeline to protect founder bandwidth."
                )
            ]
        ),
        historical_awards=[
            HistoricalAward(
                id="aw-13",
                company="GridScale Quantum Labs",
                program="DOE Advanced Computing Grant",
                agency="DOE",
                amount="$4,200,000",
                year=2024,
                location="Oak Ridge, TN",
                project_title="Exascale Simulation of Power Grid Micro-Fluctuations"
            )
        ]
    ),
]


def get_all_opportunities() -> List[OpportunityItem]:
    """
    Retrieve all government funding opportunities.
    Easy abstraction to replace with MongoDB query later:
        return [OpportunityItem(**doc) for doc in db.opportunities.find()]
    """
    return MOCK_OPPORTUNITIES


def get_opportunity_by_id(opportunity_id: str) -> Optional[OpportunityItem]:
    """
    Retrieve a specific opportunity by its unique ID.
    Easy abstraction to replace with MongoDB query later:
        doc = db.opportunities.find_one({"id": opportunity_id})
        return OpportunityItem(**doc) if doc else None
    """
    for opp in MOCK_OPPORTUNITIES:
        if opp.id == opportunity_id:
            return opp
    return None
