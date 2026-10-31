# 提示词存档（真实输入与重建模板）

> **诚实性说明（先读）**：2026-10-23 的原始精读会话由 ZCode agent（GLM-5.3）执行，委托是任务式委托（"用 AI 精读这篇论文并把过程做成分享"），agent 内部的逐步指令未逐字存档。本文件据此把提示词分两类，**不混淆**：
> 1. **[真实]** 有原文件佐证的输入（issuescout 的输入缓存与命令行、原始数据下载命令）；
> 2. **[重建]** 按 `workflow/run_log.md` 的逐阶段记录忠实重建的提示词——用于读者复现，与原始措辞可能有差异，但与记录的执行过程一一对应。
> 每条都给出"预期输出应包含什么"，供读者自查。

## 1. 会话委托（[重建]，对应 run_log §A 前提）

```
请用 AI 对这篇论文做一次完整精读：van der Maaten & Hinton, "Visualizing Data
using t-SNE", JMLR 9 (2008) 2579-2605。要求：
1) 每个结论都要锚定原文（页码+原文引文），AI 的先验记忆与原文冲突时以原文为准并记录纠错过程；
2) 对论文中的图表至少完成一次数值级复现或解析验证；
3) 全部真实输入、输出、失败尝试都要留档。
最终产出整理成 GitHub 技术分享（README + 复现材料包）。
```

预期输出应包含：论文获取与验证记录、逐节摘录（锚定页码）、至少一次图表复现、失败与降级路径的记录——对应 run_log §A–§G。

## 2. 各阶段操作提示词（[重建]，对应 run_log §A–§F）

### 2.1 先验纠错（对应 run_log §B 步骤 4–5，本分享案例一的由来）

```
凭你的记忆描述 t-SNE 论文 Figure 1 是什么内容。然后阅读原文第 2586 页的图题
与正文，核对你的描述；如与原文冲突，明确指出冲突并给出原文依据。
```
预期输出：先验描述（本会话中为"高斯 vs Student-t 核相似度曲线"——**错误**）→ 原文核对（三幅**梯度热图**）→ 纠错结论与页码引文。
对应产出：`README §2.1`、`paper_evidence/figures_paper/fig1_paper_full.png`。

### 2.2 Figure 1 解析复现（对应 run_log §C 步骤 9）

```
论文 p.2586 Figure 1 三个梯度热图没有发表坐标数据。请构造一个解析模型复现它：
按各方法梯度公式构造 g = s·(p−q)·dl·k(dl)，用正文给出的数值锚点（SNE 最大引力≈19、
UNI-SNE 斥力 −4 / 引力 14、t-SNE ≈±1）联立求解模型参数，渲染复现图并与原图
逐面板对照；不可辨识的参数要说明并做敏感性分析。
```
预期输出：参数解（s=1, ρ=2/9, σ=1）、逐面板 MATCH/PARTIAL 判定、`results/fig1_calibration.json`。
对应产出：`code/fig1_reproduce.py`、`results/fig1_*.png/json`。

### 2.3 梯度独立验证（对应 run_log §C 步骤 8，本分享案例二的由来）

```
为论文 Eq.(1)-(5) 的梯度公式写一个有限差分验证脚本：解析梯度 vs 数值梯度逐维
比对，报告最大相对误差。注意 UNI-SNE 的斥力归一化与 SNE 的"弹簧"直觉不同——
如果某个解析式验证失败，先怀疑公式理解，用失败用例定位差异来源。
```
预期输出：SNE / UNI-SNE 精确式 / t-SNE 全部 PASS（≤1.1e-8）；UNI-SNE 弹簧形式显式 FAIL（相对误差 9.26）——失败用例正是"论文表述与弹簧直觉的差异"这一发现的来源。
对应产出：`code/validate_gradients.py`、`results/gradient_validation.json`。

### 2.4 参数三方对照（对应 run_log §D 步骤 10–12）

```
对同一组 t-SNE 超参数，在三份权威来源间逐项对照：①论文（页码引文）；②作者官方
实现（lvdmaaten.github.io/tsne/code/tsne_python.zip 内 tsne.py，逐行读）；③本机
安装的 scikit-learn 1.9.1 源码（inspect.getsource）。每个参数给三个值+三处来源
（页码/文件/行号），不一致处标出。
```
预期输出：`code/parameter_drift.json`（early_exaggeration ×4 前 50 次迭代 vs ×4 撤销于 iter==100 vs ×12；eta=100 自适应 vs eta=500 vs auto；PCA→30 vs →50 维 vs 默认等）。
对应产出：`code/parameter_drift.json`、`README §2.4`。

### 2.5 社区证据链（[真实] 输入，对应 run_log §E 步骤 14–17）

真实输入（原文件在 `issuescout_run/`）：
- 输入 1：issue #18018 全文离线缓存 `issue_18018_offline_cache.json`（网页阅读器抓取，抓取时间戳在文件内）；
- 输入 2：scikit-learn 1.9.1 源码快照（codeload tarball，按 issuescout 要求做 git init 存于 `issuescout_run/repo/`，包内不入、可按 run_log §E 重建）；
- 命令：`npm run cli -- analyze 18018 <repo_dir>`（DeepSeek Chat，12 次工具调用，74,692 输入 / 1,276 输出 tokens，置信度 85%）。

预期输出：`scikit-learn__scikit-learn__18018.json`——五项已勾选任务在 1.9.1 源码中的落地证据（两处注释引用 #18018）、未完成项指向 Kobak & Linderman (2021)、auto 学习率下限与 openTSNE 表述不一致。

### 2.6 MNIST 实证（对应 run_log §F 步骤 18–19）

```
按论文 §4.1/§4.2 与表 1 复现 Figure 2(a)：从 MNIST 训练集随机抽 6,000 张
（seed=42 并存档标签），PCA→30 维，跑两次 t-SNE——A=论文参数（perplexity=40,
early_exaggeration=4, learning_rate=100, init=random, 1000 次迭代），B=scikit-learn
1.9.1 默认（perplexity=30, exagg=12, lr=auto, init=pca）。报告 trustworthiness(k=12)
与嵌入上 1-NN 5 折准确率，保存嵌入与指标。
```
预期输出：`results/fig2a_metrics.json`（A: trustworthiness 0.9877 / 1-NN 0.936；B: 0.9867 / 0.941）、嵌入 npy、双配置对比图。
注意：sklearn 无法复刻"×4 持续 50 次迭代后撤销"的论文式调度（250 次迭代内恒定 + 无动量/Jacobs 调度），该偏差已在 README §2.5 声明。

## 3. 玻尔科学空间实测提问（[真实]，2026-10-31 执行）

在玻尔科学空间（www.bohrium.com，作者账号登录）对 t-SNE 论文按本工作流提问三问，Q1/Q2 的提问原文与 AI 实际回答**逐字存档**于 `workflow/bohrium_session/`；原文核查结果（含两处可验证错误的定位）见 `README §4.3`。第 3 问回答完成后页面会话状态丢失未及存档（如实声明，不补写）。

## 4. 读者复现模板（拿走即用）

把本工作流用于任何论文的三条提示词骨架：

1. **先验-原文对照**："凭记忆描述论文的 [图表/结论 X]，然后读原文 [页码] 核对，冲突时以原文为准并说明。"
2. **数值级验证**："对论文的 [公式/图表 Y] 构造独立验证：解析推导 vs 有限差分/重算，报告误差；验证失败先怀疑理解再怀疑论文。"
3. **三方参数对照**："同一组设置在 论文原文 / 作者官方代码 / 我安装的库 三方间逐项对照，每项给三处来源定位。"

配套的核查原则见 README §5；本会话的失败与降级实例见 workflow/run_log.md（翻车 1–3 与网络降级路径）。
