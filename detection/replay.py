"""Classical layer: replay protection (one-time key ids + freshness window). Quantum physics alone does NOT stop replay."""
import config as C


class ReplayGuard:
    def __init__(self):
        self.used_keys = set()

    def check(self, key_id: str, timestamp: float, now: float):
        if key_id in self.used_keys:
            return False, "key already used (one-time key replayed)"
        if abs(now - timestamp) > C.FRESHNESS_SECONDS:
            return False, "timestamp outside freshness window (stale signature)"
        return True, "fresh"

    def consume(self, key_id: str):
        self.used_keys.add(key_id)
