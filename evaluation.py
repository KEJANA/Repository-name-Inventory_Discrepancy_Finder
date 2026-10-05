import pandas as pd

from discrepancy_engine import (
    load_data,
    investigate_sku,
)


def calculate_baseline_effort(sku, putaway, moves):
    """
    Proxy for baseline investigation effort.

    The baseline requires checking the SKU's historical
    put-away and move records to determine the latest
    known location.

    Effort = number of historical event records inspected.
    """
    putaway_events = putaway[putaway["sku"] == sku]
    move_events = moves[moves["sku"] == sku]

    return len(putaway_events) + len(move_events)


def calculate_prototype_effort(result):
    """
    Proxy for prototype investigation effort.

    Effort = number of ranked candidate locations presented.
    """
    if result is None or result.empty:
        return 0

    return len(result)


def calculate_effort_reduction(baseline_effort, prototype_effort):
    """
    Calculate investigation-effort reduction percentage.
    """

    if baseline_effort <= 0:
        return 0.0

    return (
        (baseline_effort - prototype_effort)
        / baseline_effort
    ) * 100


def evaluate_sku(sku):
    """
    Compare baseline and prototype investigation effort
    for one SKU.
    """

    data = load_data()

    inventory = data[0]
    putaway = data[1]
    moves = data[2]
    pick_failures = data[3]
    cycle_counts = data[4]
    locations = data[5]

    # Baseline effort
    baseline_effort = calculate_baseline_effort(
        sku,
        putaway,
        moves
    )

    # Prototype investigation
    prototype = investigate_sku(
        sku,
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    )

    prototype_effort = calculate_prototype_effort(prototype)

    return {
        "sku": sku,
        "baseline_effort": baseline_effort,
        "prototype_effort": prototype_effort,
        "effort_reduction_percent": calculate_effort_reduction(
            baseline_effort,
            prototype_effort
        ),
    }


def evaluate_skus(skus):
    """
    Evaluate multiple SKUs and return a summary DataFrame.
    """

    results = []

    for sku in skus:
        results.append(evaluate_sku(sku))

    return pd.DataFrame(results)