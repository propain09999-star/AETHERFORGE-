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
