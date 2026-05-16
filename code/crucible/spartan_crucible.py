import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from code.grit.models import _groq_call
from dataclasses import dataclass

@dataclass
class CrucibleVerdict:
    finding: str
    passed: bool
    confidence: int
    false_positive_risk: str
    recommendation: str
    def summary(self):
        s = "✅ PASSED" if self.passed else "❌ FAILED"
        return f"{s} | {self.confidence}% | FP: {self.false_positive_risk}\n→ {self.recommendation}"

class SpartanCrucible:
    def __init__(self): print("✓ Spartan Crucible online")

    def run(self, finding: str, target_context: str = "") -> CrucibleVerdict:
        print(f"  ⚔ Crucible: {finding[:60]}...")
        disproof = _groq_call(
            f"Try to DISPROVE this finding. Be brutal:\n{finding}",
            "llama-3.3-70b-versatile")
        verdict_raw = _groq_call(
            f"Finding: {finding}\nDisproof attempt: {disproof}\n"
            f"Return JSON only: {{\"passed\":true/false,\"confidence\":0-100,"
            f"\"false_positive_risk\":\"low/medium/high\",\"recommendation\":\"one sentence\"}}",
            "llama-3.3-70b-versatile")
        try:
            clean = verdict_raw.strip().strip("```json").strip("```").strip()
            v = json.loads(clean)
        except:
            v = {"passed": False, "confidence": 30,
                 "false_positive_risk": "high",
                 "recommendation": "Manual review required"}
        return CrucibleVerdict(
            finding=finding, passed=v.get("passed", False),
            confidence=v.get("confidence", 0),
            false_positive_risk=v.get("false_positive_risk", "unknown"),
            recommendation=v.get("recommendation", ""))
