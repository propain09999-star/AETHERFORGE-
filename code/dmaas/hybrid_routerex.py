# code/dmaas/hybrid_router.py
"""
AETHORFORGE Hybrid Router - Fixed imports
"""

try:
    from ..grit.models import get_model
except ImportError:
    # Fallback for direct running
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from grit.models import get_model


class HybridRouter:
    def __init__(self):
        self.grit_model = get_model("grit", "nano")
        self.squire_model = get_model("squire")

    def route(self, task: str, complexity: int = 1) -> str:
        print(f"→ Routing task (complexity: {complexity})")
        
        if complexity <= 4:
            result = self.grit_model.process(task)
            return f"[Grit Tier] {result}"
        else:
            grit_result = self.grit_model.process(task)
            final = self.squire_model.validate(grit_result)
            return f"[Squire Tier] {final}"


# Quick test when running directly
if __name__ == "__main__":
    router = HybridRouter()
    print(router.route("Simple metadata scan", 2))
    print(router.route("Deep zero-day analysis with OSINT", 8))
