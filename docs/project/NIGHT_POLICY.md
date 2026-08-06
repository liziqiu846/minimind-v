# Night Autonomous Research Policy

本政策定义人工预授权 Mission Envelope 内的夜间自治模式。所有工作仍受
`AGENTS.md`、`ACTIVE_RESEARCH_QUESTION.md`、统计边界和资源上限约束。

## 夜间允许

- Mission Envelope 内生成和淘汰子 idea；
- 根据失败和新现象持续进行 targeted literature search；
- 按记录规则自主切换 Active Research Question；
- read-only 分析；
- checkpoint-only 分析；
- 低成本 exploratory pilot；
- 满足下述全部授权条件的阶段三 mechanism-intervention training；
- 预授权预算内实验；
- 多 seed / budget 验证；
- prediction test；
- 理论严格化、主动反例搜索和 development 数据上的
  `PROVISIONAL_ALGORITHM_TEST`；
- 一次合法 rescue；
- 自动切换 candidate；
- 更新 registry、queue、state 和 report。

任何科学分析或实验仍必须先创建并 commit immutable experiment plan。

## 阶段三最小训练授权

训练只可用于证实或证伪已通过理论筛选的 scientific idea，不得作为阶段四正式
训练算法主实验。自动启动训练必须同时满足：

1. candidate 已登记且机制明确为 VLM-specific；
2. 已形成可证伪 prediction；
3. existing checkpoint / artifact 无法充分区分该机制；
4. 新训练能直接区分至少两个竞争解释；
5. intervention 只改变与假设直接相关的主要因素；
6. immutable plan 已创建并 commit；
7. 不使用 final confirmation set；
8. 不改变 Mission Question、核心泛化对象或数据统计关系；
9. 不超出预授权资源。

checkpoint-only 足够时不得训练。训练默认仅比较 baseline 与 hypothesis-specific
intervention，不做 hyperparameter sweep：

1. 先运行 1 个 paired seed；单 seed positive 只用于机制和运行核查，不能成为科学
   结论。若方向明显违背预注册 prediction 且无实现或测量问题，立即
   `REJECT_IDEA`。
2. paired pilot 与 prediction 一致时，保持数据、intervention、配置、指标和判定
   标准不变，只补两个 seed 至 total 3 seeds。
3. 每个 candidate 最多 2 conditions × 3 seeds = 6 model trainings。三 seed 后必须
   判为 `PROMISING` / `CONCLUSION_CANDIDATE`、`REJECT_IDEA` 或真正的
   `INCONCLUSIVE`；`INCONCLUSIVE` 不自动增加训练预算。

rescue 仅限已证明的 implementation bug、corrupted data、wrong checkpoint、
preprocessing mismatch、metric implementation error 或 job failure。effect 太小、
p-value / correlation 不佳或 seed 方向不支持均不是 rescue。禁止通过换参数、
metric、proxy、数据 subset、判定标准或继续加 seed 来维持失败 idea。

不得因为“下一步需要训练”自动结束夜间 cycle。符合上述规则的
`PROVISIONAL_ALGORITHM_TEST` 可以在 development / selection / ordinary held-out
数据上继续；官方阶段标签仍由人工决定。只有需要明显扩大当前服务器资源等级或
触发其他真正 `HARD_STOP` 条件时才停止。

## REVIEW_QUEUE 不停机

除 `HARD_STOP` 外，重要事项进入 `REVIEW_QUEUE.md` 后，冻结相关结论并继续
Mission Envelope 内其他授权研究。得到 `CONCLUSION_CANDIDATE` 后继续理论、
反例、prediction 与必要 robustness，不把 queue 或漂亮结果视为停止点。

## HARD_STOP

只有以下情况立即停止新的科学实验和研究方向扩展：

1. 必须访问 final confirmation set 才能继续；
2. 必须明显扩大当前服务器资源等级，例如切换到远大模型或大量 GPU；
3. 发现数据泄漏或可能污染独立确认集；
4. 需要修改 Mission Question 或项目最终目标；
5. 需要重新定义核心总体风险、泛化对象、核心独立性假设或 train / selection /
   confirmation 的统计关系；
6. 出现不可恢复的仓库或数据安全风险；
7. 已无服务器可用资源；
8. 外部系统强制终止。

## 夜间结束条件

autonomous session 只在以下情况结束：

- 触发上述 `HARD_STOP`；
- 外部 session / 服务器终止；
- 用户回来人工接管。

candidate pool、Active Research Question 或多批 idea 失败时，总结共同失败原因，
根据失败形成 targeted literature question，生成下一批 candidate 并继续。动态维护
1 个 `ACTIVE`、2--4 个 `NEXT` 和其余 `BACKLOG`；`NEXT` 少于 2 时自动补充。

## 夜间报告

持续更新 `docs/project/NIGHTLY_REPORT_<date>.md`，至少包含：

1. 检查了什么；
2. 淘汰了什么；
3. 最有希望的 idea；
4. 最重要证据；
5. 当前不能推出什么；
6. REVIEW_QUEUE；
7. 当前唯一主要下一步；
8. 新文献、running experiments、provisional theory / algorithm 与 commits。

Nightly report 是持续日志，不是 cycle 完成或停止信号。
