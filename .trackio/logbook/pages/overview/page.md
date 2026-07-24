# Overview

## Paper

Khellaf, Bellet & Josse, *Federated Causal Inference from Multi-Site Observational
Data via Propensity Score Aggregation* (arXiv:2505.17961). The ATE is estimated
across K sites that cannot pool patient-level data by decomposing the **global
propensity** into a weighted combination of **local propensities**:

> e(X) = Σ_k ω_k(X) · e_k(X)

Two weighting schemes: **Membership Weights** (ω_k = P(H=k|X), federated multinomial
logistic via FedAvg) and **Density-Ratio Weights** (ω_k = ρ_k f_k(X)/f(X), each site
shares only Gaussian μ̂_k, Σ̂_k). These feed Fed-IPW and doubly-robust Fed-AIPW.

## What this reproduction does

Clean-room implementation of the exact DGPs (Appendix C, Tables 1-3: d=10, K=3,
n=2000/site), FedAvg (Algorithm 1), Gaussian density-ratio weights, centralized and
meta-analysis estimators, **plus SymPy symbolic derivations** for the three theorems.
1500 Monte-Carlo runs at paper scale on CPU, with the paper's own well-specified /
misspecified DGPs serving as **built-in negative controls**.

**Source audit:** retrieved 2026-07-24 from https://ar5iv.labs.arxiv.org/html/2505.17961,
SHA-256 `e2e587cc90b99f6feefb848ad92aad62dde2cee1d933329e3a47036d586d11a2`.

## What changed vs the rejected baseline (4/12)

The previous baseline (Space revision `a7eb5704`) used 200-patient synthetic data,
did not implement density-ratio estimation (it re-used the membership-weight number
for claim 2), misidentified claim 5 (tested bias instead of the overlap bound), and
tested the theorems with loose 8-trial numerical heuristics. **That historical
logbook is preserved verbatim below on each page under "Historical rejected baseline"
and is superseded by the full-scale evidence above.** See [Verification run](#/verification-run).

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_b517ba2ca285", "created_at": "2026-07-22T04:56:17+00:00", "title": "Historical rejected baseline (4/12)"}
-->
## Historical rejected baseline (4/12) — superseded

> The content below is the **original rejected** overview, preserved unchanged for
> provenance. It is NOT the current evidence. Current evidence is above and on the
> [Claims](#/claims) / [Evidence](#/evidence) pages.

# Federated Causal Inference on Multi-Site Observational Data

OpenReview: https://openreview.net/forum?id=y3qyP3ycQi
arXiv: https://arxiv.org/abs/2505.17961

Clean-room CPU reproduction. 6 anchored claims (12 possible points). All claims verified at full scale.
