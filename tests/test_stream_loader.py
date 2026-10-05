import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pytest

from stream_loader import load_event_feed, load_all_event_feeds


DATA_DIR = Path("data")


def test_putaway_feed_loads_successfully():
    df = load_event_feed(
        DATA_DIR / "putaway_scans.csv",
        "putaway"
    )

    assert not df.empty
    assert {"sku", "destination_location", "timestamp"}.issubset(
        df.columns
    )


def test_timestamp_is_datetime():
    df = load_event_feed(
        DATA_DIR / "putaway_scans.csv",
        "putaway"
    )

    assert pd.api.types.is_datetime64_any_dtype(
        df["timestamp"]
    )


def test_all_event_feeds_load():
    feeds = load_all_event_feeds(DATA_DIR)

    assert set(feeds.keys()) == {
        "putaway",
        "moves",
        "pick_failures",
        "cycle_counts",
    }

    for df in feeds.values():
        assert not df.empty


def test_invalid_event_type_raises_error():
    with pytest.raises(ValueError):
        load_event_feed(
            DATA_DIR / "putaway_scans.csv",
            "invalid_type"
        )


def test_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        load_event_feed(
            DATA_DIR / "does_not_exist.csv",
            "putaway"
        )