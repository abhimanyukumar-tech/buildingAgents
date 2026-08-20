from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

@dataclass
class ReviewRequest:
    review_id: str
    transaction_id: str
    reason: str
    proposed_state: str
    payload: Dict[str, Any]
    created_at: str

class HumanReviewQueue:
    def __init__(self):
        self._items = []

    def create(self, transaction_id, reason, proposed_state="QUERY", payload=None):
        review = ReviewRequest(
            review_id=f"REV-{len(self._items) + 1:05d}",
            transaction_id=transaction_id,
            reason=reason,
            proposed_state=proposed_state,
            payload=payload or {},
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._items.append(review)
        return review

    def pending(self):
        return list(self._items)

    def approve(self, review_id):
        for item in self._items:
            if item.review_id == review_id:
                return {"review_id": review_id, "decision": "APPROVED"}
        raise KeyError(f"Review request not found: {review_id}")

    def reject(self, review_id):
        for item in self._items:
            if item.review_id == review_id:
                return {"review_id": review_id, "decision": "REJECTED"}
        raise KeyError(f"Review request not found: {review_id}")
