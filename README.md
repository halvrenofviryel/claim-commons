# Claim Commons

Claim Commons is an early research prototype for keeping an AI evaluation claim tied to the measurement, system revision, decision rule, scope, and missing evidence that produced it.

An evaluation result can remain syntactically intact while its meaning becomes stronger during export, import, or presentation. A score can be shown without revealing that only part of the planned population was measured. A successful run can be treated as evidence that a safety claim passed. A past result can remain green after the evaluated system changes.

This repository tests one narrow alternative: a deterministic **claim capsule** that keeps these states visible across two source formats.

## What works in this release

- A small, implementation-neutral claim-capsule schema.
- A narrow importer for selected Inspect AI evaluation-log v2 result fields.
- A narrow importer for Promptfoo JSONL rows containing `gradingResult` and numeric `score` fields.
- A dependency-free Python verifier that rechecks the capsule digest, optional source bytes, and the deterministic comparison between an admitted measurement and a declared criterion.
- Synthetic fixtures that distinguish `SUPPORTED`, `REFUTED`, `NOT_MEASURED`, `INCONCLUSIVE`, `STALE`, and `ERROR`.
- Eight automated controls covering complete, partial, absent, stale, altered, and error cases.

## What this release does not establish

This is a first-party research prototype. The two adapters have been tested only on the synthetic fixtures in this repository, shaped from the cited official documentation. No real Inspect AI or Promptfoo export has been admitted. There are no external users, independent implementations, production deployments, signatures, transparency receipts, or general semantic-truth checks.

A successful verification means that the recorded capsule is internally consistent with its digest, admitted source bytes, and declared numeric rule. It does not establish that the claim is true, that the evaluation is valid, that the source is independent, or that a system is safe.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

Build a capsule from the complete Inspect-shaped fixture:

```bash
claim-commons import \
  --format inspect-ai-v2 \
  --profile fixtures/profiles/document-triage.json \
  --source fixtures/inspect/complete.json \
  --out capsule.json
```

Verify the capsule and the exact source bytes:

```bash
claim-commons verify \
  --capsule capsule.json \
  --source fixtures/inspect/complete.json
```

Check applicability against a different current subject revision:

```bash
claim-commons verify \
  --capsule capsule.json \
  --source fixtures/inspect/complete.json \
  --current-subject-revision model-b
```

The recorded assessment remains visible, while `current_status` becomes `STALE`.

## Why a separate project

Claim Commons does not replace an evaluation framework, assurance case, runtime evidence format, or transparency service.

- [Inspect AI](https://inspect.aisi.org.uk/) and [Promptfoo](https://www.promptfoo.dev/) run evaluations and preserve their own detailed records.
- [Trustworthy and Ethical Assurance](https://www.turing.ac.uk/research/research-projects/trustworthy-and-ethical-assurance-tea) structures claims, evidence, assumptions, and stakeholder review.
- [SCITT](https://www.rfc-editor.org/rfc/rfc9943.html) defines architecture for transparent, authentic statements.
- [AIREP](https://github.com/halvrenofviryel/ai-runtime-evidence-protocol) explores per-decision runtime evidence.
- The individual Internet-Draft [Claim-Preserving Exchange of AI Evaluation Evidence](https://datatracker.ietf.org/doc/draft-abak-ai-evaluation-claim-preservation/) describes format-neutral preservation requirements. It is an individual draft, not an IETF standard or endorsement.

The research question here is narrower: can a small exchange record preserve an evaluation claim's selected measurement, rule, population completeness, revision applicability, and known limits across tool boundaries without turning missing evidence into support?

## Status and participation

The current answer is **not established** beyond the included synthetic fixtures. See [STATUS.md](docs/STATUS.md), [SPEC.md](docs/SPEC.md), [THREAT_MODEL.md](docs/THREAT_MODEL.md), and [PRIOR_ART.md](docs/PRIOR_ART.md).

The most useful early contributions are counterexamples, real export samples that can be shared safely, mapping-loss reports, and independent implementations. Please open an issue before expanding an adapter: narrow, inspectable mappings are preferred to broad format claims.

## License

Code, schema, documentation, and synthetic fixtures are released under the Apache License 2.0. No affiliation or endorsement by the projects cited above is implied.
