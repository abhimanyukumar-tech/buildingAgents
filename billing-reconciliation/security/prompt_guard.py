import re
from dataclasses import dataclass
from typing import List

@dataclass
class GuardResult:
    blocked: bool
    reasons: List[str]
    sanitized_text: str

PATTERNS = [
    (r"ignore\s+(all\s+)?previous\s+instructions", "instruction_override"),
    (r"ignore\s+(all\s+)?prior\s+instructions", "instruction_override"),
    (r"system\s+prompt", "system_prompt_extraction"),
    (r"developer\s+message", "developer_message_extraction"),
    (r"reveal\s+(your|the)\s+(prompt|instructions)", "prompt_extraction"),
    (r"disregard\s+(the|all)\s+rules", "instruction_override"),
    (r"jailbreak", "jailbreak_keyword"),
    (r"do\s+not\s+follow\s+(the|your)\s+instructions", "instruction_override"),
]

def inspect_text(text: str) -> GuardResult:
    text = text or ""
    reasons = []
    lowered = text.lower()

    for pattern, reason in PATTERNS:
        if re.search(pattern, lowered):
            reasons.append(reason)

    # Keep the original business text intact for auditability, but do not pass
    # a detected attack to the external model.
    return GuardResult(
        blocked=bool(reasons),
        reasons=sorted(set(reasons)),
        sanitized_text=text if not reasons else "[PROMPT_INJECTION_BLOCKED]",
    )
