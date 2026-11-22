from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from claim_commons.adapters import inspect_ai, promptfoo
from claim_commons.core import build_capsule, verify_capsule

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "fixtures/profiles/document-triage.json").read_text())


def capsule_for(source: Path, source_format: str):
    source_bytes = source.read_bytes()
    adapter = inspect_ai if source_format == "inspect-ai-v2" else promptfoo
    selection, measurement = adapter.admit(source_bytes, PROFILE["selector"])
    capsule = build_capsule(
        PROFILE,
        source_format=source_format,
        source_ref=source.name,
        source_bytes=source_bytes,
        adapter_version="0.1.0a1",
        selection=selection,
        measurement=measurement,
    )
    return capsule, source_bytes


class ClaimCommonsTests(unittest.TestCase):
    def test_inspect_complete_is_supported(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        self.assertEqual(capsule["assessment"]["status"], "SUPPORTED")
        self.assertTrue(verify_capsule(capsule, source_bytes=source)["valid"])

    def test_inspect_partial_is_inconclusive(self):
        capsule, _ = capsule_for(ROOT / "fixtures/inspect/partial.json", "inspect-ai-v2")
        self.assertEqual(capsule["assessment"]["status"], "INCONCLUSIVE")

    def test_promptfoo_measured_is_supported(self):
        capsule, source = capsule_for(ROOT / "fixtures/promptfoo/measured.jsonl", "promptfoo-jsonl")
        self.assertEqual(capsule["assessment"]["status"], "SUPPORTED")
        self.assertTrue(verify_capsule(capsule, source_bytes=source)["valid"])

    def test_complete_measurement_below_stricter_threshold_is_refuted(self):
        source = ROOT / "fixtures/inspect/complete.json"
        source_bytes = source.read_bytes()
        profile = deepcopy(PROFILE)
        profile["evaluation_contract"]["criterion"]["threshold"] = 0.8
        selection, measurement = inspect_ai.admit(source_bytes, profile["selector"])
        capsule = build_capsule(
            profile,
            source_format="inspect-ai-v2",
            source_ref=source.name,
            source_bytes=source_bytes,
            adapter_version="0.1.0a1",
            selection=selection,
            measurement=measurement,
        )
        self.assertEqual(capsule["assessment"]["status"], "REFUTED")

    def test_promptfoo_without_grading_is_not_measured(self):
        capsule, _ = capsule_for(ROOT / "fixtures/promptfoo/unmeasured.jsonl", "promptfoo-jsonl")
        self.assertEqual(capsule["assessment"]["status"], "NOT_MEASURED")

    def test_changed_revision_is_stale_but_does_not_alter_recorded_verdict(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        result = verify_capsule(capsule, source_bytes=source, current_subject_revision="model-b")
        self.assertTrue(result["valid"])
        self.assertEqual(result["stored_status"], "SUPPORTED")
        self.assertEqual(result["current_status"], "STALE")

    def test_altered_source_is_rejected(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        result = verify_capsule(capsule, source_bytes=source + b"\n")
        self.assertFalse(result["valid"])
        self.assertFalse(result["checks"]["source_digest"])

    def test_altered_capsule_is_rejected(self):
        capsule, source = capsule_for(ROOT / "fixtures/inspect/complete.json", "inspect-ai-v2")
        altered = deepcopy(capsule)
        altered["measurement"]["value"] = 0.1
        self.assertFalse(verify_capsule(altered, source_bytes=source)["valid"])

    def test_explicit_source_error_remains_error(self):
        source = ROOT / "fixtures/inspect/error.json"
        capsule, _ = capsule_for(source, "inspect-ai-v2")
        self.assertEqual(capsule["assessment"]["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
