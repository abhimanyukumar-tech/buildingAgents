from decimal import Decimal
from models import money, state_from_payload
from logger import JSONStateDeltaLogger

END_STATES = {"OPEN", "PARTIAL MATCH", "CLOSED", "UAC", "UIC", "QUERY"}
TOLERANCE_LIMIT = Decimal("5.00")

ADJUSTMENT_CODES = {
    "U01": "Meter Reading Dispute",
    "U02": "Service Outage Credit",
    "U03": "Estimated Bill Correction",
    "U04": "Assistance / Discount Adjustment",
    "U05": "Late Fee Waiver",
}

ADJUSTMENT_PATTERNS = [
    ("U01", ["meter", "estimated", "high reading", "read appears"]),
    ("U02", ["outage", "service outage", "sla credit"]),
    ("U03", ["actual meter", "actual read", "re-read", "estimated bill correction"]),
    ("U04", ["senior", "low-income", "subsidy", "discount", "assistance"]),
    ("U05", ["late fee", "late-payment", "goodwill", "first-time occurrence"]),
]

class ReconciliationEngine:
    def __init__(self, log_path="system.log"):
        self.audit = JSONStateDeltaLogger(log_path)

    def _transition(self, state, to_state=None, rule_context=None, **updates):
        previous = state["current_state"]
        state.update(updates)
        if to_state:
            state["current_state"] = to_state
        payment = state["payment_transaction"]
        self.audit.log_state_delta(
            payment["transaction_id"],
            payment.get("account_number"),
            previous,
            state["current_state"],
            rule_context,
            updates,
        )
        state["audit_trail"].append(
            f"{previous} -> {state['current_state']} | rule={rule_context or {}}"
        )
        return state

    def _map_adjustment(self, text):
        text = text.lower()
        for code, terms in ADJUSTMENT_PATTERNS:
            if any(term in text for term in terms):
                return code, ADJUSTMENT_CODES[code]
        return None, None

    def _priority_match(self, p, b, d):
        # Rules 1–6, evaluated sequentially as specified.
        if (
            p.get("account_number") == b.get("account_number")
            and p.get("reference_number") == b.get("bill_id")
            and money(p["amount_paid"]) == money(b["total_amount"])
        ):
            return 1, "2-Way"

        if (
            p.get("account_number") == b.get("account_number")
            and p.get("meter_id")
            and p.get("meter_id") == b.get("meter_id")
            and money(p["amount_paid"]) == money(b["total_amount"])
        ):
            return 2, "2-Way"

        if (
            p.get("account_number") == b.get("account_number")
            and p.get("reference_number") == b.get("bill_id")
            and p.get("bill_date")
            and p.get("bill_date") == b.get("bill_date")
            and money(p["amount_paid"]) == money(b["total_amount"])
        ):
            return 3, "2-Way"

        if p.get("account_number") == b.get("account_number"):
            return 4, "2-Way"

        if (
            d
            and p.get("reference_number") == b.get("bill_id")
            and p.get("account_number") == b.get("account_number")
            and p.get("bill_date") == b.get("bill_date")
        ):
            return 5, "3-Way"

        if (
            d
            and p.get("reference_number") == b.get("bill_id")
            and p.get("account_number") == b.get("account_number")
        ):
            return 6, "3-Way"

        return None, None

    def run(self, payment, billing=None, dispute=None):
        state = state_from_payload(payment, billing, dispute)
        p = state["payment_transaction"]
        b = state["billing_ar"]
        d = state["dispute_note"]

        if not p.get("account_number") and not p.get("customer_name"):
            return self._transition(
                state, "UIC", confidence=1.0
            )

        if b is None:
            return self._transition(
                state, "UAC", confidence=0.95
            )

        priority, match_type = self._priority_match(p, b, d)
        if priority is None:
            return self._transition(
                state, "QUERY", confidence=0.40, requires_human_review=True
            )

        variance = money(b["total_amount"]) - money(p["amount_paid"])
        state = self._transition(
            state,
            matched_priority_rule=priority,
            match_type=match_type,
            amount_paid=float(money(p["amount_paid"])),
            bill_amount=float(money(b["total_amount"])),
            variance=float(variance),
            confidence=0.95 if priority <= 4 else 0.90,
            rule_context={"priority_rule": priority, "match_type": match_type},
        )

        if variance <= 0:
            return self._transition(
                state, "CLOSED",
                approved_settlement_amount=float(money(p["amount_paid"]))
            )

        if d:
            code, category = self._map_adjustment(d.get("unstructured_notes", ""))
            if code:
                return self._transition(
                    state, "PARTIAL MATCH",
                    adjustment_code=code,
                    adjustment_category=category,
                    approved_settlement_amount=float(money(p["amount_paid"])),
                    held_dispute_variance=float(variance),
                    rule_context={"priority_rule": priority, "adjustment_code": code},
                )

        if variance <= TOLERANCE_LIMIT:
            return self._transition(
                state, "CLOSED",
                auto_write_off_amount=float(variance),
                approved_settlement_amount=float(money(p["amount_paid"])),
            )

        return self._transition(
            state, "QUERY", confidence=0.40, requires_human_review=True
        )
