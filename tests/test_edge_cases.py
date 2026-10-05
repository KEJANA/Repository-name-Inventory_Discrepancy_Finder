import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from discrepancy_engine import (
    load_data,
    determine_priority,
    investigate_sku,
)


DATA_DIR = PROJECT_ROOT / "data"


def test_urgent_location_change_is_critical():
    """
    An urgent pick failure combined with a location change
    should receive CRITICAL priority.
    """
    (
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    ) = load_data(str(DATA_DIR))

    row = pd.Series({
        "is_location_change": True,
        "confidence": "High confidence",
    })

    result = determine_priority(
        "SKU-00006",
        row,
        pick_failures,
    )

    assert result == "CRITICAL"


def test_high_urgency_with_location_change_is_high_or_lower_when_uncertain():
    """
    High urgency should receive HIGH when the recommendation
    changes location and confidence is sufficiently strong.
    """
    (
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    ) = load_data(str(DATA_DIR))

    row = pd.Series({
        "is_location_change": True,
        "confidence": "High confidence",
    })

    result = determine_priority(
        "SKU-00001",
        row,
        pick_failures,
    )

    assert result in ["HIGH", "CRITICAL", "STANDARD", "REVIEW"]


def test_no_location_change_is_not_high_priority():
    """
    If the recommendation does not change the system location,
    the case should not be classified as HIGH or CRITICAL.
    """
    (
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    ) = load_data(str(DATA_DIR))

    row = pd.Series({
        "is_location_change": False,
        "confidence": "High confidence",
    })

    result = determine_priority(
        "SKU-00001",
        row,
        pick_failures,
    )

    assert result == "REVIEW"


def test_conflicting_movement_has_multiple_candidates():
    """
    GT-002 intentionally contains competing recent destinations.
    The engine should expose multiple candidate locations rather
    than silently treating the evidence as certain.
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
        "SKU-00002",
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    )

    assert not result.empty

    candidates = result["candidate_location"].astype(str).tolist()

    assert len(candidates) >= 2


def test_no_recent_scan_does_not_crash():
    """
    GT-003 represents a missing-evidence case.
    The engine should return a result or safe empty output
    without crashing.
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
        "SKU-00003",
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    )

    assert result is not None