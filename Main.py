#!/usr/bin/env python3
"""
AETHORFORGE — main.py
Central launcher. Interactive CLI for Termux / any terminal.

Usage:
    python main.py                    # Interactive mode
    python main.py --mode pentest     # Start in pentest mode
    python main.py --test             # Run system health check
"""

import sys
import os
import argparse
from pathlib import Path

# ── Path bootstrap (works everywhere) ──────────────────────────────────────
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── Imports ─────────────────────────────────────────────────────────────────
def _check_env():
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        print("⚠  GROQ_API_KEY not set.")
        print("   Set it now: export GROQ_API_KEY=gsk_your_key_here")
        print("   Get a free key at: https://console.groq.com\n")
        return False
    print(f"   ✓ GROQ_API_KEY detected (ends ...{key[-6:]})")
    return True


BANNER = """
╔══════════════════════════════════════════════════════╗
║         A E T H O R F O R G E   v0.4               ║
║         Global Cyber Command Hub                    ║
║         World Serpent · SecureLead · Crucible       ║
╚══════════════════════════════════════════════════════╝
"""

MODES = {
    "1": ("router",   "Hybrid Router       — auto-route any query"),
    "2": ("pentest",  "Pentest Mode        — Xbow + Artemis + Triple-Vision"),
    "3": ("bounty",   "Bug Bounty Mode     — Lawyer→Scout→Hunter pipeline"),
    "4": ("pentagon", "Pentagon Agents     — 5 specialist recon agents"),
    "5": ("crucible", "Spartan Crucible    — adversarial finding validator"),
    "6": ("securelead","SecureLead         — assume-breach defense"),
    "q": ("quit",     "Quit"),
}


def print_menu(current_mode: str = None):
    print("\n┌─ MODES " + "─" * 44)
    for key, (mode, desc) in MODES.items():
        marker = " ◄" if mode == current_mode else ""
        print(f"│  [{key}] {desc}{marker}")
    print("└" + "─" * 52)


def run_router_mode(query: str, complexity: int = None) -> str:
    from code.dmaas.hybrid_router import HybridRouter
    router = HybridRouter()
    return router.route(query, complexity=complexity)


def run_pentest_mode(query: str) -> str:
    from code.grit.models import GritStandard
    from code.dmaas.squire import SquireValidator

    PENTEST_SYSTEM = """You are the AETHORFORGE Pentest Lead with full knowledge of:
Xbow (surgical specialist), Artemis (swarm general), Triple-Vision Stack
(Accessibility Tree + Set-of-Mark + Saliency Map), and the 8-gap matrix.
Provide structured pentest analysis: Attack Surface, Recommended Approach,
Top Exploit Paths, Where AI Agents Fail, Toolchain. Authorized scope only."""

    from code.grit.models import _groq_call
    return _groq_call(f"{PENTEST_SYSTEM}\n\nQuery: {query}",
                      model="llama-3.3-70b-versatile")


def run_bounty_mode(query: str) -> str:
    BB_SYSTEM = """You are AETHORFORGE's Bug Bounty Lead.
You know: Lawyer→Scout→Hunter pipeline, Wayback Machine + CT log recon,
JS supply chain analysis (trufflehog, semgrep), cloud bucket enumeration,
subdomain takeover fingerprints, duplicate checking, CVSS payout estimation,
and H1/Bugcrowd report writing (3-step reproduce rule).
Provide actionable bug bounty intelligence. No generic advice."""

    from code.grit.models import _groq_call
    return _groq_call(f"{BB_SYSTEM}\n\nQuery: {query}",
                      model="llama-3.3-70b-versatile")


def run_pentagon_mode(target: str, selected: list[str] = None) -> str:
    from code.pentest.pentagon_agents import PentagonOrchestrator
    pentagon = PentagonOrchestrator()
    return pentagon.brief(target, agents=selected)


def run_crucible_mode(finding: str) -> str:
    from code.crucible.spartan_crucible import SpartanCrucible
    crucible = SpartanCrucible()
    verdict = crucible.run(finding)
    return verdict.summary()


def run_securelead_mode(query: str) -> str:
    SL_SYSTEM = """You are AETHORFORGE SecureLead — quantum-hardened DMAAS platform.
Capabilities: Assume-Breach Deception Codex, metadata/OSINT analysis,
ExifTool forensics, steganography detection, PQC migration, OWASP Agentic
Security Top 10. All deception ops: PQC-signed, TEE-isolated, immutable logs.
Provide structured incident response: Threat Assessment, Containment Actions,
Deception Deployment, Human Escalation Recommendation."""

    from code.grit.models import _groq_call
    return _groq_call(f"{SL_SYSTEM}\n\nQuery: {query}",
                      model="llama-3.3-70b-versatile")


def health_check():
    """Run system health check across all modules."""
    print("\n🔬 AETHORFORGE Health Check\n")
    checks = [
        ("GROQ_API_KEY env var",   lambda: bool(os.environ.get("GROQ_API_KEY"))),
        ("code.grit.models",       lambda: __import__("code.grit.models")),
        ("code.dmaas.squire",      lambda: __import__("code.dmaas.squire")),
        ("code.dmaas.hybrid_router", lambda: __import__("code.dmaas.hybrid_router")),
        ("code.crucible.spartan_crucible", lambda: __import__("code.crucible.spartan_crucible")),
        ("code.pentest.pentagon_agents",   lambda: __import__("code.pentest.pentagon_agents")),
    ]
    all_pass = True
    for name, check_fn in checks:
        try:
            result = check_fn()
            ok = bool(result)
        except Exception as e:
            ok = False
            result = e
        status = "✓" if ok else "✗"
        print(f"   {status} {name}" + (f"  [{result}]" if not ok else ""))
        if not ok:
            all_pass = False

    print()
    if all_pass:
        print("✅ All systems operational")
    else:
        print("⚠  Some checks failed — see above")
    return all_pass


# ── Interactive Loop ─────────────────────────────────────────────────────────
def interactive():
    print(BANNER)
    _check_env()

    current_mode = "router"

    while True:
        print_menu(current_mode)
        choice = input("\nMode or command: ").strip().lower()

        if choice == "q":
            print("\n👋 AETHORFORGE offline.\n")
            sys.exit(0)

        if choice in MODES:
            current_mode = MODES[choice][0]
            if current_mode == "quit":
                sys.exit(0)
            print(f"\n✓ Switched to: {current_mode.upper()}")
            continue

        # Run the query in current mode
        query = choice if choice else input("Query: ").strip()
        if not query:
            continue

        print(f"\n{'─'*55}")
        try:
            if current_mode == "router":
                result = run_router_mode(query)
            elif current_mode == "pentest":
                result = run_pentest_mode(query)
            elif current_mode == "bounty":
                result = run_bounty_mode(query)
            elif current_mode == "pentagon":
                agents_input = input("Agents (HYDRA/MANTIS/KRAKEN/SPECTRE/CIPHER or blank for all): ").strip()
                selected = [a.strip() for a in agents_input.split(",")] if agents_input else None
                result = run_pentagon_mode(query, selected)
            elif current_mode == "crucible":
                result = run_crucible_mode(query)
            elif current_mode == "securelead":
                result = run_securelead_mode(query)
            else:
                result = run_router_mode(query)

            print(f"\n{result}\n")

        except KeyboardInterrupt:
            print("\n[Interrupted]")
        except Exception as e:
            print(f"\n⚠  Error: {e}")

        print("─" * 55)


# ── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AETHORFORGE v0.4")
    parser.add_argument("--mode", choices=["router","pentest","bounty","pentagon","crucible","securelead"],
                        default=None, help="Start in a specific mode")
    parser.add_argument("--test", action="store_true", help="Run health check and exit")
    parser.add_argument("--query", type=str, default=None, help="Run a single query and exit")
    args = parser.parse_args()

    if args.test:
        health_check()
        sys.exit(0)

    if args.query and args.mode:
        _check_env()
        MODE_FNS = {
            "router":     run_router_mode,
            "pentest":    run_pentest_mode,
            "bounty":     run_bounty_mode,
            "crucible":   run_crucible_mode,
            "securelead": run_securelead_mode,
        }
        fn = MODE_FNS.get(args.mode, run_router_mode)
        print(fn(args.query))
        sys.exit(0)

    interactive()

