from models import PaymentTransactionPayload, BillingARPayload, DisputeNotePayload
from reconciliation import ReconciliationEngine

def main():
    engine = ReconciliationEngine()

    tests = [
        (
            "Perfect Match",
            PaymentTransactionPayload("TXN-11000", "ACC-77210", 482.50, "BILL-4471"),
            BillingARPayload("BILL-4471", "ACC-77210", 482.50),
            None,
        ),
        (
            "Meter Reading Dispute",
            PaymentTransactionPayload("TXN-6055", "ACC-77210", 560.00, "BILL-4471"),
            BillingARPayload("BILL-4471", "ACC-77210", 610.00),
            DisputeNotePayload(
                "DSP-330",
                "Meter read appears estimated high in error ($50 credit requested).",
            ),
        ),
        (
            "Tolerance Write-Off",
            PaymentTransactionPayload("TXN-9002", "ACC-88510", 148.00, "BILL-2290"),
            BillingARPayload("BILL-2290", "ACC-88510", 150.00),
            None,
        ),
        (
            "UAC",
            PaymentTransactionPayload(
                "TXN-5000", None, 275.00, customer_name="Sunrise Apartments LLC"
            ),
            None,
            None,
        ),
        (
            "UIC",
            PaymentTransactionPayload("TXN-UIC-001", None, 340.00),
            None,
            None,
        ),
    ]

    for name, payment, billing, dispute in tests:
        result = engine.run(payment, billing, dispute)
        print(f"\n{name}")
        print(f"  State: {result['current_state']}")
        print(f"  Priority: {result.get('matched_priority_rule')}")
        print(f"  Adjustment: {result.get('adjustment_code')}")
        print(f"  Settlement: ${result.get('approved_settlement_amount', 0):.2f}")

if __name__ == "__main__":
    main()
