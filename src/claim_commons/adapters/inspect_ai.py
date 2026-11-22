"""Narrow importer for selected Inspect AI eval-log v2 result fields."""

from __future__ import annotations

import json
from typing import Any


def admit(source_bytes: bytes, selector: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    data = json.loads(source_bytes)
    status = data.get("status")
    selection = {
        "score_name": selector.get("score_name"),
        "metric_name": selector.get("metric_name"),
    }
    if status == "error":
        return selection, {"state": "ERROR", "complete": False, "reason": "Inspect log status is error."}
    if status != "success" or not isinstance(data.get("results"), dict):
        return selection, {
            "state": "NOT_MEASURED",
            "complete": False,
            "reason": "Inspect results are absent or the run did not finish successfully.",
        }

    results = data["results"]
    match = next(
        (score for score in results.get("scores", []) if score.get("name") == selector.get("score_name")),
        None,
    )
    metric = None if match is None else match.get("metrics", {}).get(selector.get("metric_name"))
    if not isinstance(metric, dict) or not isinstance(metric.get("value"), (int, float)):
        return selection, {
            "state": "NOT_MEASURED",
            "complete": False,
            "reason": "The selected Inspect score metric is absent.",
        }

    total = results.get("total_samples")
    completed = results.get("completed_samples")
    unscored = match.get("unscored_samples", 0)
    complete = (
        isinstance(total, int)
        and isinstance(completed, int)
        and total == completed
        and unscored == 0
    )
    return selection, {
        "state": "OBSERVED",
        "value": metric["value"],
        "unit": selector.get("unit", "ratio"),
        "complete": complete,
        "population": {
            "total_samples": total,
            "completed_samples": completed,
            "scored_samples": match.get("scored_samples"),
            "unscored_samples": unscored,
        },
    }
