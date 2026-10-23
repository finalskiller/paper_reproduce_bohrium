# 真实运行日志（本分享的完整执行记录）

> 本文件按时间顺序记录 2026-10-23 一次真实 AI 精读会话的全部关键动作，包括**失败的尝试和降级路径**。
> 执行者：ZCode agent（GLM-5.3，作为"AI 读者"）；宿主：Windows 11 本机。
> 关键文件的 SHA-256 见文末。

## A. 准备与论文获取

1. 从 JMLR 官网 `curl` 下载论文 PDF（`https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf`）。
   - **翻车 1**：首次下载在本网络超时停滞（127 KB 后挂起 5 分钟），终止后用 `curl -C -` 断点续传分次完成，最终 3,716,712 字节。
   - 验证：PyMuPDF 打开 27 页，首页文本含 "Journal of Machine Learning Research 9 (2008) 2579-2605 / Visualizing Data using t-SNE / Laurens van der Maaten / Geoffrey Hinton"。
2. 全文提取（PyMuPDF `get_text`，逐页落盘 `paper_src/fulltext.txt`，页码标记修正过一次：最初把期刊页算成 2575，实为 PDF 第 N 页 = 期刊页 2578+N）。
   - **翻车 2**：提取后用 `grep` 搜 "Figure" 无任何输出——Git Bash 的 grep 在该中文路径/编码组合下静默失败，改用 Python `re` 检索后正常。
3. 论文图表裁剪：`paper_evidence/figures_paper/` 下生成 `fig1_paper_full.png`（p.2586 上部三幅热图，220dpi）、`fig2_paper_full.png`、`fig2a_paper_tsne.png`（p.2590）。

## B. 精读与"先验纠错"

4. **AI 读者先验记忆（错误）**：会话最初凭记忆称 Figure 1 是"高斯 vs Student-t 核相似度曲线对比"。
5. **原文核对（纠正）**：p.2586 图题与正文确认为三幅**梯度热图**（SNE / UNI-SNE / t-SNE，横轴高维距离、纵轴低维距离，正值=吸引、负值=排斥），且正文给出关键数值锚点（SNE 最大引力≈19 / 最大斥力≈1）。此纠错过程记录于 README §2.1。
6. 逐节精读并摘录：Eq.1（p.2581）、对称 SNE 与 Eq.3 及其梯度（p.2584）、UNI-SNE 背景（p.2585 §3.3 前后）、Eq.4/5（p.2585–2586）、Algorithm 1（p.2587）、§3.4 优化参数与 §4.1/4.2 实验设置（p.2588–2589）→ 沉淀为 `paper_evidence/excerpts/key_excerpts.md`。
7. 视觉解析原图（图像分析模型读取裁剪件）：三面板色标分别约 −1…19 / −4…14 / −1…1，吸引/排斥区几何位置与公式构造一致。视觉描述中与数学矛盾的部分（如 t-SNE 吸引区位置）以数学与论文文字为准——视觉模型输出同样只作参考不作依据。

## C. 复现代码与验证

8. 写 `code/validate_gradients.py`（有限差分独立验证）。
   - **翻车 3**：第一版 UNI-SNE 解析式直接套用 SNE 弹簧形式，与有限差分相对误差 9.26（FAIL）；t-SNE 分支另有广播错误。
   - **修复**：推导混合核精确梯度 `4Σ(p−q)(y_i−y_j)·w_ij`，w=(1−ρ)e^{−dl²}/num_ij，重跑后 SNE/UNI-SNE 精确式/t-SNE 全部 PASS（≤1.1e-8）；弹簧形式保留为显式 MISMATCH 用例（这正是 README §2.3 的发现来源）。
9. 写 `code/fig1_reproduce.py`：
   - 构造 `g = s·(p−q)·dl·k(dl)`，三锚点联立校准（SNE≈19、UNI−4/14、t-SNE±1）→ s=1、ρ=2/9、σ=1（σ 不可辨识，敏感性说明）。
   - **修正**：初版横纵轴与论文相反（复现件 x=低维），与原图对照前发现，转置后重渲染。
   - 输出：`results/fig1_reproduction.png`、`results/fig1_calibration.json`、`results/fig1_comparison.png`（上原图下复现）。
   - 对照（图像分析模型判定）：(a)(c) 结构 MATCH，(b) PARTIAL（色图饱和度差异，几何一致）。

## D. 参数三方对照

10. 作者官方 Python 实现：从 `https://lvdmaaten.github.io/tsne/code/tsne_python.zip` 下载解包，逐行核对 `tsne.py`（max_iter=1000 / initial_momentum=0.5 仅前 20 次 / eta=500 / exaggeration ×4 撤销于 iter==100 / init 为标准正态 / PCA→50 维）。同时下载 MATLAB 包与作者自渲染的 `examples/mnist_tsne.jpg`（对照材料）。
11. 本机 scikit-learn 1.9.1：`inspect.signature` + `inspect.getsource(sklearn.manifold._t_sne)` 核对默认值与关键行（`_EXPLORATION_MAX_ITER=250`、动量 0.5→0.8、`init='pca'` 重标定注释引用 issue #18018、`random` init=1e-4·standard_normal、`auto` 学习率=N/exagg/4 下限 50、gains +0.2/−0.8 min_gain 0.01）。
12. 汇总为 `code/parameter_drift.json`（每项含论文页码或源码事实来源）。

## E. issuescout 社区证据链（issue #18018）

13. **网络降级**：`api.github.com` 在本机不可达（HTTP 000，0.02s 即失败）；`github.com` 主站不可达；`codeload.github.com` 可达。
14. 用网页阅读器（另一网络通道）抓取 `https://github.com/scikit-learn/scikit-learn/issues/18018` 全文；正文（含五项任务清单与 PR 引用）离线存档 `issuescout_run/issue_18018_offline_cache.json`。
15. 经 codeload 下载 scikit-learn 1.9.1 源码 tarball（7.7 MB）到 `issuescout_run/repo/`，`git init + remote add origin + add + commit`（issuescout 的 `git ls-files` 需要索引）。
16. 按 issuescout 缓存格式写 `~/.issuescout/cache/scikit-learn__scikit-learn.json`（真实 issue 正文，字段格式来自工具源码 `packages/github/src/records.ts`）；评论数置 0 并如实说明（评论 API 不可达，工具对失败返回空）。
17. 运行 `npm run cli -- analyze 18018 <repo_dir>`（DeepSeek Chat，真实调用）：
    - 12 次工具调用（`search_code`/`read_file` 定位 `sklearn/manifold/_t_sne.py` 等），74,692 tokens 输入 / 1,276 输出，置信度 85%。
    - 结论要点：五项已勾选任务均已在 1.9.1 源码落地（两处注释引用 #18018）；未完成项指向 Kobak & Linderman (2021)；额外发现 sklearn `auto` 学习率下限 50 与 openTSNE 的 `max(200, N/exagg)` 表述不一致。
    - 原始输出存 `issuescout_run/scikit-learn__scikit-learn__18018.json`。
    - 使用的 DeepSeek Key 为 issuescout 本机配置（工具自有配置，未进入任何分享材料）。

## F. MNIST 实证（Figure 2(a)）

18. 数据获取：OpenML（`fetch_openml`）在本机持续 WinError 10060 超时重试 → 终止，改走作者镜像 `lvdmaaten.github.io/tsne/code/mnist.zip`（该域名此前已验证可达但带宽慢，实际下载约 30 分钟）。
19. 实验：随机抽 6,000 张（seed=42）→ PCA→30 维 → 两次 TSNE 运行（A=论文参数化：perplexity=40/exagg=4/lr=100/init=random；B=sklearn 默认：perplexity=30/exagg=12/lr=auto/init=pca），指标=trustworthiness(k=12) 与 2 维嵌入上 1-NN 5 折准确率。结果回填 README §2.5 与 `results/fig2a_metrics.json`。
20. 与论文 Figure 2(a) 裁剪件、作者自渲染 `mnist_tsne.jpg` 做结构对照图 `results/fig2a_comparison.png`。

## G. 打包与提交准备

21. 本地 git 仓库初始化、`提交说明.md`、`materials.zip`（≤50 MiB，排除 .git/data_cache/大文件，保留全部证据性小文件）、`outputs/deliverables/submission.txt`。
22. 提交前实际解压自检一次（正文入口存在、索引齐全、可读、容量合规）。

---

## 关键文件 SHA-256（打包前）

（由打包脚本生成并写入 `workflow/checksums.txt`；论文 PDF 本地核查用哈希见下）

- vandermaaten08a.pdf（论文，本地留档不分发）: `f05922e427639a08cb5214cc4ef314689ecf2d87333cb5050003323d7631017f`
- tsne_python.zip（作者分发包）: `d31ed9b42d61f2fecc05179c705f1ddc47c6037c2edb287c3a0fd2e05bab54e1`
- tSNE_matlab.zip: `3fc9ba4bf74b85d5361ed4485ef439d0c0a1a6864b6e984d8697727b718708e4`
- mnist_tsne.jpg: `fa06de66cf3bed35d1ed4753c5adeac613b0c8842fcc41a6e58bda68ab502ec1`

> 说明：本日志中所有"翻车"条目均为真实发生并修复的事件，保留它们是为了让读者复现时知道哪些坑是环境/方法本身的问题。
