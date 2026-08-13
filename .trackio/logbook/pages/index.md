# Federated causal inference — scoped audit

OpenReview `y3qyP3ycQi` · [arXiv:2505.17961v4](https://arxiv.org/abs/2505.17961) ·
6 claims / 12 points.

**Current verdict:** `VERIFIED_SCOPED_WITH_LIMITATIONS`; five local contracts
report `VERIFIED`, C6 is `BLOCKED`, and the strict publication gate is **NOT
PASSED**.

| # | Claim | Local result | Key evidence |
|---|---|---|---|
| 1 | Membership Weights via FedAvg | **VERIFIED** | DGP-B correlation 0.934, AIPW bias −0.006±0.002; DGP-A negative control 0.327 |
| 2 | Gaussian Density-Ratio Weights | **VERIFIED** | DGP-A correlation 0.876, cross-entropy 0.441 vs 0.437; recorded AIPW bias +0.474 |
| 3 | Theorem 3: oracle federated = centralized | **VERIFIED** | oracle difference 5.33e−15 |
| 4 | Theorem 4: Var_fed ≤ Var_meta | **VERIFIED** | ratios 0.9236 / 0.0236 / 0.9266 |
| 5 | Theorem 5: overlap bound | **VERIFIED** | Example 1: 4.0 ≤ 101.01 |
| 6 | Traumabase real-data application | **BLOCKED** | restricted data; older C6 descriptor does not match current v4 cohort description |

The run uses `K=3`, `d=10`, `n=2000/site`, and 1,500 Monte Carlo runs per DGP.
Current v4 uses different synthetic sample-size descriptions, so this is a
scoped audit rather than an exact paper-scale replication.

## Pages

| Page | What's there |
|---|---|
| [Overview](#/overview) | Paper, method, and source/version boundaries |
| [Claims & contracts](#/claims) | Claim producers, scopes, and statuses |
| [Evidence](#/evidence) | Recorded metrics and C6 access audit |
| [Verification run](#/verification-run) | Fixed command, environment, and run output |
| [Conclusion](#/conclusion) | Gate decision and limitations |

**Reproduce:** `bash repro/run.sh`. Full report:
[`reports/fedcausal/report.md`](https://github.com/MachineLearning-Nerd/icml26-federated-causal-inference/blob/main/reports/fedcausal/report.md).
