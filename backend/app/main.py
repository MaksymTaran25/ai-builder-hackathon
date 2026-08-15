"""GovMatch API — Government Opportunity Finder backend.

All data access is GraphQL at /graphql (GraphiQL explorer in a browser).
The only REST route is the ops health check.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .gql import router as graphql_router
from .services import llm

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="GovMatch", version="0.2.0")


@app.on_event("startup")
async def _warmup():
    import asyncio

    from .services import embeddings

    asyncio.get_event_loop().run_in_executor(None, embeddings.warmup)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_router)  # GraphQL at /graphql


@app.get("/api/health")
async def health():
    return {"ok": True, "llm_provider": llm.provider(), "api": "graphql", "endpoint": "/graphql"}
