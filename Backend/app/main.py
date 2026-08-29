"""
main.py
--------
The entry point. Run this to start the server:
    uvicorn app.main:app --reload --port 8000

What it does:
  1. Creates DB tables on startup (if they don't exist)
  2. Registers all routers (bidders, documents, compliance, dashboard)
  3. Enables CORS so your frontend (running on a different port, e.g. 5173) can call this API
  4. FastAPI auto-generates interactive docs at /docs — your team's contract
     for what each endpoint expects/returns, no separate Postman collection needed
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import bidders, documents, compliance, dashboard

# Create tables (SQLite) — in prod you'd use Alembic migrations instead
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GeM Rakshak — AI Bid Compliance Verification Platform",
    description="AI-powered GeM bidder compliance verification backend (SIH problem statement). "
                 "Rakshak = 'protector' — the AI protects the procurement process by verifying "
                 "bidder compliance and flagging risk, while the final decision stays with the officer.",
    version="0.1.0",
)

# Allow the frontend dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's actual URL before deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bidders.router)
app.include_router(documents.router)
app.include_router(compliance.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "GeM Rakshak API is running"}