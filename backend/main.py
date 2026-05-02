"""
UBID Mesh - FastAPI Application Entry Point
Unified Business Identity & Active Intelligence Platform
"""

import os
from dotenv import load_dotenv
load_dotenv()  # Load .env file for MISTRAL_API_KEY etc.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routes import registry, reviewer, query, graph, audit

app = FastAPI(
    title="UBID Mesh API",
    description="Unified Business Identity & Active Intelligence Platform - Karnataka State",
    version="1.0.0",
)

# CORS for frontend (local + deployed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(registry.router)
app.include_router(reviewer.router)
app.include_router(query.router)
app.include_router(graph.router)
app.include_router(audit.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {
        "system": "UBID Mesh",
        "version": "1.0.0",
        "description": "Unified Business Identity & Active Intelligence Platform",
        "state": "Karnataka",
        "status": "operational",
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}
