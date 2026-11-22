# Project status

## Current maturity

Claim Commons 0.1.0a1 is a first-party research prototype.

The repository contains two narrow adapters, one deterministic capsule builder, one verifier, a JSON Schema, synthetic fixtures, and automated controls. The fixtures exercise only the fields documented in this repository. The project has not yet admitted captured exports from Inspect AI or Promptfoo.

## Observed in this repository

- Complete Inspect-shaped results can produce a scoped `SUPPORTED` outcome.
- Partial Inspect-shaped results remain `INCONCLUSIVE`, even when the observed numeric value is high.
- Promptfoo-shaped rows without `gradingResult` remain `NOT_MEASURED`.
- A different supplied current subject revision produces `STALE` without rewriting the recorded assessment.
- Altered source bytes and altered capsule bodies fail their respective digest checks.
- An explicit source error remains `ERROR`.

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
