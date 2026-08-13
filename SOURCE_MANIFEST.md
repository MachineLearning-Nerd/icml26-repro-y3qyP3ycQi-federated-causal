# Source and version manifest

## Primary paper source

- Canonical record: <https://arxiv.org/abs/2505.17961>
- Current version: `2505.17961v4`, revised 11 June 2026
- Authors: Rémi Khellaf, Aurélien Bellet, Julie Josse
- OpenReview identifier recorded by the repository: `y3qyP3ycQi`
- Current HTML source: <https://arxiv.org/html/2505.17961>

The abstract record and HTML source use slightly different prepositions in the
displayed title (“from” versus “on”). The citation follows the arXiv abstract
record; the v4 HTML is the source used for the current numerical boundary audit.

## Current v4 facts relevant to this audit

The v4 synthetic appendix describes `K=3`, `d=10`, DGP A with `n_k=650` per
site, and DGP B with total `n=4000`. Its real-data section describes Traumabase
across `K=14` centers, with `8,248` patients and `638` treated patients.

## Repository evidence snapshot

- Recorded run: `ea6fbba7-0813-48dc-b94f-d5dd10c458bf`
- Historical source branch: `orx/faithful-full-scale-baseline`
- Historical source commit: `9617192` (before attribution normalization)
- Recorded environment: Python 3.12, NumPy 2.5.1, 32 CPU workers,
  one BLAS thread per worker
- Local verifier scale: `K=3`, `d=10`, `n=2000/site`, 1,500 Monte Carlo runs
  for each DGP

## Explicit mismatches

1. `n=2000/site` is not the current v4 appendix setting. The checked-in
   evidence is retained as a scoped synthetic audit rather than silently
   relabeled as a faithful reproduction.
2. `outputs/claim6_traumabase.json` records the older `K=4`, `472 treated +
   5,531 control`, 17-covariate descriptor. It is not evidence for the current
   v4 `K=14`, 8,248-patient cohort. No patient-level data are included here.
3. The source snapshot does not prove that the local implementation reproduces
   every implementation detail of the paper’s current v4 experiments.

The mismatch is why the publication gate is `NOT_READY` even though five local
contracts have machine-readable evidence.
