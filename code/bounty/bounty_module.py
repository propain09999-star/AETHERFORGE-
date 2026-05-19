import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from code.grit.models import _groq_call

class BountyModule:
    def __init__(self):
        print("✓ Bug Bounty module online")

    def scope_check(self, program: str) -> str:
        return _groq_call(
            f"Analyze this bug bounty program scope: {program}. "
            f"List: in-scope assets, payout tiers, what to hunt first for max ROI.",
            "llama-3.3-70b-versatile"
        )

    def recon(self, target: str) -> str:
        return _groq_call(
            f"Bug bounty recon plan for: {target}. Include: "
            f"subdomain enum, JS supply chain audit, historical endpoints via Wayback, "
            f"cloud bucket checks, CT log mining. Give exact tools and commands.",
            "llama-3.3-70b-versatile"
        )

    def write_report(self, finding: str) -> str:
        return _groq_call(
            f"Write a HackerOne-ready bug report for this finding:\n{finding}\n"
            f"Format: Title, Severity, CVSS, Summary, Steps to Reproduce (max 3), "
            f"Impact, PoC, Remediation.",
            "llama-3.3-70b-versatile"
        )

    def check_duplicate(self, finding: str) -> str:
        return _groq_call(
            f"Is this finding likely a duplicate on HackerOne/Bugcrowd? "
            f"What prior art should I check before submitting?\n{finding}",
            "llama-3.3-70b-versatile"
        )

if __name__ == "__main__":
    b = BountyModule()
    print(b.recon("target.com"))

