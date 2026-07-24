# Federated Causal Inference — full-scale reproduction (arXiv:2505.17961)

OpenReview `y3qyP3ycQi` · arXiv [2505.17961](https://arxiv.org/abs/2505.17961) ·
6 claims / 12 points.

**Current verdict (full-scale, run `ea6fbba7`, commit `9617192`): 5/6 VERIFIED, 1/6 BLOCKED.**

| # | Claim | Verdict | Key evidence |
|---|---|---|---|
| 1 | Membership Weights via FedAvg (Eq. 3, Alg. 1) | **VERIFIED** | DGP-B propensity corr 0.934, AIPW bias −0.006±0.002; fails in DGP-A (corr 0.327) |
| 2 | Density-Ratio Weights, Gaussian shared (μ,Σ) (Eq. 4) | **VERIFIED** | DGP-A propensity corr 0.876, xent 0.441≈true 0.437; beats misspecified MW |
| 3 | Theorem 3: oracle federated = centralized | **VERIFIED** | SymPy identities ✓; oracle diff 5.3e-15 |
| 4 | Theorem 4: Var_fed ≤ Var_meta | **VERIFIED** | ratios 0.924 / 0.024 / 0.927, all ≤ 1 |
| 5 | Theorem 5: 0 ≤ O_global ≤ Σρ_k O_k | **VERIFIED** | Example 1 exact (4 ≤ 101.01); numeric ✓ |
| 6 | Traumabase real-data (K=4, 6003 pts) | **BLOCKED** | restricted-access registry; 4 routes attempted |

## Pages

| Page | What's there |
|---|---|
| [Overview](#/overview) | Paper, method, what changed from the rejected 4/12 baseline |
| [Claims & contracts](#/claims) | Exact claim contracts, assumptions, quantifiers, per-claim results |
| [Evidence](#/evidence) | Raw numbers, negative controls, symbolic + numeric theorem evidence |
| [Verification run](#/verification-run) | Fixed command, pinned env, run output, CPU/runtime |
| [Conclusion](#/conclusion) | Visibility matrix, limitations, score forecast |

**Reproduce:** `bash repro/run.sh` (→ `uv run --locked python repro/src/run_all.py`),
Python 3.12, numpy 2.5.1, sympy 1.14. K=3, d=10, n=2000/site, 1500 Monte-Carlo runs.
Full report with figures: [`reports/fedcausal/report.md`](https://github.com/MachineLearning-Nerd/icml26-repro-y3qyP3ycQi-federated-causal/blob/master/reports/fedcausal/report.md).
