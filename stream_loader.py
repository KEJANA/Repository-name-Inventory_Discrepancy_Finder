from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = {
    "putaway": {"sku", "destination_location", "timestamp"},
    "moves": {"sku", "to_location", "timestamp"},
    "pick_failures": {"sku", "expected_location", "timestamp"},
    "cycle_counts": {"sku", "location", "timestamp"},
}


def load_event_feed(file_path, event_type):
    """
    Load operational events from a CSV event feed.

    event_type must be one of:
        putaway
        moves
        pick_failures
        cycle_counts
    """

    if event_type not in REQUIRED_COLUMNS:
        raise ValueError(
            f"Unsupported event type: {event_type}"
        )

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Event feed not found: {path}"
        )

    df = pd.read_csv(path)

    required = REQUIRED_COLUMNS[event_type]
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns for {event_type}: "
            f"{sorted(missing)}"
        )

    # Convert timestamps consistently
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Remove rows with invalid timestamps
    df = df.dropna(subset=["timestamp"]).copy()

    return df


def load_all_event_feeds(data_dir):
    """
    Load all four operational event feeds from a directory.
    """

    data_dir = Path(data_dir)

    return {
        "putaway": load_event_feed(
            data_dir / "putaway_scans.csv",
            "putaway"
        ),
        "moves": load_event_feed(
            data_dir / "move_events.csv",
            "moves"
        ),
        "pick_failures": load_event_feed(
            data_dir / "pick_failures.csv",
            "pick_failures"
        ),
        "cycle_counts": load_event_feed(
            data_dir / "cycle_counts.csv",
            "cycle_counts"
        ),
    }


def append_event(feed_path, event):
    """
    Append one new operational event to a CSV feed.

    This provides a lightweight way to simulate an incoming
    event from a WMS/API stream.
    """

    path = Path(feed_path)

    event_df = pd.DataFrame([event])

    if path.exists():
        existing = pd.read_csv(path)
        updated = pd.concat(
            [existing, event_df],
            ignore_index=True
        )
    else:
        updated = event_df

    updated.to_csv(path, index=False)

    return updated