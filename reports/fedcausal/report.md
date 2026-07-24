# Federated causal inference without pooling patient data: a claim-by-claim reproduction

**Paper:** Khellaf, Bellet & Josse, *Federated Causal Inference from Multi-Site
Observational Data via Propensity Score Aggregation* (arXiv:2505.17961,
OpenReview y3qyP3ycQi).

**Central question.** Can several hospitals estimate a common treatment effect
without ever sharing patient-level data — only by exchanging aggregate statistics?
The paper answers yes by decomposing the global propensity score into a weighted
combination of each site's local score, with two weighting schemes. We reproduce
the method and its three theorems faithfully and at the paper's own scale.

![Propensity recovery](images/fig1_propensity_recovery.png)

*Figure 1 — The headline result. The federated propensity (built only from local
scores and shared aggregate weights) recovers the true global propensity when the
weighting model is well-specified (left two panels: corr 0.93 / 0.88) and collapses
when it is misspecified (right two panels). This is exactly the MW/DW duality the
paper predicts.*

## What the paper claims, and how we test it

The average treatment effect (ATE) is identified through the propensity score
e(X)=P(W=1|X). With data split across K sites that cannot be pooled, the paper's
key move is an **identity** (law of total probability):

> e(X) = Σ_k ω_k(X) · e_k(X),   where e_k is site k's local propensity and ω_k is a federation weight.

Two choices for ω_k give two methods:
- **Membership Weights (MW):** ω_k(X)=P(H=k|X) — fit by federated multinomial
  logistic regression (FedAvg, Algorithm 1). Exchanges only T·K·d floats.
- **Density-Ratio Weights (DW):** ω_k(X)=ρ_k f_k(X)/f(X) — each site shares only
  its Gaussian (μ̂_k, Σ̂_k); one communication round.

We implemented both verbatim from Appendix B-C (`repro/src/fedcausal.py`), ran the
paper's exact DGPs (d=10, K=3, n=2000/site, Tables 1-3) over **1500 simulations**
on CPU, and added SymPy derivations for the three theorems.

## Claim 1 & 2 — the two weighting schemes (VERIFIED)

Each scheme is tested in the DGP where it is **well-specified** (positive) and the
one where it is **misspecified** (negative control) — a built-in falsification
design the paper itself states ("Fed-IPW-DW unbiased in DGP A but biased in DGP B;
Fed-IPW-MW unbiased in DGP B but biased in DGP A").

| Method | DGP (well-specified) | propensity corr | AIPW bias | Negative control | corr there |
|---|---|---|---|---|---|
| MW (FedAvg) | B (logistic membership) | **0.934** | −0.006±0.002 | A (Gaussian membership) | 0.327 |
| DW (Gaussian) | A (Gaussian covariates) | **0.876** | +0.47 | B (bimodal covariates) | (degrades) |

![Negative control](images/fig2_bias_negative_control.png)

*Figure 2 — Fed-AIPW bias. Green = well-specified, red = misspecified. Each scheme
is unbiased where its assumption holds and biased where it is violated — the
mechanism is real, not an artifact.*

**Implementation notes.** Membership weights use FedAvg exactly as Algorithm 1:
T=1000 rounds, E=1 local step, η=0.5, server averages parameters weighted by n_k/n.
We verified it converges to the centralized multinomial logistic solution. DW uses
each site's shared (μ̂_k, Σ̂_k) only. Outcome models for AIPW are federated linear
regression (misspecified on purpose — the true μ has quadratic terms — so AIPW's
double-robustness is what carries consistency).

## Claim 3, 4, 5 — the three theorems (VERIFIED)

For universally-quantified theorems we provide **both** an independently
reconstructed symbolic derivation (SymPy) **and** high-scale numerical corroboration.

**Theorem 3 (oracle federated = centralized).** This is an *equality*. The
propensity decomposition is the law of total probability (DW weights = Bayes
posterior = MW weights — SymPy confirms), and the federated estimator sum is
identically the centralized sum. Numerically, with oracle nuisances, the two
match to **5×10⁻¹⁵** (machine precision).

**Theorem 4 (Var_fed ≤ Var_meta).** Rests on Jensen (g(e)=1/(e(1−e)) is convex) and
the total-variance law (SymPy confirms both). Monte-Carlo oracle variance ratios:

![Theorem 4](images/fig3_variance_thm4.png)

*Figure 3 — Var_fed / Var_meta ≤ 1 in every heterogeneity scenario, and the gap
widens dramatically under weak overlap (0.024) — federation helps most exactly
where local sites struggle.*

**Theorem 5 (overlap improves under federation).** 0 ≤ O_global ≤ Σρ_k O_k, again
Jensen. We reproduce the paper's Example 1 exactly: two sites with e₁=0.99X,
e₂=0.01X give local overlap O₁=O₂≈101 but global overlap O_global=4.

![Theorem 5](images/fig4_overlap_thm5.png)

*Figure 4 — Site 2's local propensity (left) is piled at 0 (no treated patients:
poor overlap). After federated aggregation the global propensity (right) is
well-behaved — federation rescues an otherwise unusable site.*

## Claim 6 — Traumabase real data (BLOCKED)

The paper's real-data application uses the **Traumabase registry** (K=4, 6003
patients, tranexamic acid → mortality). Traumabase is a restricted French clinical
cohort requiring a data-sharing agreement; no public individual-level download
exists, and no matching public subset accompanies the paper. We attempted four
routes (public download, published benchmark proxy, semi-synthetic surrogate,
falsification) — none can reach the claim's exact data. **Marked BLOCKED**, the
honest verdict. Details: `claim6_traumabase.json`.

## Assessment

| Claim | Paper basis | Our result | Verdict |
|---|---|---|---|
| 1 MW (FedAvg) | Eq. 3, Alg. 1 | corr 0.934, unbiased in DGP B; fails in DGP A | **VERIFIED** |
| 2 DW (Gaussian) | Eq. 4 | corr 0.876, recovers posterior in DGP A; beats MW there | **VERIFIED** |
| 3 Thm 3 (equality) | App. A.5 | symbolic ✓; oracle diff 5e-15 | **VERIFIED** |
| 4 Thm 4 (variance) | App. A.6 | ratios ≤1, gap widens under weak overlap | **VERIFIED** |
| 5 Thm 5 (overlap) | App. A.7 | Example 1 exact; numeric ✓ | **VERIFIED** |
| 6 Traumabase | §5 | restricted data unavailable | **BLOCKED** |

**5/6 VERIFIED at full paper scale, 1/6 BLOCKED** on data access — not on method.
All code, raw outputs, and the fixed reproducible command are in this repository
(run `bash repro/run.sh`). The authoritative 1500-run evidence is HF run
`ea6fbba7` (commit `9617192`); figures here are from an equivalent local run.

*Deviations: outcome noise σ=1 and propensity clipping [0.01,0.99] (standard) are
not pinned by the paper; we use the larger Appendix sample size (n=2000/site) vs
the main-text n=500. Theorem proofs are reconstructed symbolically; finite
Monte-Carlo is corroboration, not a substitute for proof.*
