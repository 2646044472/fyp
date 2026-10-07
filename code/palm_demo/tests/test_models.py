from models import CheckoutResult, IdentificationResult, PaymentResult, ROIResult
from palm_roi import ROIStatus


def test_result_objects_are_explicit_and_immutable():
    result = ROIResult("RETRY", None, "EMPTY_FRAME", {}, 1.0)
    assert result.status == "RETRY"
    assert IdentificationResult("UNKNOWN", None, 0.4, None, 2.0).user_id is None
    assert PaymentResult("SUCCESS", "tx-1", 8000).balance_cents == 8000
    assert CheckoutResult("RETRY", None, None, None, None, "bad", {}).reason == "bad"


def test_dynamic_roi_status_preserves_its_failure_evidence():
    status = ROIStatus(None, "no_hand", reason="span_too_small", diagnostics={"mcp_span_px": 61.0})

    payload = status.as_dict()

    assert payload["roi_reason"] == "span_too_small"
    assert payload["roi_diagnostics"]["mcp_span_px"] == 61.0
