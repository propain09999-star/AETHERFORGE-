import json
from pathlib import Path
from datetime import datetime
from code.grit.models import _groq_call

REVENUE_FILE = Path.home() / "aethorforge/data/revenue.json"

class RevenueTracker:
    def __init__(self):
        REVENUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.data = json.loads(REVENUE_FILE.read_text()) \
            if REVENUE_FILE.exists() else {"submissions": [], "total": 0}
        print("✓ Revenue tracker online")

    def log_submission(self, program: str, vuln: str,
                       severity: str, payout_est: str):
        entry = {
            "date":      datetime.now().isoformat(),
            "program":   program,
            "vuln":      vuln,
            "severity":  severity,
            "payout_est": payout_est,
            "status":    "submitted"
        }
        self.data["submissions"].append(entry)
        REVENUE_FILE.write_text(json.dumps(self.data, indent=2))
        return entry

    def estimate_payout(self, finding: str, program: str) -> str:
        return _groq_call(
            f"Estimate HackerOne payout range for this finding on {program}:\n{finding}\n"
            f"Give: severity tier (P1-P4), typical payout range in USD, "
            f"and likelihood of acceptance. Be specific.",
            "llama-3.1-8b-instant"
        )

    def summary(self) -> dict:
        subs = self.data["submissions"]
        return {
            "total_submissions": len(subs),
            "programs": list(set(s["program"] for s in subs)),
            "recent":   subs[-3:] if subs else []
        }

if __name__ == "__main__":
    t = RevenueTracker()
    print(t.estimate_payout("IDOR on /api/users/123", "HackerOne"))
    print(t.summary())

