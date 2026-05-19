"""
Zero-Sum Heist + AETHORFORGE SecureLead Orchestrator
FastAPI Backend — deploy on Hetzner/Railway/Fly.io ($6/mo)
"""

import asyncio
import hashlib
import json
import os
import sqlite3
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ─────────────────────────────────────────────
# CONFIG — set these as environment variables
# ─────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")           # Free at console.groq.com
GROQ_BASE    = "https://api.groq.com/openai/v1/chat/completions"

# Fast free models on Groq
ROUTER_MODEL      = "llama-3.1-8b-instant"
SPECIALIST_MODEL  = "llama-3.3-70b-versatile"
SYNTHESIZER_MODEL = "llama-3.3-70b-versatile"

DB_PATH = "heist_cache.db"

# ─────────────────────────────────────────────
# SYSTEM CONTEXTS
# ─────────────────────────────────────────────
HEIST_THESIS = """
Zero-Sum Heist studio: Fork mature but stagnant open-source projects,
AI-augmented rewrite + polish, ship commercial forks 10x faster.
Core Flywheel:
1. RECON — Scan stagnant OSS in zero-sum markets (dev tools, AI infra,
   agent frameworks, databases post-license drama).
2. FORK + BLITZ — Day 0 fork → Day 1-14 AI rewrite + enterprise polish
   (UI/UX, auth, observability, billing).
3. SHIP & DOMINATE — Freemium → paid hosted/enterprise/white-label →
   possible acqui-hire.
Toronto AI talent + execution velocity = moat. <$200k for first 3-4 heists.
"""

AETHORFORGE_CONTEXT = """
AETHORFORGE SecureLead — Quantum-Hardened Hierarchical DMAAS Platform.
SecureLead sub-swarms: Lead Orchestrator (TEE+HSM), Real-time Scanner,
Context Oracle, Hybrid Verifier/Patcher, Meta-Guard/Red-Team,
Auditor/Provenance, Proactive Threat Hunter, Human Anchor Layer.
Capabilities: Assume-Breach Deception Codex, Metadata/OSINT analysis,
PQC migration, ExifTool forensics, steganography detection,
OWASP Agentic Security Top 10 coverage, ethical non-lethal defense.
All deception ops: PQC-signed, TEE-isolated, immutable ledger logged.
"""

# ─────────────────────────────────────────────
# DATABASE (SQLite job queue + result cache)
# ─────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            mode TEXT,
            query TEXT,
            status TEXT DEFAULT 'pending',
            result TEXT,
            created_at REAL,
            completed_at REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            query_hash TEXT PRIMARY KEY,
            mode TEXT,
            result TEXT,
            created_at REAL
        )
    """)
    conn.commit()
    conn.close()

def cache_get(query: str, mode: str) -> Optional[str]:
    h = hashlib.sha256(f"{mode}:{query}".encode()).hexdigest()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT result, created_at FROM cache WHERE query_hash=?", (h,))
    row = c.fetchone()
    conn.close()
    if row and (time.time() - row[1]) < 3600:   # 1-hour cache TTL
        return row[0]
    return None

def cache_set(query: str, mode: str, result: str):
    h = hashlib.sha256(f"{mode}:{query}".encode()).hexdigest()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO cache (query_hash, mode, result, created_at)
        VALUES (?, ?, ?, ?)
    """, (h, mode, result, time.time()))
    conn.commit()
    conn.close()

def job_create(job_id: str, mode: str, query: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO jobs (id, mode, query, status, created_at)
        VALUES (?, ?, ?, 'pending', ?)
    """, (job_id, mode, query, time.time()))
    conn.commit()
    conn.close()

def job_update(job_id: str, status: str, result: str = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE jobs SET status=?, result=?, completed_at=?
        WHERE id=?
    """, (status, result, time.time(), job_id))
    conn.commit()
    conn.close()

def job_get(job_id: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, mode, query, status, result, created_at, completed_at FROM jobs WHERE id=?", (job_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0], "mode": row[1], "query": row[2],
        "status": row[3], "result": row[4],
        "created_at": row[5], "completed_at": row[6]
    }

# ─────────────────────────────────────────────
# GROQ API CALL
# ─────────────────────────────────────────────
async def groq_call(model: str, messages: list, temperature: float = 0.7) -> str:
    if not GROQ_API_KEY:
        raise HTTPException(500, "GROQ_API_KEY not set")
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            GROQ_BASE,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 1024
            }
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

# ─────────────────────────────────────────────
# HEIST ORCHESTRATOR
# ─────────────────────────────────────────────
async def heist_router(query: str) -> list[str]:
    content = await groq_call(
        ROUTER_MODEL,
        [{
            "role": "system",
            "content": f"You are a Recon router. {HEIST_THESIS}\nReturn ONLY a comma-separated list from: recon, strategy, coding, creative, monetization. Max 3."
        }, {
            "role": "user", "content": query
        }],
        temperature=0
    )
    specialists = [s.strip().lower() for s in content.split(",")]
    valid = {"recon", "strategy", "coding", "creative", "monetization"}
    return [s for s in specialists if s in valid][:3] or ["strategy"]

async def heist_specialist(name: str, query: str) -> str:
    result = await groq_call(
        SPECIALIST_MODEL,
        [{
            "role": "system",
            "content": f"You are the {name} specialist in a Zero-Sum Heist studio.\n{HEIST_THESIS}\nBe ruthlessly actionable. No fluff."
        }, {
            "role": "user", "content": query
        }]
    )
    return f"[{name.upper()}]\n{result}"

async def heist_synthesizer(query: str, specialist_outputs: list[str]) -> str:
    combined = "\n\n".join(specialist_outputs)
    return await groq_call(
        SYNTHESIZER_MODEL,
        [{
            "role": "system",
            "content": f"You are the Synthesizer for Zero-Sum Heist studio.\n{HEIST_THESIS}\nSynthesize into ONE clear, executable plan. Prioritize speed, forkable actions, monetization. Be concise."
        }, {
            "role": "user",
            "content": f"Query: {query}\n\nSpecialist responses:\n{combined}"
        }]
    )

async def run_heist(query: str) -> dict:
    specialists = await heist_router(query)
    tasks = [heist_specialist(name, query) for name in specialists]
    outputs = await asyncio.gather(*tasks)
    final = await heist_synthesizer(query, list(outputs))
    return {
        "mode": "heist",
        "specialists_used": specialists,
        "final": final,
        "timestamp": datetime.utcnow().isoformat()
    }

# ─────────────────────────────────────────────
# SECURELEAD ORCHESTRATOR
# ─────────────────────────────────────────────
SECURELEAD_AGENTS = {
    "triage":  "Real-time Scanner & Triage specialist. Identify threat vectors, IOCs, deception triggers.",
    "oracle":  "Context Oracle. Correlate metadata, OSINT, ExifTool findings, steganography signals.",
    "patcher": "Hybrid Verifier/Patcher. Recommend PQC patches, canary rollouts, containment steps.",
    "hunter":  "Proactive Threat Hunter. Map attacker TTPs, zero-day hypotheses, deception-derived intel.",
    "anchor":  "Human Anchor Layer. Summarize findings in plain language. Recommend non-lethal containment."
}

async def securelead_triage(query: str) -> list[str]:
    """Route to relevant SecureLead agents."""
    content = await groq_call(
        ROUTER_MODEL,
        [{
            "role": "system",
            "content": f"You are a SecureLead router.\n{AETHORFORGE_CONTEXT}\nReturn ONLY comma-separated agent names from: triage, oracle, patcher, hunter, anchor. Max 3."
        }, {
            "role": "user", "content": query
        }],
        temperature=0
    )
    valid = set(SECURELEAD_AGENTS.keys())
    agents = [a.strip().lower() for a in content.split(",")]
    return [a for a in agents if a in valid][:3] or ["triage", "anchor"]

async def securelead_agent(name: str, query: str) -> str:
    role = SECURELEAD_AGENTS.get(name, "SecureLead specialist")
    result = await groq_call(
        SPECIALIST_MODEL,
        [{
            "role": "system",
            "content": f"You are the {role}\n{AETHORFORGE_CONTEXT}\nBe precise, ethical, actionable. Reference relevant frameworks (OWASP, PQC, TEE) where useful."
        }, {
            "role": "user", "content": query
        }]
    )
    return f"[{name.upper()}]\n{result}"

async def securelead_synthesizer(query: str, agent_outputs: list[str]) -> str:
    combined = "\n\n".join(agent_outputs)
    return await groq_call(
        SYNTHESIZER_MODEL,
        [{
            "role": "system",
            "content": f"You are the SecureLead Lead Orchestrator.\n{AETHORFORGE_CONTEXT}\nSynthesize agent findings into a clear, prioritized incident response summary. Include: threat assessment, containment actions, human escalation recommendation."
        }, {
            "role": "user",
            "content": f"Incident query: {query}\n\nAgent reports:\n{combined}"
        }]
    )

async def run_securelead(query: str) -> dict:
    agents = await securelead_triage(query)
    tasks = [securelead_agent(name, query) for name in agents]
    outputs = await asyncio.gather(*tasks)
    final = await securelead_synthesizer(query, list(outputs))
    return {
        "mode": "securelead",
        "agents_used": agents,
        "final": final,
        "timestamp": datetime.utcnow().isoformat()
    }

# ─────────────────────────────────────────────
# BACKGROUND JOB RUNNER
# ─────────────────────────────────────────────
async def process_job(job_id: str, mode: str, query: str):
    try:
        if mode == "heist":
            result = await run_heist(query)
        else:
            result = await run_securelead(query)
        result_str = json.dumps(result)
        cache_set(query, mode, result_str)
        job_update(job_id, "done", result_str)
    except Exception as e:
        job_update(job_id, "error", json.dumps({"error": str(e)}))

# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="AETHORFORGE Orchestrator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    mode: str = "heist"   # "heist" | "securelead"

@app.get("/health")
def health():
    return {"status": "online", "timestamp": datetime.utcnow().isoformat()}

@app.post("/query")
async def submit_query(req: QueryRequest, background_tasks: BackgroundTasks):
    """Submit a query. Returns job_id immediately. Poll /job/{id} for result."""
    # Check cache first
    cached = cache_get(req.query, req.mode)
    if cached:
        return {"status": "cached", "result": json.loads(cached)}

    job_id = str(uuid.uuid4())[:8]
    job_create(job_id, req.mode, req.query)
    background_tasks.add_task(process_job, job_id, req.mode, req.query)
    return {"status": "queued", "job_id": job_id}

@app.get("/job/{job_id}")
def get_job(job_id: str):
    """Poll this to get result. status: pending | done | error"""
    job = job_get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] == "done" and job["result"]:
        job["result"] = json.loads(job["result"])
    return job

@app.get("/jobs")
def list_jobs():
    """Last 20 jobs — for history view on mobile."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, mode, query, status, created_at, completed_at
        FROM jobs ORDER BY created_at DESC LIMIT 20
    """)
    rows = c.fetchall()
    conn.close()
    return [
        {"id": r[0], "mode": r[1], "query": r[2][:60] + ("..." if len(r[2]) > 60 else ""),
         "status": r[3], "created_at": r[4], "completed_at": r[5]}
        for r in rows
    ]
