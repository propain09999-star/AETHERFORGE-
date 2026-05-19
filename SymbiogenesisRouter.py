# code/dmaas/symbiogenesis_router.py
import ollama

class SymbiogenesisRouter:
    def __init__(self):
        self.grit_model = "tinyllama"
        self.squire_model = "phi3:mini"
        self.arbiter_model = "gemma2:2b"

    def _call(self, model: str, prompt: str, system: str = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            resp = ollama.chat(model=model, messages=messages)
            return resp['message']['content']
        except ollama.ResponseError as e:
            return f"[{model} error]: {e}"

    def least_resistance(self, task: str) -> str:
        """Fast flow — grit handles it, low friction."""
        return self._call(self.grit_model, task)

    def most_resistance(self, task: str) -> str:
        """Generative friction — squire works harder, more structure emerges."""
        system = "You are a deep reasoning agent. Think slowly and structurally."
        return self._call(self.squire_model, task, system=system)

    def continuum(self, task: str) -> dict:
        """
        Interspecific zone — both models respond, arbiter synthesizes.
        This is where symbiogenesis happens.
        """
        grit_response = self._call(
            self.grit_model, task
        )
        squire_response = self._call(
            self.squire_model, task,
            system="Extend, challenge, or deepen the following with structural reasoning."
        )
        synthesis_prompt = (
            f"Original task: {task}\n\n"
            f"Fast response (grit):\n{grit_response}\n\n"
            f"Deep response (squire):\n{squire_response}\n\n"
            "Synthesize these into one emergent answer. "
            "Find what neither said alone."
        )
        synthesis = self._call(self.arbiter_model, synthesis_prompt)

        return {
            "grit": grit_response,
            "squire": squire_response,
            "synthesis": synthesis,
            "path": "continuum"
        }

    def route(self, task: str, resistance: float = 0.5) -> dict:
        """
        resistance: 0.0 (pure flow) → 1.0 (pure friction)
        The continuum between is where interspecific structure forms.
        """
        if resistance < 0.3:
            return {"path": "least", "response": self.least_resistance(task)}
        elif resistance > 0.7:
            return {"path": "most", "response": self.most_resistance(task)}
        else:
            return self.continuum(task)
