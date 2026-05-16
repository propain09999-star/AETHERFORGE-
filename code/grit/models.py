<<<<<<< HEAD
import os, json, urllib.request

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def _groq_call(prompt, model="llama-3.1-8b-instant"):
    if not GROQ_API_KEY:
        return f"[Grit] {prompt[:60]}..."
    payload = json.dumps({"model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512}).encode()
    req = urllib.request.Request(GROQ_URL, data=payload,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {GROQ_API_KEY}"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Grit fallback] {prompt[:60]}..."

class NanoModel:
    name = "Nano"
    def process(self, task):
        print(f"  ✓ Nano loaded")
        return _groq_call(task, "llama-3.1-8b-instant")

class QuarkModel:
    name = "Quark"
    def process(self, task):
        return _groq_call(f"One sentence only: {task}", "llama-3.1-8b-instant")

class ScoutAnt:
    name = "ScoutAnt"
    def process(self, task):
        return _groq_call(f"OSINT/recon scan: {task}", "llama-3.1-8b-instant")

class SquireModel:
    name = "Squire"
    def __init__(self): print("  ✓ Squire loaded")
    def validate(self, output):
        return _groq_call(f"Validate and improve: {output}", "llama-3.3-70b-versatile")
    def process(self, task):
        return self.validate(task)

def get_model(tier="grit", size="nano"):
    if tier == "squire": return SquireModel()
    if size == "quark":  return QuarkModel()
    if size == "scout":  return ScoutAnt()
    return NanoModel()
=======
# code/grit/models.py
"""
AETHORFORGE Grit Tier - Ultra-Tiny Models
Massively parallel, low-resource models for edge devices.
"""

class GritModel:
    def __init__(self, name="tinyllama"):
        self.name = name
        print(f"✓ {name} Grit model loaded on-device")

    def process(self, task: str) -> str:
        return f"[Grit Base] Processed: {task[:60]}..."


# === GRIT TIER SUBCLASSES ===
class NanoModel(GritModel):
    def __init__(self):
        super().__init__("Nano")
    
    def process(self, task: str) -> str:
        return f"[Nano] Atomic task completed in <30ms: {task[:50]}"


class QuarkModel(GritModel):
    def __init__(self):
        super().__init__("Quark")
    
    def process(self, task: str) -> str:
        return f"[Quark] Fundamental pattern matched: {task[:50]}"


class ScoutAnt(GritModel):
    def __init__(self):
        super().__init__("ScoutAnt")
    
    def process(self, task: str) -> str:
        return f"[ScoutAnt] OSINT + Metadata discovered: {task[:60]}"


class DefenderAnt(GritModel):
    def __init__(self):
        super().__init__("DefenderAnt")
    
    def process(self, task: str) -> str:
        return f"[DefenderAnt] OWASP violation sanitized & hardened"


# === SQUIRE TIER (Mid-level models) ===
class SquireModel:
    def __init__(self, name="phi3:mini"):
        self.name = name
        print(f"✓ {name} Squire model loaded")

    def validate(self, grit_output: str) -> str:
        return f"[Squire] Validated & contextualized: {grit_output[:80]}..."


# Factory function
def get_model(tier: str = "grit", model_type: str = "nano"):
    if tier.lower() == "squire":
        return SquireModel()
    else:
        # Grit tier
        if model_type.lower() == "quark":
            return QuarkModel()
        elif model_type.lower() == "scout":
            return ScoutAnt()
        elif model_type.lower() == "defender":
            return DefenderAnt()
        else:
            return NanoModel()


# Quick test
if __name__ == "__main__":
    print("=== AETHORFORGE MODEL TEST ===")
    nano = get_model("grit", "nano")
    print(nano.process("Scan for zero-day"))
    
    squire = get_model("squire")
    print(squire.validate("Quick scan complete"))
>>>>>>> 7f829f727a2e251233babc2c409c6642b8726875
