import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from ranking_evaluation import (
    evaluate_ranking,
    evaluate_ground_truth,
    calculate_hit_rates,
)


def test_known_sku_ranking_returns_rank():
    result = evaluate_ranking(
        "SKU-00001",
        "B-04-04-02",
    )

    assert result["rank"] is not None
    assert result["rank"] >= 1


def test_known_sku_is_in_top_three():
    result = evaluate_ranking(
        "SKU-00001",
        "B-04-04-02",
    )

    assert result["top_3"] is True


def test_ground_truth_evaluation_returns_all_cases():
    ground_truth = pd.read_csv("data/ground_truth.csv")

    results = evaluate_ground_truth(ground_truth)

    assert len(results) == len(ground_truth)


def test_hit_rates_are_valid_percentages():
    ground_truth = pd.read_csv("data/ground_truth.csv")

    results = evaluate_ground_truth(ground_truth)
    rates = calculate_hit_rates(results)

    assert 0 <= rates["top_1_hit_rate"] <= 100
    assert 0 <= rates["top_3_hit_rate"] <= 100
    assert 0 <= rates["top_5_hit_rate"] <= 100


def test_top_3_hit_rate_for_ground_truth():
    ground_truth = pd.read_csv("data/ground_truth.csv")

    results = evaluate_ground_truth(ground_truth)
    rates = calculate_hit_rates(results)

    assert rates["top_3_hit_rate"] == 100.0