"""Narrow importer for selected Promptfoo JSONL output fields."""

from __future__ import annotations

import json
from typing import Any

ADAPTER_VERSION = "0.1.0a2"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def admit(
    source_bytes: bytes,
    selector: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    rows = [json.loads(line) for line in source_bytes.decode("utf-8").splitlines() if line.strip()]
    selection = {
        "aggregate": selector.get("aggregate", "mean_score"),
        "unit": selector.get("unit", "ratio"),
    }
    source_binding = {
        "subject_revision": {
            "observed": False,
            "value": None,
            "source_path": None,
        }
    }
    if not rows:
        return selection, {"state": "NOT_MEASURED", "complete": False, "reason": "The JSONL file has no rows."}, source_binding

    measured = [
        row for row in rows
        if isinstance(row.get("gradingResult"), dict) and _is_number(row.get("score"))
    ]
    explicit_errors = [row for row in rows if row.get("error")]
    if explicit_errors and not measured:
        return selection, {
            "state": "ERROR",
            "complete": False,
            "reason": "Promptfoo rows report errors and no admitted graded result exists.",
        }, source_binding
    if not measured:
        return selection, {
            "state": "NOT_MEASURED",
            "complete": False,
            "reason": "No row contains both gradingResult and a numeric score.",
        }, source_binding

    value = sum(float(row["score"]) for row in measured) / len(measured)
    return selection, {
        "state": "OBSERVED",
        "value": value,
        "unit": selection["unit"],
        "complete": len(measured) == len(rows) and not explicit_errors,
        "population": {
            "total_rows": len(rows),
            "measured_rows": len(measured),
            "unmeasured_rows": len(rows) - len(measured),
            "error_rows": len(explicit_errors),
        },
    }, source_binding
