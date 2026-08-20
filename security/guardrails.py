from dataclasses import dataclass
from typing import Any, Dict

from security.pii import mask_payload
from security.prompt_guard import inspect_text

@dataclass
class GuardrailDecision:
    allowed: bool
    requires_human_review: bool
    reason: str
    payload: Dict[str, Any]

def evaluate_dispute(dispute_text: str, payload: Dict[str, Any] | None = None) -> GuardrailDecision:
    result = inspect_text(dispute_text)

    if result.blocked:
        return GuardrailDecision(
            allowed=False,
            requires_human_review=True,
            reason="Prompt injection detected: " + ", ".join(result.reasons),
            payload={"guardrail": "PROMPT_INJECTION", "reasons": result.reasons},
        )

    masked = mask_payload(payload or {"dispute_text": dispute_text})
    return GuardrailDecision(
        allowed=True,
        requires_human_review=False,
        reason="Allowed after PII masking.",
        payload=masked,
    )
