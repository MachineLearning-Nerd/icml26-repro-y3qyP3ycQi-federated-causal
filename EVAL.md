# EVAL — Federated Causal Inference reproduction (arXiv:2505.17961)

Run `ea6fbba7` (commit `9617192`), HF cpu-upgrade, 32 workers, 218 s. numpy 2.5.1.

| Claim | Status |
|---|---|
| c1_membership_weight_fedavg | VERIFIED |
| c2_density_ratio | VERIFIED |
| c3_theorem3_equality | VERIFIED |
| c4_theorem4_variance | VERIFIED |
| c5_theorem5_overlap | VERIFIED |
| c6_traumabase_realdata | BLOCKED |

5/6 resolved (VERIFIED/FALSIFIED); 1 BLOCKED.

Key numbers: C1 MW DGP-B prop corr 0.934, AIPW bias −0.006±0.002 (DGP-A corr 0.327);
C2 DW DGP-A prop corr 0.876, xent 0.441≈true 0.437; C3 oracle diff 5.3e-15;
C4 Var_fed/Var_meta = 0.924/0.024/0.927; C5 Example 1 O_global=4≤101.01.
