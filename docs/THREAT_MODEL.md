# Threat model

## Assets in scope

- The exact admitted source bytes.
- The selected measurement and population completeness fields.
- The declared claim, subject revision, criterion, and scope.
- The distinction among support, refutation, absence, partial observation, staleness, and processing error.

## Failures this prototype can expose

- Source bytes changed after capsule construction.
- Capsule body changed without recomputing its identifier.
- Stored status disagrees with the deterministic rule encoded in the capsule.
- A known supplied current subject revision differs from the recorded revision.
- A selected measurement is absent, partial, incompletely scored, or explicitly errored in the admitted fields.

## Failures outside this prototype

- A dishonest or compromised source that emits internally consistent false data.
- A wrong claim, threshold, evaluator, data set, or sampling design.
- Hidden provider changes that are not observable to the verifier.
- Incorrect interpretation of upstream fields beyond the implemented mapping.
- Collusion, issuer authority, key compromise, unauthorized disclosure, or deletion.
- Semantic equivalence between tools, real-world safety, or production effectiveness.

## Trust boundary

The host supplies the profile, source bytes, adapter selection, and optional current subject revision. The verifier does not allow model-generated text or the evaluated system to approve its own result. The current implementation has no signer identity or authorization model.
