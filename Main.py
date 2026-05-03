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

# Xbow + Artemis AI Pentesting Agent architectures, comparison, and full gap matrix
PENTEST_AGENT_CONTEXT = """
═══════════════════════════════════════════════
XBOW ARCHITECTURE — "The Specialist" (Deep Exploit Dev)
═══════════════════════════════════════════════
Philosophy: "Think like a researcher." High-quality, surgical exploitation.
Multi-agent crew: Coordinator (attack surface map) → Solvers (Docker-sandboxed,
Plan→Act→Observe→Re-plan per vuln) → Validator (PoC confirmation, no false positives).
LLM reasoning: infers param injection from empty JS vars, reasons X-Forwarded-For
bypass on 403, writes dynamic exploit scripts, reads output, re-plans.
Tools: requests, playwright, nmap, curl, custom fuzzers. Orchestration: LangGraph.
Weakness: Slower on huge networks. Struggles with blind timing attacks.

═══════════════════════════════════════════════
ARTEMIS ARCHITECTURE — "The General" (Swarm Commander, Stanford ~late 2025)
═══════════════════════════════════════════════
Philosophy: "Search every corner of the map." Massive scale + persistence.
Scale vs. Xbow: Xbow is a specialist; Artemis is a general commanding a recursive swarm.
Beat 9/10 pro human hackers in tests purely via parallel persistence (never sleeps).

CORE COMPONENTS:
1. SUPERVISOR — Takes a target, decomposes into recursive TODO tree (not flat list).
   If sub-agent hits a locked door → adds "find key" to tree → spawns new specialist.
   Tree can be N levels deep. Uses LangGraph StateGraph for global shared memory.

2. RECURSIVE TODO TREE — Each node is a task. Blocking tasks spawn child tasks.
   Parallel branches execute simultaneously. Completion propagates upward.
   Build pattern: Supervisor → Sub-tasks → Worker Agents → Global State → Supervisor.

3. CONTEXT RECYCLING (secret sauce) — Does NOT feed full history to every agent call.
   Extracts only "relevant bits" per agent invocation. Keeps token cost flat at scale.
   Critical for surviving 50+ page crawls without context fatigue.

4. TRIAGE MODULE — Dedicated "no-BS" validation layer. Validates ALL findings before
   they reach a human. Equivalent to Xbow's Validator but operates swarm-wide.

ARTEMIS GAP MATRIX:
1. GUI WALL — CLI god, browser toddler. Fails on React dashboards, drag-and-drop,
   visual spatial reasoning. Fix: multimodal LLM (GPT-4o/Claude) for screenshot
   interpretation, not just HTML parsing.
2. FALSE POSITIVE JUMPINESS — Sees 403 → hallucinates "Broken Access Control."
   Needs "Negative Constraints": force agent to DISPROVE its own finding first.
3. CREATIVE CHAINING — Misses lateral thinking. Human sees printer error → realizes
   printer shares service account with HR portal → pivots. Artemis follows the
   technical path but misses hacker-intuition cross-system links.
4. ANTI-AI HONEYPOTS (2026 meta) — Defenders embed invisible HTML links only AI
   crawlers follow. Artemis clicks them → IP banned instantly. Needs "cynicism layer":
   statistical anomaly detection on DOM elements before interaction.

XBOW vs ARTEMIS COMPARISON:
| Dimension          | Xbow                        | Artemis                      |
| Primary strength   | Deep exploit dev (quality)  | Network coverage (scale)     |
| Architecture       | Collaborative expert agents | Supervisor + recursive swarm |
| Philosophy         | Think like a researcher     | Search every corner          |
| Context strategy   | Per-agent isolation         | Context recycling + StateGraph|
| False positive rate| Low (Validator enforced)    | Higher (speed-quality tradeoff)|
| GUI handling       | playwright (limited)        | Weak — biggest gap           |
| Scale              | Slower on large networks    | Parallel swarm, never sleeps |
| Weakness           | Blind timing, large scope   | UI/UX, creative chaining     |

SHARED XBOW+ARTEMIS GAP MATRIX (build-better targets):
1. BLIND INJECTION — Neither handles blind SQLi/timing attacks well. 2s delay ignored.
2. BUSINESS LOGIC — Economic abuse, negative refunds, workflow bypass invisible to both.
3. AUTH BARRIERS — MFA + CAPTCHA break both. No reliable solver exists yet.
4. ANTI-AI HONEYPOTS — New 2026 threat. Invisible DOM traps. Neither agent is cynical.
5. CHAINED EXPLOITS — SSRF→pivot→RCE chains still require human composition.
6. NOISY RECON — Both generate detectable traffic signatures. No stealth mode.
7. CREATIVE LATERAL THINKING — Cross-system hacker intuition. Neither can do it.
8. MULTIMODAL VISION — Screenshot-based reasoning. Artemis gap; Xbow partial fix only.

REFERENCE IMPLS: Shannon Lite (GitHub, white-box OSS pentester), LangGraph StateGraph.
ETHICAL BOUNDARY: All ops must be authorized, sandboxed, scoped. No unauthorized targets.
"""

# ─────────────────────────────────────────────────────────────────────────────
# TRIPLE-VISION STACK — "Giving agents eyes that actually work" (2026 meta)
# ─────────────────────────────────────────────────────────────────────────────
VISION_STACK_CONTEXT = """
TRIPLE-VISION STACK — Hybrid Vision-DOM Framework (2026 meta):

LAYER A — ACCESSIBILITY TREE (Cheat Sheet):
Tool: page.accessibility.snapshot() in Playwright.
Strips 5000-line div soup → structured list of interactive elements only.
Output: "Button: Log In, State: Enabled, Location: (450, 120)"
Zero-cost first pass. Always run before vision layers.

LAYER B — SET-OF-MARK (SoM) VISUAL GROUNDING (The Eyes):
Tool: Playwright screenshot → PIL/OpenCV overlay numbered bounding boxes on every
interactive element → send annotated image to multimodal LLM (GPT-4o or Claude).
Agent says "click Box #42" not "click the login button." Eliminates coordinate guessing.
Critical for React dashboards, drag-and-drop, dynamic UIs that don't map cleanly to DOM.

LAYER C — SEMANTIC SALIENCY MAP (Attention Filter):
Tool: Fine-tuned CLIP or lightweight ViT model.
Generates heatmap before main agent interaction.
Output: "Ignore footer/ads. High-value region: top-right (confidence 0.87)"
Prevents wasting tokens on irrelevant regions. Feeds mask into SoM step.

OBSERVE PHASE PIPELINE (all three layers combined):
1. Load page → a11y snapshot → structured element list (Layer A)
2. Screenshot → saliency map → mask low-value regions (Layer C)
3. Apply SoM bounding boxes to high-value regions only (Layer B)
4. Send annotated screenshot + a11y tree to multimodal LLM
5. LLM returns: "Interact with Box N" → Playwright executes pixel-perfect
6. Observe result → re-plan

HUMAN-IN-THE-LOOP MFA BRIDGE:
When agent hits auth wall → emits HITL_REQUIRED event with session_id.
Operator phone receives push notification → opens live browser stream via WebSocket.
Operator solves CAPTCHA/enters 2FA → agent receives HITL_RESOLVED → resumes.
Implementation: Playwright remote debugging port + WebSocket relay + PWA live view.
Key insight: don't fight MFA — pause, hand off, resume. Keeps session alive.

ADVANCED VULN DETECTION:
PROTOTYPE POLLUTION — Inject {"__proto__": {"canary": "PPT_1337"}} → read back
  Object.prototype.canary via Playwright evaluate(). Feedback loop, not guessing.
  Targets: lodash.merge, jQuery.extend, Object.assign with user-controlled keys.

RACE CONDITIONS — Turbo Intruder pattern: 50 requests in <10ms burst. Compare
  all 50 response screenshots/status codes. 1-of-50 shows Logged-In = confirmed race.

HTTP SMUGGLING — Calculate actual Content-Length vs Transfer-Encoding byte lengths.
  Test CL.TE and TE.CL desync against frontend/backend proxy pairs.

SECOND-ORDER INJECTION — Track all stored inputs across session in a payload ledger.
  Re-test stored payloads in every subsequent context where they could render.

DESERIALIZATION — Inject ysoserial gadget chains. Monitor OOB callbacks via
  interactsh or Burp Collaborator. Target Java, PHP, Python pickle boundaries.

GRAPHQL — Always attempt introspection first. If disabled: field suggestion enum.
  Test batching (100 ops/request), deeply nested query DoS, field-level auth bypass.
"""

# ─────────────────────────────────────────────────────────────────────────────
# BUG BOUNTY INTELLIGENCE LAYER — Scope, Recon, Intel, Report
# ─────────────────────────────────────────────────────────────────────────────
BUG_BOUNTY_CONTEXT = """
BUG BOUNTY META — 2026 Operational Intelligence:

LAWYER → SCOUT → HUNTER PIPELINE:
1. LAWYER — Reads program policy (H1/Bugcrowd). Outputs Rules of Engagement:
   in-scope assets, payout tiers by severity, exclusions, special rules.
   Every downstream agent checks ROE before touching any asset.
2. SCOUT — Enumerates all assets. Filters each through Lawyer ROE.
   Outputs: cleared asset list with payout tier estimate per asset.
3. HUNTER — Only attacks Lawyer-cleared assets. Knows payout ceiling.
   Prioritizes P1/P2 paths. Explicitly skips P4 rabbit holes.

PAYOUT ROI ESTIMATOR:
Before pursuing any finding: (severity × payout_tier) / time_cost.
P1 on $50k max program >> P3 on $500 max program for same effort.
Agent must state expected payout range before deep-diving any vector.

HISTORICAL RECON LAYER (what live scanners can't see):
- Wayback Machine API: deleted endpoints from 2+ years ago often still live.
- Certificate Transparency (crt.sh): all subdomains ever issued a cert — finds
  staging, internal, forgotten assets the live scanner misses.
- Common Crawl + AlienVault OTX: passive historical data, zero detection risk.

JS SUPPLY CHAIN ANALYSIS:
For every <script src="..."> tag: download CDN script, beautify, scan for:
hardcoded API keys, auth tokens, internal endpoints, AWS keys (AKIA...),
Stripe keys (sk_live_...), debug endpoints.
Magecart skimmers hide in third-party analytics/tag manager scripts.
Tools: js-beautify, trufflehog, semgrep JS rules.

CLOUD MISCONFIGURATION RECON:
- Test SSRF to metadata: 169.254.169.254/latest/meta-data/iam/security-credentials/
- S3 buckets: [target]-dev, -staging, -backup, -assets.
- GCS: storage.googleapis.com/[target-bucket]
- Azure blob: [target].blob.core.windows.net
- Tools: cloud_enum, s3scanner, GCPBucketBrute.

DUPLICATE CHECK: Search H1 hacktivity + Bugcrowd disclosures before pursuing any
finding. Duplicate = zero payout. Always check first.

PROGRAM VELOCITY: Track avg response time, avg payout, recent activity.
Prioritize "hot" programs with recent confirmed payouts over stale ones.

SUBDOMAIN TAKEOVER: Pull all CNAME records. Cross-reference fingerprints:
GitHub Pages ("there isn't a GitHub Pages site here"), Heroku (no-such-app),
S3 (NoSuchBucket), Azure (404 blob), Fastly, Shopify.
Tools: subjack, nuclei subdomain-takeover templates, can-i-take-over-xyz.

MOBILE API SURFACE: Decompile APK (jadx/apktool) → extract hardcoded endpoints,
API keys, base URLs. Mobile endpoints often lack WAF/rate-limiting of web app.

REPORT WRITER — Standard H1/Bugcrowd format:
  Title: [Vuln Type] in [Component] allows [Impact]
  Severity: CVSS 3.1 score + vector string
  Summary: 2-sentence plain-language impact statement
  Steps to Reproduce: numbered, exact, reproducible in ≤3 steps
  Impact: what attacker achieves (data exfil, ATO, RCE, etc.)
  PoC: working curl command or code snippet
  Remediation: specific fix recommendation
Rule: if triage can't reproduce in 3 steps it gets closed. Precision over prose.
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
    "triage":   "Real-time Scanner & Triage specialist. Identify threat vectors, IOCs, deception triggers.",
    "oracle":   "Context Oracle. Correlate metadata, OSINT, ExifTool findings, steganography signals.",
    "patcher":  "Hybrid Verifier/Patcher. Recommend PQC patches, canary rollouts, containment steps.",
    "hunter":   "Proactive Threat Hunter. Map attacker TTPs, zero-day hypotheses, deception-derived intel.",
    "anchor":   "Human Anchor Layer. Summarize findings in plain language. Recommend non-lethal containment.",
    "redteam":  "Meta-Guard/Red-Team. Simulate Xbow-style autonomous attacker. Map coordinator→solver→validator flow against current defenses. Identify blind SQLi, business logic, context-fatigue, and auth-bypass gaps.",
}

# ─────────────────────────────────────────────
# PENTEST AGENT ORCHESTRATOR (Xbow-style)
# ─────────────────────────────────────────────
PENTEST_
