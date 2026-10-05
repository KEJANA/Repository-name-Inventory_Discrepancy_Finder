import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from stakeholder_validation import (
    VALIDATION_TASKS,
    create_validation_template,
    calculate_validation_summary,
)


def test_validation_template_has_five_tasks():
    template = create_validation_template()

    assert len(template) == 5
    assert list(template["task"]) == VALIDATION_TASKS


def test_validation_template_has_required_columns():
    template = create_validation_template()

    required_columns = {
        "task",
        "completed",
        "rating_1_to_5",
        "notes",
    }

    assert required_columns.issubset(template.columns)


def test_empty_validation_summary():
    template = create_validation_template()

    summary = calculate_validation_summary(template)

    assert summary["tasks_completed"] == 0
    assert summary["total_tasks"] == 5
    assert summary["completion_rate"] == 0.0
    assert summary["average_rating"] is None


def test_completed_tasks_are_counted():
    results = pd.DataFrame({
        "task": VALIDATION_TASKS,
        "completed": [True, True, False, True, False],
        "rating_1_to_5": [5, 4, None, 4, None],
        "notes": ["", "", "", "", ""],
    })

    summary = calculate_validation_summary(results)

    assert summary["tasks_completed"] == 3
    assert summary["completion_rate"] == 60.0


def test_average_rating_is_calculated():
    results = pd.DataFrame({
        "task": VALIDATION_TASKS,
        "completed": [True, True, True, True, True],
        "rating_1_to_5": [5, 4, 3, 4, 5],
        "notes": ["", "", "", "", ""],
    })

    summary = calculate_validation_summary(results)

    assert summary["average_rating"] == 4.2