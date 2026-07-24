# Verification run

## Current verifier (full-scale) — supersedes all historical runs

**Fixed run command (identical on every node):** `bash repro/run.sh`
→ `uv run --locked python repro/src/run_all.py`
**Pinned environment:** `pyproject.toml` + `uv.lock`, Python 3.12, numpy 2.5.1,
scipy 1.18.0, sympy 1.14.0, pandas 3.0.5, matplotlib 3.11.1. Image
`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`.
**Run:** HF cpu-upgrade, run id `ea6fbba7`, commit `9617192`, 32 workers
(BLAS 1 thread/worker), **218 s**, 2026-07-24. Deterministic seeds per simulation.

````bash
$ bash repro/run.sh   # uv run --locked python repro/src/run_all.py
workers=32  numpy=2.5.1
CLAIMS 1 & 2: federated Membership-Weight & Density-Ratio weighting
    ...3000/3000 runs done in 173s
  C1 MW  DGP-B(corr=0.934,acc=0.665,bias=-0.006+-0.002)  DGP-A(corr=0.327,ce=4.47) -> VERIFIED
  C2 DW  DGP-A(corr=0.876,ce=0.441~0.437,bias=+0.474)  vs MW in A(corr=0.327) -> VERIFIED
CLAIM 3 (Theorem 3): oracle federated == oracle centralized
  C3 symbolic all-True=True  num max|diff| DGP-A=5.33e-15 DGP-B=1.78e-15 -> VERIFIED
CLAIM 4 (Theorem 4): Vari[fed] <= Vari[meta] across heterogeneity
  C4 var_ratio DGP-A good=0.9236 weak=0.0236 DGP-B good=0.9266 -> VERIFIED
CLAIM 5 (Theorem 5): 0 <= O_global <= sum rho_k O_k
  C5 Example1 O_global=4.0<=bound=101.01; num A_good O=4.793<=b=5.028 -> VERIFIED
CLAIM 6: Traumabase cohort (K=4, 6003 patients) real-data application
  C6 Traumabase real-data -> BLOCKED (restricted-access data unavailable)
VERDICT SUMMARY
  [VERIFIED] c1_membership_weight_fedavg
  [VERIFIED] c2_density_ratio
  [VERIFIED] c3_theorem3_equality
  [VERIFIED] c4_theorem4_variance
  [VERIFIED] c5_theorem5_overlap
  [BLOCKED]  c6_traumabase_realdata
  5/6 resolved (VERIFIED/FALSIFIED); 1 BLOCKED
  wrote outputs/verdict.json, EVAL.md  (217.8s)
````

The verifier (`repro/src/run_all.py`) exits **nonzero** if any VERIFIED/FALSIFIED
contract fails its check. Here it exited 0. Re-running regenerates `outputs/*.json`,
`outputs/sim_raw.csv`, and `EVAL.md` from the fixed command.

---
<!-- trackio-cell
{"type": "code", "id": "cell_86f57ead86b8", "created_at": "2026-07-22T04:56:24+00:00", "title": "Historical rejected baseline (4/12)"}
-->
## Historical rejected baseline (4/12) — superseded

> The run below is the **original rejected** verification (200-patient synthetic
> data, 8 trials, loose thresholds). It is preserved unchanged for provenance and
> is **NOT** the current verifier. Current verifier is above.

````bash
$ .venv/bin/python repro/src/verify_fc.py    # HISTORICAL — rejected
````

The historical `verify_fc.py` and `fedcausal.py` (toy, 200 patients) remain in the
repo for lineage; the current full-scale code is `repro/src/run_all.py` +
`fedcausal.py` (rewritten) + `theorems.py`.
