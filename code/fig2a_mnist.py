# -*- coding: utf-8 -*-
"""
Empirical reproduction of Figure 2(a) of the t-SNE paper
(van der Maaten & Hinton, JMLR 9 (2008), p.2590): t-SNE map of 6,000 random
MNIST digits.

Paper protocol (Section 4.1 + 4.2, pp.2588-2589):
  - 6,000 images randomly selected from the 60,000 MNIST training images
  - PCA to 30 dimensions first
  - perplexity = 40 (Table 1)
  - optimisation: early exaggeration x4 for the first 50 iterations,
    T = 1000 iterations, momentum 0.5 -> 0.8 at t=250,
    learning rate eta = 100 initially, adaptive (Jacobs 1988)

We run scikit-learn's TSNE twice:
  RUN A ("paper-flavoured"): perplexity=40, early_exaggeration=4,
         learning_rate=100, init='random', max_iter=1000, random_state=42
         (sklearn cannot switch exaggeration off at iteration 50 - it keeps the
          exaggeration for the first 250 iterations and has no momentum/Jacobs
          schedule; these deviations are documented in the README)
  RUN B ("sklearn 1.9.1 defaults"): perplexity=30, early_exaggeration=12,
         learning_rate='auto', init='pca', max_iter=1000, random_state=42

Quantitative checks:
  - trustworthiness(X_pca30 -> embedding), k=12  (sklearn.manifold)
  - 1-NN accuracy of digit classification IN the 2-D map (5-fold CV)
  - KL divergence reported by the two runs
The paper's original figure cannot be scored numerically (no coordinates are
published), so the comparison with Figure 2(a) is structural/qualitative;
A-vs-B is fully quantitative.
"""

import json
import time
import numpy as np

RNG_SEED = 42
N_SAMPLES = 6000
PCA_DIM = 30


def load_mnist():
    """Load full MNIST. Source order controlled by env MNIST_SOURCE:
    'author' (default here; the mirror lvdmaaten.github.io is reachable from
    this network) or 'openml' (sklearn fetch_openml, blocked on some networks).
    """
    import os, zipfile, urllib.request, gzip, struct

    cache = "data_cache/mnist_70000.npz"
    os.makedirs("data_cache", exist_ok=True)
    if os.path.exists(cache):
        z = np.load(cache)
        return z["X"], z["y"]

    source = os.environ.get("MNIST_SOURCE", "author")
    if source == "openml":
        from sklearn.datasets import fetch_openml
        print("fetching MNIST from OpenML ...")
        bunch = fetch_openml("mnist_784", version=1, as_frame=False,
                             parser="liac-arff")
        X, y = bunch.data.astype(np.float32), bunch.target.astype(int)
        np.savez_compressed(cache, X=X, y=y)
        return X, y

    print("downloading MNIST from the author's mirror "
          "(lvdmaaten.github.io/tsne/code/mnist.zip) ...")
    base = "data_cache"
    zip_path = os.path.join(base, "mnist.zip")
    if not os.path.exists(zip_path):
        urllib.request.urlretrieve(
            "https://lvdmaaten.github.io/tsne/code/mnist.zip", zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(base)

    # the author's zip ships MATLAB .mat files (mnist_train.mat / mnist_test.mat)
    import scipy.io as sio
    m = sio.loadmat(os.path.join(base, "mnist_train.mat"))
    X = m["train_X"].astype(np.float32)      # 60000 x 784, pixels in [0, 255]
    y = m["train_labels"].flatten().astype(int)
    np.savez_compressed(cache, X=X, y=y)
    return X, y


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE, trustworthiness
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import cross_val_score

    X, y = load_mnist()
    print("MNIST loaded:", X.shape)

    rng = np.random.default_rng(RNG_SEED)
    idx = rng.choice(len(X), N_SAMPLES, replace=False)
    Xs, ys = X[idx], y[idx]

    t0 = time.time()
    Xp = PCA(n_components=PCA_DIM, random_state=RNG_SEED).fit_transform(Xs)
    print(f"PCA->30 done in {time.time()-t0:.1f}s")

    runs = {
        "A_paper_flavoured": dict(perplexity=40, early_exaggeration=4,
                                  learning_rate=100, init="random",
                                  random_state=RNG_SEED),
        "B_sklearn_defaults": dict(perplexity=30, early_exaggeration=12,
                                   learning_rate="auto", init="pca",
                                   random_state=RNG_SEED),
    }
    results = {}
    for name, params in runs.items():
        t0 = time.time()
        tsne = TSNE(n_components=2, max_iter=1000, method="barnes_hut",
                    angle=0.5, verbose=0, **params)
        E = tsne.fit_transform(Xp)
        wall = time.time() - t0
        tw = trustworthiness(Xp, E, n_neighbors=12)
        knn = cross_val_score(KNeighborsClassifier(n_neighbors=1), E, ys,
                              cv=5).mean()
        results[name] = {
            "params": params, "wall_seconds": round(wall, 1),
            "kl_divergence_final": float(tsne.kl_divergence_),
            "trustworthiness_k12": round(float(tw), 4),
            "knn1_accuracy_5cv": round(float(knn), 4),
        }
        print(name, results[name])
        np.save(f"results/mnist_embedding_{name}.npy", E)

        fig, ax = plt.subplots(figsize=(6.2, 6.2))
        sc = ax.scatter(E[:, 0], E[:, 1], c=ys, cmap="tab10", s=1.2,
                        alpha=0.75, linewidths=0)
        ax.set_title(f"{name}: perplexity={params['perplexity']}, "
                     f"exagg={params['early_exaggeration']}, "
                     f"init='{params['init']}'\n"
                     f"1-NN acc={knn:.3f}, trustworthiness={tw:.3f}")
        ax.set_xticks([]); ax.set_yticks([])
        fig.tight_layout()
        fig.savefig(f"results/fig2a_reproduction_{name}.png", dpi=200)
        plt.close(fig)

    np.save("results/mnist_sample_labels.npy", ys)
    with open("results/fig2a_metrics.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("saved results/fig2a_metrics.json")


if __name__ == "__main__":
    main()
