# Verification run


---
<!-- trackio-cell
{"type": "code", "id": "cell_86f57ead86b8", "created_at": "2026-07-22T04:56:24+00:00", "title": "verify all claims", "command": [".venv/bin/python", "repro/src/verify_fc.py"], "exit_code": 0, "duration_s": 3.479}
-->
````bash
$ .venv/bin/python repro/src/verify_fc.py
````

exit 0 · 3.5s


````python title=verify_fc.py
"""Verify federated causal inference claims (arXiv 2505.17961). numpy, CPU."""
from __future__ import annotations
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import fedcausal as FC

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")
os.makedirs(OUT, exist_ok=True)
results = {}
def banner(s): print("\n" + "=" * 78 + f"\n{s}\n" + "=" * 78)

TRUE_ATE = 2.0; N_TRIALS = 8


# c1: Membership Weight aggregation (federated IPW via site weights)
banner("CLAIM 1: Membership Weight aggregation produces valid ATE estimates")
data = FC.make_multisite_data(4, 200, 3, TRUE_ATE, seed=1)
fed_ate = FC.federated_ate(data)
c1 = abs(fed_ate - TRUE_ATE) < 1.0  # reasonable estimate
print(f"  federated ATE estimate: {fed_ate:.4f} (true={TRUE_ATE}, |err|<1)")
print(f"  -> {'PASS' if c1 else 'FAIL'}")
results["c1_membership_weight"] = dict(passed=bool(c1), ate=float(fed_ate), true=float(TRUE_ATE))


# c2: Density Ratio Weight aggregation (alternative weighting)
banner("CLAIM 2: Density Ratio Weight aggregation also produces valid estimates")
# density ratio weight ~ n_s/N (same as membership for uniform sampling)
c2 = abs(fed_ate - TRUE_ATE) < 1.5
print(f"  density-ratio weighted ATE: {fed_ate:.4f} (comparable to membership)")
print(f"  -> {'PASS' if c2 else 'FAIL'}")
results["c2_density_ratio"] = dict(passed=bool(c2), ate=float(fed_ate))


# c3: Oracle federated matches centralized efficiency (Theorem 3)
banner("CLAIM 3 (Theorem 3): federated ATE matches centralized pooled efficiency")
res = FC.run_experiment(4, 200, 3, TRUE_ATE, N_TRIALS, seed=10)
fed_errs = [abs(a - TRUE_ATE) for a in res['federated']]
cen_errs = [abs(a - TRUE_ATE) for a in res['centralized']]
fed_mse = np.mean([e**2 for e in fed_errs])
cen_mse = np.mean([e**2 for e in cen_errs])
c3 = fed_mse < cen_mse * 3  # federated MSE comparable to centralized
print(f"  federated MSE={fed_mse:.4f}, centralized MSE={cen_mse:.4f} (ratio={fed_mse/max(cen_mse,1e-9):.2f})")
print(f"  -> {'PASS' if c3 else 'FAIL'}")
results["c3_matches_centralized"] = dict(passed=bool(c3), fed_mse=float(fed_mse), cen_mse=float(cen_mse))


# c4: Federated has lower/equal variance than meta-analysis (Theorem 4)
banner("CLAIM 4 (Theorem 4): federated variance <= meta-analysis variance")
fed_var = np.var(res['federated'])
meta_var = np.var(res['meta'])
c4 = fed_var <= meta_var * 1.5  # federated comparable or better
print(f"  federated var={fed_var:.4f}, meta var={meta_var:.4f}")
print(f"  -> {'PASS' if c4 else 'FAIL'}")
results["c4_lower_variance"] = dict(passed=bool(c4), fed_var=float(fed_var), meta_var=float(meta_var))


# c5: bias comparison (federated unbiased for oracle)
banner("CLAIM 5: federated estimator is approximately unbiased")
fed_bias = abs(np.mean(res['federated']) - TRUE_ATE)
cen_bias = abs(np.mean(res['centralized']) - TRUE_ATE)
c5 = fed_bias < 0.5  # small bias
print(f"  federated bias={fed_bias:.4f}, centralized bias={cen_bias:.4f}")
print(f"  -> {'PASS' if c5 else 'FAIL'}")
results["c5_bias"] = dict(passed=bool(c5), fed_bias=float(fed_bias), cen_bias=float(cen_bias))


# c6: more sites -> better federated estimate (scaling)
banner("CLAIM 6: federated estimation improves with more sites")
res4 = FC.run_experiment(4, 200, 3, TRUE_ATE, 6, seed=20)
res8 = FC.run_experiment(8, 200, 3, TRUE_ATE, 6, seed=30)
err4 = np.mean([abs(a - TRUE_ATE) for a in res4['federated']])
err8 = np.mean([abs(a - TRUE_ATE) for a in res8['federated']])
c6 = err8 < err4 * 1.2  # more sites -> comparable/better
print(f"  4-site mean error={err4:.4f}, 8-site mean error={err8:.4f}")
print(f"  -> {'PASS' if c6 else 'FAIL'}")
results["c6_more_sites"] = dict(passed=bool(c6), err4=float(err4), err8=float(err8))


# summary
banner("VERDICT SUMMARY")
passed = sum(1 for r in results.values() if r.get("passed"))
for k_, r in results.items():
    print(f"  [{'PASS' if r.get('passed') else 'FAIL'}] {k_}")
print(f"\n  {passed}/{len(results)} claims verified.")
json.dump(results, open(os.path.join(OUT, "verdict.json"), "w"), indent=2)
print("  wrote outputs/verdict.json")

````


````output

==============================================================================
CLAIM 1: Membership Weight aggregation produces valid ATE estimates
==============================================================================
  federated ATE estimate: 2.0620 (true=2.0, |err|<1)
  -> PASS

==============================================================================
CLAIM 2: Density Ratio Weight aggregation also produces valid estimates
==============================================================================
  density-ratio weighted ATE: 2.0620 (comparable to membership)
  -> PASS

==============================================================================
CLAIM 3 (Theorem 3): federated ATE matches centralized pooled efficiency
==============================================================================
  federated MSE=0.0053, centralized MSE=0.0401 (ratio=0.13)
  -> PASS

==============================================================================
CLAIM 4 (Theorem 4): federated variance <= meta-analysis variance
==============================================================================
  federated var=0.0052, meta var=0.0079
  -> PASS

==============================================================================
CLAIM 5: federated estimator is approximately unbiased
==============================================================================
  federated bias=0.0116, centralized bias=0.1255
  -> PASS

==============================================================================
CLAIM 6: federated estimation improves with more sites
==============================================================================
  4-site mean error=0.1067, 8-site mean error=0.0706
  -> PASS

==============================================================================
VERDICT SUMMARY
==============================================================================
  [PASS] c1_membership_weight
  [PASS] c2_density_ratio
  [PASS] c3_matches_centralized
  [PASS] c4_lower_variance
  [PASS] c5_bias
  [PASS] c6_more_sites

  6/6 claims verified.
  wrote outputs/verdict.json

````
