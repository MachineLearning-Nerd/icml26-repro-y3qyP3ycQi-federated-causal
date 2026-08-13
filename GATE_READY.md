# Publication gate

`PUBLICATION_GATE: NOT_READY`

Current status: `VERIFIED_SCOPED_WITH_LIMITATIONS`.

- Five finite synthetic/theorem contracts report `VERIFIED`.
- Claim 6, the Traumabase real-data application, is `BLOCKED` because the
  restricted patient-level data are unavailable.
- The current arXiv v4 describes a different Traumabase cohort than the older
  descriptor preserved in the recorded C6 audit.
- The verifier’s synthetic sample sizes also differ from the current v4
  appendix, so the run is not labeled an exact paper-scale replication.
- `publication_gate.json` is the machine-readable source of this decision.

This gate is intentionally conservative. It should only be revisited after a
source-pinned v4 implementation and authorized Traumabase analysis are available.
