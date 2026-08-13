# Claims & contracts

The current verifier is [`repro/src/run_all.py`](https://github.com/MachineLearning-Nerd/icml26-federated-causal-inference/blob/main/repro/src/run_all.py).
Its local `VERIFIED` labels mean that the finite contract passed; the
publication gate maps them to scoped evidence.

## C1 — Membership Weights via FedAvg — VERIFIED_SCOPED

**Producer:** `run_claims_1_2` → `fedcausal.py::fedavg_multinomial_logistic`,
`membership_weights`, and `fed_aipw`.

**Contract:** DGP B positive control recovers membership probabilities and has
small AIPW bias; DGP A is an explicit misspecification control.

**Result:** DGP-B correlation `0.934`, accuracy `0.665`, AIPW bias
`−0.006±0.002`; DGP-A correlation `0.327`.

## C2 — Gaussian Density-Ratio Weights — VERIFIED_SCOPED

**Producer:** `run_claims_1_2` → `density_ratio_weights` and
`global_propensity`.

**Contract:** DGP A recovers the true posterior and beats misspecified MW.

**Result:** correlation `0.876`, cross-entropy `0.441` versus true `0.437`;
MW correlation in DGP A is `0.327`. The recorded AIPW bias is `+0.474`, so
this contract does not claim unbiased ATE estimation.

## C3 — Theorem 3 — VERIFIED_SCOPED

**Producer:** `theorems.py::symbolic_thm3` and `numerical_thm3`.

The symbolic checks cover Bayes weights, the law of total probability, and the
estimator-sum identity. Oracle numerical differences are `5.33e−15` and
`1.78e−15`. This is scoped oracle corroboration, not a replacement for the
paper’s assumptions and proof.

## C4 — Theorem 4 — VERIFIED_SCOPED

**Producer:** `theorems.py::symbolic_thm4` and `numerical_thm4`.

The symbolic path checks the convexity ingredient and total-variance identity;
the numerical path checks three finite scenarios. Ratios are `0.9236`, `0.0236`,
and `0.9266`. The corrected derivative string is recorded in
`outputs/claim4_theorem4.json`.

## C5 — Theorem 5 — VERIFIED_SCOPED

**Producer:** `symbolic_thm5`, `example1_thm5`, and `numerical_thm5`.

The code checks positivity/strict convexity, reproduces Example 1 (`4.0 ≤
101.01`), and checks generated scenarios. These are finite corroborating
checks, not an independent formal proof of every theorem assumption.

## C6 — Traumabase real data — BLOCKED

**Producer:** `run_claim_6` and `outputs/claim6_traumabase.json`.

The data-access audit attempted public download, benchmark proxy,
semi-synthetic surrogate, and falsification routes. None reaches the exact
patient-level claim. Current v4’s cohort descriptor also differs from the
older descriptor in the artifact.
