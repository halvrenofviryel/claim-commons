# Project status

## Current maturity

Claim Commons 0.1.0a2 is a first-party research prototype.

The repository contains two narrow adapters, one deterministic capsule builder, one verifier, a JSON Schema, synthetic fixtures, and automated controls. The fixtures exercise only the fields documented in this repository. The project has not yet admitted captured exports from Inspect AI or Promptfoo.

## Observed in this repository

- Complete Inspect-shaped results produce evidence finding `SUPPORTED`, recorded applicability `CURRENT`, and processing `COMPLETED` for the included profile.
- Partial Inspect-shaped results remain `INCONCLUSIVE`, even when the observed numeric value is high.
- Promptfoo-shaped rows without `gradingResult` remain `NOT_MEASURED`; the current mapping cannot bind those rows to a subject revision, so applicability is `UNKNOWN`.
- A different supplied current subject revision produces current applicability `STALE` without masking the recorded evidence or processing axes.
- No supplied current revision produces `UNKNOWN`, rather than silently presenting an earlier finding as current.
- Source-backed verification reruns the recorded adapter. Rehashed fabricated measurements and fabricated source-binding paths fail their rederivation checks.
- Inspect `eval.model` is compared with the declared subject revision during construction; a mismatch is rejected.
- Inspect completeness requires consistent total, completed, scored, and unscored counts.
- An explicit source error produces evidence finding `NOT_MEASURED` and processing `ERROR`.

These observations are bounded to the included automated tests and synthetic fixtures.

## Not measured

- Compatibility with real exports or future versions of either upstream tool.
- Independent implementation or reproduction.
- Usefulness to evaluation maintainers, auditors, civil-society users, or procurement teams.
- Preservation of nonnumeric, distributional, sample-level, or multimodal claims.
- Accessibility or usability of a viewer.
- Cryptographic issuer identity, transparency, or authority.
- Semantic truth, safety, causal attribution, or production fitness.

## Next evidence gates

1. Admit redacted or public real exports at pinned upstream revisions.
2. Record every field retained, transformed, omitted, or unavailable.
3. Compare two tools against one predeclared claim contract without flattening tool-specific unknowns.
4. Ask an external implementer to reproduce or challenge the mapping from the published specification.
5. Test whether a user can inspect and contest a capsule without a hosted service.
