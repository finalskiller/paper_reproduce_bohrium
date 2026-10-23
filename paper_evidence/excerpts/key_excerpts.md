# 论文关键原文摘录（用于核查本分享的所有关键解读）

**论文**: van der Maaten, L. & Hinton, G. (2008). *Visualizing Data using t-SNE*.
Journal of Machine Learning Research 9 (2008) 2579–2605.
**开放获取原文**: https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf
**本地下游副本**: 下载自 JMLR 官网（2026-10-23，SHA-256 见 workflow/run_log.md），仅本地核查用，不随材料包再分发全文；图表裁剪件见 `figures_paper/`，仅用于核查对照（合理引用 + 注明出处）。

页码说明：本文件页码为**期刊页码**（PDF 第 N 页 = 期刊页 2578+N）。

---

## 1. Figure 1 的定义与约定（p.2586，§3.3）

> "In Figure 1(a) to 1(c), we show the gradients between two low-dimensional
> datapoints y_i and y_j as a function of their pairwise Euclidean distances in
> the high-dimensional and the low-dimensional space (i.e., as a function of
> ‖x_i−x_j‖ and ‖y_i−y_j‖) for the symmetric versions of SNE, UNI-SNE, and
> t-SNE. In the figures, positive values of the gradient represent an
> attraction between the low-dimensional datapoints y_i and y_j, whereas
> negative values represent a repulsion between the two datapoints."

**图题**（p.2586）:
> "Figure 1: Gradients of three types of SNE as a function of the pairwise
> Euclidean distance between two points in the high-dimensional and the
> pairwise distance between the points in the low-dimensional data
> representation."

**坐标轴**: 三幅图横轴均为 "High-dimensional distance >"，纵轴均为
"Low-dimensional distance >"，刻度 0–18（从 PDF 原图裁剪件核对）。

## 2. SNE 梯度数值锚点（p.2586，§3.3）

> "First, the t-SNE gradient strongly repels dissimilar datapoints that are
> modeled by a small pairwise distance in the low-dimensional representation.
> SNE has such a repulsion as well, but its effect is minimal compared to the
> strong attractions elsewhere in the gradient (**the largest attraction in
> our graphical representation of the gradient is approximately 19, whereas
> the largest repulsion is approximately 1**). In UNI-SNE, the amount of
> repulsion between dissimilar datapoints is slightly larger, however, this
> repulsion is only strong when the pairwise distance between the points in
> the low-dimensional representation is already large ..."

> "Second, although t-SNE introduces strong repulsions between dissimilar
> datapoints that are modeled by small pairwise distances, **these repulsions
> do not go to infinity**. In this respect, t-SNE differs from UNI-SNE, in
> which **the strength of the repulsion between very dissimilar datapoints is
> proportional to their pairwise distance in the low-dimensional map**, which
> may cause dissimilar datapoints to move much too far away from each other."

（UNI-SNE 色标刻度 −4…14、t-SNE 色标刻度 −1…1 从 PDF 原图裁剪件读出。）

## 3. 核心公式（本复现直接使用的四条）

**Eq. 1（p.2581，条件概率）**
> p_{j|i} = exp(−‖x_i−x_j‖²/2σ_i²) / Σ_{k≠i} exp(−‖x_i−x_k‖²/2σ_i²)

**Eq. 3（p.2584，对称 SNE 的低维分布与梯度）**
> q_ij = exp(−‖y_i−y_j‖²) / Σ_{k≠l} exp(−‖y_k−y_l‖²)
> δC/δy_i = 4 Σ_j (p_ij − q_ij)(y_i − y_j)

**Eq. 4（p.2585，t-SNE 低维 Student-t(1 dof) 分布）**
> q_ij = (1+‖y_i−y_j‖²)⁻¹ / Σ_{k≠l} (1+‖y_k−y_l‖²)⁻¹

**Eq. 5（p.2586，t-SNE 梯度）**
> δC/δy_i = 4 Σ_j (p_ij − q_ij)(y_i − y_j)(1+‖y_i−y_j‖²)⁻¹

**对称 SNE 高维概率（p.2584）**
> p_ij = (p_{j|i} + p_{i|j}) / (2n)

## 4. 优化与实验参数（p.2587–2589）

**Algorithm 1（p.2587）**: 初始化 "sample initial solution Y(0) from N(0, 10⁻⁴ I)"。

**§3.4（p.2588）**:
> "We used the early exaggeration method with an exaggeration of 4 for the
> first 50 iterations (note that early exaggeration is not included in the
> pseudocode in Algorithm 1). The number of gradient descent iterations T was
> set 1000, and the momentum term was set to α(t) = 0.5 for t < 250 and
> α(t) = 0.8 for t ≥ 250. The learning rate η is initially set to 100 and it
> is updated after every iteration by means of the adaptive learning rate
> scheme described by Jacobs (1988)."

**§4.1（p.2588，MNIST 数据）**:
> "The MNIST data set contains 60,000 grayscale images of handwritten digits.
> For our experiments, we randomly selected 6,000 of the images for
> computational reasons. The digit images have 28 × 28 = 784 pixels."

**§4.2（p.2589，预处理与参数）**:
> "In all of our experiments, we start by using PCA to reduce the
> dimensionality of the data to 30."

**Table 1（p.2589）**: "t-SNE — Perp = 40"

## 5. Figure 2 图题（p.2590）

> "Figure 2: Visualizations of 6,000 handwritten digits from the MNIST data set."
> "(a) Visualization by t-SNE. (b) Visualization by Sammon mapping."

（本分享实证复现的目标为 Figure 2(a)。）

---

### 摘录用途与授权说明

以上摘录仅为核查目的的短片段引用（每处不超过必要限度），版权归原作者所有
（© 2008 Laurens van der Maaten and Geoffrey Hinton，JMLR 开放获取）。
`figures_paper/` 中的图表裁剪件同样仅用于核查对照，均在 README 中注明出处。
作者官方代码（tsne_python.zip / tSNE_matlab.zip）按作者页面声明"free to use,
restricted to non-commercial purposes"引用，本分享为非商业的技术分享。
