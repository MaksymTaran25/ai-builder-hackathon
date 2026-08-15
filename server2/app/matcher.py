"""
Weighted Matching & Scoring Engine
==================================
Implements a multi-factor weighted scoring algorithm evaluating startup characteristics
against federal opportunity requirements, producing normalized match scores (0.0 to 1.0),
fit tiers, and specific advisor rationale.
"""

import re
from typing import List, Tuple, Dict, Any, Optional
from .models import (
    StartupProfile,
    Opportunity,
    MatchResultItem,
    QuerySummary,
    OpportunityQueryResponse,
)
from .llm import BaseLLMClient, get_llm_client


# -----------------------------------------------------------------------------
# Configurable Factor Weights (Must sum to 1.0)
# -----------------------------------------------------------------------------

DEFAULT_WEIGHTS: Dict[str, float] = {
    "industry": 0.25,
    "technology": 0.25,
    "rd_alignment": 0.15,
    "size_eligibility": 0.10,
    "funding_alignment": 0.10,
    "customer_alignment": 0.10,
    "product_maturity": 0.05,
}


def _tokenize(text: str) -> List[str]:
    """Helper to extract lowercased alphanumeric tokens from text."""
    if not text:
        return []
    return re.findall(r"\b[a-z0-9\-]+\b", text.lower())


def _calculate_overlap_ratio(source_items: List[str], target_items: List[str]) -> float:
    """Calculates keyword/token overlap similarity between two lists."""
    if not target_items:
        return 0.5  # Neutral if opportunity has no target constraints
    if not source_items:
        return 0.0

    source_tokens = set()
    for item in source_items:
        source_tokens.update(_tokenize(item))

    target_tokens = set()
    for item in target_items:
        target_tokens.update(_tokenize(item))

    if not target_tokens:
        return 0.5

    intersection = source_tokens.intersection(target_tokens)
    return min(len(intersection) / len(target_tokens), 1.0)


def evaluate_single_opportunity(
    profile: StartupProfile,
    opp: Opportunity,
    weights: Dict[str, float],
    normalized_keywords: List[str]
) -> Tuple[float, str, List[str], List[str], List[str]]:
    """
    Computes a weighted match score (0.0 to 1.0), fit tier, and generated explanations
    for a single candidate opportunity.
    """
    why_match: List[str] = []
    potential_concerns: List[str] = []
    next_steps: List[str] = []

    # Aggregate all profile text tokens
    profile_all_text = " ".join([
        profile.company_name or "",
        profile.description or "",
        " ".join(profile.industry),
        " ".join(profile.technology),
        " ".join(profile.rd_activities),
        " ".join(profile.target_customers),
        " ".join(profile.use_of_funds),
        profile.location or "",
        " ".join(normalized_keywords),
    ]).lower()

    # 1. Industry Alignment (Weight: 0.25)
    industry_overlap = _calculate_overlap_ratio(profile.industry + normalized_keywords, opp.target_industries)
    text_industry_matches = [ind for ind in opp.target_industries if any(w in profile_all_text for w in _tokenize(ind))]
    if text_industry_matches:
        industry_score = max(industry_overlap, min(len(text_industry_matches) / max(len(opp.target_industries), 1), 1.0))
    else:
        industry_score = industry_overlap

    if industry_score >= 0.4:
        matched_str = ", ".join(text_industry_matches[:3]) if text_industry_matches else "relevant sector"
        why_match.append(f"Strong industry alignment with {opp.agency_short} priority areas ({matched_str})")
    elif industry_score < 0.2:
        potential_concerns.append(f"Opportunity focuses primarily on {', '.join(opp.target_industries[:2])} domain")

    # 2. Technology Alignment (Weight: 0.25)
    tech_overlap = _calculate_overlap_ratio(profile.technology + normalized_keywords, opp.target_technologies)
    text_tech_matches = [tech for tech in opp.target_technologies if any(w in profile_all_text for w in _tokenize(tech))]
    if text_tech_matches:
        tech_score = max(tech_overlap, min(len(text_tech_matches) / max(len(opp.target_technologies), 1), 1.0))
    else:
        tech_score = tech_overlap

    if tech_score >= 0.35:
        matched_tech_str = ", ".join(text_tech_matches[:3]) if text_tech_matches else "core software/deep tech"
        why_match.append(f"Technical stack matches solicitation requirements ({matched_tech_str})")
    elif tech_score < 0.2:
        potential_concerns.append(f"Requires specialized technology focus ({', '.join(opp.target_technologies[:2])})")

    # 3. R&D Alignment (Weight: 0.15)
    has_rd = bool(profile.rd_activities) or any(
        w in profile_all_text for w in [
            "r&d", "development", "research", "algorithm", "prototype", "pilot",
            "analytics", "sensor", "telemetry", "innovation", "engineering", "system"
        ]
    )
    if opp.requires_active_rd:
        if has_rd:
            rd_score = 1.0
            why_match.append("Active technical R&D milestones satisfy federal grant unproven innovation criteria")
        else:
            rd_score = 0.6
            potential_concerns.append("Solicitation mandates unproven technical research and scientific hurdle validation")
    else:
        rd_score = 0.9  # Procurement or non-R&D grants don't penalize

    # 4. Company Size & Eligibility (Weight: 0.10)
    emp = profile.employees or 15
    if opp.max_employees_limit:
        if emp <= opp.max_employees_limit:
            size_score = 1.0
            why_match.append(f"Small business qualifying criteria satisfied ({emp} FTE <= {opp.max_employees_limit} cap)")
        else:
            size_score = 0.0
            potential_concerns.append(f"Headcount ({emp} FTE) exceeds program cap ({opp.max_employees_limit})")
    else:
        size_score = 1.0

    # 5. Funding Needs Alignment (Weight: 0.10)
    funding_score = 0.8  # Default high-neutral overlap
    needed_min = float(profile.funding_needed_min) if profile.funding_needed_min else None
    needed_max = float(profile.funding_needed_max) if profile.funding_needed_max else None

    if needed_min is not None and needed_max is not None:
        # Check if ranges overlap
        if opp.funding_max >= needed_min and opp.funding_min <= needed_max:
            funding_score = 1.0
            why_match.append(f"Award size (${opp.funding_min:,}–${opp.funding_max:,}) fits requested capital range (${int(needed_min):,}–${int(needed_max):,})")
        elif opp.funding_max < needed_min:
            funding_score = 0.5
            potential_concerns.append(f"Maximum award (${opp.funding_max:,}) is below desired minimum capital (${int(needed_min):,})")
        else:
            funding_score = 0.7
    else:
        why_match.append(f"Non-dilutive funding pool (${opp.funding_min:,}–${opp.funding_max:,}) matches typical early-stage needs")

    # 6. Customer Persona / Domain Alignment (Weight: 0.10)
    customer_overlap = _calculate_overlap_ratio(profile.target_customers, opp.target_customers)
    text_customer_matches = [cust for cust in opp.target_customers if any(w in profile_all_text for w in _tokenize(cust))]
    if text_customer_matches:
        customer_score = max(customer_overlap, min(len(text_customer_matches) / max(len(opp.target_customers), 1), 1.0))
        why_match.append(f"Target customer segment aligns with agency users ({', '.join(text_customer_matches[:2])})")
    else:
        customer_score = 0.5

    # 7. Product Maturity & Stage (Weight: 0.05)
    maturity = (profile.product_maturity or "commercial").lower()
    if opp.opportunity_type in ["procurement", "ota_contract"]:
        if "commercial" in maturity or "pilot" in maturity:
            stage_score = 1.0
            why_match.append("Commercial/pilot maturity is well-suited for federal procurement and OTA transition")
        else:
            stage_score = 0.5
            potential_concerns.append("Procurement contracts prefer working commercial solutions over early prototypes")
    else:
        stage_score = 0.9

    # Local State Precedent Bonus
    if profile.location and opp.local_recipients_note and profile.location.lower() in opp.local_recipients_note.lower():
        why_match.append(f"State precedent demonstrated ({opp.local_recipients_note})")

    # Calculate Weighted Total Score
    raw_score = (
        industry_score * weights["industry"]
        + tech_score * weights["technology"]
        + rd_score * weights["rd_alignment"]
        + size_score * weights["size_eligibility"]
        + funding_score * weights["funding_alignment"]
        + customer_score * weights["customer_alignment"]
        + stage_score * weights["product_maturity"]
    )

    # Domain mismatch hard penalty (e.g. Nuclear/Livestock for AI healthcare)
    is_domain_mismatch = (
        ("nuclear" in opp.target_industries or "dairy" in opp.target_industries or "plasma physics" in opp.target_industries)
        and not any(w in profile_all_text for w in ["nuclear", "dairy", "farming", "plasma", "livestock"])
    )
    if is_domain_mismatch:
        raw_score = min(raw_score, 0.28)
        potential_concerns.append("Severe domain mismatch: solicitation is dedicated exclusively to unrelated physical/agricultural science")

    # Round to 2 decimal places and clamp
    score = round(max(min(raw_score, 0.98), 0.15), 2)

    # Determine Fit Tier
    if score >= 0.80:
        fit_tier = "likely_fit"
    elif score >= 0.65:
        fit_tier = "potential_fit"
    elif score >= 0.45:
        fit_tier = "adjacent"
    else:
        fit_tier = "unlikely"

    # Default fallback bullets if empty
    if not why_match:
        why_match.append("Startup profile meets baseline federal program qualification parameters")
    if not potential_concerns:
        potential_concerns.append("Verify specific annual solicitation instructions and deadlines on SAM.gov")

    # Standard next steps customized by opportunity type
    if opp.opportunity_type == "sbir_grant":
        next_steps = [
            f"Review official {opp.agency_short} solicitation topic guidance",
            "Verify active organization registration in SAM.gov and SBIR.gov",
            "Prepare 3-page Project Pitch / Specific Aims summary for Program Manager review",
            f"Assemble Phase I technical proposal before {opp.deadline}"
        ]
    elif opp.opportunity_type == "procurement":
        next_steps = [
            "Review Sources Sought Notice and Statement of Work specifications",
            "Audit cloud cybersecurity compliance (FedRAMP / ATO roadmap readiness)",
            "Schedule discovery briefing with regional agency innovation office",
            f"Submit commercial capability statement prior to {opp.deadline}"
        ]
    elif opp.opportunity_type == "ota_contract":
        next_steps = [
            "Draft 4-page Executive Abstract detailing 10x performance improvement",
            "Prepare prototype demonstration telemetry or hospital pilot metrics",
            "Engage ARPA-H / DARPA Program Manager during open office hours",
            f"Submit sprint proposal package before {opp.deadline}"
        ]
    else:
        next_steps = [
            f"Examine {opp.program} eligibility guidelines in Grants.gov",
            "Secure letters of collaboration or support from industry/clinical partners",
            f"Submit application bundle before {opp.deadline}"
        ]

    return score, fit_tier, why_match, potential_concerns, next_steps


def match_and_rank_opportunities(
    profile: StartupProfile,
    candidates: List[Opportunity],
    llm_client: Optional[BaseLLMClient] = None,
    weights: Optional[Dict[str, float]] = None
) -> OpportunityQueryResponse:
    """
    Main matching pipeline orchestrating:
    1. Semantic concept extraction (via LLM or deterministic fallback).
    2. Weighted scoring and rationale generation across candidate opportunities.
    3. Descending sort by match_score.
    4. Metric summary compilation.
    """
    client = llm_client or get_llm_client()
    active_weights = weights or DEFAULT_WEIGHTS

    # Step 1: Normalize profile concepts
    normalization_result = client.normalize_profile(profile)
    normalized_keywords = normalization_result.get("normalized_keywords", [])

    # Step 2: Score all candidate opportunities
    results: List[MatchResultItem] = []
    agencies_set = set()
    total_funding_min = 0
    total_funding_max = 0

    for opp in candidates:
        score, fit_tier, why_match, potential_concerns, next_steps = evaluate_single_opportunity(
            profile=profile,
            opp=opp,
            weights=active_weights,
            normalized_keywords=normalized_keywords
        )

        # Optional LLM explanation refinement
        enriched = client.enrich_explanation(
            profile=profile,
            opportunity=opp,
            base_why=why_match,
            base_concerns=potential_concerns,
            base_next_steps=next_steps
        )

        results.append(
            MatchResultItem(
                id=opp.id,
                program=opp.program,
                agency=opp.agency,
                opportunity_type=opp.opportunity_type,
                match_score=score,
                fit_tier=fit_tier,
                funding_min=opp.funding_min,
                funding_max=opp.funding_max,
                deadline=opp.deadline,
                why_match=enriched.get("why_match", why_match),
                potential_concerns=enriched.get("potential_concerns", potential_concerns),
                next_steps=enriched.get("next_steps", next_steps),
            )
        )

        agencies_set.add(opp.agency_short)
        total_funding_min += opp.funding_min
        total_funding_max += opp.funding_max

    # Step 3: Strictly sort in descending order of match_score
    results.sort(key=lambda item: item.match_score, reverse=True)

    # Step 4: Summary calculations
    summary = QuerySummary(
        opportunity_count=len(results),
        agencies=sorted(list(agencies_set)),
        potential_funding_min=total_funding_min,
        potential_funding_max=total_funding_max,
    )

    return OpportunityQueryResponse(
        opportunities=results,
        summary=summary
    )
