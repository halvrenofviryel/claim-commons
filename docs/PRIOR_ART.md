# Related work and boundaries

Claim Commons is designed to compose with existing work rather than duplicate it.

## Evaluation frameworks

[Inspect AI](https://inspect.aisi.org.uk/) records evaluation status, results, scores, metrics, samples, and metadata. [Promptfoo](https://www.promptfoo.dev/) runs and compares model evaluations and can export JSON and JSONL results. Claim Commons currently imports only a small documented subset of these formats and does not replace either framework.

## Assurance methods

[Trustworthy and Ethical Assurance](https://www.turing.ac.uk/research/research-projects/trustworthy-and-ethical-assurance-tea) connects claims, arguments, evidence, assumptions, and stakeholder review. A claim capsule is a smaller machine-readable exchange record; it is not a complete assurance case or deliberative process.

## Transparency and signed statements

[RFC 9943](https://www.rfc-editor.org/rfc/rfc9943.html) describes the SCITT architecture for transparent, authentic statements. A digest in this prototype checks exact bytes only. It does not provide issuer identity, authorization, a receipt, or a transparency service.

## Runtime evidence

[AIREP](https://github.com/halvrenofviryel/ai-runtime-evidence-protocol) explores per-decision evidence for AI runtimes. Claim Commons focuses on claim applicability and mapping loss across evaluation records. AIREP is related public research, not a required dependency.

## Claim preservation

The individual Internet-Draft [Claim-Preserving Exchange of AI Evaluation Evidence](https://datatracker.ietf.org/doc/draft-abak-ai-evaluation-claim-preservation/) motivates several distinctions used here. It has no IETF standards status or endorsement. This repository is one experimental mapping path and does not claim conformance to a stable standard.

No project named above has reviewed or endorsed Claim Commons.
