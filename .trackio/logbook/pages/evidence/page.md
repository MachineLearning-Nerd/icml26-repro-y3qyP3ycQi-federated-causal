# Evidence

Authoritative source: HF run `ea6fbba7`, branch `orx/faithful-full-scale-baseline`,
commit `9617192`, 218s on HF cpu-upgrade (32 workers, BLAS 1 thread/worker).
Scale: K=3, d=10, n=2000/site, 1500 Monte-Carlo runs per DGP. numpy 2.5.1.

## C1 / C2 — federated weighting (1500-run Monte-Carlo, "good" overlap)

| Estimator | DGP | propensity corr(ê,e) | cross-entropy (true) | AIPW bias | reading |
|---|---|---|---|---|---|
| **MW (FedAvg)** | B (well-spec) | **0.934** | 0.71 (0.70) | **−0.006±0.002** | unbiased ✓ |
| MW (FedAvg) | A (misspec) | 0.327 | 4.47 (0.44) | large | negative control |
| **DW (Gaussian)** | A (well-spec) | **0.876** | 0.441 (0.437) | +0.47 | recovers posterior ✓ |
| DW (Gaussian) | B (misspec) | 0.90 | 0.75 (0.70) | small | degrades gracefully |

MW membership classification accuracy in DGP B = 0.665 (chance = 0.33). The
contrast (MW unbiased in B / broken in A; DW recovers posterior in A / worse in B)
is exactly the paper's stated MW/DW duality — a built-in negative-control design.

## C3 — Theorem 3 (oracle equality)

Symbolic (SymPy), all identities evaluate True:
- DW weights ρ_k f_k/f = Bayes posterior P(H=k|X), and sum to 1;
- law of total probability: Σ_k P(H=k|X)e_k(X) = P(W=1|X);
- estimator sum: Σ_k (n_k/n)(1/n_k)Σ_{i∈k} φ(X_i) = (1/n)Σ_i φ(X_i).

Numerical (oracle nuisances, 400 trials each): max|fed − centralized| = **5.3e-15**
(DGP A), **1.8e-15** (DGP B) — machine precision, confirming the equality.

## C4 — Theorem 4 (variance ordering)

Symbolic: g(e)=1/(e(1−e)), g''(e)=2(−3e²+3e−1)/(e³(1−e)³) > 0 on (0,1) ⇒ strictly
convex ⇒ Jensen; total-variance identity Var[Y]=E[Var(Y|H)]+Var[E(Y|H)] confirmed.

Numerical (oracle, 1500 trials): Var_fed / Var_meta =
| Scenario | ratio | gap |
|---|---|---|
| DGP A, good overlap | 0.924 | small (local ≈ global propensities) |
| DGP A, weak overlap | **0.024** | large (federation rescues poor-overlap site) |
| DGP B, good overlap | 0.927 | small |

All ≤ 1; the gap widens under weak overlap, exactly as the theorem predicts.

## C5 — Theorem 5 (overlap bound)

Example 1 (reproduced exactly): K=2, X=1, e₁=0.99, e₂=0.01 ⇒ e=0.5.
O₁=O₂=(0.99·0.01)⁻¹≈101.01; O_global=(0.5·0.5)⁻¹=**4.0**; bound Σρ_k O_k=101.01.
0 ≤ 4 ≤ 101.01 ✓. Numerical DGP-A-good: O_global=4.79 ≤ 5.03 ✓.

## C6 — Traumabase (BLOCKED) — 4 routes

1. **Public download search** — Traumabase (Mayer et al. 2020) is a restricted French
   registry; no public individual-level data. → no data.
2. **Benchmark/R-package proxy** — checked Colnet et al. 2024 & Josse-group repos for
   the K=4 / 472-treated / 5531-control / 17-covariate subset; none published. → no data.
3. **Semi-synthetic surrogate at matched scale** — would exercise the pipeline but
   cannot reproduce the paper's TA/mortality point estimates. → not the claim.
4. **Falsification** — needs real covariate/outcome distributions under A1-A3; without
   data no assumption-satisfying counterexample exists. → cannot falsify.

## Raw artifacts (in repo)

`outputs/verdict.json`, `outputs/claim1_membership_weights.json`,
`outputs/claim2_density_ratio.json`, `outputs/claim3_theorem3.json`,
`outputs/claim4_theorem4.json`, `outputs/claim5_theorem5.json`,
`outputs/claim6_traumabase.json`, `outputs/sim_raw.csv` (3000 per-run rows).
Internal audit: `.openresearch/artifacts/{source_audit.md, method.md, sim_raw.csv}`.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_7f31347be0bc", "created_at": "2026-07-22T04:56:19+00:00", "title": "Historical rejected baseline (4/12)"}
-->
## Historical rejected baseline (4/12) — superseded

> Original (rejected) evidence excerpt, preserved unchanged. The current full-scale
> evidence is above. The judge rejected this for using 200-patient synthetic data,
> reusing the membership number for density-ratio (claim 2), and loose 8-trial
> heuristic theorem checks.

## Verification output (last 40 lines)
```
density-ratio weighted ATE: 2.0620 (comparable to membership)  -> PASS   [REJECTED: reuses membership value]
federated MSE=0.0053, centralized MSE=0.0401 (ratio=0.13)      -> PASS   [REJECTED: loose 8-trial heuristic]
federated var=0.0052, meta var=0.0064                           -> PASS   [REJECTED: loose 8-trial heuristic]
federated bias=0.0116                                            -> PASS   [REJECTED: misidentifies claim 5]
4-site mean error=0.1067, 8-site mean error=0.0706              -> PASS   [REJECTED: unrelated to claim 6]
6/6 claims verified.   [REJECTED overall: 4/12]
```
