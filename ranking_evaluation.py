import pandas as pd

from discrepancy_engine import load_data, investigate_sku


def evaluate_ranking(sku, expected_location, top_k_values=(1, 3, 5)):
    """
    Evaluate whether the expected ground-truth location appears
    within the prototype's ranked candidate locations.
    """

    data = load_data()

    inventory = data[0]
    putaway = data[1]
    moves = data[2]
    pick_failures = data[3]
    cycle_counts = data[4]
    locations = data[5]

    ranked = investigate_sku(
        sku,
        inventory,
        putaway,
        moves,
        pick_failures,
        cycle_counts,
        locations,
    )

    if ranked.empty:
        return {
            "sku": sku,
            "expected_location": expected_location,
            "rank": None,
            "top_1": False,
            "top_3": False,
            "top_5": False,
        }

    candidate_column = "candidate_location"

    if candidate_column not in ranked.columns:
        raise ValueError(
            f"Expected column '{candidate_column}' not found."
        )

    candidates = ranked[candidate_column].tolist()

    try:
        rank = candidates.index(expected_location) + 1
    except ValueError:
        rank = None

    return {
        "sku": sku,
        "expected_location": expected_location,
        "rank": rank,
        "top_1": rank is not None and rank <= 1,
        "top_3": rank is not None and rank <= 3,
        "top_5": rank is not None and rank <= 5,
    }


def evaluate_ground_truth(ground_truth):
    """
    Evaluate ranking quality for all ground-truth cases.

    Expected columns:
        sku
        expected_location
    """

    results = []

    for _, row in ground_truth.iterrows():
        results.append(
            evaluate_ranking(
                row["sku"],
                row["expected_location"],
            )
        )

    return pd.DataFrame(results)


def calculate_hit_rates(results):
    """
    Calculate Top-1, Top-3 and Top-5 hit rates.
    """

    if results.empty:
        return {
            "top_1_hit_rate": 0.0,
            "top_3_hit_rate": 0.0,
            "top_5_hit_rate": 0.0,
        }

    return {
        "top_1_hit_rate": results["top_1"].mean() * 100,
        "top_3_hit_rate": results["top_3"].mean() * 100,
        "top_5_hit_rate": results["top_5"].mean() * 100,
    }