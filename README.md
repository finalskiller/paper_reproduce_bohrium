# 用 AI 精读一篇经典论文：t-SNE (JMLR 2008) 的图表反推、公式验证与参数漂移核查

> **一句话**：以 "Visualizing Data using t-SNE"（van der Maaten & Hinton, JMLR 9 (2008) 2579–2605）为样本，演示一套 **"原文锚定 → 公式反推 → 独立数值验证 → 三方参数对照 → 社区证据链"** 的 AI 论文精读流程。论文 Figure 1 的三幅梯度热图被解析级复现并与原图对照；论文、作者代码与 scikit-learn 实现之间的参数漂移被逐项核对（6 组参数、页码/行号级证据）并溯源到具体 issue。

- 论文（开放获取）：https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf
- 对照实现：作者官方 Python 代码（lvdmaaten.github.io/tsne）与 scikit-learn 1.9.1（`sklearn.manifold.TSNE`）
- 全部材料（证据裁剪件、代码、校准与验证记录、真实运行日志）：见下方[材料索引](#材料索引)

---

## 1. 问题与方法

### 1.1 阅读问题是什么

读经典算法论文时最常见的三类"读不透"：

1. **图表看不懂来历**：论文 Figure 1 画了 SNE / UNI-SNE / t-SNE 三幅"梯度热图"（横轴高维距离、纵轴低维距离，颜色=梯度值），但**正文没有说明作图用的 σ、归一化方式和 UNI-SNE 背景混合比例 ρ**——读者无法从论文直接重画这张图，也就很难真正理解"t-SNE 梯度为什么更优"这一核心论证。
2. **参数与实现对不上**：论文 §3.4/§4.2 给出的优化参数（η=100、exaggeration×4/50 迭代、动量 0.5→0.8@250、初始化 N(0,1e-4)），与今天大家实际用的 scikit-learn 默认值差别很大。**这些漂移是什么、为什么发生、哪些是改进哪些只是实现惯性**，原文不会告诉你。
3. **AI 摘要不可靠**：大模型对经典论文有大量"先验记忆"，其中一部分是错的。不锚定原文的 AI 解读会污染理解。

### 1.2 方法：五步"原文锚定"精读流程

| 步骤 | 做什么 | 关键取舍 |
|---|---|---|
| ① 原文锚定 | 从出版方 PDF 提取全文与原图裁剪件，所有关键解读落到"页码+引文"（见 `paper_evidence/excerpts/key_excerpts.md`） | 不用二手转述；AI 先验记忆一律回原文核对 |
| ② 公式反推 | 从 Eq.1/3/4/5 + 对称 SNE 梯度式出发，写出 Figure 1 三幅图的解析构造；未写明的 (σ, ρ, 归一化) 用**论文自己给出的数值锚点**反推校准（见 §2.2） | 论文没写的参数不猜——用可证伪的校准流程+敏感性分析代替 |
| ③ 独立验证 | 用有限差分直接对 KL 代价函数求导，验证三条解析梯度公式本身（`code/validate_gradients.py`） | 先验证公式再谈复现：图对不上时才知道是谁的错 |
| ④ 三方参数对照 | 论文 ↔ 作者官方 Python 代码 ↔ 本机 scikit-learn 1.9.1 源码逐项核对（`code/parameter_drift.json`） | 以"源码行号/页码"级证据记录漂移，不凭印象 |
| ⑤ 社区证据链 | 用 issuescout（本分享作者开发的本地 issue 分析工具，DeepSeek 后端；源码未公开，本分享提供其真实输出与输入材料，见 `issuescout_run/`）深度分析 sklearn issue #18018，把参数漂移的"为什么"溯源到具体讨论与后续论文 | issue 正文经网页阅读器抓取后离线分析，过程可复现 |

**为什么这样设计**：图表理解的关键不是"画得像"，而是**每一个像素都能从论文公式+论文文字锚点推出来**；参数理解的关键不是"背默认值"，而是知道每个默认值从哪来（论文→作者代码→社区讨论→后续研究）。步骤③是整个流程的安全网——它把"我复现的图"与"论文的图"的差异和"我的数学写错了"彻底解耦。

### 1.3 环境与工具

- Windows 11，Python 3.14.7，numpy 2.5.4，matplotlib 3.11.2，scikit-learn 1.9.1（`pip install scikit-learn` 安装版，参数对照直接 `inspect.getsource` 核对）
- AI 工具：ZCode agent（GLM-5.3，即本流程的"AI 读者"）；DeepSeek Chat（issuescout 的分析模型，DeepSeek API）
- 论文 PDF：JMLR 官网开放获取；作者代码：lvdmaaten.github.io/tsne 官方分发包
- 诚实的网络说明：本网络环境下 OpenML 与 api.github.com 不可达，MNIST 改用作者官方镜像，issue 内容经网页阅读器抓取后离线分析——所有"降级路径"都在 `workflow/run_log.md` 留痕

---

## 2. 真实案例与结果

### 2.1 先说一个翻车：AI 的先验记忆是错的

本案例的 AI 读者（即执行本流程的 agent）在打开论文前的第一反应是：*"t-SNE 论文的 Figure 1 是高斯核与 Student-t 核的相似度曲线对比"*。**回原文核对后这是错的**——Figure 1 实际是三幅**梯度热图**（p.2586）：

> "Figure 1: Gradients of three types of SNE as a function of the pairwise Euclidean distance between two points in the high-dimensional and the pairwise distance between the points in the low-dimensional data representation."

这是本流程最有价值的一课：**AI 对经典论文的"记忆"必须当作假设而非事实**。本分享的所有结论都按"论文原文 / AI 输出 / 我的判断"三区分标注（见 `workflow/verification.md`）。

### 2.2 Figure 1 的解析反推：论文没写的作图假设，用文字锚点校准出来

**AI 推导（可核查）**：三幅图的自然构造是"逐对弹簧力"
`g(dh, dl) = s · (p(dh) − q(dl)) · dl · k(dl)`，其中 dh=高维距离、dl=低维距离，p=Eq.1 高斯核（未归一化，σ 待定），q 分别为 Eq.3 高斯核 / UNI-SNE 混合核 `(1−ρ)e^{−dl²}+ρ` / Eq.4 Student-t 核，k 为各自梯度式的核因子（SNE/UNI-SNE 为 1，t-SNE 为 `(1+dl²)⁻¹`，来自 Eq.5）。

**校准锚点（论文原文，p.2586–2587 + 原图色标）**：

| 锚点 | 论文来源 | 校准值 s=1, ρ=2/9, σ=1 时 |
|---|---|---|
| SNE 最大引力 ≈ 19 | "the largest attraction … is approximately 19" | **18.0**（网格角点；与"approximately"一致） |
| UNI-SNE 色标 −4…14 | 原图刻度 | **−4.5 / +13.5**（唯一能同时命中两端的解） |
| t-SNE 色标 −1…1 | 原图刻度 | ±0.34（对称发散色标，两端饱和显示） |

三锚点联立可**唯一确定 s 与 ρ**（s·18(1−ρ)=14 且 s·18ρ=4 ⇒ s=1, ρ=2/9）；σ 只影响沿 dh 轴的形状、不影响上述角点值，故取 σ=1 并做敏感性分析（`results/fig1_calibration.json`）。注意：若强行命中"19"（s=1.056）则 UNI-SNE 吸引力端变成 15，与色标 14 冲突——**论文自己的两个锚点在 1 个单位内互斥**，这也是"approximately 19"应读作 18.0 的旁证。

**对照结果**（`results/fig1_comparison.png`，上=原图裁剪件，下=复现）：

- (a) SNE：左上角强吸引楔形、右下弱排斥、对角零等值线——**结构一致**；最大引力 18.0 vs 论文"≈19"
- (b) UNI-SNE：排斥随 dl 线性增长（大 dh 时 −ρ·dl）、底部吸引——**结构一致**
- (c) t-SNE：底部小 dl 处强排斥带、排斥有界（峰值在 dl≈0.6）、绿色对角零带——**结构一致**，与论文文字声明逐条对应（"strongly repels dissimilar datapoints that are modeled by a small pairwise distance" / "these repulsions do not go to infinity"，p.2586–2587）

**独立验证（步骤③）**：三条解析梯度对 KL 代价函数的有限差分对照，SNE/UNI-SNE(精确式)/t-SNE 相对误差均 ≤ 1.1e-8（`results/gradient_validation.json`）。

### 2.3 意外发现：论文 Figure 1(b) 画的不是 UNI-SNE 的精确梯度

验证过程中发现：UNI-SNE 混合核代价的**精确**梯度应带权因子 `w_ij = (1−ρ)e^{−dl²} / num_ij`（混合核中只有高斯部分对导数有贡献），即 `4Σ(p_ij−q_ij)(y_i−y_j)·w_ij`。有限差分证实：精确式误差 1e-8，而论文图所用的"弹簧形式"（无 w 因子）误差 9.26。

**判断（我的解读，非论文原述）**：Figure 1(b) 采用的是与 (a)/(c) 一致的弹簧画法 `(p−q)·dl`——这既被色标锚点（−4/14 只有弹簧形式能同时命中）也被论文文字（"UNI-SNE 斥力与低维距离成正比"，精确式在大 dl 处斥力会衰减）双重支持。这是一个"论文示意图是简化约定而非精确导数"的具体案例，也说明**为什么图复现必须同时做数值验证**：单看图形永远发现不了这个差别。

### 2.4 参数漂移：论文(2008) → 作者代码 → scikit-learn 1.9.1

完整对照表（每行含页码/文件/行号级证据）见 `code/parameter_drift.json`，摘要：

| 参数 | 论文 (p.2587–2589) | 作者 Python 代码 | scikit-learn 1.9.1 默认 |
|---|---|---|---|
| early exaggeration | ×4，前 50 迭代 | ×4，前 100 迭代 | **×12，前 250 迭代** |
| 学习率 | 100 初值 + Jacobs 自适应 | 500（梯度少了因子 4，数值上被吸收） | `auto` = max(N/12/4, 50)，N=6000 时 125 |
| 动量 | 0.5→0.8 @ t=250 | 0.5→0.8 @ **t=20** | 0.5→0.8 @ 250（**回归论文**） |
| 初始化 | N(0, 1e-4·I) | **N(0, I)**（尺度差 1e4 倍） | `random`=1e-4·standard_normal（**与论文逐字一致**）；默认 `pca`（PC1 重标定 1e-4） |
| PCA 预降维 | 30 维 | 50 维 | 不预降维（文档建议外部做） |
| MNIST 实验 perplexity | 40 | 默认 30 | 默认 30 |

**溯源（步骤⑤，issuescout 真实分析）**：sklearn 的 exaggeration=12 与 `init='pca'` 重标定都来自 issue [#18018](https://github.com/scikit-learn/scikit-learn/issues/18018)（2020，已关闭）推动的改动，源码两处注释直接引用该编号；该 issue 未完成项指向 Kobak & Linderman (2021) 的后续研究——exaggeration=12 正是后者建议的值。issuescout（DeepSeek 驱动，12 次工具调用读取 sklearn 源码）的分析还发现一个文档级细节：**sklearn 的 `auto` 学习率下限 50 与 openTSNE 的 `max(200, N/exagg)` 不一致**。分析全文见 `issuescout_run/scikit-learn__scikit-learn__18018.json`。

### 2.5 Figure 2(a) 实证复现：论文参数 vs sklearn 默认（MNIST 6000）

按论文协议（6000 张随机训练图、PCA→30、Barnes-Hut、seed=42）跑双配置，结果（`results/fig2a_metrics.json`，`results/fig2a_comparison.png` 四方对照：论文原图 | 作者自渲染 | 我方 A | 我方 B）：

| 配置 | 参数 | KL | trustworthiness(k=12) | 2 维 1-NN 5 折 | 耗时 |
|---|---|---|---|---|---|
| A 论文参数化 | Perp=40, exagg=4, lr=100, init=random | **1.514** | **0.9877** | 93.6% | 31 s |
| B sklearn 1.9.1 默认 | Perp=30, exagg=12, lr=auto(=125), init=pca | 1.550 | 0.9867 | **94.1%** | 31 s |

**观察**：① 两配置都完整复现论文级结构（~10 个数字簇清晰分离；1/7 相邻），四方对照图结构一致；② 两配置数值指标非常接近且**不同向**（A 的 KL/trustworthiness 略优，B 的 1-NN 略优，视觉上 B 的簇更干净、A 略有拉伸）——说明经过社区 15 年打磨的默认值与论文原始参数在这个基准上没有实质差别，"论文参数"并不神圣；③ 视觉模型对 A 给出 PARTIAL（簇间轻微桥接）与 A 的 KL 更低并存，提醒我们**单一指标（无论数值还是视觉）都不足以下结论**。论文原图无法数值对照（未发布坐标），此对照为结构级。

### 2.6 局限（如实）

1. **Figure 1**：σ=1 是唯一无法从锚点识别的自由参数（锚点都位于 p∈{0,1} 的角点），已做敏感性说明；对定性结论（三种梯度的结构差异）无影响，因为它们对 (σ, ρ) 参数稳健。
2. **Figure 2(a)**：论文未发布嵌入坐标，无法与原图做数值级对照，只做结构对照 + 我方两次运行的定量指标互比；论文用精确 t-SNE，本次用 Barnes-Hut 近似（论文一作 2014 年的加速工作）；sklearn 的 exaggeration 时长不可配置为论文的 50 次（固定 250）——这些偏差都已在参数表中标注。
3. **issuescout 分析**基于 issue 正文（网页阅读器抓取）+ 本地 sklearn 1.9.1 源码快照；issue 的讨论评论未能离线获取（api.github.com 不可达，工具对评论拉取失败返回空并继续），分析基于正文的输入范围已在分析记录中体现。
4. **玻尔科学空间**：本次实践未在玻尔平台执行（零生态分声明，不虚报）。附迁移指南见 §4.3。

---

## 3. 复现步骤与材料

### 3.1 环境

```
Windows 11 / Python 3.14.7
numpy==2.5.4  matplotlib==3.11.2  scikit-learn==1.9.1  pymupdf==1.28.2（仅图表提取用）
Node v24 + 本仓库 vendor 的 issuescout（仅 §2.4 溯源分析需要，可选）
```

### 3.2 一键复现

```bash
# ① Figure 1 解析复现 + 校准报告（<10 秒）
python code/fig1_reproduce.py        # -> results/fig1_reproduction.png, fig1_calibration.json

# ② 梯度公式有限差分验证（<10 秒）
python code/validate_gradients.py    # -> results/gradient_validation.json（应全 PASS）

# ③ Figure 2(a) MNIST 双配置实验（含数据下载，分钟级）
python code/fig2a_mnist.py           # -> results/fig2a_reproduction_*.png, fig2a_metrics.json

# ④（可选）issuescout 对 sklearn issue #18018 的深度分析
#    见 workflow/run_log.md §E：离线缓存构造 + npm run cli -- analyze 18018 <repo>
```

**结果检查**：② 中三行 `PASS`（相对误差 < 1e-5）；① 中校准输出 σ=1.0, ρ=0.211, s=1.0 且 SNE/UNI-SNE 的 max/min 与 §2.2 表一致；③ 的两幅嵌入图应呈现论文级结构（10 个数字簇清晰分离、1/7 与 3/5/8 的邻近关系）；参数对照打开 `code/parameter_drift.json` 与本 README §2.4 逐行核对。

### 3.3 材料索引

| 材料 | 位置 |
|---|---|
| 分享正文（本文件） | `README.md` |
| 论文关键原文摘录（页码级） | `paper_evidence/excerpts/key_excerpts.md` |
| 论文原图裁剪件（Figure 1 / 2 / 2a） | `paper_evidence/figures_paper/*.png`（出处均在文件名与 §来源） |
| 作者官方代码（核查用副本+下载脚本） | `author_code/`（原始 zip 保留，解包件仅含 tsne.py 等核心文件） |
| 复现代码 | `code/fig1_reproduce.py`, `code/validate_gradients.py`, `code/fig2a_mnist.py` |
| 参数漂移对照表 | `code/parameter_drift.json` |
| 复现输出（图/表/指标） | `results/` |
| AI 阅读过程与真实运行日志 | `workflow/run_log.md` |
| 逐条核查记录（原文/AI/我的判断三区分） | `workflow/verification.md` |
| issuescout 分析（issue #18018，真实 DeepSeek 输出） | `issuescout_run/scikit-learn__scikit-learn__18018.json` + 离线缓存构造说明 |
| 知识提取（可复用经验） | `trace.md` |

---

## 4. 来源、贡献与致谢

### 4.1 来源与授权

- **论文**：© 2008 Laurens van der Maaten and Geoffrey Hinton，JMLR 开放获取。本仓库仅含**短片段引文与图表裁剪件**（核查用途，注明出处），不分发论文全文；全文请从 JMLR 官网获取。
- **作者官方代码**（tsne_python.zip / tSNE_matlab.zip / mnist.zip / mnist_tsne.jpg）：来自 [lvdmaaten.github.io/tsne](https://lvdmaaten.github.io/tsne/)，按作者声明"free to use, restricted to non-commercial purposes"用于非商业核查；仓库内保留原始分发包以供溯源（`author_code/`），另有 `mnist_tsne.jpg`（作者自己的 MNIST 可视化）作为对照材料。
- **scikit-learn**：BSD-3-Clause。参数对照基于本机安装的 1.9.1 源码；issue #18018 内容来自 GitHub 公开页面（抓取存档见 `issuescout_run/issue_18018_offline_cache.json`）。
- **issuescout**：本分享作者开发的本地 issue 分析工具（DeepSeek 后端，源码未公开），本次为真实使用并完整留痕；本分享包含其真实输出与离线输入材料，读者无需该工具即可核查全部结论（`issuescout_run/`）。

### 4.2 本次个人贡献

1. **完整精读流程**的设计与全程真实执行记录（含两次翻车与修复：AI 先验记忆纠错、UNI-SNE 精确梯度推导纠错）。
2. Figure 1 的解析构造、数值锚点校准方法（三锚点联立唯一确定 s 与 ρ）及其开源实现 `code/fig1_reproduce.py`。
3. UNI-SNE 混合核精确梯度推导 + "论文示意图为弹簧约定"的论证（有限差分数值证据）`code/validate_gradients.py`。
4. 论文↔作者代码↔sklearn 的页码/行号级参数漂移表 `code/parameter_drift.json` 及 issue #18018 溯源链。
5. issuescout 在"论文参数考古"场景的用法演示（离线缓存构造流程见 `workflow/run_log.md` §E）。

未包括在个人贡献内（如实声明）：论文本身、作者代码、scikit-learn、MNIST 数据集、Distill 博客与 Kobak & Linderman 论文的任何内容——它们只作为核查对象/引用。

### 4.3 玻尔科学空间迁移指南（本分享未在玻尔执行，此为操作说明而非使用记录）

本流程全部步骤（论文 PDF 下载与裁剪、Figure 1 解析复现、MNIST 实验、issuescout 分析）都是标准 Python/Node 工作负载，可直接搬到玻尔科学空间的 Notebook 环境：

1. 在玻尔科学空间新建 Notebook（镜像选 pytorch/sklearn 系，含 numpy/matplotlib/scikit-learn）；
2. 上传本仓库 `code/` 目录，逐格执行 §3.2 的三段脚本（MNIST 下载走 OpenML，玻尔网络可达，无需镜像降级）；
3. 论文 PDF 与本仓库 `paper_evidence/` 一起上传，即可在格子里对照 `fig1_comparison.png` 核验；
4. issuescout 步骤需 Node 环境与 DeepSeek Key，可用玻尔的 Web 终端跑 `npm run cli -- analyze ...`。
玻尔环境如与本机产生结果差异（包版本不同），以 `results/` 内留存的原始输出为准对照排查——这也是把真实输出全部入库的原因。

---

## 5. 结论

- 论文没写明的作图假设（σ、ρ、归一化、全局尺度）**可以被系统性地反推**：把论文文字里的数值声明当作校准锚点，联立求解并做敏感性分析（§2.2）。这套方法适用于一切"图很关键但参数没写全"的经典论文。
- **图复现之前先做公式级独立验证**（有限差分/解析极限），否则分不清"论文画错了"还是"我没读懂"（§2.3 的弹簧约定发现即源于此）。
- 今天的 sklearn 默认参数是一条"论文→作者代码→社区 issue→后续论文"的演化链产物，不是对 2008 论文的直接实现；`init='random'` 和动量调度反而与论文逐字一致（§2.4）。
- AI 读论文的正确姿势：**先验当假设、原文当法庭、数值当陪审团**（§2.1 的记忆纠错即本流程第一步）。
