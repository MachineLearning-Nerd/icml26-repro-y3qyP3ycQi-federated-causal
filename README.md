# Repro — Federated Causal Inference on Multi-Site Observational Data

OpenReview `y3qyP3ycQi` · arXiv [2505.17961](https://arxiv.org/abs/2505.17961) · 6 claims / 12 pts.

## Reproduction summary

**Paper:** Khellaf, Bellet & Josse — estimate a common ATE across hospitals that
cannot pool patient data, by decomposing the global propensity into a weighted
combination of local propensities (Membership Weights via FedAvg, or Density-Ratio
Weights from shared Gaussian moments).

**What we did:** clean-room implementation of the exact DGPs (Appendix C, d=10, K=3,
n=2000/site), FedAvg (Algorithm 1), Gaussian density-ratio weights, centralized &
meta-analysis baselines, plus SymPy symbolic derivations for the three theorems.
1500-run Monte-Carlo at paper scale on CPU, with built-in negative controls.

**Result: 5/6 VERIFIED, 1/6 BLOCKED** (claim 6 needs the restricted Traumabase registry).

| Claim | Method / theorem | Paper | Observed | Assessment |
|---|---|---|---|---|
| 1 | Membership Weights (FedAvg, Eq. 3) | — | prop corr 0.934, AIPW bias −0.006±0.002 | VERIFIED |
| 2 | Density-Ratio Weights (Eq. 4) | — | prop corr 0.876, xent 0.441≈true | VERIFIED |
| 3 | Theorem 3 (fed = centralized) | equality | oracle diff 5.3e-15 | VERIFIED |
| 4 | Theorem 4 (Var_fed ≤ Var_meta) | ≤ | ratios 0.924/0.024/0.927 ≤ 1 | VERIFIED |
| 5 | Theorem 5 (overlap bound) | ≤ | Example 1: 4 ≤ 101.01 | VERIFIED |
| 6 | Traumabase real data | — | restricted data unavailable | BLOCKED |

**Downscaling/substitutions:** n=2000/site (Appendix value; main text says 500);
outcome noise σ=1 and propensity clipping [0.01,0.99] not pinned by paper (standard).
**Compute:** local CPU for figures (~60 s); HF cpu-upgrade for the authoritative
1500-run verification (218 s, 32 vCPUs, no GPU).

📖 **Full illustrated report:** [`reports/fedcausal/report.md`](reports/fedcausal/report.md)

## Reproduce

```bash
bash repro/run.sh   # = uv run --locked python repro/src/run_all.py
```
Python 3.12, numpy 2.5.1, sympy 1.14 (pinned in `pyproject.toml` / `uv.lock`).
Writes `outputs/verdict.json`, `outputs/claim*.json`, `outputs/sim_raw.csv`, `EVAL.md`.

## Experiment log

| Branch / experiment | Purpose | Exact run command | Outcome | Compute |
|---|---|---|---|---|
| `master` | publication surface | not run as an experiment (publication surface) | — | — |
| [`orx/faithful-full-scale-baseline`](https://github.com/MachineLearning-Nerd/icml26-repro-y3qyP3ycQi-federated-causal/tree/orx/faithful-full-scale-baseline) | full faithful reproduction of all 6 claims | `bash repro/run.sh` | 5/6 VERIFIED, 1/6 BLOCKED (run `ea6fbba7`) | HF cpu-upgrade, 218 s |

> Internal run/experiment IDs are kept in `orx exp desc`; this table shows the
> reader-facing lineage. `master` is presentation-only here.
