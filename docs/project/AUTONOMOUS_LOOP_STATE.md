# Autonomous Loop State

```text
MODE: AUTONOMOUS_RESEARCH
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: COMP-01
CURRENT_ROUND: 1
CURRENT_STATE: 18_MODEL_SCORING_RUNNING
RUNNING_JOB: COMP-01_MATRIX_BACKGROUND
LAST_PLAN: experiments/plans/COMP-01_round1.md
LAST_RESULT: experiments/results/COMP-01_round1/smoke/M2-current-seed-43101/run_receipt.json
GPU_HOURS_USED_THIS_CYCLE: 0
ACTIVE_QUEUE: COMP-01
NEXT_QUEUE: XMC-01-model-retention,VISCOND-01
BACKLOG_QUEUE: OBJ-01,COVER-01
WINOGROUND_ACCESS: blocked_by_access
RESOURCE_NOTE: GPU-1-5-7-idle-at-last-audit;disk-available-48.84GB
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
