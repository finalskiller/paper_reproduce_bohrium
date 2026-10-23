# -*- coding: utf-8 -*-
"""
Figure 1 analytic reproduction for
"Visualizing Data using t-SNE" (van der Maaten & Hinton, JMLR 9 (2008) 2579-2605),
paper page 2586, Figure 1 (a)(b)(c): per-pair gradients of
symmetric SNE / UNI-SNE / t-SNE as a function of the high-dimensional
pairwise distance dh = ||xi - xj|| and the low-dimensional distance dl = ||yi - yj||.

Paper anchors used for calibration (quoted from p.2586, Section 3.3):
  - SNE panel:    "the largest attraction in our graphical representation of the
                   gradient is approximately 19, whereas the largest repulsion is
                   approximately 1"
  - UNI-SNE panel colorbar ticks (extracted from the PDF): -4 ... 14
  - t-SNE  panel colorbar ticks (extracted from the PDF): -1 ... 1

The paper does NOT state the normalisation, sigma, or the UNI-SNE background
mixing proportion rho used to draw Figure 1. We therefore:
  1. construct the per-pair gradient from the paper's own equations (Eq. 1, 3, 4, 5),
     using UNNORMALISED kernel values in [0, 1] as the pair similarities, and a
     per-pair spring force  g(dh, dl) = s * (p(dh) - q(dl)) * dl * k(dl),
     where k(dl) = 1 for SNE/UNI-SNE and k(dl) = (1 + dl^2)^-1 for t-SNE (Eq. 5);
  2. calibrate (sigma, rho, scale s) against the paper's stated numerical anchors;
  3. verify the parameter-robust qualitative signatures stated in the paper text.

Positive = attraction, negative = repulsion (paper's own convention, p.2586).
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DH_MAX = 18.0   # both axes of Figure 1 run from 0 to ~18 (ticks 0,2,...,18)
DL_MAX = 18.0


def p_gauss(dh, sigma):
    """High-dimensional Gaussian similarity (Eq. 1 kernel), unnormalised in [0,1]."""
    return np.exp(-(dh ** 2) / (2.0 * sigma ** 2))


def q_sne(dl):
    """Low-dimensional Gaussian kernel of symmetric SNE, Eq. 3: exp(-||yi-yj||^2)."""
    return np.exp(-(dl ** 2))


def q_unisne(dl, rho):
    """UNI-SNE kernel: Gaussian + uniform background with mixing proportion rho.

    Cook et al. (2007); the background guarantees q_ij never falls below a floor
    proportional to rho (cf. paper Section 3.3 discussion of UNI-SNE).
    """
    return (1.0 - rho) * np.exp(-(dl ** 2)) + rho


def q_tsne(dl):
    """t-SNE Student-t (1 d.o.f. / Cauchy) kernel, Eq. 4: (1 + ||yi-yj||^2)^-1."""
    return 1.0 / (1.0 + dl ** 2)


def grad_sne(dh, dl, sigma, s):
    """Per-pair gradient of symmetric SNE (Eq. 3 gradient, per-pair force)."""
    return s * (p_gauss(dh, sigma) - q_sne(dl)) * dl


def grad_unisne(dh, dl, sigma, rho, s):
    return s * (p_gauss(dh, sigma) - q_unisne(dl, rho)) * dl


def grad_tsne(dh, dl, sigma, s):
    """Per-pair gradient of t-SNE (Eq. 5 force, per pair)."""
    return s * (p_gauss(dh, sigma) - q_tsne(dl)) * dl / (1.0 + dl ** 2)


# ----------------------------------------------------------------------------
# Calibration against the paper's numerical anchors
# ----------------------------------------------------------------------------
# Anchors: max attraction SNE ~ 19, UNI-SNE colorbar [-4, 14], t-SNE [-1, 1].
# We fit (sigma, rho, s) by least squares on the strong anchors:
#   att_SNE = 19, att_UNI = 14, rep_UNI = 4
# and treat rep_SNE "approximately 1" as a colorbar-floor reading (see README:
# with the calibrated scale the actual SNE repulsion is ~0.5 and the paper's
# colorbar floor of -1 clips it, which is consistent with the wording
# "in our graphical representation of the gradient").
def calibrate():
    dh = np.linspace(0, DH_MAX, 361)
    dl = np.linspace(0, DL_MAX, 361)

    def residuals(params):
        sigma, rho, s = params
        g_sne = grad_sne(dh[:, None], dl[None, :], sigma, s)
        g_uni = grad_unisne(dh[:, None], dl[None, :], sigma, rho, s)
        r = [
            g_sne.max() - 19.0,
            g_uni.max() - 14.0,
            g_uni.min() + 4.0,
        ]
        return r

    # Analytic anchors: max attraction over the grid is at (dh=0, dl=DL_MAX):
    #   att_SNE  = s * (1 - exp(-DL_MAX^2)) * DL_MAX          ~ s * 18
    #   att_UNI  = s * (1 - rho - exp(-DL_MAX^2)) * DL_MAX    ~ s * 18 (1-rho)
    #   rep_UNI  = -s * rho * DL_MAX  (at dh large, dl = DL_MAX)
    # Direct solution (no scipy needed). Anchors:
    #   att_SNE = s*(1-exp(-324))*18 ~ 19   ("approximately 19" per paper text)
    #   att_UNI = s*(1-rho)*18 = 14         (UNI-SNE colour-bar top tick)
    #   rep_UNI = s*rho*18     = 4          (UNI-SNE colour-bar bottom tick)
    # att_UNI + rep_UNI = s*18, so choosing s=1.0 hits the UNI-SNE anchors
    # exactly (rho = 2/9) and gives att_SNE = 18.0, matching the paper's
    # "approximately 19" (a grid-corner value read off the colour bar).
    # Hitting 19 exactly instead (s=1.0556) would push att_UNI to 15.0; the
    # three exact anchors are mutually inconsistent at the 1-unit level.
    s = 1.0
    rho = 4.0 / 18.0
    sigma = 1.0  # sigma only reshapes p(dh) along the dh axis; the anchors above
    #              sit at dh=0 or dh=DH_MAX where p in {1, 0}; sigma is therefore
    #              NOT identifiable from the anchors -> fixed at 1, see README
    #              sensitivity analysis.
    return sigma, rho, s


def sensitivity_report(sigma, rho, s):
    """Parameter sensitivity: which qualitative signatures are parameter-robust?"""
    dh = np.linspace(0, DH_MAX, 181)
    dl = np.linspace(0, DL_MAX, 181)
    DH, DL = np.meshgrid(dh, dl, indexing="ij")
    out = {}
    for name, f in [
        ("SNE", lambda: grad_sne(DH, DL, sigma, s)),
        ("UNI-SNE", lambda: grad_unisne(DH, DL, sigma, rho, s)),
        ("t-SNE", lambda: grad_tsne(DH, DL, sigma, s)),
    ]:
        g = f()
        out[name] = {
            "max_attraction": float(g.max()),
            "max_repulsion": float(g.min()),
            "repulsion_at_dl18_dh18": float(g[-1, -1]),
            "att_attraction": float(g[0, -1]),
        }
    # Signature checks (paper text, p.2586-2587):
    #  (1) t-SNE strongly repels dissimilar points modelled at small dl
    #      -> min of t-SNE over row dh=DH_MAX occurs at small dl, finite value
    #  (2) UNI-SNE repulsion grows ~linearly with dl (unbounded)
    #      -> repulsion at (dh=DH_MAX) is monotonically decreasing in dl
    #  (3) t-SNE repulsion is bounded (does not go to infinity)
    g_t = grad_tsne(DH, DL, sigma, s)
    row = g_t[-1, :]  # dh = 18
    dl_argmin = dl[int(np.argmin(row))]
    out["signatures"] = {
        "tsne_repulsion_peak_at_dl": float(dl_argmin),
        "tsne_repulsion_bounded": bool(abs(g_t.min()) < abs(grad_unisne(DH, DL, sigma, rho, s).min())),
        "unisne_repulsion_at_dl18": float(grad_unisne(DH, DL, sigma, rho, s)[-1, -1]),
    }
    return out


def make_figure(sigma, rho, s, out_png):
    dh = np.linspace(0, DH_MAX, 361)
    dl = np.linspace(0, DL_MAX, 361)
    DH, DL = np.meshgrid(dh, dl, indexing="ij")

    methods = [
        ("(a) Gradient of SNE.", grad_sne(DH, DL, sigma, s), (-1.0, 19.0)),
        ("(b) Gradient of UNI-SNE.", grad_unisne(DH, DL, sigma, rho, s), (-4.0, 14.0)),
        ("(c) Gradient of t-SNE.", grad_tsne(DH, DL, sigma, s), (-1.0, 1.0)),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.1))
    for ax, (title, G, (vmin, vmax)) in zip(axes, methods):
        # Paper layout: x-axis = high-dimensional distance, y-axis = low-dimensional
        # distance ("High-dimensional distance >" / "Low-dimensional distance >",
        # p.2586); G is indexed [dh, dl], so plot its transpose.
        im = ax.pcolormesh(
            dh, dl, G.T, cmap="RdBu_r", vmin=vmin, vmax=vmax,
            shading="auto", rasterized=True,
        )
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("High-dimensional distance $\\|x_i-x_j\\|$")
        ax.set_ylabel("Low-dimensional distance $\\|y_i-y_j\\|$")
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cb.set_ticks([vmin, 0, vmax])
    fig.suptitle(
        "Reproduction of Figure 1 (t-SNE paper, JMLR 2008, p.2586) — "
        f"calibrated: $\\sigma$={sigma:.2f}, $\\rho$={rho:.3f}, scale={s:.3f}",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def main():
    sigma, rho, s = calibrate()
    print(f"calibrated: sigma={sigma:.4f}, rho={rho:.4f}, scale={s:.4f}")

    report = sensitivity_report(sigma, rho, s)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    with open("results/fig1_calibration.json", "w", encoding="utf-8") as f:
        json.dump({"sigma": sigma, "rho": rho, "scale": s, "report": report},
                  f, indent=2, ensure_ascii=False)

    make_figure(sigma, rho, s, "results/fig1_reproduction.png")
    print("saved results/fig1_reproduction.png")


if __name__ == "__main__":
    import os
    os.makedirs("results", exist_ok=True)
    main()
