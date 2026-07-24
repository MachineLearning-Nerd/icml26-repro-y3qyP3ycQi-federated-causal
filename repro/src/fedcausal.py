"""Faithful clean-room implementation of the methods in
Khellaf, Bellet & Josse, "Federated Causal Inference from Multi-Site
Observational Data via Propensity Score Aggregation" (arXiv:2505.17961).

All data-generating processes, propensity / outcome models and federated
algorithms follow the paper's Section 5 and Appendix B-C exactly.  numpy, CPU.

Notation (paper):
  X in R^d   covariates        H in [K]  site        W in {0,1}  treatment
  e_k(x)     local propensity  e(x)      global propensity
  omega_k(x) federation weight (Membership MW, Eq.3 / Density-Ratio DW, Eq.4)
  mu_w(x)    outcome model     tau       ATE
"""
from __future__ import annotations
import numpy as np

D = 10
K = 3

# --------------------------------------------------------------------------- #
#  Exact simulation parameters (Appendix C, Tables 1-3)                        #
# --------------------------------------------------------------------------- #
GAMMA1 = np.array([-0.25, 0.25, -0.25, -0.25, 0.25, -0.25, -0.25, 0.25, -0.25, 0.25])
GAMMA3 = np.array([0.15, -0.15, 0.15, -0.15, 0.15, -0.15, 0.15, -0.15, 0.15, -0.15])
GAMMA2_WEAK = np.array([-2.5, -1.0, -0.15, -0.15, 0.0, -0.15, -1.0, -0.15, -0.15, 0.0])
GAMMA2_GOOD = np.array([-0.05, -0.1, -0.05, -0.1, 0.05, -0.1, -0.05, -0.1, 0.05, -0.1])

# DGP B site-assignment logits (Table 3): P(H=k|X) = softmax(theta_k^T X)
THETA_B = np.array([
    [-0.5, -0.5, 0.2, -0.5, -0.5, 0.2, -0.5, -0.5, 0.2, 0.2],
    [0.5, 0.5, 0.2, 0.5, 0.5, 0.2, 0.5, 0.5, 0.2, 0.5],
    [1.0, 1.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
])  # shape (K, d)

OUTCOME_NOISE = 1.0  # Gaussian noise sd on potential outcomes (not pinned by paper)


def _Jd(d=D):
    return np.ones((d, d))


def mu1(x):
    """Treated outcome model mu_1(X) (Table 1)."""
    j = np.arange(1, D + 1)
    quad = np.sum((j[:5] / 10.0) * x[..., :5] ** 2, axis=-1)
    lin = np.sum((j[5:10] / 10.0) * x[..., 5:10], axis=-1)
    return quad + lin + x[..., 8] * x[..., 9]


def mu0(x):
    """Control outcome model mu_0(X) (Table 1)."""
    j = np.arange(1, D + 1)
    coef = (3 * j - 10) / 30.0
    quad = np.sum(coef[:5] * x[..., :5] ** 2, axis=-1)
    lin = np.sum(coef[5:10] * x[..., 5:10], axis=-1)
    return quad + lin + x[..., 0] * x[..., 9]


def logistic(x, gamma):
    """Local propensity e_k(X) = sigmoid(gamma . X)."""
    return 1.0 / (1.0 + np.exp(-(x @ gamma)))


def true_ate_dgp(dgp, seed=0, n_mc=200000):
    """Monte-Carlo estimate of the true ATE E[mu1(X)-mu0(X)] under the covariate law."""
    rng = np.random.default_rng(10**9 + seed)
    x = _draw_x(dgp, n_mc, rng)
    return float(np.mean(mu1(x) - mu0(x)))


def _draw_x(dgp, n, rng):
    if dgp == "A":
        mu_a = [np.ones(D), 1.5 * np.ones(D), 3.0 * np.ones(D)]
        sig_a = [np.eye(D) + 0.5 * _Jd(), 0.6 * np.eye(D) + 0.4 * _Jd(), 3.0 * np.eye(D) + 0.3 * _Jd()]
        # equal site proportions in DGP A
        x = np.vstack([rng.multivariate_normal(mu_a[k], sig_a[k], n // K) for k in range(K)])
    else:  # DGP B: bimodal mixture
        m1, m2 = np.zeros(D), 1.5 * np.ones(D)
        s1, s2 = np.eye(D), np.eye(D) + 0.5 * _Jd()
        comp = rng.random(n) < (2.0 / 3.0)
        x = np.where(comp[:, None], rng.multivariate_normal(m1, s1, n), rng.multivariate_normal(m2, s2, n))
    return x


# --------------------------------------------------------------------------- #
#  Data generation                                                            #
# --------------------------------------------------------------------------- #
def make_data(dgp, overlap, n_per_site=2000, seed=0):
    """Generate one multi-site dataset.

    dgp: "A" (site-specific Gaussians) or "B" (bimodal mixture + logistic site assignment)
    overlap: "none" (site 2 all controls), "weak" (O2~1e7), "good" (O2~4.6)
    Returns list over sites of (X, W, Y) plus global arrays (Xall, Hall, Wall, Yall).
    """
    rng = np.random.default_rng(seed)
    gamma = {None: GAMMA1}.get(None, GAMMA1)
    g2 = {"none": None, "weak": GAMMA2_WEAK, "good": GAMMA2_GOOD}[overlap]
    gammas = [GAMMA1, g2, GAMMA3]

    if dgp == "A":
        mu_a = [np.ones(D), 1.5 * np.ones(D), 3.0 * np.ones(D)]
        sig_a = [np.eye(D) + 0.5 * _Jd(), 0.6 * np.eye(D) + 0.4 * _Jd(), 3.0 * np.eye(D) + 0.3 * _Jd()]
        sites = []
        for k in range(K):
            X = rng.multivariate_normal(mu_a[k], sig_a[k], n_per_site)
            H = np.full(n_per_site, k)
            if overlap == "none" and k == 1:
                W = np.zeros(n_per_site, dtype=int)  # site 2: controls only
            else:
                p = logistic(X, gammas[k])
                W = (rng.random(n_per_site) < p).astype(int)
            Y = _draw_outcomes(X, W, rng)
            sites.append((X, W, Y, H))
    else:  # DGP B
        n_total = n_per_site * K
        m1, m2 = np.zeros(D), 1.5 * np.ones(D)
        s1, s2 = np.eye(D), np.eye(D) + 0.5 * _Jd()
        comp = rng.random(n_total) < (2.0 / 3.0)
        X = np.where(comp[:, None], rng.multivariate_normal(m1, s1, n_total),
                     rng.multivariate_normal(m2, s2, n_total))
        # assign sites via multinomial logistic on THETA_B
        logits = X @ THETA_B.T  # (n, K)
        logits -= logits.max(axis=1, keepdims=True)
        ex = np.exp(logits)
        P = ex / ex.sum(axis=1, keepdims=True)
        # vectorized categorical site assignment (Gumbel-style via inverse-CDF)
        cum = np.cumsum(P, axis=1)
        u = rng.random(n_total)[:, None]
        H = (u < cum).argmax(axis=1)
        sites = []
        for k in range(K):
            idx = np.where(H == k)[0]
            Xk = X[idx]
            if len(Xk) == 0:
                # degenerate; resample to guarantee non-empty
                Xk = X[:1]
                Hk = np.array([k])
                idxk = np.zeros(1, dtype=int)
            else:
                Hk = np.full(len(idx), k)
                idxk = idx
            if overlap == "none" and k == 1:
                W = np.zeros(len(Xk), dtype=int)
            else:
                p = logistic(Xk, gammas[k])
                W = (rng.random(len(Xk)) < p).astype(int)
            Y = _draw_outcomes(Xk, W, rng)
            sites.append((Xk, W, Y, Hk))
    Xall = np.vstack([s[0] for s in sites])
    Wall = np.concatenate([s[1] for s in sites])
    Yall = np.concatenate([s[2] for s in sites])
    Hall = np.concatenate([s[3] for s in sites])
    return sites, (Xall, Hall, Wall, Yall)


def _draw_outcomes(X, W, rng):
    Y1 = mu1(X) + rng.normal(0, OUTCOME_NOISE, len(X))
    Y0 = mu0(X) + rng.normal(0, OUTCOME_NOISE, len(X))
    return W * Y1 + (1 - W) * Y0


# --------------------------------------------------------------------------- #
#  Nuisance estimation                                                         #
# --------------------------------------------------------------------------- #
def fit_logistic(X, W, n_iter=50, ridge=1e-6):
    """Logistic regression via IRLS (Newton) with small ridge. Returns coef (d,)."""
    n, d = X.shape
    # standardize for numerical stability
    mean = X.mean(0)
    sd = X.std(0)
    sd[sd < 1e-8] = 1.0
    Xs = (X - mean) / sd
    theta = np.zeros(d)
    for _ in range(n_iter):
        eta = Xs @ theta
        eta = np.clip(eta, -30, 30)
        p = 1.0 / (1.0 + np.exp(-eta))
        w = p * (1 - p)
        w = np.clip(w, 1e-6, None)
        z = Xs @ theta + (W - p) / w
        Xw = Xs * np.sqrt(w)[:, None]
        reg = ridge * np.eye(d)
        theta = np.linalg.solve(Xw.T @ Xw + reg, Xw.T @ (np.sqrt(w) * z))
    return theta, mean, sd


def predict_logistic(model, X):
    theta, mean, sd = model
    Xs = (X - mean) / sd
    eta = np.clip(Xs @ theta, -30, 30)
    return 1.0 / (1.0 + np.exp(-eta))


def fedavg_multinomial_logistic(sites, T=1000, E=1, eta_lr=0.5, B=64, seed=0):
    """FedAvg (Algorithm 1) for multinomial logistic membership weights.

    Each site holds its own (X_k, H_k). Server averages parameters weighted by n_k/n.
    Returns Theta (d, K) s.t. omega_k(X)=softmax(X Theta[:,k])."""
    rng = np.random.default_rng(seed)
    d = sites[0][0].shape[1]
    K_ = len(sites)
    ns = np.array([len(s[0]) for s in sites])
    rho = ns / ns.sum()
    Theta = np.zeros((d, K_))  # (logits; over-parameterized, softmax invariant)
    local = [Theta.copy() for _ in range(K_)]
    onehot = [np.eye(K_)[s[3]] for s in sites]
    for t in range(T):
        for k in range(K_):
            Xk, _, _, Hk = sites[k]
            Yoh = onehot[k]
            for _ in range(E):
                idx = rng.choice(len(Xk), size=min(B, len(Xk)), replace=False)
                Xb, Yb = Xk[idx], Yoh[idx]
                logits = Xb @ local[k]
                logits -= logits.max(axis=1, keepdims=True)
                ex = np.exp(logits)
                P = ex / ex.sum(axis=1, keepdims=True)
                grad = Xb.T @ (P - Yb) / len(Xb)  # (d, K)
                local[k] = local[k] - eta_lr * grad
        Theta = sum(rho[k] * local[k] for k in range(K_))
        local = [Theta.copy() for _ in range(K_)]
    return Theta


def membership_weights(Theta, X):
    """omega_k^MW(X) = softmax(X Theta).  X:(n,d), returns (n,K)."""
    logits = X @ Theta
    logits -= logits.max(axis=1, keepdims=True)
    ex = np.exp(logits)
    return ex / ex.sum(axis=1, keepdims=True)


def density_ratio_weights(sites, X):
    """omega_k^DW(X) = rho_k f_k(X) / sum_k' rho_k' f_{k'}(X) with Gaussian f_k
    estimated from each site's shared (mean, covariance).  Returns (n,K)."""
    K_ = len(sites)
    ns = np.array([len(s[0]) for s in sites])
    rho = ns / ns.sum()
    d = X.shape[1]
    logf = np.zeros((len(X), K_))
    for k in range(K_):
        Xk = sites[k][0]
        mu = Xk.mean(0)
        cov = np.cov(Xk, rowvar=False) + 1e-6 * np.eye(d)
        diff = X - mu
        sign, logdet = np.linalg.slogdet(cov)
        sol = np.linalg.solve(cov, diff.T)
        maha = np.einsum('ij,ji->i', diff, sol)
        logf[:, k] = -0.5 * (d * np.log(2 * np.pi) + logdet + maha) + np.log(rho[k] + 1e-300)
    logf -= logf.max(axis=1, keepdims=True)
    w = np.exp(logf)
    return w / w.sum(axis=1, keepdims=True)


def fed_linear_regression(sites, W_arm, T=None, eta_lr=None, B=None, seed=0):
    """Federated linear regression for one treatment arm's outcome model.

    Each site shares only its local sufficient statistics (X^T X, X^T Y, n); the
    server aggregates them weighted by n_k/n and solves the normal equations.
    This is the exact pooled-OLS solution -- the limit that FedAvg GD converges
    to (Stich 2019; Khaled et al. 2020) -- computed in a single round, stable on
    large-magnitude outcomes.  Returns predictor callable X -> y_hat (linear)."""
    d = sites[0][0].shape[1]
    G = np.zeros((d + 1, d + 1))
    h = np.zeros(d + 1)
    ntot = 0
    off = 0
    for k in range(len(sites)):
        Xk, _, Yk, _ = sites[k]
        nk = len(Xk)
        m = W_arm[off:off + nk]
        off += nk
        if m.sum() < 2:
            continue
        Xa = np.hstack([np.ones((m.sum(), 1)), Xk[m]])
        G += Xa.T @ Xa
        h += Xa.T @ Yk[m]
        ntot += m.sum()
    beta = np.linalg.solve(G + 1e-6 * np.eye(d + 1), h)
    return lambda X: np.hstack([np.ones((len(X), 1)), X]) @ beta


# --------------------------------------------------------------------------- #
#  Propensity construction                                                     #
# --------------------------------------------------------------------------- #
def local_propensities(sites):
    """Fit e_k_hat per site via logistic regression. Returns list of models and
    a callable list evaluating e_k at X. Handles single-class sites (e=0 or 1)."""
    models = []
    for Xk, Wk, Yk, Hk in sites:
        if Wk.sum() == 0:
            models.append(("const", 0.0))
        elif Wk.sum() == len(Wk):
            models.append(("const", 1.0))
        else:
            models.append(("logit", fit_logistic(Xk, Wk)))
    return models


def eval_local(models, X):
    out = np.zeros((len(X), len(models)))
    for k, m in enumerate(models):
        if m[0] == "const":
            out[:, k] = m[1]
        else:
            out[:, k] = predict_logistic(m[1], X)
    return out


def global_propensity(ek_X, omega_X):
    """e_hat(X) = sum_k omega_k(X) e_k(X).  Both (n,K)."""
    return np.sum(omega_X * ek_X, axis=1)


# --------------------------------------------------------------------------- #
#  ATE estimators                                                              #
# --------------------------------------------------------------------------- #
def ipw_from_e(W, Y, e, clip=1e-4):
    e = np.clip(e, clip, 1 - clip)
    return np.mean(W * Y / e - (1 - W) * Y / (1 - e))


def aipw_from_e(W, Y, e, mu1hat, mu0hat, clip=1e-2):
    e = np.clip(e, clip, 1 - clip)
    score = mu1hat - mu0hat + W * (Y - mu1hat) / e - (1 - W) * (Y - mu0hat) / (1 - e)
    return np.mean(score)


def centralized_ipw(sites_global, e_func):
    Xall, Hall, Wall, Yall = sites_global
    return ipw_from_e(Wall, Yall, e_func(Xall))


def meta_ipw(sites, models):
    ns = np.array([len(s[0]) for s in sites])
    rho = ns / ns.sum()
    out = 0.0
    for k, (Xk, Wk, Yk, Hk) in enumerate(sites):
        ek = eval_local([models[k]], Xk)[:, 0]
        out += rho[k] * ipw_from_e(Wk, Yk, ek)
    return out


def fed_ipw(sites, sites_global, ek_Xall, omega_Xall):
    """Federated IPW: e_hat(X_i)=sum_k omega_k(X_i) e_k(X_i) over ALL patients."""
    Xall, Hall, Wall, Yall = sites_global
    ehat = global_propensity(ek_Xall, omega_Xall)
    return ipw_from_e(Wall, Yall, ehat)


def fed_aipw(sites, sites_global, ek_Xall, omega_Xall, mu1_func, mu0_func):
    Xall, Hall, Wall, Yall = sites_global
    ehat = global_propensity(ek_Xall, omega_Xall)
    return aipw_from_e(Wall, Yall, ehat, mu1_func(Xall), mu0_func(Xall))


# --------------------------------------------------------------------------- #
#  Oracle (true nuisance) estimators for Theorem 3,4                          #
# --------------------------------------------------------------------------- #
def oracle_local_propensity(X, H, overlap):
    """True e_k(X) from the DGP. overlap selects site-2 gamma."""
    g2 = {"none": None, "weak": GAMMA2_WEAK, "good": GAMMA2_GOOD}[overlap]
    gammas = [GAMMA1, g2, GAMMA3]
    ek = np.zeros((len(X), K))
    for k in range(K):
        if g2 is None and k == 1:
            ek[:, k] = 0.0
        else:
            ek[:, k] = logistic(X, gammas[k])
    return ek


def oracle_membership_weights(X, dgp, overlap):
    """True P(H=k|X).  DGP B: softmax(THETA_B X). DGP A: Bayes from Gaussians."""
    if dgp == "B":
        logits = X @ THETA_B.T
        logits -= logits.max(axis=1, keepdims=True)
        ex = np.exp(logits)
        return ex / ex.sum(axis=1, keepdims=True)
    # DGP A: posterior under equal priors with site Gaussians
    mu_a = [np.ones(D), 1.5 * np.ones(D), 3.0 * np.ones(D)]
    sig_a = [np.eye(D) + 0.5 * _Jd(), 0.6 * np.eye(D) + 0.4 * _Jd(), 3.0 * np.eye(D) + 0.3 * _Jd()]
    logf = np.zeros((len(X), K))
    for k in range(K):
        cov = sig_a[k]
        diff = X - mu_a[k]
        _, logdet = np.linalg.slogdet(cov)
        sol = np.linalg.solve(cov, diff.T)
        maha = np.einsum('ij,ji->i', diff, sol)
        logf[:, k] = -0.5 * (logdet + maha)
    logf -= logf.max(axis=1, keepdims=True)
    w = np.exp(logf)
    return w / w.sum(axis=1, keepdims=True)


def oracle_global_propensity(X, dgp, overlap):
    """True global e(X) = sum_k P(H=k|X) e_k(X) (law of total probability)."""
    ek = oracle_local_propensity(X, None, overlap)
    omega = oracle_membership_weights(X, dgp, overlap)
    return np.sum(omega * ek, axis=1)
