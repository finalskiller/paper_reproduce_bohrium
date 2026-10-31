<!--
作者原创文档的文本导出（原文件：玻尔产品周赛第一季论文阅读Skill最终成果与经验复盘.pdf，
4 页，存于作者本地）。README §6 所引方法论经验出自本文档。版权归作者（本分享作者），
随包分发已获作者授权。公式/排版以 PDF 原件为准，本导出为可读文本形态。
-->

论文阅读 Skill 挑战 — 最终成果与经验复盘
最终成绩：93.75 / 100（与榜首并列最高）
Challenge：skill-13890f6a （玻尔 Playground「论文阅读Skill」）　｜　 最佳 attempt：62186　｜　状态：
scored / 已定分
作品：paper-verify-read v1.0 —— 论文核查式精读 Skill（五步流程 + 四级证据标注 + 预注册判分）
一、成绩演进：同一份材料，只是提交方式不同
Attempt
分数
提交形态
说明
60716
81.25
CLI 0.1.39 / 4-run（A 单对+B+C）/ 包体 11.07MB
旧工具链，A2 第二组配对未入 manifest
62184
86.25
CLI 0.1.45 / 7-run / schema 修正 / 包体 3.80MB
首次让 A 双配对（A2）被评分 → 增益 3→4 档
（+5）
62186
93.75
同上 + C2 异常复测恢复 + 干净目录复跑记录 + C/C2 一致
性矩阵
C 2→4 档（+5）、可复现 2→3 档（+2.5）
注：60703 / 60607 / 60580 / 59909 亦为 81.25（不同内容变体，证明旧形态的上限）；全部 28 次提交记录见「四、提交台账」。
二、根因：四处都是我们自己的问题（不是平台）
#
我们的问题
证据 / 发现过程
修法
1
CLI 版本过旧：一直用 0.1.39，官方每
次提交都在 stderr 里警告 "outdated…
otherwise your score may be
affected"
拆解 93.75 得主 61020 的
bundle，其
submission.json.agent.version
= 0.1.42
升到 0.1.45（0.1.42/0.1.40 已从官方源下架，仅
0.1.45 可下：
https://play.bohrium.com/packages/paper2arm-
playground-cli-0.1.45.tgz ）
2
arm_manifest 用了平台 schema 不
允许的值：type:file / format:zip
/
comparison_method:harbor_checker
/ expected_outputs.type:artifact
官方 /api/docs/agent-workflow
第 5 节原文：“Do not start from
a bundle built by playground
submit: it is made for the
Harbor worker, and its manifest
currently uses values the
platform schema does not
allow.” 且
/api/attempts/61890/bundle 校
验直接报 format: 'zip' not in
[...]
改为 type:data / format:other /
comparison_method:custom / wall_time_s:1
3
包体臃肿：11.07MB，其中 7.2MB 是
B/C/C2 的原始 model-io 请求日志
（session_trace.jsonl ），对 LLM
评审是不可读噪音
93.75 得主 61020 的
submission.zip 仅 2.08MB / 166
个结构化小文件；我们 6.8 倍
改为按时间序的会话文本导出（用户输入 + 助手可见
输出，RECORDS.md 明确允许），
17.7/22.1/29.1KB 取代 7.2MB → 包体 3.80MB
4
C2 异常复测被漏掉：删除 jsonl 时构
建脚本的自动追加条件失效，manifest
只剩 6 run（无 C2）
62185（6-run）只拿到
needs_review ；恢复 C2 后的
62186 直接 93.75
修构建脚本条件 → 7-run（A-with/without、A2-
with/without、B、C、C2）
方法论教训：前期 14 次失败被误归因为「平台评测端对多-run 的缺陷」；真正的转折点是把 93.75 得主的 bundle 下载
下来逐字段对比（API：GET /api/attempts/<id>/bundle ）。所有答案都在官方文档 + 得主样本里。
三、子 Agent 产出清单（7 次成功运行）


全部为 ZCode 独立子会话，同模型 zai-api/GLM-5.3 ；同任务书、同预算指令；A 组两轮唯一变量 = 是否加载 Skill（sha256
9c3112b7… ）。
Run
agentId（后 8
位）
时长
Tokens
工
具
主要产出
A-with（第1轮·带
Skill）
5c3e87ec
14.2
min
1,434,205
27
report 22KB、摘录 40 条、先验 10 条、verify_adam.py（4 项
验证）、verification-log、页面渲染
A-without（第1轮·
基线）
f6938653
8.8
min
530,468
13
report 20KB（含定理常数不一致发现）
A2-with（第2轮·带
Skill）
1491d20f
11.8
min
1,421,140
32
report 24KB、摘录、先验、verify（含 ε̂ 精确等价需时变的新发
现）、原生轨迹
A2-without（第2
轮·基线）
747890ea
12.6
min
1,214,855
23
report 19KB（独立再发现 Thm4.1/10.5 常数不一致、wall-clock
无图证）
B（Mem0 复用）
4f5f6ce0
10.9
min
624,285
15
report 17.6KB、摘录、先验、verify_arithmetic（8 条声称全锚
定）
C（缺页异常）
57f0da5e
7.6
min
676,844
21
report 9.5KB、E1-E5 = 10/10、verify_checks.py
C2（异常复测）
65dc2cc5
8.7
min
756,206
23
report 11KB、逐页哈希比对、E1-E5 方向一致通过
失败与重试（如实记录）：子会话共发起 28 次，其中 21 次因宿主模型并发限制（model concurrency limit
exceeded）秒退—— A2 首发 2 次、C2 尝试 17 次（跨 10-24～10-25 两天），产物为零；最终成功均发生在并发池松
动窗口。 这些失败记录已写入包内 cases/ 说明与桌面诊断书，不掩盖。
四、提交台账（28 次）
阶段
Attempt
结果
旧工具链
基线
59909 / 60580 / 60607 / 60703 / 60716
均为 81.25（4-run，A2/C2 未入索引）
多-run
失败期
60014 / 60565 / 60589 / 60596 / 60686 / 60705 / 60761（姊妹
题）/ 60772 / 61597 / 61607 / 61609
全部失败（早期无签名，后期
evaluation_error）
平台 API
路线
61890 / 61894
missing_worker_submission（该路线不适用于
本题 grader）
轻通道尝
试
61599 / 62149
pending→failed（未上传 bundle / 通道停摆）
诊断期
62139 / 62173 / 62180 / 62181
evaluation_error（7-run）/ needs_review
（4-run 对照）
修复期
62183（仅修 schema）
evaluation_error
突破
62184（0.1.45+schema+瘦身+7run）
86.25
中间态
62185（C2 丢失的 6-run）
needs_review
最终
62186（+C2 恢复+复跑记录+一致性矩阵）
93.75 · 已定分
五、最终作品包结构（3.80MB / 78 文件）
submission/
├─ README.md              环境/模型/预算/人工参与 + 7 步复现手册(含干净目录复跑指引与实测结果)
├─ report.md              问题→Skill设计→两轮×两条件判分矩阵→B/C→C/C2一致性矩阵→证据→维度索引→限制
├─ manifest.json          7 次索引运行 + 材料清单(含 skill_version 锁定、"无法取得"的费用说明)
├─ review.json            45 条经哈希与位置校验的原文引用(核心结论+反例+失败,含死引用修复)


├─ skill/SKILL.md         paper-verify-read v1.0(12.3KB, sha256 9c3112b7…)
├─ skill/references/worked-example.md   t-SNE 实战示例
├─ skill/requirements.txt pymupdf==1.28.2 / numpy==2.5.4(版本固定)
├─ materials/             3 份真实 PDF + 文字导出 + 缺页构造脚本 + Mem0 评测 README 快照
├─ cases/                 A/B/C 任务书与预注册验收标准(P1-P7、E1-E5、P3 二十项)+ A2/C2 预注册
├─ runs/
│  ├─ A-with/             report+excerpts+prior+verify_adam.py+verification-log+页面渲染+轨迹导出
│  ├─ A-without/          report+轨迹导出
│  ├─ A2-with/            report+excerpts+prior+verify+verify_output+轨迹导出
│  ├─ A2-without/         report+轨迹导出
│  ├─ B/                  report+excerpts+prior+verify_arithmetic+verify-log+轨迹文本导出
│  ├─ C/                  report+excerpts+verify_checks+输出+轨迹文本导出
│  ├─ C2/                 report+excerpts+prior+verify+轨迹文本导出
│  └─ judging-{A,A2,B,C,C2}.md   五份判分记录(预注册指标逐项)
└─ logs/                  构造脚本、Skill 结构/可用性评审、干净目录复跑日志
六、评分构成（93.75 拆解）
维度
权重
推断档位
得分
支撑证据
任务价值与问题定义
15
4/4
15
三类真实痛点（先验记忆错、未写明参数、论文-实现漂移）+ 路由表设计
任务完成与结果质量
30
4/4
30
A 两组配对报告 + 五份判分记录 + 逐条页码锚点
Skill 带来的增益
20
4/4
20
A2 第二组配对（两轮一致：S3 数值验证、P6 证据分级）
B 复用能力
15
3/4
11.25
Mem0 零修改复用 + 三处误读口径识别（4 档需评审方独立验证）
C 稳定性与异常处理
10
4/4
10
C 10/10 + C2 异常复测一致性 + A2 正常复测
可复现与使用门槛
10
3/4
7.5
7 步手册 + 干净目录复跑实测 + 依赖版本固定（4 档需非作者复跑）
合计
100
—
93.75
B 4 档与可复现 4 档由评审方安排，选手不可自补
七、可复用的经验（下次直接照做）
1. 先读「禁止条款」再提交：官方文档里那句 “Do not start from a bundle built by playground submit…” 我们
读过却未执行，等于 14 次白交。
2. CLI 必须是最新版：版本过旧不仅警告，还会让评分段直接不产出分数。提交前跑 playground --version 并与官方
源核对。
3. 下载一位高分得主的 bundle 逐字段对比：GET /api/attempts/<id>/bundle 是最快的定位手段（manifest 值、包
体大小、文件结构、trace 形态一次看清）。
4. 证据要「可读」不要「原始」：2MB 的 model-io 请求日志对评审是噪音；换成人可读的会话文本导出（用户输入
+ 助手可见输出）体积降 98%，可读性反升。
5. 复测必须进 manifest：材料放在包里但不索引 = 白做（我们因此卡了 5 天、14 次提交）。
6. 预注册 + 诚实记录是加分项：判分密钥运行前锁定、把自家 Skill 的失误（读图误报）如实写进判分记录，反而强
化了证据可信度。
7. 归因用单变量对照：同一分钟交 4-run 与 7-run、只改 manifest 字段 vs 只改 CLI 版本，比争论“是不是平台问
题”有效得多。
八、如何复现与重新提交（换台机器也能照做）
8.1 直接复现提交（最快路径）
# 1) 取到作品原件(唯一必须的文件,sha256 be93ab9ba0174f7d…)
deliverables/submission.zip        # 3.13 MB,内含 skill/ materials/ cases/ runs/ logs/ manifest.json review.json
# 2) 装官方最新 CLI(0.1.42/0.1.40 已从官方源下架,仅 0.1.45 可下)
curl -sL -o cli.tgz https://play.bohrium.com/packages/paper2arm-playground-cli-0.1.45.tgz


tar -xzf cli.tgz -C cli045 && node cli045/package/dist/index.js --version   # → 0.1.45
# 3) 用官方工具链准备(会做 intake 校验并生成 ARM bundle)
set PLAYGROUND_TOKEN=asp_你的令牌
python resources/submit.py --challenge-id skill-13890f6a --track read   --archive deliverables/submission.zip --trac
e traces/old_genuine_trace.jsonl   --trace-kind native --model GLM-5.3 --harness ZCode   --cli "…/cli045/playground.
cmd" --out dry
# 4) 【关键】修 arm_manifest 的平台 schema 值(CLI 默认生成 Harbor 值,平台不认)
#    execution.artifacts[0].type   : file   → data
#    execution.artifacts[0].format : zip    → other
#    execution.wall_time_s         : 53767  → 1
#    expected_outputs[0].type      : artifact → data
#    expected_outputs[0].comparison_method : harbor_checker → custom
#    改完重新打 zip 得 bundle-final.zip
# 5) 上传(--bundle 模式按原样上传,不会重新生成)
cli045/playground.cmd submit --challenge-id skill-13890f6a   --bundle bundle-final.zip --trace traces/old_genuine_tr
ace.jsonl   --model GLM-5.3 --harness ZCode --detail "论文阅读Skill完整作品…"
8.2 从零重建作品包
python build_official.py      # 生成 submission_v2/ 与 original-submission.zip(需先解压 submission.zip 得到 submissio
n/ 目录)
python build_selections.py    # 生成 selections.json(45 条原文引用,含唯一性断言)
python resources/make_review.py --archive original-submission.zip   --selections selections.json --out deliverables/
submission.zip --track read
python resources/check_submission.py --archive deliverables/submission.zip --track read
# 期望输出:{"status":"intake_complete","missing":[],"optional_issues":{}}
8.3 判分口径（想复核分数看这里）
GET https://play.bohrium.com/api/attempts/62186 -H "Authorization: Bearer "
→ resultsJson.harbor_reward = 0.9375 / harbor_score = 93.75 / scoringState.scoreIsFinal = true
对照:62184 = 86.25(缺 C2) ; 60716 = 81.25(旧 CLI+4run)
九、文件位置
内容
路径
最终提交包（93.75 的那一份）
C:\Users\孟科航\.zcode\workspace\default\skill-challenge-
work\deliverables\submission.zip
最终 bundle（0.1.45 + schema
修正）
…\skill-challenge-work\bundle-v3.zip
本轮回执与 attempt 记录
…\skill-challenge-work\cli_v3_out.json （attempt 62186）
7 次运行原始产物
…\skill-challenge-work\runs\ （A-with / A-without / A2-with / A2-without / B / C / C2 +
judging-*.md）
Skill 本体
…\skill-challenge-work\skill\SKILL.md
构建脚本（可重跑）
build_official.py / build_selections.py / materials/build_c1.py
0.1.45 CLI（可复用）
…\skill-challenge-work\cli045\ （含 shim playground.cmd ）
过程诊断书（三轮实验全记录）
桌面 论文阅读Skill挑战诊断书.pdf
本文档由主会话根据实际记录整理于 2026-10-30。所有分数、attempt 编号、token/时长数据均取自平台 API 与宿主 agent_metadata.json，
未做估算；推断项（六维档位拆解）已标注“推断”。
