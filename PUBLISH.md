# 一键发布到 GitHub（给仓库所有者的操作说明）

本仓库已做好全部提交内容。你只需：在 GitHub 上新建一个**空**公开仓库（不要勾选初始化 README/license），然后在本目录执行：

```bash
cd ai-paper-reading-tsne
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
# 建议打一个 Release:
git tag -a v1.0 -m "AI 文献阅读分享:t-SNE (JMLR 2008) 图表反推、公式验证与参数漂移核查"
git push origin v1.0
# 然后在 GitHub 仓库页 Releases -> Draft new release -> 选择 tag v1.0 -> Publish
```

推送后把仓库 URL（形如 `https://github.com/<你的用户名>/<仓库名>`）填入：
1. `提交说明.md` 的"作品链接"行
2. `outputs/deliverables/submission.txt`（一行 URL）

再重新运行 `python build_materials.py` 更新材料包，最后在平台提交。

> 已提交内容包含 `.gitignore`：数据缓存、sklearn 源码快照、论文 PDF 本地副本均不入库（获取/重建步骤都在 README 与 workflow/run_log.md 中）。
