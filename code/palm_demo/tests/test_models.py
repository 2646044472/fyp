from models import CheckoutResult, IdentificationResult, PaymentResult, ROIResult


def test_result_objects_are_explicit_and_immutable():
    result = ROIResult("RETRY", None, "EMPTY_FRAME", {}, 1.0)
    assert result.status == "RETRY"
    assert IdentificationResult("UNKNOWN", None, 0.4, None, 2.0).user_id is None
    assert PaymentResult("SUCCESS", "tx-1", 8000).balance_cents == 8000
    assert CheckoutResult("RETRY", None, None, None, None, "bad", {}).reason == "bad"
