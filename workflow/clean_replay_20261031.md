# 干净目录复跑记录（2026-10-31，真预注册）

> 判据 C-R1/C-R2/C-R3 于复跑前写定（`workflow/acceptance_criteria.md` §3，先于执行提交到 git）。
> 复跑环境：从 `materials.zip`（v1.1.2，45 文件）解压到全新空目录，无 git 历史、无缓存；
> 进程级禁用网络（`socket.getaddrinfo` / `socket.create_connection` / `urllib.request.urlopen`
> 替换为拦截器，任何网络尝试都会抛错并被计数）。
> 执行器：`run_replay.py`（随包提供，任何人可重放）；原始输出：`replay_output.log`。

## 命令序列

```
# 全新目录
python -c "zipfile.ZipFile('materials.zip').extractall('.')"   # 45 个文件
cp results/fig2a_metrics.json results/fig2a_metrics_original_archive.json  # 重跑会覆盖，先备份原档
python run_replay.py                                            # 三步 + 三判据
```

## 结果（replay_output.log 摘录，逐项判定）

| 判据 | 内容 | 结果 |
|---|---|---|
| C-R1 | ①② 退出码 0；scale=1.0、ρ=0.222222（=2/9）；三条 exact 梯度 PASS、最大相对误差 1.04e-8 < 1e-5；UNI-SNE 弹簧形式显式 FAIL 保留 | **PASS** |
| C-R2 | ③ 退出码 0（`MNIST_SOURCE=sample` 离线样本）；重跑 KL 1.5138412714004517 / 1.5501009225845337 与原始存档**逐位一致** | **PASS** |
| C-R3 | 全程无网络请求（拦截器计数 0——脚本自身连尝试都没有发起） | **PASS** |

失败清单：无。

## 说明

1. 本次复跑同时覆盖了 README §3.2 "零网络复现路径" 的全部声明——此前该声明基于本机验证，本次在**从材料包解压的全新目录**中再次成立。
2. 复跑产生的 `results/fig1_calibration.json`、`results/gradient_validation.json`、`results/fig2a_metrics.json` 与包内存档一致（重跑前已备份原档用于 C-R2 对照）；`replay_output.log` 保留完整输出。
3. 与第一次提交（Attempt 62235/62237/62280）所用包的差异：v1.1.2 起材料包自带离线样本 npz，本次复跑不依赖任何下载。
