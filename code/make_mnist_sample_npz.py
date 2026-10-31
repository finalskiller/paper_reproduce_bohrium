# -*- coding: utf-8 -*-
"""从作者官方镜像 mnist.zip 构建本作品离线样本包 author_code/mnist6000_sample.npz。

这个 npz 是 fig2a_mnist.py 原始运行（2026-10-23，MNIST_SOURCE=author，seed=42）
所用 6,000 张样本的**无损离线副本**。构建后与 results/mnist_sample_labels.npy
（原始运行存档的抽样标签）逐一比对——全部一致才写入，证明子集与原始输入相同。

用法：python code/make_mnist_sample_npz.py [--mnist-zip path/to/mnist.zip]
依赖：numpy, scipy（读作者 .mat 格式）
"""
import argparse
import os
import sys
import zipfile

import numpy as np

RNG_SEED = 42
N_SAMPLES = 6000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mnist-zip", default="data_cache/mnist.zip",
                    help="作者镜像 mnist.zip 路径（lvdmaaten.github.io/tsne/code/mnist.zip）")
    ap.add_argument("--out", default=os.path.join("author_code", "mnist6000_sample.npz"))
    args = ap.parse_args()

    import scipy.io as sio
    with zipfile.ZipFile(args.mnist_zip) as zf:
        zf.extractall(os.path.dirname(args.mnist_zip) or ".")
    base = os.path.dirname(args.mnist_zip) or "."
    m = sio.loadmat(os.path.join(base, "mnist_train.mat"))
    X = m["train_X"]                            # 60000 x 784 float64, 值 = k/255（作者 zip 已归一化）
    assert 0.0 <= X.min() and X.max() <= 1.0
    y = m["train_labels"].flatten().astype(np.int64)
    print("full MNIST train:", X.shape, "| 值域 [0,1]，256 级灰度（k/255）")

    rng = np.random.default_rng(RNG_SEED)
    idx = rng.choice(len(X), N_SAMPLES, replace=False)
    K = np.round(X[idx] * 255).astype(np.uint8)  # k = round(k/255*255)，无损（见下方断言）
    ys = y[idx]
    assert np.abs(X[idx] * 255 - K.astype(np.float64)).max() == 0, "像素值不是 k/255 整数级，uint8 存储有损！"
    # 位级自检：加载器的重建路径 (uint8 -> float64/255 -> float32) 必须与
    # 原始运行路径 (mat float64 -> astype float32) 完全一致
    Xs_orig = X[idx].astype(np.float32)
    Xs_recon = (K.astype(np.float64) / 255.0).astype(np.float32)
    assert np.array_equal(Xs_orig, Xs_recon), "float32 重建与原始路径不一致！"
    print("位级自检: uint8 重建与原始 float32 输入完全一致（max diff 0.0）")

    # 与原始运行存档的抽样标签逐一核对（顺序敏感）
    ref = np.load(os.path.join("results", "mnist_sample_labels.npy"))
    assert (ys == ref).all(), "抽样标签与原始运行存档不一致——禁止发布该 npz！"
    print(f"标签核验: 6,000/6,000 与 results/mnist_sample_labels.npy 一致（顺序敏感）")

    header = (
        "Offline copy of the exact 6,000-sample MNIST subset used by the original "
        "Figure 2(a) run of this repo (fig2a_mnist.py, MNIST_SOURCE=author, seed=42, "
        "2026-10-23). Label-identity to results/mnist_sample_labels.npy verified "
        f"{N_SAMPLES}/{N_SAMPLES} (order-sensitive); X stored as uint8 pixel levels k "
        "in {0..255} where the author zip's value is k/255 (256-level grayscale). The "
        "loader reconstructs the original float32 input BIT-EXACTLY via "
        "(X.astype(float64)/255.0).astype(float32) — verified at build time against "
        "the mat source. Source: lvdmaaten.github.io/tsne/code/mnist.zip "
        "(author-declared free to use, non-commercial)."
    )
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    np.savez_compressed(args.out, X=K, y=ys, _header=np.array(header))
    print("written:", args.out, os.path.getsize(args.out), "bytes")


if __name__ == "__main__":
    main()
