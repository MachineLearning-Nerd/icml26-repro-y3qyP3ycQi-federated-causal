"""Generate report figures from a modest local Monte-Carlo (illustrative; the
authoritative 1500-run evidence is HF run ea6fbba7, commit 9617192)."""
from __future__ import annotations
import os
os.environ.update({k: "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                 "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")})
import sys, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(__file__))
import fedcausal as fc
import theorems as TH

FIG = os.path.join(os.path.dirname(__file__), "..", "..", "reports", "fedcausal", "images")
os.makedirs(FIG, exist_ok=True)
NR = 120


def sim(dgp, overlap, seed):
    sites, g = fc.make_data(dgp, overlap, n_per_site=2000, seed=seed)
    Xall, Hall, Wall, Yall = g
    tau = fc.true_ate_dgp(dgp, seed=seed)
    e_true = fc.oracle_global_propensity(Xall, dgp, overlap)
    models = fc.local_propensities(sites)
    ek = fc.eval_local(models, Xall)
    Theta = fc.fedavg_multinomial_logistic(sites, T=1000, eta_lr=0.5, B=64, seed=seed)
    om_mw = fc.membership_weights(Theta, Xall)
    om_dw = fc.density_ratio_weights(sites, Xall)
    e_mw = fc.global_propensity(ek, om_mw)
    e_dw = fc.global_propensity(ek, om_dw)
    mu1f = fc.fed_linear_regression(sites, Wall == 1)
    mu0f = fc.fed_linear_regression(sites, Wall == 0)
    return dict(tau=tau, e_true=e_true, e_mw=e_mw, e_dw=e_dw,
                aipw_mw=fc.fed_aipw(sites, g, ek, om_mw, mu1f, mu0f),
                aipw_dw=fc.fed_aipw(sites, g, ek, om_dw, mu1f, mu0f))


print("running local sims...", flush=True)
res = {dgp: [sim(dgp, "good", 500 + s) for s in range(NR)] for dgp in ["A", "B"]}

# ---- Figure 1: propensity recovery (claimed global e vs true e) -----------
fig, axs = plt.subplots(1, 4, figsize=(13, 3.2))
panels = [("MW", "DGP B (well-specified)", "B", "e_mw"), ("MW", "DGP A (misspecified)", "A", "e_mw"),
          ("DW", "DGP A (well-specified)", "A", "e_dw"), ("DW", "DGP B (misspecified)", "B", "e_dw")]
for ax, (sch, label, dgp, key) in zip(axs, panels):
    et = np.concatenate([r["e_true"] for r in res[dgp]])
    ee = np.concatenate([r[key] for r in res[dgp]])
    ax.scatter(et[::37], ee[::37], s=4, alpha=0.4, color="#2a6")
    lo, hi = 0, 1
    ax.plot([lo, hi], [lo, hi], "k--", lw=1)
    c = np.corrcoef(et, ee)[0, 1]
    ax.set_title(f"{sch}, {label}\ncorr={c:.3f}", fontsize=9)
    ax.set_xlabel("true global propensity $e(X)$")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
axs[0].set_ylabel("federated estimate $\\hat e(X)$")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig1_propensity_recovery.png"), dpi=130)
plt.close()

# ---- Figure 2: AIPW bias (negative-control structure) ---------------------
fig, ax = plt.subplots(figsize=(6, 3.6))
mwA = np.array([r["aipw_mw"] - r["tau"] for r in res["A"]])
mwB = np.array([r["aipw_mw"] - r["tau"] for r in res["B"]])
dwA = np.array([r["aipw_dw"] - r["tau"] for r in res["A"]])
dwB = np.array([r["aipw_dw"] - r["tau"] for r in res["B"]])
pos = np.arange(4)
means = [mwB.mean(), mwA.mean(), dwA.mean(), dwB.mean()]
ses = [mwB.std()/np.sqrt(NR), mwA.std()/np.sqrt(NR), dwA.std()/np.sqrt(NR), dwB.std()/np.sqrt(NR)]
cols = ["#2a6", "#d44", "#2a6", "#d44"]
lbls = ["MW\nDGP B", "MW\nDGP A", "DW\nDGP A", "DW\nDGP B"]
ax.bar(pos, means, yerr=ses, color=cols, alpha=0.8, capsize=4)
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(pos); ax.set_xticklabels(lbls)
ax.set_ylabel("Fed-AIPW bias (estimate - true ATE)")
ax.set_title("Each scheme unbiased when well-specified, biased when misspecified")
ax.annotate("well-specified", (0, means[0]), (0, means[0]+0.5), ha="center", fontsize=8, color="#2a6")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig2_bias_negative_control.png"), dpi=130)
plt.close()

# ---- Figure 3: variance ratio (Theorem 4) ---------------------------------
print("thm4 sims...", flush=True)
scen = [("DGP-A good", "A", "good"), ("DGP-A weak", "A", "weak"), ("DGP-B good", "B", "good")]
names = [s[0] for s in scen]
ratios = []
for nm, dgp, ov in scen:
    r = TH.numerical_thm4(dgp, ov, n_trials=800, seed=hash(nm) % 1000)
    ratios.append(r["ratio"])
fig, ax = plt.subplots(figsize=(5.5, 3.4))
ax.bar(names, ratios, color="#46a", alpha=0.85)
ax.axhline(1.0, color="r", ls="--", lw=1, label="equality (V_fed = V_meta)")
for i, r in enumerate(ratios):
    ax.text(i, r + 0.01, f"{r:.3f}", ha="center", fontsize=9)
ax.set_ylabel("$\\mathrm{Var}_{fed}\\,/\\,\\mathrm{Var}_{meta}$")
ax.set_title("Theorem 4: federated variance $\\leq$ meta-analysis variance")
ax.set_ylim(0, 1.08); ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig3_variance_thm4.png"), dpi=130)
plt.close()

# ---- Figure 4: overlap improvement (Theorem 5) ----------------------------
sites, g = fc.make_data("A", "weak", n_per_site=2000, seed=3)
Xall, Hall, Wall, Yall = g
e2 = fc.oracle_local_propensity(Xall, None, "weak")[:, 1]
e_glob = fc.oracle_global_propensity(Xall, "A", "weak")
fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
axs[0].hist(e2, bins=40, color="#d44", alpha=0.8)
axs[0].set_title(f"Local $e_2$ (poor overlap)\n$\\mathcal{{O}}_2$={np.mean(1/(np.clip(e2,1e-6,1-1e-6)*(1-np.clip(e2,1e-6,1-1e-6)))):.0f}")
axs[0].set_xlabel("local propensity site 2")
axs[1].hist(e_glob, bins=40, color="#2a6", alpha=0.8)
eg = np.clip(e_glob, 1e-6, 1-1e-6)
axs[1].set_title(f"Global $e(X)$ (improved)\n$\\mathcal{{O}}_{{global}}$={np.mean(1/(eg*(1-eg))):.1f}")
axs[1].set_xlabel("global propensity")
plt.suptitle("Theorem 5: federation improves covariate overlap", y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig4_overlap_thm5.png"), dpi=130, bbox_inches="tight")
plt.close()
print("figures written to", FIG, flush=True)
