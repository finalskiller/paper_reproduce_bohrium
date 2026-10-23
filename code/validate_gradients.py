# -*- coding: utf-8 -*-
"""
Independent validation of the gradient formulas used to reproduce Figure 1
(Phase-2 "independent reference" step of the reproduce-paper workflow).

For each method (symmetric SNE, UNI-SNE, t-SNE) we build a random system of
n = 8 points (3-D data -> 2-D map), evaluate ANALYTIC gradient formulas, and
compare them with a central FINITE-DIFFERENCE derivative of the corresponding
KL cost  C = sum_{i != j} p_ij * log(p_ij / q_ij)  (paper p.2583).

Kernels (numerators, before normalisation by Z = sum_{k != l} num_kl):
  SNE:     num_ij = exp(-||yi-yj||^2)                      (Eq. 3)
  UNI-SNE: num_ij = (1-rho) * exp(-||yi-yj||^2) + rho      (uniform background,
             Cook et al. 2007; floor proportional to rho)
  t-SNE:   num_ij = (1 + ||yi-yj||^2)^-1                   (Eq. 4)

Gradients validated:
  SNE   (paper, p.2584):  dC/dyi = 4 sum_j (pij - qij) (yi - yj)
  t-SNE (paper, Eq. 5):   dC/dyi = 4 sum_j (pij - qij) (yi - yj) (1+||yi-yj||^2)^-1
  UNI-SNE (exact, derived): dC/dyi = 4 sum_j (pij - qij) (yi - yj) * w_ij,
    with w_ij = (1-rho) exp(-||yi-yj||^2) / num_ij  (only the Gaussian part of
    the mixture contributes to dnum/dyi; see README for the derivation).

We also test the "spring form" 4 sum (pij - qij)(yi - yj)  WITHOUT w_ij for
UNI-SNE and report its mismatch: the paper's Figure 1(b) follows this spring
convention (it matches the paper's stated colour-bar anchors and the text claim
"strength of the repulsion ... is proportional to their pairwise distance in
the low-dimensional map", p.2587), but it is NOT the exact gradient of the
mixture cost. This distinction is one of the findings of this reproduction.
"""

import json
import numpy as np

rng = np.random.default_rng(42)


def make_system(n=8, d_in=3, d_out=2, sigma=1.0, rho=0.21):
    X = rng.normal(size=(n, d_in)) * 2.0
    Y = rng.normal(size=(n, d_out)) * 0.5
    # conditional probabilities p_{j|i} with common sigma (Eq. 1)
    D2 = ((X[:, None, :] - X[None, :, :]) ** 2).sum(-1)
    Pc = np.exp(-D2 / (2 * sigma ** 2))
    np.fill_diagonal(Pc, 0.0)
    Pc /= Pc.sum(1, keepdims=True)
    P = (Pc + Pc.T) / (2 * n)          # symmetrised joint (p.2584)
    np.fill_diagonal(P, 0.0)
    return X, Y, P, rho


def kernels(Y, method, rho=0.21):
    D2 = ((Y[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
    if method == "sne":
        num = np.exp(-D2)
    elif method == "unisne":
        num = (1 - rho) * np.exp(-D2) + rho
    elif method == "tsne":
        num = 1.0 / (1.0 + D2)
    else:
        raise ValueError(method)
    np.fill_diagonal(num, 0.0)
    Q = num / num.sum()
    return num, Q


def cost(Y, P, method, rho=0.21):
    _, Q = kernels(Y, method, rho)
    Q = np.maximum(Q, 1e-12)
    return float(np.sum(P * np.log(np.maximum(P, 1e-12) / Q)))


def analytic_grad_i(Y, P, i, method, rho=0.21, form="exact"):
    num, Q = kernels(Y, method, rho)
    diff = Y[i] - Y                                   # (n, d)
    pq = P[i] - Q[i]                                  # (n,)
    if method == "tsne":
        w = 1.0 / (1.0 + (diff ** 2).sum(1))          # Eq. 5 kernel factor
        return 4.0 * ((pq * w)[:, None] * diff).sum(0)
    if method == "unisne" and form == "exact":
        dl2 = (diff ** 2).sum(1)
        w = (1 - rho) * np.exp(-dl2) / num[i]         # Gaussian part / mixture
        w[i] = 0.0
        return 4.0 * ((pq * w)[:, None] * diff).sum(0)
    # spring form (paper's Figure-1 drawing convention)
    return 4.0 * (pq[:, None] * diff).sum(0)


def numeric_grad_i(Y, P, i, method, rho=0.21, eps=1e-6):
    g = np.zeros(Y.shape[1])
    for k in range(Y.shape[1]):
        Yp, Ym = Y.copy(), Y.copy()
        Yp[i, k] += eps
        Ym[i, k] -= eps
        g[k] = (cost(Yp, P, method, rho) - cost(Ym, P, method, rho)) / (2 * eps)
    return g


def main():
    X, Y, P, rho = make_system()
    results = {}
    checks = [
        ("sne", "exact"),
        ("unisne", "exact"),
        ("unisne", "spring"),   # expected to FAIL: documented as a finding
        ("tsne", "exact"),
    ]
    for method, form in checks:
        rows = []
        for i in range(Y.shape[0]):
            ga = analytic_grad_i(Y, P, i, method, rho, form=form)
            gn = numeric_grad_i(Y, P, i, method, rho)
            denom = max(np.abs(gn).max(), 1e-12)
            rows.append(float(np.abs(ga - gn).max() / denom))
        key = f"{method}:{form}"
        ok = max(rows) < 1e-5
        results[key] = {"max_relative_error": max(rows), "passes": ok}
        print(f"{key:16s} max rel. err vs finite difference: {max(rows):.3e}"
              f"  {'PASS' if ok else 'MISMATCH (expected for spring form)'}")

    with open("results/gradient_validation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("saved results/gradient_validation.json")


if __name__ == "__main__":
    main()
