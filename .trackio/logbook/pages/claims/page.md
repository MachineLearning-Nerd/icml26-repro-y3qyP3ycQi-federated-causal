# Claims


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_d07327926a6b", "created_at": "2026-07-22T04:56:18+00:00", "title": "Claims to reproduce"}
-->
## Claims to reproduce

1. Membership Weight aggregation estimates the probability of belonging to each site given covariates via federated multinomial logistic regression trained with FedAvg, without centralizing patient-level data (Equation 3).
2. Density Ratio Weight aggregation instead models the ratio between a site's covariate density and the overall population density, estimated parametrically from shared means and covariances (Equation 4).
3. Theorem 3 shows the oracle federated IPW/AIPW estimators achieve the same asymptotic efficiency as estimators computed on centrally pooled data (Theorem 3).
4. Theorem 4 proves the federated estimators have lower or equal variance than meta-analysis approaches across all considered heterogeneity scenarios (Theorem 4).
5. Theorem 5 establishes that the global (federated) overlap measure is bounded as 0 ≤ 𝒪_global ≤ Σ_k ρ_k 𝒪_k, i.e., federation can improve on the overlap achievable at any single site (Theorem 5).
6. On the Traumabase cohort (K=4 trauma centers, 6,003 patients) studying tranexamic acid's effect on mortality, federated AIPW estimates match centralized estimates while achieving lower variance than meta-analysis (Section 5, real-data application).
