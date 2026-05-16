#!/usr/bin/env python3
"""AETHORFORGE v1.9 — World Serpent"""
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

BANNER = """
╔══════════════════════════════════════════╗
║    AETHORFORGE v1.9 — WORLD SERPENT     ║
║    Cyber · Energy · Biotech             ║
║    Finance · Learning · Voice           ║
╚══════════════════════════════════════════╝"""

MENU = """
┌─ MODES ──────────────────────────────────
│  [1] Router      — auto-route any query
│  [2] Pentest     — recon + vuln analysis
│  [3] Bounty      — scope, recon, report
│  [4] Forge       — generate + review code
│  [5] Domains     — energy/bio/finance/etc
│  [6] Blockchain  — sign + audit actions
│  [7] Crucible    — validate any finding
│  [8] Transcribe  — check voice setup
│  [q] Quit
└──────────────────────────────────────────"""

def load_all():
    from code.dmaas.hybrid_router import HybridRouter
    from code.crucible.spartan_crucible import SpartanCrucible
    from code.evolution.forge_builder import ForgeBuilder
    from code.pentest.pentest_module import PentestModule
    from code.bounty.bounty_module import BountyModule
    from code.security.blockchain_layer import BlockchainLayer
    from code.domains.domain_module import DomainModule
    from code.voice.transcriber import Transcriber
    return {
        "router":     HybridRouter(),
        "crucible":   SpartanCrucible(),
        "forge":      ForgeBuilder(),
        "pentest":    PentestModule(),
        "bounty":     BountyModule(),
        "chain":      BlockchainLayer(),
        "domains":    DomainModule(),
        "voice":      Transcriber(),
    }

def run(modules, mode, query):
    m = modules
    if mode == "1":
        cx = input("  complexity 1-10 [Enter=auto]: ").strip()
        return m["router"].route(query, int(cx) if cx.isdigit() else None)
    elif mode == "2":
        sub = input("  [r]econ / [a]nalyze / [g]aps: ").strip()
        if sub == "a": return m["pentest"].analyze(query)
        if sub == "g": return m["pentest"].xbow_gaps(query)
        return m["pentest"].recon(query)
    elif mode == "3":
        sub = input("  [s]cope / [r]econ / [w]rite report / [d]upe check: ").strip()
        if sub == "s": return m["bounty"].scope_check(query)
        if sub == "w": return m["bounty"].write_report(query)
        if sub == "d": return m["bounty"].check_duplicate(query)
        return m["bounty"].recon(query)
    elif mode == "4":
        return m["forge"].full_pipeline(query)["code"]
    elif mode == "5":
        domain = input("  domain [energy/physical/biotech/finance/learning]: ").strip()
        return m["domains"].query(domain, query) if domain else m["domains"].auto_route(query)
    elif mode == "6":
        return m["chain"].audit(query)
    elif mode == "7":
        verdict = m["crucible"].run(query)
        return verdict.summary()
    elif mode == "8":
        return f"whisper: {'✓' if (Path.home()/'whisper.cpp/build/bin/whisper-cli').exists() else '✗'}"
    return "Unknown mode"

def main():
    print(BANNER)
    key = os.environ.get("GROQ_API_KEY", "")
    print(f"  Groq: {'✓ connected' if key else '✗ set GROQ_API_KEY'}\n")
    print("  Loading modules...")
    modules = load_all()
    print("\n✓ ALL SYSTEMS ONLINE")

    mode = "1"
    while True:
        print(MENU)
        choice = input("Mode: ").strip().lower()
        if choice == "q":
            print("\n👋 World Serpent offline.\n")
            break
        if choice in [str(i) for i in range(1, 9)]:
            mode = choice
        query = input("Query: ").strip()
        if not query:
            continue
        print(f"\n{'─'*50}")
        try:
            result = run(modules, mode, query)
            if isinstance(result, dict):
                for k, v in result.items():
                    print(f"[{k}] {str(v)[:200]}")
            else:
                print(result)
        except Exception as e:
            print(f"Error: {e}")
        print(f"{'─'*50}\n")

if __name__ == "__main__":
    main()

