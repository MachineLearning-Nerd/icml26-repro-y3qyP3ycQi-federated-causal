# Conclusion

## Result

**Five local contracts report `VERIFIED`; C6 is `BLOCKED`.** The overall status
is `VERIFIED_SCOPED_WITH_LIMITATIONS`, and the strict publication gate is
**NOT PASSED**.

| Claim | Producer | Evidence | Gate status |
|---|---|---|---|
| C1 | FedAvg membership path | correlation 0.934; negative control 0.327 | VERIFIED_SCOPED |
| C2 | Gaussian density-ratio path | correlation 0.876; AIPW bias +0.474 | VERIFIED_SCOPED |
| C3 | symbolic + oracle numerical path | max difference 5.33e−15 | VERIFIED_SCOPED |
| C4 | convexity + variance path | ratios ≤ 1 in three scenarios | VERIFIED_SCOPED |
| C5 | convexity + Example 1 + numerical path | 4.0 ≤ 101.01 | VERIFIED_SCOPED |
| C6 | Traumabase access audit | restricted data and version boundary | BLOCKED |

## Why the gate is not passed

- C6 cannot be reproduced without authorized clinical data.
- Current arXiv v4 describes a 14-center, 8,248-patient Traumabase cohort;
  the checked-in C6 descriptor is an older four-center subset.
- Current v4 synthetic sample-size descriptions differ from the local verifier’s
  `n=2000/site` setting.
- Finite checks and symbolic ingredients are valuable evidence but are not a
  full paper-level proof or replication.

The machine-readable decision is [`publication_gate.json`](../../../../publication_gate.json).
The source/version details are in [`SOURCE_MANIFEST.md`](../../../../SOURCE_MANIFEST.md).

## Reproduction boundary

The repository’s current code is the publication surface. The old toy verifier
is under `repro/legacy/` and is explicitly excluded. The old `orx/*` branch was
an ancestor of the publication tree and is removed after its role was recorded
in [`BRANCH_AUDIT.md`](../../../../BRANCH_AUDIT.md).

## Citation and thanks

Please cite Khellaf, Bellet, and Josse, [arXiv:2505.17961](https://arxiv.org/abs/2505.17961).
Thank you to the authors for making the method and assumptions sufficiently
clear for independent auditing. This work is independent and not author
reviewed or endorsed.
