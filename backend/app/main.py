"""GovMatch API — Government Opportunity Finder backend."""
from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .gql import router as graphql_router
from .models import ExtractResponse, MatchResponse, StartupProfile
from .services import llm, matching

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="GovMatch", version="0.1.0")


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

app.include_router(graphql_router)  # GraphQL at /graphql (GraphiQL explorer in browser)


class ExtractRequest(BaseModel):
    text: str


@app.get("/api/health")
async def health():
    return {"ok": True, "llm_provider": llm.provider()}


@app.post("/api/profile/extract", response_model=ExtractResponse)
async def extract_profile(req: ExtractRequest):
    profile, followups = await llm.extract_profile(req.text)
    return ExtractResponse(profile=profile, followups=followups)


@app.post("/api/match", response_model=MatchResponse)
async def match(profile: StartupProfile):
    return await matching.run_match(profile)
