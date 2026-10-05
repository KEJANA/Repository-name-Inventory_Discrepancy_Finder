import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation import (
    calculate_baseline_effort,
    calculate_prototype_effort,
    calculate_effort_reduction,
    evaluate_sku,
)
def test_baseline_effort_is_positive_for_known_sku():
    result = evaluate_sku("SKU-00001")

    assert result["baseline_effort"] > 0


def test_prototype_effort_is_non_negative():
    result = evaluate_sku("SKU-00001")

    assert result["prototype_effort"] >= 0


def test_effort_reduction_calculation():
    reduction = calculate_effort_reduction(10, 4)

    assert reduction == 60.0


def test_zero_baseline_effort_returns_zero():
    reduction = calculate_effort_reduction(0, 4)

    assert reduction == 0.0


def test_evaluation_returns_required_fields():
    result = evaluate_sku("SKU-00001")

    required_fields = {
        "sku",
        "baseline_effort",
        "prototype_effort",
        "effort_reduction_percent",
    }

    assert required_fields.issubset(result.keys())