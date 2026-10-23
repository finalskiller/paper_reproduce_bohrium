# 逐条核查记录

标注约定：**【原文】**=论文可直接核对（页码见 `paper_evidence/excerpts/key_excerpts.md`）；**【AI】**=AI（本会话 agent / DeepSeek / 视觉模型）输出；**【判断】**=我的解读，需证据支持；**【实测】**=本仓库代码真实运行结果。

| # | 关键解读 | 证据类型 | 核查结果 |
|---|---|---|---|
| V1 | Figure 1 是三幅梯度热图（横轴高维距离、纵轴低维距离、正=吸引） | 【原文】p.2586 图题+正文 | ✅ AI 最初凭记忆称其为"核函数曲线对比"——**错**，已纠正 |
| V2 | SNE 面板锚点：最大引力≈19、最大斥力≈1 | 【原文】p.2586 | ✅ 复现件为 18.0 / −0.45（s=1, 网格角点）；19 读作色标约数，详见 V5 |
| V3 | UNI-SNE 色标 −4…14；t-SNE 色标 −1…1 | 【原文】PDF 原图刻度（裁剪件） | ✅ 三锚点联立得 s=1、ρ=2/9；复现 UNI-SNE 端点 −4.5/+13.5 |
| V4 | 三条梯度公式（Eq.3 梯度式、Eq.5、UNI-SNE 精确式）数学正确 | 【实测】`results/gradient_validation.json` | ✅ 有限差分对照 ≤1.1e-8；弹簧形式 UNI-SNE 9.26（预期 MISMATCH，保留为证据） |
| V5 | "≈19"的读法：三锚点在 1 个单位内互斥（19 vs 14/4 不能同时精确命中） | 【判断】+【实测】 | ✅ 解析：s·18(1−ρ)=14 且 s·18ρ=4 ⟹ s=1 ⟹ SNE 角点=18.0；若强取 19 则 UNI-SNE 吸引端=15≠14 |
| V6 | Figure 1(b) 用弹簧约定而非混合核精确梯度 | 【判断】 | 支持证据三条：①色标 −4/14 仅弹簧形式可同时命中；②【原文】p.2587"UNI-SNE 斥力与低维距离成正比"（精确式大 dl 处衰减）；③V4 中精确式与弹簧式数值可分 |
| V7 | 论文优化参数（exagg ×4/50、T=1000、动量 0.5→0.8@250、η=100+Jacobs、init N(0,1e-4)、PCA→30、MNIST 6000、Perp=40） | 【原文】p.2587–2589 | ✅ 逐条摘录见 excerpts §4 |
| V8 | 作者 Python 代码与论文的 6 处漂移 | 【实测】author_code/tsne_python/tsne.py 逐行 | ✅ 见 `code/parameter_drift.json`（如 init=N(0,I)、exagg 撤销于 iter 100、eta=500、PCA→50） |
| V9 | sklearn 1.9.1 默认值与实现细节 | 【实测】`inspect.getsource`（本机安装版） | ✅ exagg=12/250、auto=N/12/4 下限 50、random init=1e-4·randn、动量 0.5→0.8、`init='pca'` 重标定 |
| V10 | sklearn 的 12/250 与 pca-init 重标定源于 issue #18018 | 【实测】sklearn 源码两处注释引用 "#18018"；【AI】issuescout 分析交叉确认 | ✅ issue 正文任务清单与源码现状一一对应 |
| V11 | exaggeration=12 的学术出处是 Kobak & Linderman | 【AI】issuescout 分析引用 issue 未完成项；【判断】 | ⚠️ 部分核实：issue 原文确列"Consider … Kobak & Linderman"为未完成任务；"12 这个值来自该论文"的强断言未逐页核对 K&L 原文，README 表述为"未完成项指向后续研究"，不做超出证据的声明 |
| V12 | sklearn auto 学习率下限与 openTSNE 不一致 | 【AI】issuescout（DeepSeek）输出 | ⚠️ 记录为"分析发现"，未独立核对 openTSNE 源码；如需引用请自行核对 openTSNE 文档 |
| V13 | MNIST 复现结构（10 簇分离、1/7 与 3/5/8 邻近）与论文一致 | 【实测】+【原文】p.2590 原图对照 | 结构性对照（论文未发布坐标，无法数值级对照，已在 README §2.6 声明） |
| V14 | 视觉模型对热图的几何描述 | 【AI】 | ⚠️ 仅作参考：与数学矛盾的描述一律以公式+论文文字为准（本会话中视觉描述出现过 t-SNE 吸引区位置偏差） |
| V15 | 本分享未使用玻尔科学空间执行 | 【实测】 | ✅ 如实声明，README §4.3 仅提供迁移指南 |

## 三区分原则的落实

- 所有【原文】条目在 `paper_evidence/excerpts/key_excerpts.md` 有页码级引文；
- 所有【AI】条目保留原始输出（issuescout JSON、视觉分析在日志中的引用位置）；
- 所有【实测】条目可用 `code/` 三段脚本重跑，且 `results/` 留有原始输出。
