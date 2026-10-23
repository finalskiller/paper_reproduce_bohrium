# issuescout 分析记录（sklearn issue #18018）

## 这是什么

对 scikit-learn 仓库 issue
[#18018 "t-SNE default parameters and clarifying documentation"](https://github.com/scikit-learn/scikit-learn/issues/18018)
的一次真实 Agent 深度分析（2026-10-23 执行）。分析由本地工具 issuescout
（DeepSeek Chat 驱动，含 12 次真实代码检索/读取工具调用）完成。

## 文件说明

| 文件 | 内容 |
|---|---|
| `scikit-learn__scikit-learn__18018.json` | issuescout 的原始分析输出（摘要/根因/受影响文件/建议/风险/置信度/tokens 计数），未做任何修改 |
| `issue_18018_offline_cache.json` | 分析的输入之一：issue 正文的离线缓存（由网页阅读器从 GitHub 公开页面抓取，按 issuescout 缓存格式写入） |

## 如何核查（不需要 issuescout 也能做）

1. 打开上面的 issue 链接（或 `issue_18018_offline_cache.json`），看正文任务清单；
2. 对照 scikit-learn 1.9.1 源码 `sklearn/manifold/_t_sne.py`：
   - `__init__` 中 `learning_rate="auto"`、`init="pca"` 默认值；
   - `X_embedded = X_embedded / np.std(X_embedded[:, 0]) * 1e-4`（搜索 `18018`，注释直接引用该 issue）；
   - `self.learning_rate_ = X.shape[0] / self.early_exaggeration / 4`（同样注释引用 #18018）。
3. 分析输出中的每条"受影响文件"论断都可按此方式独立复核。

## 如需复跑（需要 issuescout 工具，源码未公开，本节仅说明当时流程）

```text
1. codeload.github.com 下载 scikit-learn 1.9.1 tarball(7.7MB) -> 解压 -> git init + remote add origin + commit
2. 将 issue_18018_offline_cache.json 内容写入 ~/.issuescout/cache/scikit-learn__scikit-learn.json
3. 在 issuescout 仓库目录: npm run cli -- analyze 18018 <sklearn 快照目录>
   (工具对 GitHub API 的访问在本机不可达,issue 列表读缓存、评论返回空,均属该工具的既定降级行为)
4. DeepSeek 分析完成后输出写入 ~/.issuescout/analyses/,即本目录保存的 JSON
```

## 分析结论摘要（人工核对后采纳的部分）

- issue 五项已勾选任务在 1.9.1 源码中全部落地，其中两处有注释级引用（已独立核实 ✅）；
- 未完成项指向 Kobak & Linderman (2021) 对初始化与 early exaggeration 的建议（与 issue 原文一致 ✅）；
- "sklearn `auto` 学习率下限 50 与 openTSNE `max(200, N/exagg)` 不一致"为模型输出（未独立核对 openTSNE，标记 ⚠️ 见 workflow/verification.md V12）。
