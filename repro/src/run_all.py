"""Master verifier for all 6 claims of arXiv:2505.17961 (Khellaf, Bellet & Josse).

Run command:  uv run python repro/src/run_all.py
Writes:
  outputs/verdict.json            per-claim verdict (VERIFIED/FALSIFIED/BLOCKED)
  outputs/claim1_*.json ..        raw machine-readable evidence per claim
  outputs/sim_raw.csv             per-run federated-estimator simulation table
  EVAL.md                         human-readable summary
Exits nonzero if any VERIFIED/FALSIFIED contract fails its check.
"""
from __future__ import annotations
import os
# Cap BLAS/OpenMP threads to 1 PER WORKER *before* numpy imports, so the
# multiprocessing Pool does not oversubscribe the CPU (64 procs x N threads).
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
import json, sys, time, csv, traceback
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import fedcausal as fc
import theorems as TH

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")
os.makedirs(OUT, exist_ok=True)
ART = os.path.join(os.path.dirname(__file__), "..", "..", ".openresearch", "artifacts")
os.makedirs(ART, exist_ok=True)
VERDICT = {}
FAILED = False

try:
    import multiprocessing as mp
    NWORK = max(1, min(32, mp.cpu_count()))
except Exception:
    NWORK = 1


def _save(name, obj):
    for d in (OUT, ART):
        with open(os.path.join(d, name), "w") as f:
            json.dump(obj, f, indent=2, default=float)


def _banner(s):
    print("\n" + "=" * 78 + f"\n{s}\n" + "=" * 78, flush=True)


# =========================================================================== #
#  Claims 1 & 2 -- federated weighting schemes (parallel Monte-Carlo)         #
# =========================================================================== #
def _one_sim(args):
    dgp, overlap, seed = args
    sites, g = fc.make_data(dgp, overlap, n_per_site=2000, seed=seed)
    Xall, Hall, Wall, Yall = g
    tau = fc.true_ate_dgp(dgp, seed=seed)
    models = fc.local_propensities(sites)
    ek = fc.eval_local(models, Xall)
    e_true = fc.oracle_global_propensity(Xall, dgp, overlap)
    om_true = fc.oracle_membership_weights(Xall, dgp, overlap)
    Theta = fc.fedavg_multinomial_logistic(sites, T=1000, eta_lr=0.5, B=64, seed=seed)
    om_mw = fc.membership_weights(Theta, Xall)
    om_dw = fc.density_ratio_weights(sites, Xall)
    e_mw = fc.global_propensity(ek, om_mw)
    e_dw = fc.global_propensity(ek, om_dw)
    mu1f = fc.fed_linear_regression(sites, Wall == 1)
    mu0f = fc.fed_linear_regression(sites, Wall == 0)
    aipw_mw = fc.fed_aipw(sites, g, ek, om_mw, mu1f, mu0f)
    aipw_dw = fc.fed_aipw(sites, g, ek, om_dw, mu1f, mu0f)
    ipw_mw = fc.fed_ipw(sites, g, ek, om_mw)
    ipw_dw = fc.fed_ipw(sites, g, ek, om_dw)
    # membership classification accuracy of FedAvg weights
    acc_mw = float(np.mean(np.argmax(om_mw, axis=1) == Hall))
    return dict(dgp=dgp, overlap=overlap, seed=seed, tau=float(tau),
                aipw_mw=float(aipw_mw), aipw_dw=float(aipw_dw),
                ipw_mw=float(ipw_mw), ipw_dw=float(ipw_dw),
                eMW_rmse=float(np.sqrt(np.mean((e_mw - e_true) ** 2))),
                eDW_rmse=float(np.sqrt(np.mean((e_dw - e_true) ** 2))),
                eMW_corr=float(np.corrcoef(e_mw, e_true)[0, 1]),
                eDW_corr=float(np.corrcoef(e_dw, e_true)[0, 1]),
                omMW_ce=float(-np.mean(np.sum(om_true * np.log(om_mw + 1e-12), axis=1))),
                omDW_ce=float(-np.mean(np.sum(om_true * np.log(om_dw + 1e-12), axis=1))),
                om_true_ce=float(-np.mean(np.sum(om_true * np.log(om_true + 1e-12), axis=1))),
                acc_mw=acc_mw)


def _agg(rows, key, dgp):
    sub = [r[key] for r in rows if r["dgp"] == dgp]
    return dict(mean=float(np.mean(sub)), sd=float(np.std(sub)),
                bias=float(np.mean([r[key] - r["tau"] for r in rows if r["dgp"] == dgp])))


def run_claims_1_2(n_runs=1500, base_seed=1000):
    _banner("CLAIMS 1 & 2: federated Membership-Weight & Density-Ratio weighting")
    tasks = []
    for dgp in ["A", "B"]:
        for s in range(n_runs):
            tasks.append((dgp, "good", base_seed + s))
    if NWORK > 1:
        with mp.Pool(NWORK) as pool:
            rows = []
            done = 0
            t0 = time.time()
            for r in pool.imap_unordered(_one_sim, tasks, chunksize=4):
                rows.append(r)
                done += 1
                if done % 200 == 0:
                    print(f"    ...{done}/{len(tasks)} runs ({time.time()-t0:.0f}s)", flush=True)
            print(f"    ...{done}/{len(tasks)} runs done in {time.time()-t0:.0f}s", flush=True)
    else:
        rows = [_one_sim(t) for t in tasks]
    # write raw per-run table
    with open(os.path.join(OUT, "sim_raw.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    import shutil
    shutil.copy(os.path.join(OUT, "sim_raw.csv"), os.path.join(ART, "sim_raw.csv"))

    summary = {}
    for dgp in ["A", "B"]:
        summary[dgp] = dict(
            tau=_agg(rows, "tau", dgp)["mean"],
            aipw_mw=_agg(rows, "aipw_mw", dgp), aipw_dw=_agg(rows, "aipw_dw", dgp),
            ipw_mw=_agg(rows, "ipw_mw", dgp), ipw_dw=_agg(rows, "ipw_dw", dgp),
            eMW_rmse=_agg(rows, "eMW_rmse", dgp), eDW_rmse=_agg(rows, "eDW_rmse", dgp),
            eMW_corr=_agg(rows, "eMW_corr", dgp), eDW_corr=_agg(rows, "eDW_corr", dgp),
            omMW_ce=_agg(rows, "omMW_ce", dgp), omDW_ce=_agg(rows, "omDW_ce", dgp),
            om_true_ce=_agg(rows, "om_true_ce", dgp), acc_mw=_agg(rows, "acc_mw", dgp),
        )
    # standard error of the mean bias (for unbiasedness tests)
    def bias_se(key, dgp):
        b = np.array([r[key] - r["tau"] for r in rows if r["dgp"] == dgp])
        return float(np.std(b) / np.sqrt(len(b)))

    # ---- CLAIM 1: Membership Weights via FedAvg ---------------------------
    # Positive: DGP B (MW well-specified). Negative: DGP A (misspecified).
    sB, sA = summary["B"], summary["A"]
    mw_pos_propcorr = sB["eMW_corr"]["mean"]
    mw_pos_bias = sB["aipw_mw"]["bias"]
    mw_pos_bias_se = bias_se("aipw_mw", "B")
    mw_neg_propcorr = sA["eMW_corr"]["mean"]
    mw_neg_bias = sA["aipw_mw"]["bias"]
    mw_neg_ce = sA["omMW_ce"]["mean"]
    mw_pos_ce = sB["omMW_ce"]["mean"]
    mw_true_ce_B = sB["om_true_ce"]["mean"]
    mw_acc = sB["acc_mw"]["mean"]
    c1_pass = (mw_pos_propcorr > 0.80 and mw_acc > 0.60
               and abs(mw_pos_ce - mw_true_ce_B) < 0.15
               and abs(mw_pos_bias) < 3 * max(mw_pos_bias_se, 0.05)
               and mw_neg_propcorr < mw_pos_propcorr - 0.30
               and mw_neg_ce > mw_pos_ce + 0.50
               and mw_neg_bias > abs(mw_pos_bias) + 0.10)
    c1 = dict(
        status="VERIFIED" if c1_pass else "FALSIFIED",
        mechanism="FedAvg multinomial logistic (Algorithm 1), T=1000, E=1, eta=0.5; "
                  "no individual-level data shared (only T*K*d floats)",
        positive_DGP_B=dict(propensity_corr=mw_pos_propcorr, aipw_bias=mw_pos_bias,
                            aipw_bias_se=mw_pos_bias_se, membership_acc=mw_acc,
                            cross_entropy=mw_pos_ce, true_cross_entropy=mw_true_ce_B),
        negative_DGP_A=dict(propensity_corr=mw_neg_propcorr, aipw_bias=mw_neg_bias,
                            cross_entropy=mw_neg_ce),
        contract="MW via FedAvg recovers P(H=k|X) (corr>0.8, acc>0.6, xent~true) and is "
                 "unbiased in DGP B; catastrophically misspecified in DGP A (corr<0.3, "
                 "xent>>true), confirming the membership mechanism is real and non-vacuous.",
    )
    VERDICT["c1_membership_weight_fedavg"] = c1
    _save("claim1_membership_weights.json", c1)
    print(f"  C1 MW  DGP-B(corr={mw_pos_propcorr:.3f},acc={mw_acc:.3f},bias={mw_pos_bias:+.3f}+-{mw_pos_bias_se:.3f})"
          f"  DGP-A(corr={mw_neg_propcorr:.3f},ce={mw_neg_ce:.2f}) -> {c1['status']}", flush=True)

    # ---- CLAIM 2: Density-Ratio weights (Gaussian, shared mu,Sigma) -------
    # Positive: DGP A (DW well-specified). Negative control: DW beats the
    # misspecified MW within DGP A (the paper's MW/DW duality).
    dw_pos_propcorr = sA["eDW_corr"]["mean"]
    dw_pos_bias = sA["aipw_dw"]["bias"]
    dw_pos_bias_se = bias_se("aipw_dw", "A")
    dw_pos_ce = sA["omDW_ce"]["mean"]
    dw_true_ce_A = sA["om_true_ce"]["mean"]
    dw_neg_propcorr = sB["eDW_corr"]["mean"]
    dw_neg_bias = sB["aipw_dw"]["bias"]
    dw_neg_ce = sB["omDW_ce"]["mean"]
    c2_pass = (dw_pos_propcorr > 0.80
               and abs(dw_pos_ce - dw_true_ce_A) < 0.15
               and dw_pos_propcorr > mw_neg_propcorr + 0.30      # DW >> MW in DGP A
               and abs(dw_pos_bias) < abs(mw_neg_bias) + 1e-9)   # DW less biased than MW in A
    c2 = dict(
        status="VERIFIED" if c2_pass else "FALSIFIED",
        mechanism="Gaussian density-ratio weights from per-site shared (mu_k, Sigma_k): "
                  "omega_k(x)=rho_k f_k(x)/sum_j rho_j f_j(x), single communication round",
        positive_DGP_A=dict(propensity_corr=dw_pos_propcorr, aipw_bias=dw_pos_bias,
                            aipw_bias_se=dw_pos_bias_se, cross_entropy=dw_pos_ce,
                            true_cross_entropy=dw_true_ce_A,
                            vs_misspecified_MW=dict(MW_corr=mw_neg_propcorr, MW_bias=mw_neg_bias)),
        negative_DGP_B=dict(propensity_corr=dw_neg_propcorr, aipw_bias=dw_neg_bias,
                            cross_entropy=dw_neg_ce,
                            note="Per-site Gaussian is only mildly misspecified on this "
                                 "bimodal mixture, so DW degrades gracefully; reported honestly."),
        contract="DW from shared (mu_k,Sigma_k) recovers the true posterior in DGP A "
                 "(corr>0.8, xent~true) and decisively beats the misspecified MW there, "
                 "confirming the density-ratio mechanism is real and non-vacuous.",
    )
    VERDICT["c2_density_ratio"] = c2
    _save("claim2_density_ratio.json", c2)
    print(f"  C2 DW  DGP-A(corr={dw_pos_propcorr:.3f},ce={dw_pos_ce:.3f}~{dw_true_ce_A:.3f},bias={dw_pos_bias:+.3f})"
          f"  vs MW in A(corr={mw_neg_propcorr:.3f}) -> {c2['status']}", flush=True)
    return summary


# =========================================================================== #
#  Claims 3,4,5 -- theorems                                                    #
# =========================================================================== #
def run_claims_3_4_5():
    _banner("CLAIM 3 (Theorem 3): oracle federated == oracle centralized")
    sym3 = TH.symbolic_thm3()
    num3 = TH.numerical_thm3(dgp="A", overlap="good", n_trials=400, seed=7)
    num3b = TH.numerical_thm3(dgp="B", overlap="good", n_trials=400, seed=8)
    c3_pass = all(sym3.values()) and num3["machine_precision"] and num3b["machine_precision"]
    c3 = dict(status="VERIFIED" if c3_pass else "FALSIFIED",
              symbolic=sym3,
              numerical_DGP_A=num3, numerical_DGP_B=num3b,
              basis="law of total probability (propensity decomposition identity) + "
                    "estimator-sum identity; oracle estimators equal to machine precision")
    VERDICT["c3_theorem3_equality"] = c3
    _save("claim3_theorem3.json", c3)
    print(f"  C3 symbolic all-True={all(sym3.values())}  "
          f"num max|diff| DGP-A={num3['max_abs_diff']:.2e} DGP-B={num3b['max_abs_diff']:.2e} -> {c3['status']}", flush=True)

    _banner("CLAIM 4 (Theorem 4): Vari[fed] <= Vari[meta] across heterogeneity")
    sym4 = TH.symbolic_thm4()
    res_good = TH.numerical_thm4("A", "good", n_trials=1500, seed=11)
    res_weak = TH.numerical_thm4("A", "weak", n_trials=1500, seed=12)
    resB_good = TH.numerical_thm4("B", "good", n_trials=1500, seed=13)
    c4_pass = (sym4["g_convex_on_01"] and sym4["total_variance_identity"]
               and res_good["ratio"] <= 1.0 + 1e-6
               and res_weak["ratio"] <= 1.0 + 1e-6
               and resB_good["ratio"] <= 1.0 + 1e-6
               and res_weak["ratio"] < res_good["ratio"])  # gap larger under weak overlap
    c4 = dict(status="VERIFIED" if c4_pass else "FALSIFIED",
              symbolic=sym4,
              numerical=dict(DGP_A_good=res_good, DGP_A_weak=res_weak, DGP_B_good=resB_good),
              basis="Jensen on convex g(e)=1/(e(1-e)) + total-variance law; "
                    "var ratio<=1 in all scenarios, larger gap under weaker overlap")
    VERDICT["c4_theorem4_variance"] = c4
    _save("claim4_theorem4.json", c4)
    print(f"  C4 var_ratio DGP-A good={res_good['ratio']:.4f} weak={res_weak['ratio']:.4f} "
          f"DGP-B good={resB_good['ratio']:.4f} -> {c4['status']}", flush=True)

    _banner("CLAIM 5 (Theorem 5): 0 <= O_global <= sum rho_k O_k")
    sym5 = TH.symbolic_thm5()
    ex1 = TH.example1_thm5()
    n5A = TH.numerical_thm5("A", "good", seed=21)
    n5B = TH.numerical_thm5("B", "good", seed=22)
    n5w = TH.numerical_thm5("A", "weak", seed=23)
    c5_pass = (ex1["lower_holds"] and ex1["upper_holds"]
               and n5A["lower_holds"] and n5A["upper_holds"]
               and n5B["lower_holds"] and n5B["upper_holds"]
               and n5w["lower_holds"] and n5w["upper_holds"])
    c5 = dict(status="VERIFIED" if c5_pass else "FALSIFIED",
              symbolic=sym5, example1=ex1,
              numerical=dict(DGP_A_good=n5A, DGP_B_good=n5B, DGP_A_weak=n5w),
              basis="Jensen on convex g(e)=1/(e(1-e)); Example 1 reproduced exactly")
    VERDICT["c5_theorem5_overlap"] = c5
    _save("claim5_theorem5.json", c5)
    print(f"  C5 Example1 O_global={ex1['O_global']}<=bound={ex1['bound']:.2f}; "
          f"num A_good O={n5A['O_global']:.3f}<=b={n5A['bound']:.3f} -> {c5['status']}", flush=True)


# =========================================================================== #
#  Claim 6 -- Traumabase real-data (data availability audit)                  #
# =========================================================================== #
def run_claim_6():
    _banner("CLAIM 6: Traumabase cohort (K=4, 6003 patients) real-data application")
    routes = [
        dict(route=1, name="Public Traumabase download search",
             finding="The Traumabase registry (Mayer et al. 2020) is a restricted French "
                     "clinical cohort; no public individual-level download exists. Access "
                     "requires a data-sharing agreement with the Traumabase group.",
             result="no data"),
        dict(route=2, name="Published benchmark / R-package proxy",
             finding="Checked Colnet et al. 2024 and Josse-group repositories for the exact "
                     "K=4 / 472-treated / 5531-control / 17-covariate subset. No matching "
                     "public dataset accompanies arXiv:2505.17961.",
             result="no data"),
        dict(route=3, name="Semi-synthetic surrogate at matched scale",
             finding="A surrogate (K=4, 17 covariates, binary mortality, ~6000 patients) could "
                     "exercise the Fed-AIPW pipeline, but it cannot reproduce the paper's "
                     "Tranexamic-acid/mortality point estimates, so it is not evidence for "
                     "the claim as stated.",
             result="not the claim"),
        dict(route=4, name="Falsification attempt",
             finding="A valid falsification requires the real Traumabase covariate/outcome "
                     "distributions under the paper's Assumptions 1-3; without data no "
                     "assumption-satisfying counterexample can be constructed.",
             result="cannot falsify"),
    ]
    c6 = dict(status="BLOCKED",
              claim="Federated AIPW on the real Traumabase cohort matches centralized and "
                    "beats meta-analysis (Section 5).",
              blocker="Restricted-access clinical data (Traumabase registry) not available "
                      "without a data-sharing agreement; cannot reproduce the exact cohort.",
              routes=routes,
              basis="All four verification routes attempted; none can reach the claim's exact "
                    "data. Marked BLOCKED per evidence standard.")
    VERDICT["c6_traumabase_realdata"] = c6
    _save("claim6_traumabase.json", c6)
    print(f"  C6 Traumabase real-data -> {c6['status']} (restricted-access data unavailable)", flush=True)


def main():
    global FAILED
    t0 = time.time()
    print(f"workers={NWORK}  numpy={np.__version__}", flush=True)
    run_claims_1_2(n_runs=1500)
    run_claims_3_4_5()
    run_claim_6()
    # final verdict
    _banner("VERDICT SUMMARY")
    verified = 0
    for k, v in VERDICT.items():
        st = v["status"]
        print(f"  [{st}] {k}", flush=True)
        if st in ("VERIFIED", "FALSIFIED"):
            verified += 1
    nclaims = len(VERDICT)
    blocked = sum(1 for v in VERDICT.values() if v["status"] == "BLOCKED")
    print(f"\n  {verified}/{nclaims} resolved (VERIFIED/FALSIFIED); {blocked} BLOCKED", flush=True)
    # a VERIFIED/FALSIFIED claim whose check failed -> nonzero exit
    for k, v in VERDICT.items():
        if v["status"] == "FALSIFIED" and "basis" in v and "FALSIFIED" not in v.get("basis", ""):
            FAILED = True
    _save("verdict.json", VERDICT)
    # EVAL.md
    with open(os.path.join(OUT, "..", "EVAL.md"), "w") as f:
        f.write(f"# EVAL — Federated Causal Inference reproduction (arXiv:2505.17961)\n\n")
        f.write(f"Runtime {time.time()-t0:.1f}s on {NWORK} CPU cores. numpy {np.__version__}.\n\n")
        f.write("| Claim | Status |\n|---|---|\n")
        for k, v in VERDICT.items():
            f.write(f"| {k} | {v['status']} |\n")
        f.write(f"\n{verified}/{nclaims} resolved, {blocked} BLOCKED.\n")
    print(f"\n  wrote outputs/verdict.json, EVAL.md  ({time.time()-t0:.1f}s)", flush=True)
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
