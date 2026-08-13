# Verification run

## Recorded current verifier

**Command:** `bash repro/run.sh` → `uv run --locked python repro/src/run_all.py`

**Environment:** Python 3.12, NumPy 2.5.1, SciPy 1.18.0, SymPy 1.14.0,
32 CPU workers, one BLAS thread per worker.

**Run:** `ea6fbba7-0813-48dc-b94f-d5dd10c458bf`, historical source commit
`9617192`, 218 seconds.

```text
C1 MW  DGP-B(corr=0.934,acc=0.665,bias=-0.006+-0.002)
    DGP-A(corr=0.327) -> VERIFIED
C2 DW  DGP-A(corr=0.876,ce=0.441~0.437,bias=+0.474)
    vs MW in A(corr=0.327) -> VERIFIED
C3 oracle max|diff| DGP-A=5.33e-15 DGP-B=1.78e-15 -> VERIFIED
C4 var_ratio DGP-A good=0.9236 weak=0.0236 DGP-B good=0.9266 -> VERIFIED
C5 Example1 O_global=4.0 <= bound=101.01 -> VERIFIED
C6 Traumabase -> BLOCKED (restricted-access data unavailable)
5/6 local contracts resolved; 1 BLOCKED
```

The verifier exited `0` because no finite contract was falsified. The gate is
still `NOT_READY`: C6 is blocked and the run’s scale/source boundaries are not
fully aligned with current arXiv v4.

## Historical baseline

The superseded 200-patient toy verifier is preserved under `repro/legacy/` for
provenance only. It is not part of the current evidence and is not used by
`repro/run.sh`.
