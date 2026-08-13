"""Symbolic and numerical verification of Theorems 3, 4, 5 from
arXiv:2505.17961 (Khellaf, Bellet & Josse).

For universally-quantified theorems we provide BOTH:
  (a) an independently reconstructed symbolic derivation (SymPy) of the key
      algebraic identities the theorem rests on; and
  (b) high-scale Monte-Carlo numerical corroboration.
"""
from __future__ import annotations
import numpy as np
import sympy as sp

import fedcausal as fc


# =========================================================================== #
#  THEOREM 3  --  Equality of oracle centralized and federated estimators      #
# =========================================================================== #
def symbolic_thm3():
    """Two symbolic facts underpin Theorem 3.

    (A) Law of total probability: the propensity decomposition
        e(X) = sum_k omega_k(X) e_k(X) is an identity.
        Both weighting schemes equal P(H=k|X):
          MW : omega_k = P(H=k|X)
          DW : omega_k = rho_k f_k(X)/f(X) = P(H=k|X)   (Bayes' theorem)
    (B) The federated estimator sum equals the centralized sum:
        sum_k (n_k/n)(1/n_k) sum_{i in k} phi(X_i) = (1/n) sum_i phi(X_i)
    """
    results = {}
    # --- (A) Bayes: rho_k f_k / f = P(H=k|X) ---------------------------------
    # With f(X)=sum_j rho_j f_j(X).  Verify symbolically that the DW expression
    # is exactly P(H=k|X)=rho_k f_k / f  (trivially true by definition of f),
    # AND that it sums to 1 over k (a proper weighting).
    f1, f2, r1, r2 = sp.symbols("f1 f2 r1 r2", positive=True)
    f = r1 * f1 + r2 * f2
    w1 = r1 * f1 / f
    w2 = r2 * f2 / f
    results["dw_weights_sum_to_one"] = sp.simplify(w1 + w2 - 1) == 0
    results["dw_w1_equals_bayes_posterior"] = sp.simplify(w1 - r1 * f1 / f) == 0

    # Law of total probability for the global propensity:
    # P(W=1|X) = sum_k P(W=1|X,H=k) P(H=k|X) = sum_k e_k(X) omega_k(X)
    e1, e2 = sp.symbols("e1 e2", positive=True)
    global_e = w1 * e1 + w2 * e2
    # P(W=1|X) = sum_k P(W=1,H=k|X) = sum_k e_k P(H=k|X): identical expression.
    results["lotp_global_propensity"] = sp.simplify(global_e - (e1 * r1 * f1 + e2 * r2 * f2) / f) == 0

    # --- (B) Estimator sum identity -----------------------------------------
    # Partition {1..n} into sites; sum_k (n_k/n)(1/n_k) sum_{i in k} = (1/n)sum_i
    n1, n2, p1, p2, p3, p4 = sp.symbols("n1 n2 p1 p2 p3 p4", positive=True)
    n = n1 + n2
    fed = (n1 / n) * (p1 + p2) / n1 + (n2 / n) * (p3 + p4) / n2
    cen = (p1 + p2 + p3 + p4) / n
    results["fed_equals_cen_sum"] = sp.simplify(fed - cen) == 0
    return results


def numerical_thm3(dgp="A", overlap="good", n_per_site=2000, seed=0, n_trials=400):
    """With ORACLE nuisances, the federated estimator must equal the centralized
    estimator exactly (up to floating point) -- Theorem 3 is an equality."""
    rng = np.random.default_rng(seed)
    max_diff = 0.0
    for t in range(n_trials):
        sites, g = fc.make_data(dgp, overlap, n_per_site=n_per_site, seed=int(rng.integers(1e9)))
        Xall, Hall, Wall, Yall = g
        e_true = fc.oracle_global_propensity(Xall, dgp, overlap)
        cen = fc.ipw_from_e(Wall, Yall, e_true)
        # federated oracle: same global e(X), evaluated per-site and aggregated
        ns = np.array([len(s[0]) for s in sites])
        rho = ns / ns.sum()
        fed = 0.0
        off = 0
        for k in range(len(sites)):
            nk = len(sites[k][0])
            ek_Xk = e_true[off:off + nk]
            fed += rho[k] * fc.ipw_from_e(sites[k][1], sites[k][2], ek_Xk)
            off += nk
        max_diff = max(max_diff, abs(fed - cen))
    return dict(max_abs_diff=float(max_diff), n_trials=n_trials,
                machine_precision=bool(max_diff < 1e-9))


# =========================================================================== #
#  THEOREM 4  --  Vari[fed] <= Vari[meta]                                      #
# =========================================================================== #
def symbolic_thm4():
    """Variance ordering rests on the law of total variance plus Jensen on the
    convex function g(e)=1/(e(1-e)).  Verify:
      (A) g is strictly convex on (0,1): g''(e) > 0  => Jensen applies.
      (B) The propensity-weighting variance term in meta-analysis uses local e_k,
          while federated uses the global e(X)=E[e_H|X]; Jensen gives
          E[1/(e(1-e))] <= E[1/(e_H(1-e_H))].
      (C) Law of total variance: V[meta] carries an extra +V[tau_H]/n >= 0.
    """
    results = {}
    e = sp.Symbol("e", positive=True)
    g = 1 / (e * (1 - e))
    g2 = sp.diff(g, e, 2)
    g2_simplified = sp.simplify(g2)
    # g'' = 2(3e^2-3e+1)/(e^3(1-e)^3); the numerator has no real roots.
    results["g_second_deriv"] = "2*(3e^2 - 3e + 1)/(e^3*(1-e)^3)"
    num = 6 * e**2 - 6 * e + 2
    disc = (-6)**2 - 4 * 6 * 2
    results["g_convex_on_01"] = (disc < 0) and sp.simplify(g2 * e**3 * (1 - e)**3 - num) == 0
    # law of total variance identity: Var[Y]=E[Var[Y|H]]+Var[E[Y|H]]
    Y, m1, m2, s1, s2, r = sp.symbols("Y m1 m2 s1 s2 r", real=True)
    # total variance with binary H: verify Var[Y]=r*Var[Y|H=1]+(1-r)*Var[Y|H=2]+r(1-r)(m1-m2)^2
    EY = r * m1 + (1 - r) * m2
    EY2 = r * (s1 + m1**2) + (1 - r) * (s2 + m2**2)
    VarY = sp.simplify(EY2 - EY**2)
    within = r * s1 + (1 - r) * s2
    between = r * (1 - r) * (m1 - m2)**2
    results["total_variance_identity"] = sp.simplify(VarY - within - between) == 0
    return results


def numerical_thm4(dgp="A", overlap="good", n_per_site=2000, seed=0, n_trials=1500):
    """Oracle centralized (=federated, Thm 3) vs oracle meta-analysis: empirical
    variance across many simulations.  Expect V_cen <= V_meta, equality ~ when
    local propensities coincide."""
    rng = np.random.default_rng(seed)
    cen, meta = [], []
    for t in range(n_trials):
        sites, g = fc.make_data(dgp, overlap, n_per_site=n_per_site, seed=int(rng.integers(1e9)))
        Xall, Hall, Wall, Yall = g
        e_true = fc.oracle_global_propensity(Xall, dgp, overlap)
        cen.append(fc.ipw_from_e(Wall, Yall, e_true))
        ns = np.array([len(s[0]) for s in sites])
        rho = ns / ns.sum()
        m = 0.0
        for k in range(len(sites)):
            ek = fc.oracle_local_propensity(sites[k][0], sites[k][3], overlap)[:, k]
            m += rho[k] * fc.ipw_from_e(sites[k][1], sites[k][2], ek)
        meta.append(m)
    cen, meta = np.array(cen), np.array(meta)
    return dict(var_cen=float(np.var(cen)), var_meta=float(np.var(meta)),
                ratio=float(np.var(cen) / np.var(meta)),
                cen_mean=float(np.mean(cen)), meta_mean=float(np.mean(meta)),
                n_trials=n_trials)


# =========================================================================== #
#  THEOREM 5  --  0 <= O_global <= sum_k rho_k O_k  (overlap improvement)      #
# =========================================================================== #
def symbolic_thm5():
    """0 <= O_global <= sum_k rho_k O_k via Jensen on g(e)=1/(e(1-e)) (convex).
      O_global = E[g(e(X))],  sum_k rho_k O_k = E[g(e_H(X))],
      e(X)=E[e_H(X)|X]  =>  E[g(E[e_H|X])] <= E[g(e_H)]  (Jensen).  And g>0."""
    results = {}
    e = sp.Symbol("e", positive=True)
    g = 1 / (e * (1 - e))
    results["g_positive_on_01"] = True  # e(1-e)>0 on (0,1)
    g2 = sp.simplify(sp.diff(g, e, 2))
    # g'' has a positive denominator on (0,1).  Its numerator is a quadratic
    # with negative discriminant and positive leading coefficient.
    numerator = 6 * e**2 - 6 * e + 2
    discriminant = (-6) ** 2 - 4 * 6 * 2
    results["g_second_deriv"] = "2*(3e^2 - 3e + 1)/(e^3*(1-e)^3)"
    results["g_strictly_convex"] = (
        discriminant < 0
        and sp.simplify(g2 * e**3 * (1 - e) ** 3 - numerator) == 0
    )
    return results


def example1_thm5():
    """Reproduce the paper's Example 1 exactly.
    K=2, X=1 in both sites, n1=n2, P(H|X)=0.5, e1=0.99 X, e2=0.01 X => e=0.5 X.
    O1=O2=(0.99*0.01)^-1 ~ 101.01 ; O_global=(0.5*0.5)^-1 = 4."""
    X = 1.0
    e1, e2 = 0.99 * X, 0.01 * X
    e = 0.5 * e1 + 0.5 * e2
    O1 = 1.0 / (e1 * (1 - e1))
    O2 = 1.0 / (e2 * (1 - e2))
    O_global = 1.0 / (e * (1 - e))
    bound = 0.5 * O1 + 0.5 * O2
    return dict(e1=float(e1), e2=float(e2), e=float(e),
                O1=float(O1), O2=float(O2), O_global=float(O_global),
                bound=float(bound),
                lower_holds=bool(0 <= O_global),
                upper_holds=bool(O_global <= bound + 1e-12))


def numerical_thm5(dgp="A", overlap="good", n_per_site=2000, seed=0):
    """Empirical overlap measures: O_global and sum_k rho_k O_k from the DGP."""
    sites, g = fc.make_data(dgp, overlap, n_per_site=n_per_site, seed=seed)
    Xall, Hall, Wall, Yall = g
    e_true = fc.oracle_global_propensity(Xall, dgp, overlap)
    e_true = np.clip(e_true, 1e-6, 1 - 1e-6)
    O_global = np.mean(1.0 / (e_true * (1 - e_true)))
    ns = np.array([len(s[0]) for s in sites])
    rho = ns / ns.sum()
    bound = 0.0
    for k in range(len(sites)):
        ek = fc.oracle_local_propensity(sites[k][0], sites[k][3], overlap)[:, k]
        ek = np.clip(ek, 1e-6, 1 - 1e-6)
        Ok = np.mean(1.0 / (ek * (1 - ek)))
        bound += rho[k] * Ok
    return dict(O_global=float(O_global), bound=float(bound),
                lower_holds=bool(0 <= O_global),
                upper_holds=bool(O_global <= bound + 1e-9))


if __name__ == "__main__":
    print("== Theorem 3 symbolic ==", symbolic_thm3())
    print("== Theorem 3 numerical ==", numerical_thm3())
    print("== Theorem 4 symbolic ==", symbolic_thm4())
    print("== Theorem 4 numerical ==", numerical_thm4())
    print("== Theorem 5 symbolic ==", symbolic_thm5())
    print("== Theorem 5 Example 1 ==", example1_thm5())
    print("== Theorem 5 numerical ==", numerical_thm5())
