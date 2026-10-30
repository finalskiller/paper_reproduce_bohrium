# -*- coding: utf-8 -*-
"""构建提交材料包 outputs/deliverables/{materials.zip, submission.txt}。

用法:
    python build_materials.py https://github.com/<user>/<repo>   # 有作品链接时
    python build_materials.py                                    # 预检模式(链接待填)

材料包结构(根目录含 提交说明.md,其余与公开仓库一致,排除 .git/大文件/所有者内部文件):
    提交说明.md  README.md  trace.md  code/  paper_evidence/  author_code/(核心)
    results/  workflow/  issuescout_run/(不含 sklearn 源码快照)
"""

import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))

EXCLUDE_DIRS = {
    ".git", "outputs", "data_cache", "paper_src", "node_modules",
    "__pycache__", "__MACOSX",  # __MACOSX: 作者官方 zip 内的 macOS AppleDouble 垃圾文件
}
EXCLUDE_FILES = {
    "build_materials.py",      # 打包脚本本身(仓库中保留,材料包不需要)
    "PUBLISH.md",              # 所有者操作说明
    "提交说明.md",              # 单独写入 zip 根,避免双层
    ".gitignore",
    # 约 31MB 纯文本数据(作者官方 tsne_python.zip 解包副本),与包内 tsne_python.zip
    # 内容完全重复,且 fig2a_mnist.py 运行时自行下载数据、不读取该文件;
    # 240KiB 文本预算装不下,按"去掉重复副本"自材料包排除(公开仓库保留),见提交说明容量条目
    "mnist2500_X.txt",
}
EXCLUDE_PREFIXES = [
    "issuescout_run/repo/",    # sklearn 源码快照(约 200MB,按 run_log §E 可重建)
]


def collect():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        rel_dir = os.path.relpath(dirpath, ROOT).replace("\\", "/")
        if rel_dir == ".":
            rel_dir = ""
        for fn in filenames:
            if fn in EXCLUDE_FILES:
                continue
            rel = f"{rel_dir}/{fn}" if rel_dir else fn
            if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            out.append((os.path.join(dirpath, fn), rel))
    return sorted(out, key=lambda x: x[1])


SUBMISSION_NOTE = """作品链接：{url}
版本：{version}
正文入口：README.md

材料索引：
- 分享正文:README.md(问题与方法/真实案例与结果/复现步骤/来源与贡献/结论)
- 论文关键原文摘录(页码级引文,核查用):paper_evidence/excerpts/key_excerpts.md
- 论文原图裁剪件(Figure 1 / Figure 2 / Figure 2(a),出处与页码见 README §4.1):
  paper_evidence/figures_paper/fig1_paper_full.png, fig2_paper_full.png, fig2a_paper_tsne.png, pdf_page8_full.png
- 复现代码:code/fig1_reproduce.py(Figure 1 解析复现+锚点校准),
  code/validate_gradients.py(梯度公式有限差分独立验证),
  code/fig2a_mnist.py(MNIST 双配置实验),code/parameter_drift.json(三方参数对照表),code/requirements.txt
- 复现真实输出:results/fig1_reproduction.png, fig1_comparison.png(上原图下复现),
  fig1_calibration.json(校准与敏感性), gradient_validation.json(验证记录),
  fig2a_reproduction_A_paper_flavoured.png, fig2a_reproduction_B_sklearn_defaults.png,
  fig2a_comparison.png(四方对照), fig2a_metrics.json, mnist_embedding_*.npy, mnist_sample_labels.npy
- 作者官方实现核查副本:author_code/tsne_python.zip, tSNE_matlab.zip(原始分发包),
  tsne_python/tsne_python/tsne.py, tSNE_matlab/*.m(解包核对件), mnist_tsne.jpg(作者自渲染对照图)
- issuescout 真实分析(DeepSeek,12 次工具调用):issuescout_run/scikit-learn__scikit-learn__18018.json;
  输入与复现说明:issuescout_run/issue_18018_offline_cache.json, issuescout_run/README.md
- 真实过程日志(含失败与降级路径):workflow/run_log.md;逐条核查记录(原文/AI/判断/实测四区分):
  workflow/verification.md;关键文件哈希:workflow/checksums.txt
- 知识提取:trace.md
- 容量说明:author_code/tsne_python/tsne_python/mnist2500_X.txt(约31MB纯文本,作者官方
  tsne_python.zip 解包所得的数据文件)自材料包排除——它与包内 author_code/tsne_python.zip
  内容完全重复,且 fig2a_mnist.py 运行时自行按 README §3.2 下载数据、不读取该文件;
  240KiB 文本预算无法容纳。完整文件在公开仓库同版本同路径可得,其 SHA256 见
  workflow/checksums.txt;包内另保留 mnist2500_labels.txt 与三份 .npy 嵌入结果,
  足以核验 Figure 2(a) 实验的输出结论。

来源与贡献：
- 论文:van der Maaten & Hinton (2008), JMLR 9:2579-2605,开放获取(© 作者,JMLR);
  本包仅含短片段引文与图表裁剪件(核查用途,注明出处),不含论文全文,获取方式见 README §4.1。
- 作者官方代码/示例图:来自 lvdmaaten.github.io/tsne(作者声明 free to use, non-commercial);
  原始 zip 完整保留以供溯源。
- scikit-learn:BSD-3-Clause,参数对照基于本机安装的 1.9.1 源码;issue #18018 为 GitHub 公开内容(抓取存档)。
- issuescout:本分享作者开发的本地工具(源码未公开),本包提供其真实输入与输出,全部结论可在无该工具条件下核查。
- 本次个人贡献:精读流程设计与执行、Figure 1 解析构造与锚点校准方法、UNI-SNE 精确梯度推导与
  "弹簧约定"论证、参数漂移表与 issue 溯源链、issuescout 用法演示;详见 README §4.2。
- 本分享未使用玻尔科学空间执行(如实声明);迁移指南见 README §4.3。
"""


def main():
    args = sys.argv[1:]
    url = args[0] if args else None
    version_arg = None
    if url and "--version" in args:
        version_arg = args[args.index("--version") + 1]
    # 版本 = 指定值或当前 commit 完整哈希
    import subprocess
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    short = sha[:12]
    url_field = url if url else "待填:公开仓库推送后回填(见 PUBLISH.md)"
    version_field = (version_arg if version_arg
                     else (f"commit {sha}" if url
                           else f"commit {short}(推送后建议打 Release v1.0 并回填)"))

    files = collect()
    os.makedirs(os.path.join(ROOT, "outputs", "deliverables"), exist_ok=True)
    zip_path = os.path.join(ROOT, "outputs", "deliverables", "materials.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("提交说明.md", SUBMISSION_NOTE.format(url=url_field, version=version_field))
        for abs_path, rel in files:
            zf.write(abs_path, rel)

    if url:
        with open(os.path.join(ROOT, "outputs", "deliverables", "submission.txt"),
                  "w", encoding="utf-8") as f:
            f.write(url + "\n")

    # 报告
    total_u = sum(os.path.getsize(p) for p, _ in files)
    print(f"files in zip: {len(files) + 1}")
    print(f"uncompressed (approx): {total_u/1e6:.1f} MB")
    print(f"zip size: {os.path.getsize(zip_path)/1e6:.1f} MB")
    print(f"url: {url_field}")
    print(f"version: {version_field}")
    if not url:
        print("(预检模式:submission.txt 未生成;推送后带链接重跑)")


if __name__ == "__main__":
    main()
