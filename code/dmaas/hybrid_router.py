import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from code.grit.models import get_model, NanoModel, SquireModel

class HybridRouter:
    def __init__(self):
        self.nano   = get_model("grit", "nano")
        self.squire = get_model("squire")
        print("✓ HybridRouter online")

    def route(self, task: str, complexity: int = None) -> str:
        if complexity is None:
            complexity = self._classify(task)
        print(f"  → complexity {complexity}/10")
        if complexity <= 4:
            return self.nano.process(task)
        else:
            result = self.nano.process(task)
            return self.squire.validate(result)

    def _classify(self, task: str) -> int:
        keywords = ["zero-day","chain","ssrf","smuggl","deserializ","lateral"]
        return 8 if any(k in task.lower() for k in keywords) else 3

if __name__ == "__main__":
    r = HybridRouter()
    print(r.route("Simple metadata scan", 2))
    print(r.route("Deep zero-day SSRF chain analysis", 8))
