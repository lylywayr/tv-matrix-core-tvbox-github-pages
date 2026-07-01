from tv_matrix.models import SourceCandidate, SourceFormat, ValidationResult
from tv_matrix.scoring import label_for_score, score_result


def test_score_success_result():
    result = ValidationResult(
        candidate=SourceCandidate(name="x", url="https://example.com"),
        checked_at="2026-01-01T00:00:00+00:00",
        ok=True,
        http_status=200,
        elapsed_ms=1000,
        content_format=SourceFormat.TVBOX_JSON,
        content_quality=1.0,
        valid_item_count=5,
        tcp_ok=True,
    )
    score = score_result(result, {"records": []}, {"weights": {}})
    assert score > 80
    assert label_for_score(score, result.elapsed_ms) in {"快", "稳定"}
