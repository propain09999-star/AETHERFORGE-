import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from code.grit.models import _groq_call

class ForgeBuilder:
    def __init__(self):
        print("✓ Forge Builder online")

    def generate(self, prompt: str, domain: str = "general") -> str:
        return _groq_call(
            f"You are a senior {domain} engineer. Generate clean, production-ready code for: {prompt}. Include comments.",
            "llama-3.3-70b-versatile"
        )

    def full_pipeline(self, prompt: str) -> dict:
        print(f"  [Forge] Building: {prompt[:60]}...")
        code = self.generate(prompt)
        review = _groq_call(
            f"Review this code for bugs and security issues. Be specific:\n{code}",
            "llama-3.3-70b-versatile"
        )
        return {"code": code, "review": review, "status": "ready"}

if __name__ == "__main__":
    f = ForgeBuilder()
    result = f.full_pipeline("bug bounty recon script that checks for open S3 buckets")
    print(result["code"][:500])

