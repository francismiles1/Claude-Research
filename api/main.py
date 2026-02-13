"""
FastAPI backend for the Cap/Ops Balance Research Platform.

Thin API layer wrapping the existing Python computation modules in src/.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add src/ to sys.path so we can import the computation modules
_SRC_DIR = str(Path(__file__).resolve().parent.parent / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from api.routers import context, grid, data, assessment  # noqa: E402

app = FastAPI(
    title="Cap/Ops Balance Research Platform",
    description="API for the capability vs operational maturity simulation",
    version="0.1.0",
)

# CORS — same-origin in production (Vercel), allow dev servers locally
import os
_origins = [
    "http://localhost:5173",   # Vite dev server
    "http://localhost:3000",   # Alternative dev
    "http://127.0.0.1:5173",
]
_vercel_url = os.getenv("VERCEL_URL")
if _vercel_url:
    _origins.append(f"https://{_vercel_url}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(context.router, prefix="/api")
app.include_router(grid.router, prefix="/api")
app.include_router(assessment.router, prefix="/api")
app.include_router(data.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
