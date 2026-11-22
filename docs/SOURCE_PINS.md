# Source documentation pins

The first two adapters were shaped from public upstream documentation and source at the following revisions, observed on 22 November 2026.

## Inspect AI

- Repository: https://github.com/UKGovernmentBEIS/inspect_ai
- Main revision: `da25f0bf0ad0bd4a6efddb6065ffd33a38da3538`
- Evaluation logs: https://inspect.aisi.org.uk/eval-logs.html

The adapter uses only run `status`, `results.total_samples`, `results.completed_samples`, selected `scores`, scored and unscored counts, and a selected metric value.

## Promptfoo

- Repository: https://github.com/promptfoo/promptfoo
- Main revision: `04ab49ccca3242b0309a60919c5c9180dc5b6703`
- Output formats: https://www.promptfoo.dev/docs/configuration/outputs/

The adapter uses only JSONL rows with `gradingResult`, numeric `score`, and an explicit `error` field when present.

These pins identify the material consulted. They do not establish compatibility with the full pinned codebase or later revisions.
