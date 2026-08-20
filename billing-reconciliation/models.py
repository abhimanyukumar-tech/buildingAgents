from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

@dataclass
class PaymentTransactionPayload:
    transaction_id: str
    account_number: Optional[str]
    amount_paid: Decimal
    reference_number: Optional[str] = None
    customer_name: Optional[str] = None
    meter_id: Optional[str] = None
    bill_date: Optional[str] = None

    def __post_init__(self):
        self.amount_paid = money(self.amount_paid)

@dataclass
class BillingARPayload:
    bill_id: str
    account_number: str
    total_amount: Decimal
    meter_id: Optional[str] = None
    bill_date: Optional[str] = None

    def __post_init__(self):
        self.total_amount = money(self.total_amount)

@dataclass
class DisputeNotePayload:
    dispute_id: str
    unstructured_notes: str
    adjustment_code: Optional[str] = None

def state_from_payload(payment, billing=None, dispute=None):
    return {
        "payment_transaction": asdict(payment),
        "billing_ar": asdict(billing) if billing else None,
        "dispute_note": asdict(dispute) if dispute else None,
        "current_state": "OPEN",
        "matched_priority_rule": None,
        "match_type": None,
        "adjustment_code": None,
        "adjustment_category": None,
        "amount_paid": float(payment.amount_paid),
        "bill_amount": float(billing.total_amount) if billing else 0.0,
        "variance": 0.0,
        "approved_settlement_amount": 0.0,
        "held_dispute_variance": 0.0,
        "auto_write_off_amount": 0.0,
        "confidence": 0.0,
        "requires_human_review": False,
        "audit_trail": [],
    }
