import json
from datetime import datetime, timezone
from pathlib import Path

class SecurityAuditLogger:
    def __init__(self, path="security_audit.log"):
        self.path = Path(path)

    def write(self, event, transaction_id=None, decision=None, details=None):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "transaction_id": transaction_id,
            "decision": decision,
            "details": details or {},
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
        return record
