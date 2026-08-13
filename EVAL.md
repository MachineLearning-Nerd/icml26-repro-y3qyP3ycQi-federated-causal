# Evaluation — scoped federated causal audit

Paper: [arXiv:2505.17961v4](https://arxiv.org/abs/2505.17961), OpenReview
`y3qyP3ycQi`.

Recorded run `ea6fbba7` used historical source commit `9617192`, an HF
cpu-upgrade with 32 workers and one BLAS thread per worker, and completed in
218 seconds with NumPy 2.5.1.

| Claim | Verifier result | Gate interpretation |
| --- | --- | --- |
| C1 Membership Weights | `VERIFIED` | `VERIFIED_SCOPED` |
| C2 Density-Ratio Weights | `VERIFIED` | `VERIFIED_SCOPED` |
| C3 Theorem 3 | `VERIFIED` | `VERIFIED_SCOPED` |
| C4 Theorem 4 | `VERIFIED` | `VERIFIED_SCOPED` |
| C5 Theorem 5 | `VERIFIED` | `VERIFIED_SCOPED` |
| C6 Traumabase | `BLOCKED` | `BLOCKED` |

The local verifier exited `0` because no finite contract was falsified. That
exit code does not mean that the paper-level publication gate passed. The
current gate is `NOT_READY`; see [`publication_gate.json`](publication_gate.json).

The checked-in synthetic run uses `n=2000/site`, while current arXiv v4 uses
`n_k=650` in DGP A and total `n=4000` in DGP B. The current v4 Traumabase
description is also different from the older descriptor in the C6 artifact.
