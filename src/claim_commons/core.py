"""Deterministic claim-capsule construction and verification."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

OUTCOMES = {
    "SUPPORTED",
    "REFUTED",
    "NOT_MEASURED",
    "STALE",
    "INCONCLUSIVE",
    "ERROR",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def validate_profile(profile: dict[str, Any]) -> None:
    _require_mapping(profile, "profile")
    for name in ("profile_version", "recorded_at", "claim", "subject", "evaluation_contract"):
        if name not in profile:
            raise ValueError(f"profile.{name} is required")
    for group, fields in {
        "claim": ("id", "text"),
        "subject": ("id", "revision"),
        "evaluation_contract": ("id", "revision", "criterion"),
    }.items():
        obj = _require_mapping(profile[group], f"profile.{group}")
        for field in fields:
            if field not in obj:
                raise ValueError(f"profile.{group}.{field} is required")
    criterion = _require_mapping(
        profile["evaluation_contract"]["criterion"],
        "profile.evaluation_contract.criterion",
    )
    if criterion.get("operator") not in {"gte", "gt", "lte", "lt", "eq"}:
        raise ValueError("criterion.operator must be gte, gt, lte, lt, or eq")
    if not isinstance(criterion.get("threshold"), (int, float)):
        raise ValueError("criterion.threshold must be numeric")


def _compare(value: float, operator: str, threshold: float) -> bool:
    return {
        "gte": value >= threshold,
        "gt": value > threshold,
        "lte": value <= threshold,
        "lt": value < threshold,
        "eq": value == threshold,
    }[operator]


def derive_outcome(
    measurement: dict[str, Any],
    criterion: dict[str, Any],
    *,
    recorded_subject_revision: str,
    current_subject_revision: str | None = None,
) -> tuple[str, str]:
    """Derive a bounded outcome from host-supplied measurement fields."""

    if current_subject_revision is not None and current_subject_revision != recorded_subject_revision:
        return "STALE", "The supplied current subject revision differs from the recorded revision."

    state = measurement.get("state")
    if state == "ERROR":
        return "ERROR", "The source reports an execution or processing error."
    if state == "NOT_MEASURED":
        return "NOT_MEASURED", "The selected measurement is absent or was not completed."
    if state != "OBSERVED":
        return "ERROR", "The measurement state is not recognized by this prototype."
    if measurement.get("complete") is not True:
        return "INCONCLUSIVE", "The source contains a partial or incompletely scored population."

    value = measurement.get("value")
    if not isinstance(value, (int, float)):
        return "ERROR", "The observed measurement has no numeric value."
    passed = _compare(value, criterion["operator"], criterion["threshold"])
    if passed:
        return "SUPPORTED", "The complete observed value satisfies the declared criterion."
    return "REFUTED", "The complete observed value does not satisfy the declared criterion."


def build_capsule(
    profile: dict[str, Any],
    *,
    source_format: str,
    source_ref: str,
    source_bytes: bytes,
    adapter_version: str,
    selection: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    """Build a deterministic capsule from a declared profile and admitted measurement."""

    validate_profile(profile)
    criterion = deepcopy(profile["evaluation_contract"]["criterion"])
    status, basis = derive_outcome(
        measurement,
        criterion,
        recorded_subject_revision=str(profile["subject"]["revision"]),
    )
    body = {
        "capsule_version": "0.1",
        "created_at": profile["recorded_at"],
        "claim": deepcopy(profile["claim"]),
        "subject": deepcopy(profile["subject"]),
        "evaluation_contract": deepcopy(profile["evaluation_contract"]),
        "source": {
            "format": source_format,
            "ref": source_ref,
            "sha256": sha256_bytes(source_bytes),
            "adapter_version": adapter_version,
        },
        "selection": deepcopy(selection),
        "measurement": deepcopy(measurement),
        "assessment": {
            "status": status,
            "basis": basis,
            "qualifications": [
                "This status is derived from the admitted source fields and declared criterion.",
                "It is not a finding of semantic truth, safety, independence, or production fitness.",
            ],
        },
        "scope": deepcopy(profile.get("scope", {})),
    }
    return {"capsule_id": sha256_bytes(canonical_bytes(body)), **body}


def verify_capsule(
    capsule: dict[str, Any],
    *,
    source_bytes: bytes | None = None,
    current_subject_revision: str | None = None,
) -> dict[str, Any]:
    """Check structural digest, optional source bytes, and deterministic assessment."""

    checks: dict[str, bool] = {}
    problems: list[str] = []
    body = {key: deepcopy(value) for key, value in capsule.items() if key != "capsule_id"}
    expected_id = sha256_bytes(canonical_bytes(body))
    checks["capsule_digest"] = capsule.get("capsule_id") == expected_id
    if not checks["capsule_digest"]:
        problems.append("capsule_id does not match the canonical capsule body")

    if source_bytes is None:
        checks["source_digest"] = True
        source_check = "NOT_CHECKED"
    else:
        source_check = "CHECKED"
        checks["source_digest"] = capsule.get("source", {}).get("sha256") == sha256_bytes(source_bytes)
        if not checks["source_digest"]:
            problems.append("source bytes do not match source.sha256")

    try:
        criterion = capsule["evaluation_contract"]["criterion"]
        recorded_revision = str(capsule["subject"]["revision"])
        stored_status, _ = derive_outcome(
            capsule["measurement"],
            criterion,
            recorded_subject_revision=recorded_revision,
        )
        checks["stored_assessment"] = capsule.get("assessment", {}).get("status") == stored_status
        if not checks["stored_assessment"]:
            problems.append("assessment.status does not match the admitted measurement and criterion")
        current_status, current_basis = derive_outcome(
            capsule["measurement"],
            criterion,
            recorded_subject_revision=recorded_revision,
            current_subject_revision=current_subject_revision,
        )
    except (KeyError, TypeError, ValueError) as exc:
        checks["stored_assessment"] = False
        current_status = "ERROR"
        current_basis = f"Verification could not derive an assessment: {exc}"
        problems.append(str(exc))

    return {
        "valid": all(checks.values()),
        "checks": checks,
        "source_bytes": source_check,
        "stored_status": capsule.get("assessment", {}).get("status"),
        "current_status": current_status,
        "current_basis": current_basis,
        "problems": problems,
        "limitation": "valid means digest and decision consistency only; it does not establish claim truth",
    }
