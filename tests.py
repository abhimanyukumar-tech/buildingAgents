from models import PaymentTransactionPayload, BillingARPayload, DisputeNotePayload
from reconciliation import ReconciliationEngine

engine = ReconciliationEngine("test_system.log")

def test_perfect_match():
    r = engine.run(
        PaymentTransactionPayload("TXN-11000", "ACC-77210", 482.50, "BILL-4471"),
        BillingARPayload("BILL-4471", "ACC-77210", 482.50),
    )
    assert r["matched_priority_rule"] == 1
    assert r["current_state"] == "CLOSED"

def test_dispute():
    r = engine.run(
        PaymentTransactionPayload("TXN-6055", "ACC-77210", 560.00, "BILL-4471"),
        BillingARPayload("BILL-4471", "ACC-77210", 610.00),
        DisputeNotePayload("DSP-330", "Meter read appears estimated high in error."),
    )
    assert r["adjustment_code"] == "U01"
    assert r["current_state"] == "PARTIAL MATCH"
    assert r["held_dispute_variance"] == 50.0

def test_tolerance():
    r = engine.run(
        PaymentTransactionPayload("TXN-9002", "ACC-88510", 148.00, "BILL-2290"),
        BillingARPayload("BILL-2290", "ACC-88510", 150.00),
    )
    assert r["auto_write_off_amount"] == 2.0
    assert r["current_state"] == "CLOSED"

def test_uac():
    r = engine.run(
        PaymentTransactionPayload("TXN-5000", None, 275.00, customer_name="Sunrise Apartments LLC")
    )
    assert r["current_state"] == "UAC"

def test_uic():
    r = engine.run(PaymentTransactionPayload("TXN-UIC-001", None, 340.00))
    assert r["current_state"] == "UIC"

if __name__ == "__main__":
    test_perfect_match()
    test_dispute()
    test_tolerance()
    test_uac()
    test_uic()
    print("All tests passed.")
