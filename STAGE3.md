# Stage 3 — Security, Guardrails, Audit, and HITL

This stage wraps the Stage 1/2 reconciliation flow with security controls.

## Components

- `security/pii.py` — masks common email, phone, account, and card-like values.
- `security/prompt_guard.py` — detects common prompt-injection/instruction-override patterns.
- `security/guardrails.py` — blocks detected attacks and masks PII before external-model use.
- `audit.py` — JSON-line security audit logger.
- `hitl.py` — human review queue for QUERY/blocked cases.
- `secure_pipeline.py` — orchestration wrapper.

## Test

```bash
python tests_stage3.py
```

Expected:

```text
Stage 3 tests passed.
```

## Important

This is a defensive application-layer baseline, not a claim of complete security.
Production deployment should add Azure-side identity/access controls, secret
management, network restrictions, content filtering, rate limits, monitoring,
and formal security testing.
