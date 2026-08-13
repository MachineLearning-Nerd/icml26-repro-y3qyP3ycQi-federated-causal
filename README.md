# ICML 2026 — Federated Causal Inference

Independent, clean-room reproduction audit for **Federated Causal Inference
from Multi-Site Observational Data via Propensity Score Aggregation** by Rémi
Khellaf, Aurélien Bellet, and Julie Josse.

> **Current status:** `VERIFIED_SCOPED_WITH_LIMITATIONS` — five local synthetic
> contracts report `VERIFIED`, Claim 6 is `BLOCKED`, and the strict publication
> gate is **NOT PASSED**.

This repository is part of the `MachineLearning-Nerd` ICML 2026 reproduction
collection. It is an independent audit, not the authors’ implementation and
not an author-endorsed replication.

## Paper

- **Title:** [Federated Causal Inference from Multi-Site Observational Data via
  Propensity Score Aggregation](https://arxiv.org/abs/2505.17961)
- **Authors:** Rémi Khellaf, Aurélien Bellet, Julie Josse
- **arXiv:** `2505.17961v4` (current version revised 11 June 2026)
- **OpenReview:** `y3qyP3ycQi`
- **Repository homepage:** <https://arxiv.org/abs/2505.17961>

The paper estimates an average treatment effect (ATE) when patient-level data
remain at separate sites. Each site estimates a local propensity score

\[
e_k(x)=P(W=1\mid X=x,H=k),
\]

and the federation constructs a global score by combining local scores:

\[
e(x)=\sum_k \omega_k(x)e_k(x).
\]

The paper studies Membership Weights (MW), Density-Ratio Weights (DW), and the
resulting federated IPW/AIPW estimators. Its theory compares the oracle
federated estimator with centralized and meta-analysis estimators and studies
global overlap.

## Reproduction verdict

The authoritative recorded run is `ea6fbba7-0813-48dc-b94f-d5dd10c458bf`.
It ran the local verifier from historical source commit `9617192` on a
32-worker CPU environment in 218 seconds. The source branch used for that run
was `orx/faithful-full-scale-baseline`; that branch is now documented and
removed as a publication branch during cleanup.

| Claim | Local contract result | Evidence path | Scope boundary |
| --- | --- | --- | --- |
| C1 — MW via FedAvg | `VERIFIED` | `run_all.py::run_claims_1_2` → `fedcausal.py::fedavg_multinomial_logistic`, `membership_weights`, `fed_aipw` | 1,500 seeded simulations, DGP B positive control and DGP A negative control |
| C2 — Gaussian DW | `VERIFIED` | `run_all.py::run_claims_1_2` → `density_ratio_weights`, `global_propensity` | Posterior-recovery contract in DGP A; the recorded AIPW bias is `+0.474`, so this is not an unbiased-ATE claim |
| C3 — Theorem 3 | `VERIFIED` | `run_all.py::run_claims_3_4_5` → `theorems.py::symbolic_thm3`, `numerical_thm3` | Oracle identity and finite numerical equality; not a proof of every paper assumption |
| C4 — Theorem 4 | `VERIFIED` | `theorems.py::symbolic_thm4`, `numerical_thm4` | Key Jensen/variance identities plus 1,500-trial variance ratios |
| C5 — Theorem 5 | `VERIFIED` | `theorems.py::symbolic_thm5`, `example1_thm5`, `numerical_thm5` | Convexity check, exact Example 1, and finite numerical bounds |
| C6 — Traumabase | `BLOCKED` | `run_all.py::run_claim_6` → `outputs/claim6_traumabase.json` | Restricted clinical data unavailable; current arXiv v4 also uses a different cohort description |

The five `VERIFIED` labels are verifier-contract results, not universal claims
that the paper has been fully replicated. The conservative gate therefore
records `publication_gate_passed: false`.

### Key recorded numbers

- C1, positive DGP B: propensity correlation `0.934`, membership accuracy
  `0.665`, AIPW bias `−0.006 ± 0.002`; DGP A negative-control correlation
  `0.327`.
- C2, positive DGP A: propensity correlation `0.876`, cross-entropy
  `0.441` versus true `0.437`; AIPW bias `+0.474`.
- C3: oracle federated/centralized maximum absolute difference
  `5.33e−15` in DGP A and `1.78e−15` in DGP B.
- C4: recorded federated/meta variance ratios `0.9236`, `0.0236`, and
  `0.9266` across the three scenarios.
- C5: Example 1 gives `O_global = 4.0 ≤ 101.01`; numerical DGP-A-good gives
  `4.793 ≤ 5.028`.

## Important source-version and scale boundaries

The earlier repository text called the run “paper scale.” That description was
too strong and has been removed.

1. The current arXiv v4 describes the synthetic DGP A with `K=3`, `d=10`, and
   `n_k=650` per site, and DGP B with total `n=4000`. This repository’s
   verifier uses `n=2000/site` for both DGPs. The run is therefore a useful
   scoped synthetic audit, not an exact reproduction of the current simulation
   sample sizes.
2. The current arXiv v4 Traumabase section describes `K=14`, `8,248` patients,
   and `638` treated patients. The recorded C6 audit still carries the older
   `K=4`, `472 treated + 5,531 control` descriptor. Because the restricted data
   are unavailable and the source-version boundary is unresolved, C6 remains
   `BLOCKED` and no real-data result is claimed.
3. Outcome noise `σ=1` and propensity clipping `[0.01, 0.99]` are implementation
   choices not pinned in the repository’s source record. The theorem checks use
   oracle quantities; finite Monte Carlo is corroboration, not a substitute for
   the paper’s proof.

The exact source-version audit is recorded in
[`SOURCE_MANIFEST.md`](SOURCE_MANIFEST.md), and the machine-readable gate is
[`publication_gate.json`](publication_gate.json).

## How each claim is produced

The flow is deliberately explicit:

```text
fedcausal.py
  ├─ local propensity models e_k(X)
  ├─ FedAvg membership weights ω_k(X)       ─┐
  └─ Gaussian density-ratio weights ω_k(X)  ─┼─ global e(X) ── Fed-IPW/Fed-AIPW
                                             ┘
theorems.py
  ├─ symbolic identities for Theorem 3
  ├─ convexity + total-variance checks for Theorem 4
  └─ convexity, Example 1, and numerical bound checks for Theorem 5
run_all.py
  ├─ runs the seeded synthetic contracts
  ├─ performs the four-route C6 data-availability audit
  └─ writes outputs/claim*.json and outputs/verdict.json
```

The authoritative code paths are:

- `repro/src/fedcausal.py`: DGPs, local propensity models, FedAvg, MW, DW,
  global propensity, IPW, AIPW, and oracle helpers.
- `repro/src/run_all.py`: the six claim contracts and output generation.
- `repro/src/theorems.py`: symbolic and numerical checks for Theorems 3–5.
- `outputs/claim*.json`: one machine-readable record per claim.
- `outputs/verdict.json`: the consolidated recorded verdict.
- `reports/fedcausal/report.md`: the narrative audit with figures.

Run the current verifier with:

```bash
bash repro/run.sh
```

It uses the locked Python environment and writes generated `outputs/sim_raw.csv`
and `.openresearch/artifacts/` files locally; those generated files are ignored
by Git. A full run is CPU-intensive. The checked-in JSON artifacts above are the
recorded evidence used by the gate.

## Branch map

The source repository had two branches before cleanup:

| Historical branch | What it contained | Final treatment |
| --- | --- | --- |
| `master` | Publication surface, evidence outputs, report, and later marimo notebook merge | Renamed to `main` |
| `orx/faithful-full-scale-baseline` | Full-scale synthetic verifier and evidence run used for `ea6fbba7` | Its tree was already an ancestor of `master`; documented, then removed as a stale branch ref |

The final publication surface is the sole `main` branch. No `orx/*` branch is
needed for the checked-in evidence. Future work should use descriptive branches
such as `audit/traumabase-v4` or `audit/current-simulation-scale`, and merge only
reviewed evidence into `main`.

See [`BRANCH_AUDIT.md`](BRANCH_AUDIT.md) for the pre-cleanup topology and the
final branch invariant.

## Repository contents

- [`repro/src/fedcausal.py`](repro/src/fedcausal.py) — clean-room implementation.
- [`repro/src/run_all.py`](repro/src/run_all.py) — authoritative verifier.
- [`repro/src/theorems.py`](repro/src/theorems.py) — theorem checks.
- [`repro/notebooks/federated_causal_tutorial.py`](repro/notebooks/federated_causal_tutorial.py) —
  lightweight identity/Example 1 walkthrough.
- [`reports/fedcausal/report.md`](reports/fedcausal/report.md) — illustrated report.
- [`outputs/`](outputs/) — checked-in claim artifacts.
- [`repro/legacy/`](repro/legacy/) — superseded toy verifier, provenance only.
- [`EVAL.md`](EVAL.md), [`STATUS.md`](STATUS.md), [`GATE_READY.md`](GATE_READY.md) —
  status and gate records.

## Citation

```bibtex
@article{khellaf2025federated,
  title         = {Federated Causal Inference from Multi-Site Observational Data via Propensity Score Aggregation},
  author        = {Khellaf, R{\'e}mi and Bellet, Aur{\'e}lien and Josse, Julie},
  journal       = {arXiv preprint arXiv:2505.17961},
  year          = {2025},
  doi           = {10.48550/arXiv.2505.17961}
}
```

Please cite the version of the paper you actually use; the current record is
[`arXiv:2505.17961v4`](https://arxiv.org/abs/2505.17961).

## Thank you

Thank you to Rémi Khellaf, Aurélien Bellet, and Julie Josse for making this
research available and for clearly exposing the assumptions, weighting schemes,
and theoretical comparisons that make an independent audit possible. This
repository is an independent reproduction audit and does not imply review,
approval, or endorsement by the authors.
