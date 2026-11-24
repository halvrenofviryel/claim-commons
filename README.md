# Claim Commons — development moved to CPP

Claim Commons is no longer a separately maintained claim-preservation product.
Its useful source-binding, mapping-loss, Inspect AI/Promptfoo adapter, deterministic
rederivation, fixture, and control work has been consolidated into the
[`source-capsule/`](https://github.com/halvrenofviryel/claim-preservation-profile/tree/main/source-capsule)
module of the
[Claim Preservation Profile](https://github.com/halvrenofviryel/claim-preservation-profile)
repository.

CPP is the single maintained public repository for this claim-preservation work.
New issues, counterexamples, reproductions, and adapter proposals should be filed
there. This repository is retained as read-only history so existing links, commits,
and the original pull-request record remain inspectable.

## Why the projects were consolidated

CPP defines the broader claim-transformation model, requirements, conformance
corpus, and reference validator. Claim Commons explored a narrower evaluation
export-to-source-capsule path. Keeping both as active products would duplicate the
same problem family and make their ownership boundary unclear.

The migrated module remains an experimental, unreleased candidate. Consolidation
does not establish CPP conformance, semantic truth, general upstream-tool
compatibility, independent reproduction, deployment fitness, or standards
adoption. Exact source and destination hashes for the migration are recorded in
CPP's `source-capsule/MIGRATION_PROVENANCE.json`.

## Historical status

This repository contains the initial public prototype and an unmerged public
source-rederivation branch. Later reviewed local candidate work was migrated under
an explicit file allowlist; it was not released from this repository. Git history
is preserved for provenance, not as a second supported implementation line.
