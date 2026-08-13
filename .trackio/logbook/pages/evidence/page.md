# Evidence

Authoritative recorded run: `ea6fbba7-0813-48dc-b94f-d5dd10c458bf`, historical
source commit `9617192`, 218 seconds on an HF cpu-upgrade with 32 workers and
one BLAS thread per worker. Scale: `K=3`, `d=10`, `n=2000/site`, 1,500 runs per
DGP, NumPy 2.5.1.

## C1 / C2 — weighting mechanisms

| Estimator | DGP | Propensity correlation | Cross-entropy (true) | AIPW bias | Reading |
|---|---|---:|---:|---:|---|
| MW (FedAvg) | B, well-specified | **0.934** | 0.712 (0.702) | **−0.006±0.002** | positive contract |
| MW (FedAvg) | A, misspecified | 0.327 | 4.47 | large | negative control |
| DW (Gaussian) | A, well-specified | **0.876** | **0.441 (0.437)** | +0.474 | posterior recovery contract |
| DW (Gaussian) | B, misspecified | recorded in raw run | recorded in raw run | — | degradation control |

The DW result is deliberately not described as an unbiased ATE result because
its recorded AIPW bias is `+0.474`.

## C3 — oracle equality

SymPy checks the Bayes posterior/decomposition and estimator-sum identities.
Across 400 oracle trials per DGP, maximum absolute differences are `5.33e−15`
and `1.78e−15`.

## C4 — variance ordering

The corrected expression is

`g''(e) = 2*(3e^2 - 3e + 1)/(e^3*(1-e)^3) > 0` for `0 < e < 1`.

Finite oracle variance ratios are:

| Scenario | `Var_fed / Var_meta` |
|---|---:|
| DGP A, good overlap | 0.9236 |
| DGP A, weak overlap | **0.0236** |
| DGP B, good overlap | 0.9266 |

![Theorem 4](../../../../reports/fedcausal/images/fig3_variance_thm4.png)

## C5 — overlap bound

Example 1 uses `e₁=0.99`, `e₂=0.01`, and equal weights: `O_global=4.0`, local
bound `101.01`. A generated DGP-A-good setting gives `4.793 ≤ 5.028`.

![Theorem 5](../../../../reports/fedcausal/images/fig4_overlap_thm5.png)

## C6 — access audit

The restricted Traumabase data are not checked in. Four routes were attempted:
public download, benchmark/package proxy, matched-scale surrogate, and
falsification. Each failed to reach the exact claim, so C6 is `BLOCKED`.

Current v4 describes 14 centers and 8,248 patients/638 treated; the artifact’s
older four-center descriptor is retained only as a versioned audit note.

## Raw artifacts

`outputs/verdict.json` and `outputs/claim*.json` are checked-in evidence. A fresh
run additionally generates ignored `outputs/sim_raw.csv` and
`.openresearch/artifacts/` intermediates.
