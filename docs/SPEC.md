# Claim capsule draft 0.1

## Purpose

A claim capsule binds one declared claim to one subject revision, one evaluation-contract revision, one admitted source record, one selected measurement, and one deterministic criterion. It keeps processing state, evidence finding, and current applicability distinguishable.

## Required bindings

- **Claim:** stable identifier and human-readable statement.
- **Subject:** evaluated system identifier and recorded revision.
- **Evaluation contract:** contract identifier, revision, operator, and threshold.
- **Source:** format label, reference, exact-byte SHA-256 digest, and adapter version.
- **Selection:** the fields used to choose a score or aggregation.
- **Measurement:** processing state, admitted value when present, unit, completeness, and population counts.
- **Assessment:** derived status, basis, and qualifications.
- **Scope:** explicit statements of what the record supports and does not support.

## Outcome derivation

The prototype applies the following order:

1. A supplied current subject revision different from the recorded revision yields `STALE` for current applicability.
2. An admitted source error yields `ERROR`.
3. A missing selected measurement yields `NOT_MEASURED`.
4. An observed value from an incomplete or incompletely scored population yields `INCONCLUSIVE`.
5. A complete numeric measurement is compared with the declared criterion and yields `SUPPORTED` or `REFUTED`.

These labels are local deterministic results. They do not authenticate the source, validate the evaluation design, or establish semantic truth.

## Integrity

The capsule identifier is SHA-256 over canonical JSON bytes of the capsule body without `capsule_id`. The source digest is SHA-256 over exact source bytes. Canonicalization here is the Python `json.dumps` representation with sorted keys, compact separators, UTF-8, and non-finite numbers rejected. This is a prototype convention, not a cross-language canonicalization standard.

## Change policy

Version 0.1 may change incompatibly. A future revision must define a cross-language canonicalization profile, explicit mapping-loss records, stronger schema constraints, and migration behavior before claiming stable interoperability.
