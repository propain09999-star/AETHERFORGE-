class HybridRouter:
    def route(self, task: dict) -> dict:
        # Grit tier first (tiny models)
        grit_out = "Grit processed atomic task"
        
        # Escalate based on complexity
        if task.get("complexity", 0) > 5:
            squire_out = "Squire validated context"
            final = "Overlord strategic decision"
            return {"status": "approved", "result": final, "tier": "Overlord"}
        return {"status": "approved", "result": grit_out, "tier": "Grit"}
