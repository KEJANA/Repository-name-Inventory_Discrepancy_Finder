import sys
from pathlib import Path

import pandas as pd

# Allow pytest to import discrepancy_engine.py from the project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from discrepancy_engine import (
    load_data,
    investigate_sku,
    find_discrepancies,
)


DATA_DIR = PROJECT_ROOT / "data"


def test_load_data_contains_all_operational_signals():
    """
    Verify that the prototype loads all five operational signals
    plus inventory and location master data.
    """
    inventory, putaway, moves, pick_failures, cycle_counts, locations = load_data(
        str(DATA_DIR)
    )

    assert not inventory.empty
    assert not putaway.empty
    assert not moves.empty
    assert not pick_failures.empty
    assert not cycle_counts.empty
    assert not locations.empty

    assert "sku" in inventory.columns
    assert "destination_location" in putaway.columns
    assert "to_location" in moves.columns
    assert "expected_location" in pick_failures.columns
    assert "location" in cycle_counts.columns
    assert "location_id" in locations.columns


def test_investigate_ground_truth_skus():
    """
    Every ground-truth SKU should produce an investigation result.
    """
    (
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    ) = load_data(str(DATA_DIR))

    ground_truth = pd.read_csv(DATA_DIR / "ground_truth.csv")

    for sku in ground_truth["sku"]:
        result = investigate_sku(
            sku,
            inventory,
            putaway,
            moves,
            pick_failures,
            cycle_counts,
            locations,
        )

        assert not result.empty, f"No investigation result for {sku}"


def test_investigation_result_has_required_columns():
    """
    Verify that investigation output contains the fields required
    by the stakeholder-facing application.
    """
    (
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    ) = load_data(str(DATA_DIR))

    result = investigate_sku(
        "SKU-00001",
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    )

    required_columns = {
        "sku",
        "candidate_location",
        "evidence_score",
        "confidence",
        "evidence_strength",
        "evidence",
        "recommended_action",
        "rank",
    }

    assert required_columns.issubset(set(result.columns))


def test_investigation_scores_are_sorted():
    """
    Candidate locations should be ranked from strongest evidence
    to weakest evidence.
    """
    (
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    ) = load_data(str(DATA_DIR))

    result = investigate_sku(
        "SKU-00001",
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    )

    scores = result["evidence_score"].tolist()

    assert scores == sorted(scores, reverse=True)


def test_find_discrepancies_returns_expected_schema():
    """
    Verify the end-to-end discrepancy finder produces the fields
    required by the Streamlit investigation queue.
    """
    result = find_discrepancies(str(DATA_DIR))

    assert not result.empty

    required_columns = {
        "sku",
        "expected_location",
        "recommended_location",
        "evidence_score",
        "confidence",
        "recommended_action",
        "is_location_change",
        "priority",
    }

    assert required_columns.issubset(set(result.columns))


def test_invalid_locations_are_not_recommended_for_gt004():
    """
    GT-004 represents an invalid/inactive-location case.
    The engine should not recommend the invalid location as a
    safe correction.
    """
    (
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    ) = load_data(str(DATA_DIR))

    ground_truth = pd.read_csv(DATA_DIR / "ground_truth.csv")
    case = ground_truth[ground_truth["case_id"] == "GT-004"].iloc[0]

    invalid_location = str(case["actual_candidate_location"])

    result = investigate_sku(
        case["sku"],
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    )

    assert not result.empty

    top_location = str(result.iloc[0]["candidate_location"])

    assert top_location != invalid_location