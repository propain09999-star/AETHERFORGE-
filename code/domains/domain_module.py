import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from code.grit.models import _groq_call

DOMAIN_SYSTEMS = {
    "energy": "You are an energy sovereignty analyst. Focus on: micro-grid orchestration, VPP management, low-power compute modes, solar/battery optimization.",
    "physical": "You are a physical AI security analyst. Focus on: sensor spoofing defense, hardware soul verification, drone/robot security, supply chain integrity.",
    "biotech": "You are a bio-sovereignty analyst. Focus on: local-first medical AI, PQC-encrypted genomic privacy, O2O bio-vault architecture, BIOSECURE Act compliance.",
    "finance": "You are a sovereign finance analyst. Focus on: flash-loan attack detection, smart contract auditing, DeFi stability protocols, anti-fragile wealth strategies.",
    "learning": "You are a learning accelerator. Focus on: knowledge gap identification, Socratic scaffolding, adversarial learning challenges, skill progression tracking.",
}

class DomainModule:
    def __init__(self):
        print("✓ Domain module online")
        print(f"  Domains: {', '.join(DOMAIN_SYSTEMS.keys())}")

    def query(self, domain: str, question: str) -> str:
        system = DOMAIN_SYSTEMS.get(domain.lower())
        if not system:
            available = ", ".join(DOMAIN_SYSTEMS.keys())
            return f"Unknown domain. Available: {available}"
        return _groq_call(f"{system}\n\nQuery: {question}",
                          "llama-3.3-70b-versatile")

    def auto_route(self, question: str) -> str:
        keywords = {
            "energy":   ["power","grid","solar","battery","energy","watt"],
            "physical": ["robot","drone","sensor","hardware","physical","actuator"],
            "biotech":  ["bio","dna","medical","health","genetic","genomic"],
            "finance":  ["defi","crypto","finance","money","wallet","token","flash"],
            "learning": ["learn","teach","skill","study","explain","understand"],
        }
        q = question.lower()
        for domain, words in keywords.items():
            if any(w in q for w in words):
                return self.query(domain, question)
        return self.query("learning", question)

if __name__ == "__main__":
    d = DomainModule()
    print(d.auto_route("How do I secure a DeFi smart contract?"))

