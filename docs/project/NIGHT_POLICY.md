# Night Autonomous Research Policy

本政策定义人工预授权 Research Envelope 内的夜间自治模式。所有工作仍受
`AGENTS.md`、`ACTIVE_RESEARCH_QUESTION.md`、统计边界和资源上限约束。

## 夜间允许

- Research Envelope 内生成和淘汰子 idea；
- 文献核查；
- read-only 分析；
- checkpoint-only 分析；
- 低成本 exploratory pilot；
- 预授权预算内实验；
- 多 seed / budget 验证；
- prediction test；
- 一次合法 rescue；
- 自动切换 candidate；
- 更新 registry、queue、state 和 report。

任何科学分析或实验仍必须先创建并 commit immutable experiment plan。

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
