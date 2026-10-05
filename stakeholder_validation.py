import pandas as pd


VALIDATION_TASKS = [
    "Find a discrepancy",
    "Interpret the recommendation",
    "Interpret uncertainty",
    "Review supporting evidence",
    "Make a safe decision",
]


def create_validation_template():
    """
    Create a blank stakeholder-validation form.
    """

    return pd.DataFrame(
        {
            "task": VALIDATION_TASKS,
            "completed": [None] * len(VALIDATION_TASKS),
            "rating_1_to_5": [None] * len(VALIDATION_TASKS),
            "notes": [""] * len(VALIDATION_TASKS),
        }
    )


def calculate_validation_summary(results):
    """
    Summarize completed stakeholder-validation tasks.

    Results should contain:
        task
        completed
        rating_1_to_5
        notes
    """

    if results.empty:
        return {
            "tasks_completed": 0,
            "total_tasks": len(VALIDATION_TASKS),
            "completion_rate": 0.0,
            "average_rating": None,
        }

    completed = results["completed"].fillna(False).astype(bool)

    tasks_completed = int(completed.sum())
    total_tasks = len(results)

    completion_rate = (
        tasks_completed / total_tasks * 100
        if total_tasks > 0
        else 0.0
    )

    ratings = pd.to_numeric(
        results["rating_1_to_5"],
        errors="coerce"
    )

    average_rating = (
        ratings.mean()
        if ratings.notna().any()
        else None
    )

    return {
        "tasks_completed": tasks_completed,
        "total_tasks": total_tasks,
        "completion_rate": completion_rate,
        "average_rating": average_rating,
    }