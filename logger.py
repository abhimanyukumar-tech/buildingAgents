import json
from datetime import datetime, timezone
from pathlib import Path

class JSONStateDeltaLogger:
    def __init__(self, path="system.log"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log_state_delta(
        self, transaction_id, account_number, from_state, to_state,
        rule_context=None, delta_payload=None
    ):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "telemetry_event": "STATE_DELTA_TRANSITION",
            "transaction_id": transaction_id,
            "account_number": account_number,
            "state_transition": {"from": from_state, "to": to_state},
            "rule_context": rule_context or {},
            "delta_payload": delta_payload or {},
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, default=str) + "\n")
        return event

def read_telemetry_events(path="system.log"):
    p = Path(path)
    if not p.exists():
        return []
    return [
        json.loads(line)
        for line in p.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
