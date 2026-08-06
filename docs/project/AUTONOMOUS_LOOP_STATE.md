# Autonomous Loop State

```text
MODE: NIGHT_AUTONOMOUS
ACTIVE_RESEARCH_QUESTION: docs/project/ACTIVE_RESEARCH_QUESTION.md
CURRENT_IDEA: LITMAP-01
CURRENT_ROUND: 1
CURRENT_STATE: PLAN_COMMIT_PENDING
RUNNING_JOB: NONE
LAST_PLAN: experiments/plans/LITMAP-01_round1.md
LAST_RESULT: NONE
GPU_HOURS_USED_THIS_CYCLE: 0
IDEAS_TESTED_THIS_CYCLE: 0
HARD_STOP: false
```

Agent 重启时优先读取本文件、新增结果及其直接相关日志，不要在没有状态变化时
重新扫描整个项目。每次开始或结束 candidate、启动或完成任务、进入 review 或
触发 `HARD_STOP` 时，及时更新本文件。
