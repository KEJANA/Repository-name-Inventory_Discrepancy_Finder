import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from discrepancy_engine import (
    load_data,
    baseline_last_known_location,
)


DATA_DIR = PROJECT_ROOT / "data"


def test_baseline_returns_location_for_gt001():
    """
    GT-001 has a known relocation event.
    The simple baseline should return the latest recorded
    put-away/move destination.
    """
    inventory, putaway, moves, pick_failures, cycle_counts, locations = load_data(
        str(DATA_DIR)
    )

    gt = pd.read_csv(DATA_DIR / "ground_truth.csv")
    case = gt[gt["case_id"] == "GT-001"].iloc[0]

    result = baseline_last_known_location(
        case["sku"],
        inventory,
        putaway,
        moves,
    )

    assert result is not None
    assert "location" in result
    assert result["location"] != ""


def test_baseline_uses_latest_event():
    """
    The baseline must choose the location from the latest
    put-away/move event rather than an older event.
    """
    inventory, putaway, moves, pick_failures, cycle_counts, locations = load_data(
        str(DATA_DIR)
    )

    sku = "SKU-00001"

    result = baseline_last_known_location(
        sku,
        inventory,
        putaway,
        moves,
    )

    assert result is not None

    events = []

    p = putaway[putaway["sku"] == sku]
    for _, row in p.iterrows():
        events.append(
            {
                "location": row["destination_location"],
                "timestamp": row["timestamp"],
            }
        )

    m = moves[moves["sku"] == sku]
    for _, row in m.iterrows():
        events.append(
            {
                "location": row["to_location"],
                "timestamp": row["timestamp"],
            }
        )

    assert events

    expected_latest = max(
        events,
        key=lambda x: x["timestamp"]
    )

    assert result["location"] == expected_latest["location"]
    assert result["timestamp"] == expected_latest["timestamp"]


def test_baseline_is_not_perfect_for_recoverable_cases():
    """
    Verify that the simple baseline does not solve every
    recoverable ground-truth case.
    """
    inventory, putaway, moves, pick_failures, cycle_counts, locations = load_data(
        str(DATA_DIR)
    )

    gt = pd.read_csv(DATA_DIR / "ground_truth.csv")

    recoverable_types = [
        "CLEAR_RELOCATION",
        "URGENT_DEMAND_DISRUPTION",
    ]

    recoverable = gt[
        gt["case_type"].isin(recoverable_types)
    ]

    baseline_hits = 0

    for _, case in recoverable.iterrows():
        result = baseline_last_known_location(
            case["sku"],
            inventory,
            putaway,
            moves,
        )

        target = str(case["actual_candidate_location"])

        if result is not None:
            baseline_hits += int(
                str(result["location"]) == target
            )

    assert baseline_hits < len(recoverable)


def test_baseline_result_contains_timestamp():
    """
    Baseline output should include the timestamp of the
    last known location evidence.
    """
    inventory, putaway, moves, pick_failures, cycle_counts, locations = load_data(
        str(DATA_DIR)
    )

    result = baseline_last_known_location(
        "SKU-00001",
        inventory,
        putaway,
        moves,
    )

    assert result is not None
    assert "timestamp" in result
    assert pd.notna(result["timestamp"])