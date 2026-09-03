import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

NUM_SKUS = 2000
NUM_LOCATIONS = 600
NUM_ORDERS = 5000
BASE_DATE = datetime(2026, 9, 1, 6, 0, 0)

ZONES = list("ABCDEF")
CATEGORIES = ["Electronics", "Home", "Beauty", "Stationery", "Accessories", "Kitchen", "Fitness", "Toys"]
OPERATORS = [f"OP-{i}" for i in range(101, 109)]
FAILURE_REASONS = ["NOT_FOUND", "EMPTY_BIN", "WRONG_LOCATION", "QUANTITY_MISMATCH", "LOCATION_BLOCKED"]
GT_SKUS = {f"SKU-{i:05d}" for i in range(1, 7)}


def random_timestamp(start, end):
    seconds = random.randint(0, int((end - start).total_seconds()))
    return start + timedelta(seconds=seconds)


def make_location_id(zone, aisle, rack, bin_number):
    return f"{zone}-{aisle:02d}-{rack:02d}-{bin_number:02d}"


# 1. LOCATION MASTER
locations = []
for zone in ZONES:
    for aisle in range(1, 11):
        for rack in range(1, 6):
            for bin_number in range(1, 3):
                if len(locations) >= NUM_LOCATIONS:
                    break
                locations.append({
                    "location_id": make_location_id(zone, aisle, rack, bin_number),
                    "zone": zone,
                    "aisle": aisle,
                    "rack": rack,
                    "bin": bin_number,
                    "capacity": random.choice([20, 30, 40, 50, 60]),
                    "status": random.choices(["ACTIVE", "INACTIVE", "BLOCKED"], weights=[0.94, 0.04, 0.02])[0],
                    "allowed_category": random.choice(CATEGORIES),
                })
location_master = pd.DataFrame(locations)
location_master.to_csv(os.path.join(DATA_DIR, "location_master.csv"), index=False)
active_locations = location_master.loc[location_master.status == "ACTIVE", "location_id"].tolist()
inactive_locations = location_master.loc[location_master.status != "ACTIVE", "location_id"].tolist()

# 2. INVENTORY MASTER
inventory = []
for i in range(1, NUM_SKUS + 1):
    category = random.choice(CATEGORIES)
    inventory.append({
        "sku": f"SKU-{i:05d}",
        "product_name": f"{category} Item {i:04d}",
        "category": category,
        "system_location": random.choice(active_locations),
        "system_quantity": random.randint(1, 30),
        "unit_value": round(random.uniform(5, 250), 2),
        "inventory_status": random.choice(["AVAILABLE", "AVAILABLE", "AVAILABLE", "HOLD"]),
    })
inventory_df = pd.DataFrame(inventory)
inventory_df.to_csv(os.path.join(DATA_DIR, "inventory.csv"), index=False)

# Use lightweight Python lists instead of DataFrame.sample() inside thousands of loops.
normal_skus = [sku for sku in inventory_df["sku"].tolist() if sku not in GT_SKUS]
inv_by_sku = inventory_df.set_index("sku").to_dict("index")

# 3. PUT-AWAY SCANS
putaway_events = []
for event_id in range(1, 9001):
    sku = random.choice(normal_skus)
    sku_row = inv_by_sku[sku]
    putaway_events.append({
        "scan_id": f"PA-{event_id:06d}",
        "timestamp": random_timestamp(BASE_DATE, BASE_DATE + timedelta(days=2)),
        "sku": sku,
        "quantity": random.randint(1, 10),
        "destination_location": sku_row["system_location"],
        "operator_id": random.choice(OPERATORS),
        "event_type": "PUT_AWAY",
        "scenario": "NORMAL",
    })
putaway_df = pd.DataFrame(putaway_events)

# 4. MOVE EVENTS
move_events = []
for event_id in range(1, 12001):
    sku = random.choice(normal_skus)
    from_location = random.choice(active_locations)
    to_location = random.choice(active_locations)
    while to_location == from_location:
        to_location = random.choice(active_locations)
    move_events.append({
        "move_id": f"MOVE-{event_id:06d}",
        "timestamp": random_timestamp(BASE_DATE, BASE_DATE + timedelta(days=2)),
        "sku": sku,
        "from_location": from_location,
        "to_location": to_location,
        "quantity": random.randint(1, 8),
        "operator_id": random.choice(OPERATORS),
        "event_type": "MOVE",
        "scenario": "NORMAL",
    })
move_df = pd.DataFrame(move_events)

# 5. PICK FAILURES
pick_failures = []
for failure_id in range(1, 3001):
    sku = random.choice(normal_skus)
    sku_row = inv_by_sku[sku]
    pick_failures.append({
        "failure_id": f"PF-{failure_id:06d}",
        "timestamp": random_timestamp(BASE_DATE + timedelta(hours=2), BASE_DATE + timedelta(days=2)),
        "order_id": f"ORD-{random.randint(1, NUM_ORDERS):06d}",
        "sku": sku,
        "expected_location": sku_row["system_location"],
        "failure_reason": random.choice(FAILURE_REASONS),
        "urgency": random.choice(["NORMAL", "NORMAL", "HIGH", "URGENT"]),
        "scenario": "NORMAL",
    })
pick_df = pd.DataFrame(pick_failures)

# 6. CYCLE COUNTS
cycle_counts = []
for count_id in range(1, 2501):
    sku = random.choice(normal_skus)
    sku_row = inv_by_sku[sku]
    system_quantity = int(sku_row["system_quantity"])
    if random.random() < 0.88:
        counted_quantity = system_quantity
    else:
        counted_quantity = max(0, system_quantity + random.choice([-5, -3, -2, -1, 1, 2, 3]))
    cycle_counts.append({
        "count_id": f"CC-{count_id:06d}",
        "timestamp": random_timestamp(BASE_DATE, BASE_DATE + timedelta(days=2)),
        "sku": sku,
        "location": sku_row["system_location"],
        "counted_quantity": counted_quantity,
        "system_quantity": system_quantity,
        "variance": counted_quantity - system_quantity,
        "scenario": "NORMAL",
    })
cycle_df = pd.DataFrame(cycle_counts)

# 7. ISOLATED, DETERMINISTIC GROUND-TRUTH CASES
# The six evaluation SKUs are excluded from random events above. This prevents
# unrelated later events from corrupting the intended test condition.
ground_truth = []

def inv_loc(sku):
    return inv_by_sku[sku]["system_location"]

# GT-001 clear relocation
sku = "SKU-00001"
expected = inv_loc(sku)
candidate = next(loc for loc in active_locations if loc != expected)
t = BASE_DATE + timedelta(hours=20)
move_df.loc[len(move_df)] = ["MOVE-GT-001", t, sku, expected, candidate, 5, "OP-101", "MOVE", "NORMAL"]
putaway_df.loc[len(putaway_df)] = ["PA-GT-001", t - timedelta(minutes=5), sku, 5, candidate, "OP-101", "PUT_AWAY", "NORMAL"]
pick_df.loc[len(pick_df)] = ["PF-GT-001", t + timedelta(minutes=10), "ORD-GT-001", sku, expected, "NOT_FOUND", "HIGH", "NORMAL"]
ground_truth.append({"case_id":"GT-001","sku":sku,"expected_location":expected,"actual_candidate_location":candidate,"case_type":"CLEAR_RELOCATION","scenario":"NORMAL"})

# GT-002 conflicting movement
sku = "SKU-00002"
expected = inv_loc(sku)
candidate_b, candidate_c = random.sample([x for x in active_locations if x != expected], 2)
t = BASE_DATE + timedelta(hours=18)
move_df.loc[len(move_df)] = ["MOVE-GT-002A", t, sku, expected, candidate_b, 3, "OP-102", "MOVE", "NORMAL"]
move_df.loc[len(move_df)] = ["MOVE-GT-002B", t + timedelta(minutes=2), sku, expected, candidate_c, 3, "OP-103", "MOVE", "NORMAL"]
pick_df.loc[len(pick_df)] = ["PF-GT-002", t + timedelta(minutes=10), "ORD-GT-002", sku, expected, "WRONG_LOCATION", "NORMAL", "NORMAL"]
ground_truth.append({"case_id":"GT-002","sku":sku,"expected_location":expected,"actual_candidate_location":f"{candidate_b}|{candidate_c}","case_type":"CONFLICTING_MOVEMENT","scenario":"NORMAL"})

# GT-003 no recent scan
sku = "SKU-00003"
expected = inv_loc(sku)
t = BASE_DATE + timedelta(days=2)
pick_df.loc[len(pick_df)] = ["PF-GT-003", t, "ORD-GT-003", sku, expected, "NOT_FOUND", "HIGH", "NORMAL"]
ground_truth.append({"case_id":"GT-003","sku":sku,"expected_location":expected,"actual_candidate_location":"","case_type":"NO_RECENT_SCAN","scenario":"NORMAL"})

# GT-004 invalid/inactive location
sku = "SKU-00004"
expected = inv_loc(sku)
invalid = inactive_locations[0] if inactive_locations else next(loc for loc in active_locations if loc != expected)
t = BASE_DATE + timedelta(hours=22)
move_df.loc[len(move_df)] = ["MOVE-GT-004", t, sku, expected, invalid, 4, "OP-104", "MOVE", "NORMAL"]
pick_df.loc[len(pick_df)] = ["PF-GT-004", t + timedelta(minutes=5), "ORD-GT-004", sku, expected, "WRONG_LOCATION", "HIGH", "NORMAL"]
ground_truth.append({"case_id":"GT-004","sku":sku,"expected_location":expected,"actual_candidate_location":invalid,"case_type":"INVALID_LOCATION","scenario":"NORMAL"})

# GT-005 cycle-count contradiction
sku = "SKU-00005"
expected = inv_loc(sku)
system_qty = int(inv_by_sku[sku]["system_quantity"])
t = BASE_DATE + timedelta(hours=23)
cycle_df.loc[len(cycle_df)] = ["CC-GT-005", t, sku, expected, 0, system_qty, -system_qty, "NORMAL"]
pick_df.loc[len(pick_df)] = ["PF-GT-005", t + timedelta(minutes=5), "ORD-GT-005", sku, expected, "EMPTY_BIN", "HIGH", "NORMAL"]
ground_truth.append({"case_id":"GT-005","sku":sku,"expected_location":expected,"actual_candidate_location":"","case_type":"CYCLE_COUNT_CONTRADICTION","scenario":"NORMAL"})

# GT-006 disruption / urgent demand
sku = "SKU-00006"
expected = inv_loc(sku)
disruption_candidate = next(loc for loc in active_locations if loc != expected)
t = BASE_DATE + timedelta(days=2, hours=1)
move_df.loc[len(move_df)] = ["MOVE-GT-006", t, sku, expected, disruption_candidate, 8, "OP-105", "MOVE", "DISRUPTION"]
pick_df.loc[len(pick_df)] = ["PF-GT-006", t + timedelta(minutes=3), "ORD-GT-006", sku, expected, "NOT_FOUND", "URGENT", "DISRUPTION"]
ground_truth.append({"case_id":"GT-006","sku":sku,"expected_location":expected,"actual_candidate_location":disruption_candidate,"case_type":"URGENT_DEMAND_DISRUPTION","scenario":"DISRUPTION"})

# 8. DISRUPTION EVENTS — also exclude the six GT cases.
disruption_skus = random.sample(normal_skus, 250)
disruption_moves = []
for event_id, sku in enumerate(disruption_skus, start=1):
    row = inv_by_sku[sku]
    from_location = row["system_location"]
    to_location = random.choice(active_locations)
    while to_location == from_location:
        to_location = random.choice(active_locations)
    disruption_moves.append({
        "move_id": f"DIS-MOVE-{event_id:05d}",
        "timestamp": random_timestamp(BASE_DATE + timedelta(days=2), BASE_DATE + timedelta(days=3)),
        "sku": sku,
        "from_location": from_location,
        "to_location": to_location,
        "quantity": random.randint(1, 10),
        "operator_id": random.choice(OPERATORS),
        "event_type": "MOVE",
        "scenario": "DISRUPTION",
    })
move_df = pd.concat([move_df, pd.DataFrame(disruption_moves)], ignore_index=True)

disruption_failures = []
for failure_id in range(1, 1201):
    sku = random.choice(disruption_skus)
    row = inv_by_sku[sku]
    disruption_failures.append({
        "failure_id": f"DIS-PF-{failure_id:05d}",
        "timestamp": random_timestamp(BASE_DATE + timedelta(days=2), BASE_DATE + timedelta(days=3)),
        "order_id": f"DIS-ORD-{failure_id:05d}",
        "sku": sku,
        "expected_location": row["system_location"],
        "failure_reason": random.choice(["NOT_FOUND", "EMPTY_BIN", "WRONG_LOCATION"]),
        "urgency": random.choice(["HIGH", "URGENT", "URGENT"]),
        "scenario": "DISRUPTION",
    })
pick_df = pd.concat([pick_df, pd.DataFrame(disruption_failures)], ignore_index=True)

# Final ordering and persistence
for frame in (putaway_df, move_df, pick_df, cycle_df):
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])

putaway_df = putaway_df.sort_values("timestamp")
move_df = move_df.sort_values("timestamp")
pick_df = pick_df.sort_values("timestamp")
cycle_df = cycle_df.sort_values("timestamp")

putaway_df.to_csv(os.path.join(DATA_DIR, "putaway_scans.csv"), index=False)
move_df.to_csv(os.path.join(DATA_DIR, "move_events.csv"), index=False)
pick_df.to_csv(os.path.join(DATA_DIR, "pick_failures.csv"), index=False)
cycle_df.to_csv(os.path.join(DATA_DIR, "cycle_counts.csv"), index=False)
pd.DataFrame(ground_truth).to_csv(os.path.join(DATA_DIR, "ground_truth.csv"), index=False)

print("\n" + "=" * 65)
print(" INVENTORY DISCREPANCY FINDER — DATA GENERATION COMPLETE")
print("=" * 65)
print(f"Locations          : {len(location_master):,}")
print(f"SKUs               : {len(inventory_df):,}")
print(f"Put-away scans     : {len(putaway_df):,}")
print(f"Move events        : {len(move_df):,}")
print(f"Pick failures      : {len(pick_df):,}")
print(f"Cycle counts       : {len(cycle_df):,}")
print(f"Ground-truth cases : {len(ground_truth):,}")
print("\nGround-truth cases:")
print(pd.DataFrame(ground_truth)[["case_id","sku","case_type","scenario"]].to_string(index=False))
print("\nReady for discrepancy engine.\n")
