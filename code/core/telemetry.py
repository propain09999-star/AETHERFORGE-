import time
from collections import deque
from code.core.router import HybridPolymathRouter
from code.core.sysstats import snapshot


class TelemetryEngine:
    def __init__(self):
        self.router = HybridPolymathRouter()
        self.last_query = "system boot"
        self.history = deque(maxlen=80)

    def update_query(self, query: str):
        self.last_query = query
        self.history.appendleft({
            "timestamp": time.time(),
            "type": "query",
            "value": query
        })

    def generate(self) -> dict:
        routing = self.router.evaluate(self.last_query)
        stats = snapshot()

        snapshot_data = {
            "timestamp": time.time(),
            "routing_engine": routing["engine"],
            "active_hardware_kernel": routing["active_kernel"],
            "kv_cache_savings": f'{routing["kv_cache_savings_pct"]}%',
            "allocation_justification": routing["reasoning"],
            "system": stats
        }

        self.history.appendleft({
            "timestamp": snapshot_data["timestamp"],
            "type": "telemetry",
            "value": snapshot_data
        })

        return snapshot_data

    def get_history(self):
        return list(self.history)
