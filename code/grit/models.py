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
