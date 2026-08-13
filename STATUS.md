# Status

**Overall:** `VERIFIED_SCOPED_WITH_LIMITATIONS`

| Area | Status | Reason |
| --- | --- | --- |
| C1–C5 synthetic/theorem contracts | `VERIFIED` locally | Recorded finite checks and symbolic identities are available in `outputs/`. |
| C6 Traumabase | `BLOCKED` | Restricted patient-level data are unavailable, and the current v4 cohort description differs from the older audit descriptor. |
| Paper-level replication | `NOT PASSED` | Simulation scale and real-data source version are not fully aligned. |
| Publication gate | `NOT_READY` | See [`publication_gate.json`](publication_gate.json). |

This status distinguishes a reproducible local contract from a claim that the
paper has been fully replicated. See [`SOURCE_MANIFEST.md`](SOURCE_MANIFEST.md)
for the source/version boundary and [`BRANCH_AUDIT.md`](BRANCH_AUDIT.md) for
repository history cleanup.
