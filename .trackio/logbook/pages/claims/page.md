# Claims & contracts

Each claim is reduced to a machine-checkable contract (`repro/src/run_all.py`,
exits nonzero on failure). Verifier source: [`repro/src/run_all.py`](https://github.com/MachineLearning-Nerd/icml26-repro-y3qyP3ycQi-federated-causal/blob/master/repro/src/run_all.py),
[`fedcausal.py`](https://github.com/MachineLearning-Nerd/icml26-repro-y3qyP3ycQi-federated-causal/blob/master/repro/src/fedcausal.py),
[`theorems.py`](https://github.com/MachineLearning-Nerd/icml26-repro-y3qyP3ycQi-federated-causal/blob/master/repro/src/theorems.py).

## C1 — Membership Weights via FedAvg — VERIFIED
**Exact claim (Eq. 3, §4.2.2, Alg. 1):** ω_k(X)=P(H=k|X) estimated by federated
multinomial logistic regression trained with FedAvg, exchanging only T·K·d floats,
no patient-level data centralized.
**Contract:** recovers P(H=k|X) in DGP B (corr>0.8, acc>0.6, xent≈Bayes optimum,
AIPW unbiased |bias|<3·SE); misspecified in DGP A (corr drops >0.3, xent rises >0.5).
**Result:** DGP-B corr=**0.934**, acc=0.665, AIPW bias=**−0.006±0.002**; DGP-A corr=0.327, xent=4.47.

## C2 — Density-Ratio Weights (Gaussian shared μ,Σ) — VERIFIED
**Exact claim (Eq. 4, §4.2.2):** ω_k(X)=ρ_k f_k(X)/f(X), each site shares (μ̂_k,Σ̂_k),
Gaussian f_k, one communication round.
**Contract:** recovers posterior in DGP A (corr>0.8, xent≈optimum) and decisively
beats misspecified MW there (corr_DW−corr_MW>0.3).
**Result:** DGP-A corr=**0.876**, xent=**0.441≈true 0.437**; vs MW corr=0.327 in DGP A.

## C3 — Theorem 3 (oracle federated = centralized) — VERIFIED
**Exact claim (Thm 3, App. A.5):** under A1-A3 the oracle federated estimators
(Def. 3) are **equal** to oracle centralized (Def. 1).
**Contract:** (a) SymPy confirms the decomposition identity (law of total probability;
DW weights = Bayes posterior = MW weights; sum to 1) and the estimator-sum identity;
(b) numerically oracle fed == centralized to <1e-9.
**Result:** symbolic all-True; oracle max|fed−cen| = **5.3e-15**.

## C4 — Theorem 4 (Var_fed ≤ Var_meta) — VERIFIED
**Exact claim (Thm 4, App. A.6):** under A1,A2,A4, V[τ̂*_IPW]=V[τ̂^fed*]≤V[τ̂^meta*]
(and AIPW), equality iff local propensities coincide.
**Contract:** (a) SymPy confirms g(e)=1/(e(1−e)) strictly convex (Jensen) and the
total-variance identity; (b) oracle V_fed/V_meta ≤ 1 across scenarios, gap larger
under weak overlap.
**Result:** ratios **0.924** (A good), **0.024** (A weak), **0.927** (B good).

## C5 — Theorem 5 (0 ≤ O_global ≤ Σρ_k O_k) — VERIFIED
**Exact claim (Thm 5, App. A.7):** global overlap bounded by weighted local overlaps.
**Contract:** Jensen on convex g; reproduce Example 1 exactly; numeric check.
**Result:** Example 1 **O_global=4.0 ≤ 101.01**; DGP-A-good O=4.79 ≤ 5.03.

## C6 — Traumabase real data — BLOCKED
**Exact claim (§5):** Fed-AIPW on Traumabase (K=4, 472 treated + 5531 control, 17
covariates, tranexamic acid → mortality) matches centralized, beats Meta-SW.
**Blocker:** restricted-access registry; 4 routes attempted (public download,
benchmark proxy, semi-synthetic surrogate, falsification) — none reach the exact data.
**Verdict:** BLOCKED (data access, not method).

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_d07327926a6b", "created_at": "2026-07-22T04:56:18+00:00", "title": "Historical rejected baseline (4/12)"}
-->
## Historical rejected baseline (4/12) — superseded

> Original claim list, preserved unchanged. The current contracts/results are above.

## Claims to reproduce

1. Membership Weight aggregation estimates the probability of belonging to each site given covariates via federated multinomial logistic regression trained with FedAvg, without centralizing patient-level data (Equation 3).
2. Density Ratio Weight aggregation instead models the ratio between a site's covariate density and the overall population density, estimated parametrically from shared means and covariances (Equation 4).
3. Theorem 3 shows the oracle federated IPW/AIPW estimators achieve the same asymptotic efficiency as estimators computed on centrally pooled data (Theorem 3).
4. Theorem 4 proves the federated estimators have lower or equal variance than meta-analysis approaches across all considered heterogeneity scenarios (Theorem 4).
5. Theorem 5 establishes that the global (federated) overlap measure is bounded as 0 ≤ 𝒪_global ≤ Σ_k ρ_k 𝒪_k, i.e., federation can improve on the overlap achievable at any single site (Theorem 5).
6. On the Traumabase cohort (K=4 trauma centers, 6,003 patients) studying tranexamic acid's effect on mortality, federated AIPW estimates match centralized estimates while achieving lower variance than meta-analysis (Section 5, real-data application).
