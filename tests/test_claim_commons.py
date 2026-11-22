from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from claim_commons.adapters import inspect_ai, promptfoo
from claim_commons.core import build_capsule, canonical_bytes, sha256_bytes, verify_capsule

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "fixtures/profiles/document-triage.json").read_text())


def capsule_for(source: Path, source_format: str, *, profile: dict | None = None):
    source_bytes = source.read_bytes()
    adapter = inspect_ai if source_format == "inspect-ai-v2" else promptfoo
    profile = deepcopy(profile or PROFILE)
    selection, measurement, source_binding = adapter.admit(source_bytes, profile["selector"])
    capsule = build_capsule(
        profile,
        source_format=source_format,
        source_ref=source.name,
        source_bytes=source_bytes,
        adapter_version=adapter.ADAPTER_VERSION,
        selection=selection,
        measurement=measurement,
        source_binding=source_binding,
    )
    return capsule, source_bytes


def rehash(capsule: dict) -> None:
    body = {key: deepcopy(value) for key, value in capsule.items() if key != "capsule_id"}
    capsule["capsule_id"] = sha256_bytes(canonical_bytes(body))


class ClaimCommonsTests(unittest.TestCase):
    def test_inspect_complete_has_three_separate_axes(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        self.assertEqual(capsule["assessment"]["evidence_finding"], "SUPPORTED")
        self.assertEqual(capsule["assessment"]["applicability"], "CURRENT")
        self.assertEqual(capsule["assessment"]["processing"], "COMPLETED")
        result = verify_capsule(capsule, source_bytes=source, current_subject_revision="model-a")
        self.assertTrue(result["valid"])
        self.assertEqual(result["verification_level"], "SOURCE_DERIVED")
        self.assertEqual(result["current_applicability"], "CURRENT")

    def test_inspect_partial_is_inconclusive(self):
        capsule, _ = capsule_for(ROOT / "fixtures/inspect/partial.json", "inspect-ai-v2")
        self.assertEqual(capsule["assessment"]["evidence_finding"], "INCONCLUSIVE")
        self.assertEqual(capsule["assessment"]["processing"], "COMPLETED")

    def test_promptfoo_measured_has_unknown_source_applicability(self):
        capsule, source = capsule_for(ROOT / "fixtures/promptfoo/measured.jsonl", "promptfoo-jsonl")
        self.assertEqual(capsule["assessment"]["evidence_finding"], "SUPPORTED")
        self.assertEqual(capsule["assessment"]["applicability"], "UNKNOWN")
        result = verify_capsule(capsule, source_bytes=source, current_subject_revision="model-a")
        self.assertTrue(result["valid"])
        self.assertEqual(result["current_applicability"], "UNKNOWN")

    def test_complete_measurement_below_stricter_threshold_is_refuted(self):
        profile = deepcopy(PROFILE)
        profile["evaluation_contract"]["criterion"]["threshold"] = 0.8
        capsule, _ = capsule_for(
            ROOT / "fixtures/inspect/complete.json",
            "inspect-ai-v2",
            profile=profile,
        )
        self.assertEqual(capsule["assessment"]["evidence_finding"], "REFUTED")

    def test_promptfoo_without_grading_is_not_measured(self):
        capsule, _ = capsule_for(ROOT / "fixtures/promptfoo/unmeasured.jsonl", "promptfoo-jsonl")
        self.assertEqual(capsule["assessment"]["evidence_finding"], "NOT_MEASURED")
        self.assertEqual(capsule["assessment"]["processing"], "COMPLETED")

    def test_unknown_current_revision_is_explicit(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        result = verify_capsule(capsule, source_bytes=source)
        self.assertTrue(result["valid"])
        self.assertEqual(result["current_applicability"], "UNKNOWN")
        self.assertEqual(result["recorded_assessment"]["evidence_finding"], "SUPPORTED")

    def test_changed_revision_is_stale_without_masking_evidence_or_processing(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/error.json", "inspect-ai-v2")
        result = verify_capsule(capsule, source_bytes=source, current_subject_revision="model-b")
        self.assertTrue(result["valid"])
        self.assertEqual(result["current_applicability"], "STALE")
        self.assertEqual(result["recorded_assessment"]["evidence_finding"], "NOT_MEASURED")
        self.assertEqual(result["recorded_assessment"]["processing"], "ERROR")

    def test_altered_source_is_rejected(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        result = verify_capsule(capsule, source_bytes=source + b"\n")
        self.assertFalse(result["valid"])
        self.assertFalse(result["checks"]["source_digest"])

    def test_altered_capsule_without_rehash_is_rejected(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        altered = deepcopy(capsule)
        altered["measurement"]["value"] = 0.1
        self.assertFalse(verify_capsule(altered, source_bytes=source)["valid"])

    def test_fabricated_measurement_with_rehash_is_rejected_by_source_rederivation(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        forged = deepcopy(capsule)
        forged["measurement"]["value"] = 0.99
        rehash(forged)
        result = verify_capsule(forged, source_bytes=source, current_subject_revision="model-a")
        self.assertFalse(result["valid"])
        self.assertTrue(result["checks"]["capsule_digest"])
        self.assertFalse(result["checks"]["source_measurement"])

    def test_fabricated_binding_with_rehash_is_rejected_by_source_rederivation(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        forged = deepcopy(capsule)
        forged["source_binding"]["subject_revision"]["source_path"] = "invented.path"
        rehash(forged)
        result = verify_capsule(forged, source_bytes=source, current_subject_revision="model-a")
        self.assertFalse(result["valid"])
        self.assertFalse(result["checks"]["source_binding"])

    def test_profile_revision_must_match_observed_inspect_model(self):
        profile = deepcopy(PROFILE)
        profile["subject"]["revision"] = "model-b"
        with self.assertRaisesRegex(ValueError, "source subject revision"):
            capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2", profile=profile)

    def test_unsupported_adapter_version_fails_source_backed_verification(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        altered = deepcopy(capsule)
        altered["source"]["adapter_version"] = "unknown"
        rehash(altered)
        result = verify_capsule(altered, source_bytes=source)
        self.assertFalse(result["valid"])
        self.assertFalse(result["checks"]["adapter_supported"])

    def test_inspect_scored_sample_mismatch_is_incomplete(self):
        data = json.loads((ROOT / "fixtures/inspect/complete.json").read_text())
        data["results"]["scores"][0]["scored_samples"] = 3
        source = json.dumps(data).encode()
        selection, measurement, _ = inspect_ai.admit(source, PROFILE["selector"])
        self.assertEqual(selection["unit"], "ratio")
        self.assertFalse(measurement["complete"])

    def test_capsule_only_verification_is_labeled_and_does_not_claim_source_check(self):
        capsule, _ = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        result = verify_capsule(capsule)
        self.assertTrue(result["valid"])
        self.assertEqual(result["verification_level"], "CAPSULE_ONLY")
        self.assertEqual(result["source_bytes"], "NOT_CHECKED")
        self.assertNotIn("source_measurement", result["checks"])

    def test_explicit_source_error_is_not_an_evidence_finding(self):
        capsule, _ = capsule_for(ROOT / "fixtures/inspect/error.json", "inspect-ai-v2")
        self.assertEqual(capsule["assessment"]["evidence_finding"], "NOT_MEASURED")
        self.assertEqual(capsule["assessment"]["processing"], "ERROR")


if __name__ == "__main__":
    unittest.main()
