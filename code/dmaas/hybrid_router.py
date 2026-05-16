<<<<<<< HEAD
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
=======
# code/dmaas/hybrid_router.py
import ollama

class HybridRouter:
    def __init__(self):
        self.grit_model = "tinyllama"
        self.squire_model = "phi3:mini"

    def route(self, task: str, complexity: int = 1) -> str:
        if complexity <= 3:
            resp = ollama.chat(model=self.grit_model, messages=[{"role": "user", "content": task}])
            return resp['message']['content']
        else:
            resp = ollama.chat(model=self.squire_model, messages=[{"role": "user", "content": task}])
            return resp['message']['content']
>>>>>>> 7f829f727a2e251233babc2c409c6642b8726875
