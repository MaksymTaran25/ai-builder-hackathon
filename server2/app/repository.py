"""
Repository Abstraction Layer
============================
Defines the abstract interface for querying government funding opportunities,
allowing the matching engine and FastAPI routes to remain completely decoupled
from the underlying storage engine (Mock data today, MongoDB tomorrow).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import os
import logging

from .models import Opportunity, StartupProfile
from .mock_data import MOCK_OPPORTUNITIES

logger = logging.getLogger("server2.repository")


class OpportunityRepository(ABC):
    """
    Abstract Base Class for government opportunity data access.
    All data store implementations (Mock, MongoDB, PostgreSQL) must implement this interface.
    """

    @abstractmethod
    def search_candidates(self, profile: StartupProfile) -> List[Opportunity]:
        """
        Retrieves candidate opportunities from the database that could potentially
        match the startup profile. Can apply initial broad database-level filters.
        """
        pass

    @abstractmethod
    def get_all_opportunities(self) -> List[Opportunity]:
        """
        Retrieves all active government funding opportunities in the store.
        """
        pass

    @abstractmethod
    def get_opportunity_by_id(self, opportunity_id: str) -> Optional[Opportunity]:
        """
        Retrieves a single opportunity by unique identifier.
        """
        pass


class MockOpportunityRepository(OpportunityRepository):
    """
    In-memory mock repository implementation using synthetic hackathon demo data.
    """

    def __init__(self, data: Optional[List[Opportunity]] = None):
        self._opportunities = data if data is not None else MOCK_OPPORTUNITIES
        logger.info("Initialized MockOpportunityRepository with %d opportunities.", len(self._opportunities))

    def search_candidates(self, profile: StartupProfile) -> List[Opportunity]:
        """
        Returns active opportunities from in-memory collection.
        Performs preliminary hard-filter checks where applicable (e.g. employee size caps).
        """
        candidates: List[Opportunity] = []
        for opp in self._opportunities:
            if not opp.is_active:
                continue

            # Elimination check 1: Small business employee cap
            # If the opportunity has a strict employee cap and the profile explicitly exceeds it
            if opp.max_employees_limit and profile.employees and profile.employees > opp.max_employees_limit:
                logger.debug("Skipping %s: startup employees (%d) exceeds limit (%d)", opp.id, profile.employees, opp.max_employees_limit)
                continue

            candidates.append(opp)

        return candidates

    def get_all_opportunities(self) -> List[Opportunity]:
        """Returns all opportunities in the mock store."""
        return [opp for opp in self._opportunities if opp.is_active]

    def get_opportunity_by_id(self, opportunity_id: str) -> Optional[Opportunity]:
        """Looks up an opportunity by ID."""
        for opp in self._opportunities:
            if opp.id == opportunity_id:
                return opp
        return None


# -----------------------------------------------------------------------------
# Blueprint for Future MongoDB Implementation
# -----------------------------------------------------------------------------

class MongoOpportunityRepository(OpportunityRepository):
    """Read-only repository over the GovMatch warehouse (Server 1's MongoDB).

    Server 1 harvests every posted + forecasted Grants.gov opportunity nightly and
    enriches each with synopsis, award range, deadline and parsed applicant-type
    eligibility. This adapter maps those documents onto Server 2's Opportunity model,
    so the matching engine runs unchanged on ~1,700 real federal programs.
    """

    def __init__(self, uri: str, db_name: str, collection_name: str):
        from pymongo import MongoClient

        self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        self.client.admin.command("ping")          # fail fast so the factory can fall back
        self.collection = self.client[db_name][collection_name]
        n = self.collection.estimated_document_count()
        logger.info("MongoOpportunityRepository connected: %s.%s (%d documents)", db_name, collection_name, n)

    # ---- mapping -------------------------------------------------------------

    @staticmethod
    def _money(v) -> int:
        try:
            return int(float(v or 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _days_left(close: Optional[str]) -> int:
        """close_date is MM/DD/YYYY in the warehouse; no date means rolling."""
        import re
        from datetime import date

        if not close:
            return 365
        m = re.match(r"(\d{2})/(\d{2})/(\d{4})", str(close))
        if not m:
            return 365
        try:
            d = date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError:
            return 365
        return max((d - date.today()).days, 0)

    @staticmethod
    def _short_agency(agency: str) -> str:
        table = {
            "National Institutes of Health": "NIH", "Department of Health and Human Services": "HHS",
            "U.S. National Science Foundation": "NSF", "National Science Foundation": "NSF",
            "Department of Defense": "DoD", "Department of War": "DoW", "Department of Energy": "DOE",
            "Environmental Protection Agency": "EPA", "Department of Homeland Security": "DHS",
            "National Aeronautics and Space Administration": "NASA", "Bureau of Reclamation": "USBR",
            "Department of Agriculture": "USDA", "Department of Commerce": "DOC",
        }
        for full, short in table.items():
            if (agency or "").startswith(full):
                return short
        words = [w for w in (agency or "").split() if w[:1].isupper() and w.lower() not in ("of", "the", "and", "for")]
        return "".join(w[0] for w in words)[:6] or (agency or "")[:6]

    @classmethod
    def _to_opportunity(cls, doc: dict) -> Optional[Opportunity]:
        """Warehouse document -> Server 2 Opportunity. Returns None if unusable."""
        title = (doc.get("title") or "").strip()
        if not title:
            return None
        agency = doc.get("agency") or ""
        summary = (doc.get("summary") or "").strip()
        days = cls._days_left(doc.get("close_date"))
        flag = doc.get("eligibility_flag")
        domains = doc.get("domains") or []
        text = f"{title} {summary}".lower()

        # keywords for the matcher: domain tags + salient title words
        stop = {"the", "and", "for", "with", "from", "this", "that", "program", "grant", "funding",
                "opportunity", "notice", "announcement", "federal", "national", "research", "of"}
        title_words = [w.strip("():,.-").lower() for w in title.split()]
        keywords = domains + [w for w in title_words if len(w) > 4 and w not in stop][:12]

        return Opportunity(
            id=doc.get("source_id") or title[:40],
            # `program` identifies the program the way her mocks did (agency + number),
            # not just the bare Grants.gov opportunity number.
            program=" ".join(x for x in [cls._short_agency(agency), doc.get("program") or ""] if x).strip(),
            agency=agency,
            agency_short=cls._short_agency(agency),
            opportunity_type="SBIR/STTR" if "sbir" in text or "sttr" in text else "Federal Grant",
            title=title,
            summary=summary[:1200] or title,
            funding_min=cls._money(doc.get("award_floor_usd")),
            funding_max=cls._money(doc.get("award_ceiling_usd")),
            deadline=doc.get("close_date") or "Rolling / see listing",
            days_left=days,
            is_active=not doc.get("archived_at"),
            target_industries=_industries_for(text, domains),
            target_technologies=_technologies_for(text, domains),
            target_customers=_customers_for(text),
            keywords=list(dict.fromkeys(keywords)),
            max_employees_limit=500,
            requires_us_ownership=True,
            requires_active_rd="research" in text or "r&d" in text or "development" in text,
            similar_companies_funded=int((doc.get("history") or {}).get("similar_companies") or 0),
            total_historical_funding=_usd((doc.get("history") or {}).get("total_awarded_usd")),
            median_award=_usd((doc.get("history") or {}).get("median_award_usd")),
            local_recipients_note=(
                f"{(doc.get('history') or {}).get('in_state_recipients', 0)} in-state recipients"
                if doc.get("history") else ""
            ),
            is_demo_data=False,          # real federal data, not synthetic
        )

    # ---- interface -----------------------------------------------------------

    def _query(self, profile: Optional[StartupProfile] = None) -> dict:
        q: dict = {"archived_at": {"$exists": False}, "source": "grants_gov"}
        # programs whose official applicant list excludes for-profits are not candidates
        q["eligibility_flag"] = {"$in": ["ok", "verify", None]}
        return q

    def search_candidates(self, profile: StartupProfile, limit: int = 150) -> List[Opportunity]:
        """Database-level relevance prefilter: full-text search over the warehouse using
        the profile's own words, so the matching engine scores a relevant shortlist
        instead of all ~1,700 programs."""
        terms = _profile_terms(profile)
        try:
            q = self._query(profile)
            if terms:
                q["$text"] = {"$search": terms}
                cursor = (
                    self.collection.find(q, {"_id": 0, "score": {"$meta": "textScore"}})
                    .sort([("score", {"$meta": "textScore"})])
                    .limit(limit)
                )
            else:
                cursor = self.collection.find(q, {"_id": 0}).limit(limit)
            out = [o for o in (self._to_opportunity(d) for d in cursor) if o]
            logger.info("Mongo repository returned %d candidates (text search: %r).", len(out), terms[:60])
            return out
        except Exception as exc:
            logger.error("Mongo search_candidates failed (%s); returning empty set.", exc)
            return []

    def get_all_opportunities(self) -> List[Opportunity]:
        try:
            docs = self.collection.find({"archived_at": {"$exists": False}}, {"_id": 0}).limit(2000)
            return [o for o in (self._to_opportunity(d) for d in docs) if o]
        except Exception as exc:
            logger.error("Mongo get_all_opportunities failed: %s", exc)
            return []

    def get_opportunity_by_id(self, opportunity_id: str) -> Optional[Opportunity]:
        try:
            doc = self.collection.find_one({"source_id": opportunity_id}, {"_id": 0})
            return self._to_opportunity(doc) if doc else None
        except Exception as exc:
            logger.error("Mongo get_opportunity_by_id failed: %s", exc)
            return None


def _usd(n) -> str:
    try:
        n = float(n or 0)
    except (TypeError, ValueError):
        return "$0"
    if n >= 1_000_000:
        return f"${n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"${n / 1_000:.0f}K"
    return f"${n:.0f}"


# -----------------------------------------------------------------------------
# Dependency Injection Factory
# -----------------------------------------------------------------------------

_REPO_INSTANCE: Optional[OpportunityRepository] = None

def get_opportunity_repository() -> OpportunityRepository:
    """
    Returns the configured OpportunityRepository instance.
    Defaults to MockOpportunityRepository for hackathon development.
    """
    global _REPO_INSTANCE
    if _REPO_INSTANCE is None:
        mongo_uri = os.getenv("MONGODB_URI")
        if mongo_uri and mongo_uri.strip():
            logger.info("MONGODB_URI detected; attempting MongoOpportunityRepository initialization.")
            try:
                db_name = os.getenv("MONGODB_DATABASE", "federal_opportunities")
                col_name = os.getenv("MONGODB_COLLECTION", "opportunities")
                _REPO_INSTANCE = MongoOpportunityRepository(mongo_uri, db_name, col_name)
            except Exception as exc:
                logger.error("Failed to initialize MongoOpportunityRepository (%s). Falling back to MockOpportunityRepository.", exc)
                _REPO_INSTANCE = MockOpportunityRepository()
        else:
            _REPO_INSTANCE = MockOpportunityRepository()

    return _REPO_INSTANCE


# -----------------------------------------------------------------------------
# Mapping helpers
# -----------------------------------------------------------------------------

_INDUSTRY_MAP = {
    "healthcare": ["healthcare", "health", "clinical", "hospital", "medical", "nursing", "patient"],
    "biotech": ["biotech", "biomedical", "genomics", "drug", "diagnostics"],
    "cybersecurity": ["cybersecurity", "security", "cyber", "threat"],
    "manufacturing": ["manufacturing", "production", "industrial", "fabrication"],
    "aerospace_defense": ["aerospace", "defense", "space", "aeronautics", "military"],
    "energy": ["energy", "power", "grid", "renewable", "solar", "battery"],
    "water_environment": ["water", "environmental", "climate", "wastewater", "conservation"],
    "agriculture": ["agriculture", "farm", "crop", "food"],
    "education_workforce": ["education", "training", "workforce", "stem", "students"],
    "transportation": ["transportation", "transit", "vehicle", "logistics", "infrastructure"],
    "community": ["community", "economic development", "small business", "rural"],
}

_TECH_MAP = {
    "ai": ["artificial intelligence", "machine learning", " ai ", "deep learning", "algorithm"],
    "software": ["software", "platform", "application", "saas", "cloud", "data"],
    "sensors_iot": ["sensor", "internet of things", "monitoring", "instrumentation"],
    "robotics": ["robot", "autonomous", "automation", "uav", "drone"],
    "quantum_semiconductors": ["quantum", "semiconductor", "microelectronics", "photonics"],
    "materials": ["materials", "composite", "coating", "alloy", "nanotech"],
}


# The matching engine scores tag overlap as matched/total, so a program tagged with
# everything scores poorly on everything. Keep only the dominant few, strongest first.
_MAX_TAGS = 3


def _rank_tags(text: str, domains: List[str], table: dict) -> List[str]:
    """Tags the program's own words support, strongest first.

    Server 1's semantic domain tags lead the ranking when the text backs them up, and
    stand in on their own only when the text is too thin to tag at all. Taking them on
    faith mislabels programs — a forensic-healthcare grant came back tagged
    "cybersecurity", which then diluted its healthcare score.
    """
    scored = sorted(
        ((sum(text.count(n) for n in needles), name) for name, needles in table.items()),
        reverse=True,
    )
    supported = [name for hits, name in scored if hits]
    ordered = ([n for n in supported if n in domains]
               + [n for n in supported if n not in domains])
    if not ordered:
        ordered = [d for d in domains if d in table]
    return ordered[:_MAX_TAGS]


_CUSTOMER_MAP = {
    "hospitals": ["hospital", "clinic", "patient", "provider", "nursing", "physician"],
    "utilities": ["utility", "utilities", "municipal", "water system", "grid operator"],
    "schools": ["school", "college", "university", "student", "educator", "classroom"],
    "farms": ["farm", "rancher", "grower", "producer", "agricultur"],
    "state and local government": ["state", "local government", "tribal", "county", "city"],
    "small businesses": ["small business", "entrepreneur", "startup", "commercializ"],
    "federal agencies": ["federal agency", "department of defense", "warfighter", "military"],
    "manufacturers": ["manufacturer", "supply chain", "industrial base", "factory"],
}


def _customers_for(text: str) -> List[str]:
    scored = sorted(
        ((sum(text.count(n) for n in needles), name) for name, needles in _CUSTOMER_MAP.items()),
        reverse=True,
    )
    return [name for hits, name in scored if hits][:_MAX_TAGS]


def _industries_for(text: str, domains: List[str]) -> List[str]:
    """The few industries a program actually serves (domain tags + its own text)."""
    return _rank_tags(text, domains, _INDUSTRY_MAP)


def _technologies_for(text: str, domains: List[str]) -> List[str]:
    return _rank_tags(text, domains, _TECH_MAP)


_STOP = {
    "the", "and", "for", "with", "from", "this", "that", "our", "are", "were", "have", "has",
    "company", "startup", "based", "team", "people", "employees", "revenue", "raised", "looking",
    "funding", "capital", "million", "help", "helps", "using", "build", "building", "we're", "we",
}


def _profile_terms(profile: StartupProfile) -> str:
    """Salient words from the startup's own description, for the Mongo text index."""
    import re

    def _flat(v) -> str:
        if v is None:
            return ""
        if isinstance(v, (list, tuple, set)):
            return " ".join(_flat(x) for x in v)
        return str(v)

    parts = [
        _flat(getattr(profile, f, None))
        for f in ("story", "industry", "technology", "rd_activities", "target_customers", "name")
    ]
    words = re.findall(r"[a-zA-Z]{4,}", " ".join(parts).lower())
    seen: List[str] = []
    for w in words:
        if w not in _STOP and w not in seen:
            seen.append(w)
    return " ".join(seen[:18])
