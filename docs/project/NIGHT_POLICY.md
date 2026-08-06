# Night Autonomous Research Policy

本政策定义人工预授权 Research Envelope 内的夜间自治模式。所有工作仍受
`AGENTS.md`、`ACTIVE_RESEARCH_QUESTION.md`、统计边界和资源上限约束。

## 夜间允许

- Research Envelope 内生成和淘汰子 idea；
- 文献核查；
- read-only 分析；
- checkpoint-only 分析；
- 低成本 exploratory pilot；
- 满足下述全部授权条件的阶段三 mechanism-intervention training；
- 预授权预算内实验；
- 多 seed / budget 验证；
- prediction test；
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
8. 不改变一级科学问题、核心泛化对象或数据统计关系；
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

不得因为“下一步需要训练”自动结束夜间 cycle。只有训练超出上述最小授权、需要
明显扩大模型/数据/算力、实际进入阶段四正式算法主实验，或触发其他 `HARD_STOP`
条件时，才停止并请求人工决定。

## REVIEW_QUEUE 不停机

除 `HARD_STOP` 外，重要事项进入 `REVIEW_QUEUE.md` 后，冻结相关结论并继续
Research Envelope 内其他授权研究。

## HARD_STOP

只有以下情况立即停止新的科学实验和研究方向扩展：

1. 需要改变一级科学问题；
2. 需要改变项目最终目标；
3. 需要重新定义核心总体风险或泛化对象；
4. 需要改变核心独立性假设；
5. 需要改变 train / selection / confirmation 的统计关系；
6. 需要访问 final confirmation set；
7. 需要明显扩大 GPU、模型规模、数据规模或总训练预算；
8. 准备正式进入阶段四；
9. 准备启动由理论规律导出的正式训练算法主实验；
10. Research Envelope 本身被稳定证据否定，需要重新选择一级问题。

## 夜间结束条件

任一条件满足后，停止新的科学实验，只整理报告：

- 一个 autonomous cycle 已测试 5 个 idea；
- 得到一个完成 prediction test 的 `CONCLUSION_CANDIDATE`；
- 连续 3 个 candidate 为 `INCONCLUSIVE`；
- 下一步触发 `HARD_STOP`；
- 预授权资源耗尽；
- 已无新增可靠信息。

## 夜间报告

最终生成 `docs/project/NIGHTLY_REPORT_<date>.md`，只包含：

1. 检查了什么；
2. 淘汰了什么；
3. 最有希望的 idea；
4. 最重要证据；
5. 当前不能推出什么；
6. REVIEW_QUEUE；
7. 唯一推荐下一步。
