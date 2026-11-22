"""Narrow importer for selected Promptfoo JSONL output fields."""

from __future__ import annotations

import json
from typing import Any


def admit(source_bytes: bytes, selector: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    rows = [json.loads(line) for line in source_bytes.decode("utf-8").splitlines() if line.strip()]
    selection = {"aggregate": selector.get("aggregate", "mean_score")}
    if not rows:
        return selection, {"state": "NOT_MEASURED", "complete": False, "reason": "The JSONL file has no rows."}

    measured = [
        row for row in rows
        if isinstance(row.get("gradingResult"), dict) and isinstance(row.get("score"), (int, float))
    ]
    explicit_errors = [row for row in rows if row.get("error")]
    if explicit_errors and not measured:
        return selection, {
            "state": "ERROR",
            "complete": False,
            "reason": "Promptfoo rows report errors and no admitted graded result exists.",
        }
    if not measured:
        return selection, {
            "state": "NOT_MEASURED",
            "complete": False,
            "reason": "No row contains both gradingResult and a numeric score.",
        }

    value = sum(float(row["score"]) for row in measured) / len(measured)
    return selection, {
        "state": "OBSERVED",
        "value": value,
        "unit": selector.get("unit", "ratio"),
        "complete": len(measured) == len(rows) and not explicit_errors,
        "population": {
            "total_rows": len(rows),
            "measured_rows": len(measured),
            "unmeasured_rows": len(rows) - len(measured),
            "error_rows": len(explicit_errors),
        },
    }
