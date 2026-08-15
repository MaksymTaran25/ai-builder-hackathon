"""GraphQL API (strawberry) — mirrors the REST surface at /graphql.

Field names stay snake_case (auto_camel_case off) so the frontend types are
identical across REST and GraphQL.
"""
from __future__ import annotations

from typing import Optional

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON
from strawberry.schema.config import StrawberryConfig

from . import models
from .services import llm, matching, person as person_svc, sbir, store




@strawberry.experimental.pydantic.type(model=models.StartupProfile, all_fields=True)
class StartupProfile:
    pass


@strawberry.experimental.pydantic.input(model=models.StartupProfile, all_fields=True)
class StartupProfileInput:
    pass


@strawberry.experimental.pydantic.type(model=models.FollowUpQuestion, all_fields=True)
class FollowUpQuestion:
    pass


@strawberry.experimental.pydantic.type(model=models.Explanation, all_fields=True)
class Explanation:
    pass


@strawberry.type
class SampleRecipient:
    name: Optional[str] = None
    agency: Optional[str] = None
    program: Optional[str] = None
    amount: Optional[float] = None
    year: Optional[int] = None


@strawberry.type
class HistoricalStats:
    similar_companies: int
    total_awarded_usd: float
    median_award_usd: float
    in_state_recipients: int
    sample_recipients: list[SampleRecipient]

    @staticmethod
    def from_model(m: models.HistoricalStats) -> "HistoricalStats":
        return HistoricalStats(
            similar_companies=m.similar_companies,
            total_awarded_usd=m.total_awarded_usd,
            median_award_usd=m.median_award_usd,
            in_state_recipients=m.in_state_recipients,
            sample_recipients=[
                SampleRecipient(
                    name=r.get("name"), agency=r.get("agency"), program=r.get("program"),
                    amount=r.get("amount"), year=r.get("year"),
                )
                for r in m.sample_recipients
            ],
        )


@strawberry.type
class Opportunity:
    source: str
    source_id: str
    title: str
    agency: str
    agency_code: str
    program: str
    status: str
    cfda: list[str]
    open_date: Optional[str]
    close_date: Optional[str]
    award_floor_usd: Optional[float]
    award_ceiling_usd: Optional[float]
    estimated_total_funding_usd: Optional[float]
    expected_awards: Optional[int]
    cost_sharing: Optional[bool]
    eligibility_flag: Optional[str]
    eligible_applicants: list[str]
    url: Optional[str]
    summary: str
    score: float
    fit_tier: str  # REST-parity string values: likely_fit | potential_fit | adjacent | not_a_fit
    llm_reason: str
    explanation: Optional[Explanation]
    history: Optional[HistoricalStats]

    @staticmethod
    def from_model(o: models.Opportunity) -> "Opportunity":
        return Opportunity(
            source=o.source, source_id=o.source_id, title=o.title, agency=o.agency,
            agency_code=o.agency_code, program=o.program, status=o.status, cfda=o.cfda,
            open_date=o.open_date, close_date=o.close_date,
            award_floor_usd=o.award_floor_usd, award_ceiling_usd=o.award_ceiling_usd,
            estimated_total_funding_usd=o.estimated_total_funding_usd,
            expected_awards=o.expected_awards, cost_sharing=o.cost_sharing,
            eligibility_flag=o.eligibility_flag, eligible_applicants=o.eligible_applicants,
            url=o.url, summary=o.summary, score=o.score, fit_tier=o.fit_tier.value,
            llm_reason=o.llm_reason,
            explanation=Explanation.from_pydantic(o.explanation) if o.explanation else None,
            history=HistoricalStats.from_model(o.history) if o.history else None,
        )


@strawberry.experimental.pydantic.type(model=models.MatchSummary, all_fields=True)
class MatchSummary:
    pass


@strawberry.experimental.pydantic.type(model=models.SimilarCompany, all_fields=True)
class SimilarCompany:
    pass


@strawberry.experimental.pydantic.type(model=models.AgencyMapEntry, all_fields=True)
class AgencyMapEntry:
    pass


@strawberry.type
class ExtractResult:
    profile: StartupProfile
    followups: list[FollowUpQuestion]


@strawberry.type
class MatchResult:
    summary: MatchSummary
    opportunities: list[Opportunity]
    similar_companies: list[SimilarCompany]
    agency_map: list[AgencyMapEntry]


@strawberry.type
class SbirAward:
    company: str
    title: str
    agency: str
    phase: str
    program: str
    award_year: int
    award_amount: float
    state: str
    city: str


@strawberry.type
class Query:
    # ---- warehouse reads: any process can query the stored government data ----

    @strawberry.field
    async def stored_opportunities(self, search: Optional[str] = None, limit: int = 20) -> JSON:
        """Grants.gov opportunities previously fetched + enriched (from MongoDB)."""
        import asyncio

        return await asyncio.to_thread(store.stored_opportunities, search, min(limit, 200))

    @strawberry.field
    async def sbir_awards(
        self, search: str, state: Optional[str] = None, limit: int = 20
    ) -> list[SbirAward]:
        """Full-text search over the 39.8K-award SBIR corpus (from MongoDB)."""
        import asyncio

        rows = await asyncio.to_thread(sbir.search_awards, search, state, min(limit, 100))
        return [
            SbirAward(
                company=r.get("company") or "", title=r.get("title") or "",
                agency=r.get("agency") or "", phase=r.get("phase") or "",
                program=r.get("program") or "", award_year=r.get("award_year") or 0,
                award_amount=r.get("award_amount") or 0, state=r.get("state") or "",
                city=r.get("city") or "",
            )
            for r in rows[:limit]
        ]

    @strawberry.field
    async def match_runs(self, limit: int = 5) -> JSON:
        """Recent profile->map runs with their results (from MongoDB)."""
        import asyncio

        return await asyncio.to_thread(store.stored_match_runs, min(limit, 50))

    @strawberry.field
    async def award_history(self, limit: int = 20) -> JSON:
        """Cached USAspending recipient stats per CFDA program set (from MongoDB)."""
        import asyncio

        return await asyncio.to_thread(store.stored_award_history, min(limit, 100))

    @strawberry.field
    async def match_person(self, person: JSON) -> JSON:
        """JSON in -> JSON out for external processes: accepts a person/company
        document in any reasonable shape, normalizes it, runs the full matching
        pipeline against the database, returns the complete result as JSON."""
        profile = await person_svc.to_profile(dict(person))
        result = await matching.run_match(profile)
        out = result.model_dump()
        out["normalized_profile"] = profile.model_dump()
        return out

    # ---- live pipeline ----

    @strawberry.field
    async def extract_profile(self, text: str) -> ExtractResult:
        profile, followups = await llm.extract_profile(text)
        return ExtractResult(
            profile=StartupProfile.from_pydantic(profile),
            followups=[FollowUpQuestion.from_pydantic(f) for f in followups],
        )

    @strawberry.field
    async def match(self, profile: StartupProfileInput) -> MatchResult:
        result = await matching.run_match(profile.to_pydantic())
        return MatchResult(
            summary=MatchSummary.from_pydantic(result.summary),
            opportunities=[Opportunity.from_model(o) for o in result.opportunities],
            similar_companies=[SimilarCompany.from_pydantic(c) for c in result.similar_companies],
            agency_map=[AgencyMapEntry.from_pydantic(a) for a in result.agency_map],
        )


schema = strawberry.Schema(query=Query, config=StrawberryConfig(auto_camel_case=False))
router = GraphQLRouter(schema, path="/graphql")
