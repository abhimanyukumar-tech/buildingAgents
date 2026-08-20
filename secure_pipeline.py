from audit import SecurityAuditLogger
from hitl import HumanReviewQueue
from security.guardrails import evaluate_dispute

class SecureReconciliationPipeline:
    """Security/HITL wrapper around the existing Stage 1/2 components."""

    def __init__(self, reconciliation_engine=None):
        self.engine = reconciliation_engine
        self.audit = SecurityAuditLogger()
        self.review_queue = HumanReviewQueue()

    def inspect(self, transaction_id, dispute_text, payload=None):
        decision = evaluate_dispute(dispute_text, payload)

        if not decision.allowed:
            review = self.review_queue.create(
                transaction_id=transaction_id,
                reason=decision.reason,
                proposed_state="QUERY",
                payload=decision.payload,
            )
            self.audit.write(
                "PROMPT_INJECTION_BLOCKED",
                transaction_id,
                "HUMAN_REVIEW",
                {"review_id": review.review_id, "reason": decision.reason},
            )
            return {
                "state": "QUERY",
                "requires_human_review": True,
                "review_id": review.review_id,
                "reason": decision.reason,
            }

        self.audit.write(
            "INPUT_ACCEPTED",
            transaction_id,
            "ALLOWED",
            {"pii_masked": True},
        )
        return {
            "state": "ALLOWED",
            "requires_human_review": False,
            "masked_payload": decision.payload,
        }
