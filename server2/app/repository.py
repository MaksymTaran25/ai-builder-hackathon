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
    """
    Read-only MongoDB repository blueprint for when the team finalizes the schema.
    
    Usage:
        To activate, set MONGODB_URI in .env and update get_opportunity_repository().
    """

    def __init__(self, uri: str, db_name: str, collection_name: str):
        try:
            # from pymongo import MongoClient
            # self.client = MongoClient(uri)
            # self.collection = self.client[db_name][collection_name]
            logger.info("Connecting to MongoDB at %s (database: %s, collection: %s)", uri, db_name, collection_name)
            raise NotImplementedError("MongoDB connection will be configured once the cluster is finalized.")
        except Exception as e:
            logger.warning("MongoOpportunityRepository not initialized: %s", e)

    def search_candidates(self, profile: StartupProfile) -> List[Opportunity]:
        # Example query:
        # query = {"is_active": True}
        # if profile.employees:
        #     query["$or"] = [{"max_employees_limit": None}, {"max_employees_limit": {"$gte": profile.employees}}]
        # docs = self.collection.find(query)
        # return [Opportunity(**doc) for doc in docs]
        raise NotImplementedError

    def get_all_opportunities(self) -> List[Opportunity]:
        # docs = self.collection.find({"is_active": True})
        # return [Opportunity(**doc) for doc in docs]
        raise NotImplementedError

    def get_opportunity_by_id(self, opportunity_id: str) -> Optional[Opportunity]:
        # doc = self.collection.find_one({"id": opportunity_id})
        # return Opportunity(**doc) if doc else None
        raise NotImplementedError


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
