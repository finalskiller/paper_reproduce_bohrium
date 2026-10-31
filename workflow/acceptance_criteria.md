# 验收判据（正式化记录）

> **性质声明（诚实性）**：本文件是 2026-10-31（v1.2）对原实践（2026-10-23，见 `workflow/run_log.md`）所用验收标准的**事后正式化**，不是运行前的预注册——原会话按 run_log 的过程执行并按这些口径判定，但当时未把判据独立成文。为避免误述，本文不使用"预注册"一词指代 2026-10-23 的工作。
> 作为对照，**§3 的干净目录复跑（2026-10-31）是真预注册**：判据先于复跑写定并提交（见 git 历史 v1.1.2 之后的 commit 顺序），复跑只是执行。

## 1. 各案例验收判据（原实践口径，正式化）

| 案例 | 判据编号 | 通过标准 | 判定用文件 |
|---|---|---|---|
| Figure 1 反推 | F1-P1 | 三锚点校准参数唯一确定：s·18(1−ρ)=14 且 s·18ρ=4 ⇒ s=1, ρ=2/9 | `results/fig1_calibration.json` |
| Figure 1 反推 | F1-P2 | 复现图与原图逐面板结构对照 ≥2 个 MATCH（SNE/t-SNE 必须命中） | `results/fig1_comparison.png` |
| Figure 1 反推 | F1-P3 | σ 不可辨识性有敏感性说明 | README §2.6 局限 1 |
| 梯度验证 | G-P1 | SNE/UNI-SNE(精确式)/t-SNE 三条解析梯度 vs 有限差分：最大相对误差 < 1e-5 | `results/gradient_validation.json` |
| 梯度验证 | G-P2 | UNI-SNE 弹簧形式保留为显式 FAIL 用例（相对误差 > 1），作为发现证据 | 同上 |
| 参数对照 | D-P1 | 6 组参数三方对照，每行有三处来源（页码/文件/行号） | `code/parameter_drift.json` |
| MNIST 实验 | M-P1 | trustworthiness(k=12) ≥ 0.98（两配置） | `results/fig2a_metrics.json` |
| MNIST 实验 | M-P2 | 嵌入上 1-NN 5 折 ≥ 0.90（两配置） | 同上 |
| MNIST 实验 | M-P3 | 抽样标签存档（`results/mnist_sample_labels.npy`）且 seed 公开（42） | 同上 |
| 社区溯源 | I-P1 | issue 分析的每个结论都能定位到 sklearn 1.9.1 源码具体位置 | `issuescout_run/*.json` |
| 玻尔实测（v1.1 新增） | B-P1 | 平台回答逐字存档，不转述 | `workflow/bohrium_session/*.txt` |
| 玻尔实测（v1.1 新增） | B-P2 | 每条与论文相关的事实性陈述都经原文核查并标注对/错 | README §4.3 核查表 |
| 离线复现（v1.1 新增） | R-P1 | 无网络环境三步复现全部可执行且输出与存档一致 | §3.2 + `author_code/mnist6000_sample.npz` |

## 2. 原实践判定结果（按上述口径回放）

F1-P1 ✓（s=1, ρ=2/9）/ F1-P2 ✓（(a)(c) MATCH，(b) PARTIAL）/ F1-P3 ✓ / G-P1 ✓（≤1.1e-8）/ G-P2 ✓（9.26 显式 FAIL）/ D-P1 ✓（6 组×3 来源）/ M-P1 ✓（0.9877, 0.9867）/ M-P2 ✓（0.936, 0.941）/ M-P3 ✓ / I-P1 ✓（两处注释引用 #18018 等）/ B-P1 ✓ / B-P2 ✓（两处错误定位）/ R-P1 ✓（六项指标完全一致）。

## 3. 干净目录复跑（2026-10-31，真预注册）

**预注册判据（复跑前写定）**：在一台无本仓库 git 历史、无 pip 缓存、断网的目录中，仅凭材料包内容执行 §3.2 的①②③，须满足：

- C-R1：①② 退出码 0，`fig1_calibration.json` 参数 s=1.0、ρ=2/9±0.01，`gradient_validation.json` 三行 PASS 且相对误差 < 1e-5；
- C-R2：③ 在 `MNIST_SOURCE=sample` 下退出码 0，重算的六项指标与 `results/fig2a_metrics.json` 存档完全一致（KL 差 < 1e-9，其余相等）；
- C-R3：全程无任何网络请求（hosts 屏蔽或离线环境）。

**复跑记录**：见 `workflow/clean_replay_20261031.md`（含命令、输出、逐项判定）。
