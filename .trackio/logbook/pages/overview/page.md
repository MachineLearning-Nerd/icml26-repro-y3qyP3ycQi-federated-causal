# Overview

## Paper

Rémi Khellaf, Aurélien Bellet, and Julie Josse, *Federated Causal Inference
from Multi-Site Observational Data via Propensity Score Aggregation*,
[arXiv:2505.17961v4](https://arxiv.org/abs/2505.17961), OpenReview `y3qyP3ycQi`.

The paper estimates an ATE across sites that cannot pool patient-level data. It
decomposes the global propensity score as

> `e(X) = Σ_k ω_k(X) · e_k(X)`

using Membership Weights (`ω_k=P(H=k|X)`) or Density-Ratio Weights
(`ω_k=ρ_k f_k(X)/f(X)`), then constructs federated IPW/AIPW estimators.

## What this audit does

The clean-room implementation exercises the two weighting mechanisms, the
oracle estimator identity, variance comparisons, and the overlap example. It
uses the code in `repro/src/` and the recorded run `ea6fbba7`.

The local verifier uses `K=3`, `d=10`, `n=2000/site`, and 1,500 Monte Carlo
runs per DGP. Current v4 describes DGP A with `n_k=650` and DGP B with total
`n=4000`; this difference is now explicit, so the run is called a scoped
synthetic audit rather than “paper scale.”

Current v4 also describes Traumabase as 14 centers, 8,248 patients, and 638
treated patients. The checked-in C6 artifact retains an older four-center
descriptor and has no patient-level data. C6 is therefore `BLOCKED`.

See [`SOURCE_MANIFEST.md`](https://github.com/MachineLearning-Nerd/icml26-federated-causal-inference/blob/main/SOURCE_MANIFEST.md)
for the full boundary audit.
