"""Narrow importer for selected Inspect AI eval-log v2 result fields."""

from __future__ import annotations

import json
from typing import Any

ADAPTER_VERSION = "0.1.0a2"


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def admit(
    source_bytes: bytes,
    selector: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    data = json.loads(source_bytes)
    status = data.get("status")
    selection = {
        "score_name": selector.get("score_name"),
        "metric_name": selector.get("metric_name"),
        "unit": selector.get("unit", "ratio"),
    }
    source_model = data.get("eval", {}).get("model") if isinstance(data.get("eval"), dict) else None
    source_binding = {
        "subject_revision": {
            "observed": isinstance(source_model, str),
            "value": source_model if isinstance(source_model, str) else None,
            "source_path": "eval.model" if isinstance(source_model, str) else None,
        }
    }
    if status == "error":
        return selection, {"state": "ERROR", "complete": False, "reason": "Inspect log status is error."}, source_binding
    if status != "success" or not isinstance(data.get("results"), dict):
        return (
            selection,
            {
                "state": "NOT_MEASURED",
                "complete": False,
                "reason": "Inspect results are absent or the run did not finish successfully.",
            },
            source_binding,
        )

    results = data["results"]
    match = next(
        (score for score in results.get("scores", []) if score.get("name") == selector.get("score_name")),
        None,
    )
    metric = None if match is None else match.get("metrics", {}).get(selector.get("metric_name"))
    if not isinstance(metric, dict) or not _is_number(metric.get("value")):
        return (
            selection,
            {
                "state": "NOT_MEASURED",
                "complete": False,
                "reason": "The selected Inspect score metric is absent.",
            },
            source_binding,
        )

    total = results.get("total_samples")
    completed = results.get("completed_samples")
    scored = match.get("scored_samples")
    unscored = match.get("unscored_samples", 0)
    complete = (
        _is_int(total)
        and _is_int(completed)
        and _is_int(scored)
        and _is_int(unscored)
        and total == completed
        and total == scored + unscored
        and scored == total
        and unscored == 0
    )
    return (
        selection,
        {
            "state": "OBSERVED",
            "value": metric["value"],
            "unit": selection["unit"],
            "complete": complete,
            "population": {
                "total_samples": total,
                "completed_samples": completed,
                "scored_samples": scored,
                "unscored_samples": unscored,
            },
        },
        source_binding,
    )
