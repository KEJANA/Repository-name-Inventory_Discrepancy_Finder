import os
import math
import pandas as pd

DATA_DIR = "data"


def load_data(data_dir=DATA_DIR):
    inventory = pd.read_csv(os.path.join(data_dir, "inventory.csv"))
    putaway = pd.read_csv(os.path.join(data_dir, "putaway_scans.csv"), parse_dates=["timestamp"])
    moves = pd.read_csv(os.path.join(data_dir, "move_events.csv"), parse_dates=["timestamp"])
    pick_failures = pd.read_csv(os.path.join(data_dir, "pick_failures.csv"), parse_dates=["timestamp"])
    cycle_counts = pd.read_csv(os.path.join(data_dir, "cycle_counts.csv"), parse_dates=["timestamp"])
    locations = pd.read_csv(os.path.join(data_dir, "location_master.csv"))
    return inventory, putaway, moves, pick_failures, cycle_counts, locations


def recency_score(timestamp, reference_time, decay_hours=48):
    if pd.isna(timestamp):
        return 0.0
    age_hours = max(0.0, (reference_time - timestamp).total_seconds() / 3600.0)
    return math.exp(-age_hours / decay_hours)


def confidence_label(score):
    if score >= 0.80:
        return "High confidence"
    if score >= 0.60:
        return "Moderate confidence"
    if score >= 0.40:
        return "Low confidence"
    return "Insufficient evidence"


def evidence_strength(score):
    if score >= 0.80:
        return "Strong"
    if score >= 0.60:
        return "Useful"
    if score >= 0.40:
        return "Weak"
    return "Insufficient"


def _prepare_indexes(inventory, putaway, moves, pick_failures, cycle_counts, locations):
    """Build lookup dictionaries once; avoids repeated full-dataframe scans."""
    inv = inventory.set_index("sku").to_dict("index")
    loc_status = locations.set_index("location_id")["status"].to_dict()

    putaway_by_sku = {k: g.sort_values("timestamp") for k, g in putaway.groupby("sku", sort=False)}
    moves_by_sku = {k: g.sort_values("timestamp") for k, g in moves.groupby("sku", sort=False)}
    failures_by_sku = {k: g.sort_values("timestamp") for k, g in pick_failures.groupby("sku", sort=False)}
    counts_by_sku = {k: g.sort_values("timestamp") for k, g in cycle_counts.groupby("sku", sort=False)}
    return inv, loc_status, putaway_by_sku, moves_by_sku, failures_by_sku, counts_by_sku


def baseline_last_known_location(sku, inventory, putaway, moves):
    """Simple baseline: latest recorded put-away/move destination."""
    events = []
    p = putaway[putaway["sku"] == sku]
    if not p.empty:
        events.extend(p[["destination_location", "timestamp"]].rename(columns={"destination_location": "location"}).to_dict("records"))
    m = moves[moves["sku"] == sku]
    if not m.empty:
        events.extend(m[["to_location", "timestamp"]].rename(columns={"to_location": "location"}).to_dict("records"))
    if not events:
        return None
    latest = max(events, key=lambda x: x["timestamp"])
    return {"location": latest["location"], "timestamp": latest["timestamp"]}


def generate_candidates(sku, inventory, putaway, moves, pick_failures, cycle_counts, locations):
    candidates = set()
    inv_rows = inventory[inventory["sku"] == sku]
    if not inv_rows.empty:
        candidates.add(inv_rows.iloc[0]["system_location"])
    for frame, column in ((putaway, "destination_location"), (moves, "to_location"), (pick_failures, "expected_location"), (cycle_counts, "location")):
        rows = frame[frame["sku"] == sku]
        if not rows.empty:
            candidates.update(rows[column].dropna().tolist())
    return list(candidates)


def _score_from_rows(sku, candidate_location, inv_row, location_status, sku_putaway, sku_moves, latest_failure, latest_count, reference_time):
    score = 0.0
    evidence = []
    system_location = inv_row["system_location"] if inv_row else None

    if location_status.get(candidate_location) == "ACTIVE":
        score += 0.08
        evidence.append("Location is active in location master.")
    else:
        score -= 0.30
        evidence.append("Location is inactive or invalid.")

    if candidate_location == system_location:
        score += 0.10
        evidence.append("Candidate matches the current system location.")

    candidate_putaway = sku_putaway[sku_putaway["destination_location"] == candidate_location]
    if not candidate_putaway.empty:
        latest = candidate_putaway.iloc[-1]
        score += 0.28 * recency_score(latest["timestamp"], reference_time)
        evidence.append("Recent put-away scan supports this location.")

    candidate_moves = sku_moves[sku_moves["to_location"] == candidate_location]
    if not candidate_moves.empty:
        latest = candidate_moves.iloc[-1]
        score += 0.30 * recency_score(latest["timestamp"], reference_time)
        evidence.append("Recent move event points to this location.")

    if latest_failure is not None:
        failed_location = latest_failure["expected_location"]
        reason = latest_failure["failure_reason"]
        if candidate_location != failed_location:
            score += 0.16
            evidence.append("Pick failure occurred at a different expected location.")
        else:
            score -= 0.05
            evidence.append(f"Pick failure reported at this location ({reason}).")

    candidate_counts = latest_count
    if candidate_counts is not None and candidate_counts["location"] == candidate_location:
        counted = int(candidate_counts["counted_quantity"])
        variance = int(candidate_counts["variance"])
        if counted > 0:
            score += 0.12
            evidence.append(f"Cycle count found {counted} unit(s) here.")
        else:
            score -= 0.25
            evidence.append("Latest cycle count found zero stock here.")
        if variance != 0:
            evidence.append(f"Cycle-count variance: {variance:+d}.")

    putaway_quantity = int(candidate_putaway["quantity"].sum()) if not candidate_putaway.empty else 0
    move_quantity = int(candidate_moves["quantity"].sum()) if not candidate_moves.empty else 0
    if putaway_quantity > 0 or move_quantity > 0:
        score += 0.04
        evidence.append("Quantity movement evidence is available.")

    # Invalid/inactive locations must never outrank a valid location.
    # Keep the candidate visible for auditability, but make it non-actionable.
    if location_status.get(candidate_location) != "ACTIVE":
        score = 0.0
    else:
        score = max(0.0, min(1.0, score))
    label = confidence_label(score)
    if label == "High confidence":
        action = f"Search {candidate_location} first, then verify before correcting the record."
    elif label == "Moderate confidence":
        action = f"Prioritise {candidate_location}, then verify the next candidate."
    elif label == "Low confidence":
        action = "Perform a targeted cycle count before correcting the inventory record."
    else:
        action = "Insufficient evidence. Trigger manual investigation; do not assume this location."
    return {
        "sku": sku,
        "candidate_location": candidate_location,
        "evidence_score": round(score, 3),
        "confidence": label,
        "evidence_strength": evidence_strength(score),
        "evidence": evidence,
        "recommended_action": action,
    }


def investigate_sku(sku, inventory, putaway, moves, pick_failures, cycle_counts, locations, _indexes=None):
    if _indexes is None:
        _indexes = _prepare_indexes(inventory, putaway, moves, pick_failures, cycle_counts, locations)
    inv, loc_status, putaway_by_sku, moves_by_sku, failures_by_sku, counts_by_sku = _indexes
    inv_row = inv.get(sku)
    sku_putaway = putaway_by_sku.get(sku, putaway.iloc[0:0])
    sku_moves = moves_by_sku.get(sku, moves.iloc[0:0])
    sku_failures = failures_by_sku.get(sku, pick_failures.iloc[0:0])
    sku_counts = counts_by_sku.get(sku, cycle_counts.iloc[0:0])

    timestamps = []
    for frame in (sku_putaway, sku_moves, sku_failures, sku_counts):
        if not frame.empty:
            timestamps.append(frame["timestamp"].max())
    reference_time = max(timestamps) if timestamps else pd.Timestamp.now()

    candidates = set()
    if inv_row:
        candidates.add(inv_row["system_location"])
    if not sku_putaway.empty:
        candidates.update(sku_putaway["destination_location"].dropna().tolist())
    if not sku_moves.empty:
        candidates.update(sku_moves["to_location"].dropna().tolist())
    if not sku_failures.empty:
        candidates.update(sku_failures["expected_location"].dropna().tolist())
    if not sku_counts.empty:
        candidates.update(sku_counts["location"].dropna().tolist())

    latest_failure = sku_failures.iloc[-1] if not sku_failures.empty else None
    latest_count = sku_counts.iloc[-1] if not sku_counts.empty else None
    results = [_score_from_rows(sku, loc, inv_row, loc_status, sku_putaway, sku_moves, latest_failure, latest_count, reference_time) for loc in candidates]
    if not results:
        return pd.DataFrame(columns=["sku", "candidate_location", "evidence_score", "confidence", "evidence_strength", "evidence", "recommended_action", "rank"])
    result_df = pd.DataFrame(results).sort_values(["evidence_score", "candidate_location"], ascending=[False, True]).reset_index(drop=True)

    # Detect recent competing destinations. This is a safety signal, not a confidence boost.
    if len(sku_moves) >= 2:
        recent = sku_moves.tail(2)
        if recent["to_location"].nunique() > 1 and (recent.iloc[-1]["timestamp"] - recent.iloc[-2]["timestamp"]).total_seconds() <= 15 * 60:
            result_df.loc[result_df["candidate_location"].isin(recent["to_location"].tolist()), "evidence" ] = result_df.loc[result_df["candidate_location"].isin(recent["to_location"].tolist()), "evidence"].apply(lambda x: x + ["Competing recent destinations detected; verify before correction."])
            result_df.loc[result_df["candidate_location"].isin(recent["to_location"].tolist()), "confidence"] = result_df.loc[result_df["candidate_location"].isin(recent["to_location"].tolist()), "evidence_score"].apply(confidence_label)
    result_df["rank"] = result_df.index + 1
    return result_df


def determine_priority(sku, row, pick_failures):
    failures = pick_failures[pick_failures["sku"] == sku]
    if failures.empty:
        return "REVIEW"
    urgency = str(failures.sort_values("timestamp").iloc[-1]["urgency"]).upper()
    location_change = bool(row["is_location_change"])
    confidence = row["confidence"]
    if urgency == "URGENT" and location_change:
        return "CRITICAL"
    if urgency == "HIGH" and location_change and confidence in ["High confidence", "Moderate confidence"]:
        return "HIGH"
    if location_change:
        return "STANDARD"
    return "REVIEW"


def find_discrepancies(data_dir=DATA_DIR):
    inventory, putaway, moves, pick_failures, cycle_counts, locations = load_data(data_dir)
    indexes = _prepare_indexes(inventory, putaway, moves, pick_failures, cycle_counts, locations)
    records = []
    for sku in pick_failures["sku"].dropna().unique().tolist():
        results = investigate_sku(sku, inventory, putaway, moves, pick_failures, cycle_counts, locations, indexes)
        if results.empty or sku not in indexes[0]:
            continue
        best = results.iloc[0]
        inv_row = indexes[0][sku]
        expected = inv_row["system_location"]
        recommended = best["candidate_location"]
        records.append({
            "sku": sku,
            "product_name": inv_row["product_name"],
            "expected_location": expected,
            "quantity": int(inv_row["system_quantity"]),
            "recommended_location": recommended,
            "evidence_score": best["evidence_score"],
            "confidence": best["confidence"],
            "recommended_action": best["recommended_action"],
            "is_location_change": expected != recommended,
        })
    discrepancies = pd.DataFrame(records)
    if discrepancies.empty:
        discrepancies["priority"] = pd.Series(dtype=str)
        return discrepancies
    discrepancies["priority"] = discrepancies.apply(lambda r: determine_priority(r["sku"], r, pick_failures), axis=1)
    return discrepancies.sort_values(["priority", "evidence_score"], ascending=[True, False]).reset_index(drop=True)


if __name__ == "__main__":
    d = find_discrepancies()
    print("=" * 70)
    print("FULFILMENT INTELLIGENCE — ENGINE TEST")
    print("=" * 70)
    print(f"Investigations analysed: {len(d):,}")
    if not d.empty:
        print(d[["sku", "expected_location", "recommended_location", "evidence_score", "confidence", "priority"]].head(15).to_string(index=False))
    print("=" * 70)
