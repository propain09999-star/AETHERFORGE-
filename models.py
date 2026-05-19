# code/grit/models.py
"""
AETHORFORGE Grit Tier - Ultra-Tiny Models
These are the smallest, fastest models that run on the phone itself.
"""

class GritModel:
    def __init__(self, name="tinyllama"):
        self.name = name
        print(f" {name} model initialized on-device")

    def process(self, task: str) -> str:
        # Simulate very fast on-device response
        if "scan" in task.lower() or "check" in task.lower():
            return "Quick scan complete. No immediate threats detected."
        elif "zero-day" in task.lower():
            return "Legacy pattern matched. Flagging for Squire review."
        return "Task processed at edge level."


class NanoModel(GritModel):
    def __init__(self):
        super().__init__("Nano")
    
    def process(self, task: str) -> str:
        return " Atomic task completed in <50ms."


class QuarkModel(GritModel):
    def __init__(self):
        super().__init__("Quark")
    
    def process(self, task: str) -> str:
        return " Metadata triage finished."


# Simple factory to pick the right tiny model
def get_grit_model(model_type: str = "nano"):
    if model_type.lower() == "quark":
        return QuarkModel()
    elif model_type.lower() == "nano":
        return NanoModel()
    else:
        return GritModel("tinyllama")


# Test it
if __name__ == "__main__":
    model = get_grit_model("nano")
    print(model.process("Scan for zero-day"))
